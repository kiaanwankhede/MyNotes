# Chapter 6: Build your first Joule skill (Joule Studio, Classic Edition)

*A hands-on path: environment, destinations, action projects, then one skill that calls two systems.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how a Joule skill is built from the ground up: test environment, destinations, action projects, skill inputs and outputs, actions, a message card, release, deploy and test
> - **You will build:** a `CreateBadge` skill that reads an employee from one system and creates a badge request in another
> - **Level:** beginner · **Time:** about 70 minutes for the three tutorials here (the whole group is 120 minutes with 5 tutorials)
> - **Source:** three SAP Developer tutorials by one author (SAP Developers), plus the group page, read 8 November 2026 with all their screenshots
> - **Builds on:** [Chapter 2](02-joule-studio.md) (what Joule Studio is) and [Chapter 5](05-setting-up-joule-by-product.md) (the BTP and identity setup)

**After this chapter you can:**

- Create a test environment and destinations, with the three properties actions need
- Build action projects from live OData services, then release and publish them
- Build a skill with inputs, two actions, a message and an end mapping
- Release, deploy and test the skill in the standalone assistant
- Name what the Design Console complains about, and why

> [!WARNING]
> **What this chapter is**
> - It follows **Joule Studio, Classic Edition**. Chapter 2 describes the newer Joule Studio; screens and names differ. Check which edition you have first
> - The tutorials use **mock services** (a mock S/4HANA business-partner API and a badge service), not a real S/4HANA system
> - I did not run any of it: no BTP account or Joule Studio tenant was used
> - The tutorials were created July 2025 and updated August 2026

> [!CAUTION]
> **Shared demo login in the source**
> - Step 8 of the skill tutorial prints a shared user name and password for the demo badge app. I did **not** copy them into these notes
> - SAP itself warns that the shared login can get locked and says you may skip that check

## 6.1 The big picture

```mermaid
flowchart LR
  E["1 Environment (Control Tower)"] --> D["2 Destinations (BTP cockpit)"]
  D --> A["3 Action projects (SAP Build Actions)"]
  A --> S["4 Joule skill (Joule Studio)"]
  S --> R["5 Release and deploy"]
  R --> T["6 Test in standalone Joule"]
```

- **Action** = one call to an external system (GET, POST, PATCH and so on); actions come from SAP Build Process Automation
- **Action project** = a bundle of actions made from an OData service
- **Destination** = the BTP connection to that service
- **Skill** = the Joule capability that uses the actions
- **Scenario:** get the employee (a business partner) from system one, then create a badge request in system two

## 6.2 Tutorial 1: environment and destinations

*Source: SAP Developer tutorial *Setup Environment and Connectivity for Joule Skills* (20 min, 4 steps; 13 images read).*

- **Prerequisite:** a BTP tenant set up for Joule and Joule Studio Classic Edition (the tutorial points to its set-up page and a Discovery Center mission; see 6.9)

**Step 1: environment.**

1. SAP Build Lobby, then **Control Tower**, then **Environments**
2. **Create**, give a name and description (the screenshot uses the name "tutorial")
3. Open the environment and its **Joule tab**
   - It is empty for now, and you cannot launch the standalone Joule Digital Assistant until a skill is deployed

**Step 2: destinations (BTP cockpit, Connectivity, Destinations).**

| Destination | Purpose |
|---|---|
| `S4HANA_MOCK` | Mock S/4HANA business partner OData API |
| `Badge_Service` | Mock third-party badge request OData service |

- Create from scratch, type HTTP, no authentication, then use **Check Connection**
- Add **three properties** to the destination:

| Key | Value |
|---|---|
| `sap.processautomation.enabled` | `true` |
| `sap.applicationdevelopment.actions.enabled` | `true` |
| `sap.build.usage` | `odata_gen` |

- The second destination is made with **Duplicate**, then a new name and URL
- The screenshots show the names prefixed with "tutorial_"

**Step 3: associate destinations with environments.**

- Control Tower, **Destinations**, **Add**, pick the destination, then **Specific Environments**
- Add **both** your environment and the **Public** environment
- Repeat for the second destination, then check that both show both environments

> [!IMPORTANT]
> **Quiz in the tutorial:** "Which additional parameters must be configured in your destinations?" The answer options were not visible in the page text; by the tutorial text it is the three properties above.

## 6.2a The same set-up as a 4-part workshop (SJ030)

*Source: SAP Community blog, Part 1 of 4, about 5 minutes (text and all 4 screenshots read).*

- **Series:** Part 1 environment setup, Part 2 actions with OData V4, Part 3 conversational skills, Part 4 process automation integration (parts 2–4 are **not read**)
- **Goal of Part 1:** a development environment so skills can reach S/4HANA Cloud
- **Steps:** Lobby → **Control Tower** → **Environments** → **Create** (name, description) → open it → **Joule** tab
- **Expect:** the tab is empty and you cannot launch the standalone assistant until you deploy a skill
- **Prerequisites:** a BTP tenant set up for Joule Studio; the S/4HANA destination set up first; basic destination knowledge
- **Same as 6.2:** this repeats the environment step of tutorial 1; it adds only the workshop plan

## 6.3 Tutorial 2: action projects

*Source: SAP Developer tutorial *Create Action Projects* (20 min, 3 steps; 21 images read). The skill group page lists it second.*

**Business partner project.**

1. Lobby, **Connectors**, **Actions**, **Create**
2. API source: **Live API**, then **OData Destinations**, then the `S4HANA_MOCK` tile
3. Name and describe the project (screenshot name: `tutorial_API_BUSINESS_PARTNER`)
4. Select `GET /A_BusinessPartner` and `GET /A_BusinessPartner('{BusinessPartner}')`, **Add**
5. For the action "Retrieves business partner data by using business partner number":
   - **Output tab:** keep only `BusinessPartner`, `FirstName`, `LastName`
   - **Test tab:** use business partner `1003764`, pick the right destination, **Test**, **Save**
6. Trim the output of the second action ("general data") the same way and test it
7. **Release**, then **Publish**

**Badge service project.**

1. Same start, but choose the `Badge_Service` tile (screenshot name: `tutorial_BadgeRequestsService`)
2. Select the **five** actions the screenshot marks; the project then shows 5 actions, and one of them is **Invoke action createBadge**
3. Open `POST Invoke action createBadge`:
   - **Output:** change the type of `badgeId` to **number**
   - **Input:** remove `processInstanceId`
4. **Save**, **Release**, **Publish**
5. **Test** with: status `NEW`, last name `Doe`, first name `John`, a community ID (an e-mail style value), business partner `1003764`

> [!IMPORTANT]
> **Quiz in the tutorial:** "True or False: you can only see your destination if it has been associated with the Public environment." The answer was not shown. From 6.2 the tutorial associates **both** the Public and your own environment, so treat "only Public" as doubtful and check it yourself.

## 6.4 Tutorial 3: the skill

*Source: SAP Developer tutorial *Use Joule Studio, Classic Edition to Create and Deploy a Joule Skill* (30 min, 9 steps; 43 images read).*

**Step 1: create the skill.**

- Lobby, **Create**, tile **Joule Skill** (the picker also shows other project types such as application and automated process)
- Name `CreateBadge`; description "Create a badge for an employee given the employee's ID"

> [!TIP]
> **The description matters:** the tutorial says Joule uses it to pick the right skill during a conversation.

**Step 2: inputs and outputs.**

- Open the Trigger panel and **turn off "Allow Joule to generate a response"**
- Parameters, **Configure** under Skill Inputs: `EmployeeID` (required), `Status`, `CommunityID`
- Skill Outputs: `Badge` (number), `Employee ID` (string), `Employee Name` (string), all required
- **Save**, then open the **Design Console**: it shows errors on purpose (see 6.5)

**Step 3: first action.**

- Add step (+) between Trigger and End, **Call Action**, **Browse All Actions**
- Pick `GET Retrieves business partner data by using business partner number`
- Create a **destination variable** `S4HANA_MOCK` and select it
- Input: map `BusinessPartner` to `EmployeeID` from the Skill Content pane

**Step 4: second action.**

- Add `POST Invoke action createBadge`; create destination variable `Badge_Service`
- Map the inputs from the skill inputs and the first action's output (the screenshot maps `businesspartnerId`, status, community ID and names)
- Check the outputs tree

**Step 5: the message.**

- Add **Send Message**, open the message editor
- Title "Badge Request"; text "Badge has been created for", then use the data-mapping `<>` picker to insert `badgeId` and `firstname`
- Choose an illustration, add a button "Go to Badge System" with a URL
- Preview: a card with the illustration, the text and the button

**Step 6: End.**

- Map the End outputs (Badge, Employee ID, Employee Name) to the action results

**Step 7: release and deploy.**

1. **Release** (version number, release notes), then **Show Project Version** to switch to the released version
2. **Deploy**, choose your environment
3. A **Define Variables** screen asks which real destination each variable uses: set `Badge_Service` and `S4HANA_MOCK` to your destinations
4. **Deploy**; a green confirmation follows

**Step 8: test.**

- Control Tower, Environments, your environment, **Joule** tab, **Launch**
- Prompt used: "Please create a badge for the employee with the ID 1003764. The badge status is NEW and his community ID is ..." (an e-mail style value)
- The reply is your **Badge Request card** with the "Go to Badge System" button
- The badge also appears in the OData service (filter by `badgeId`); the screenshot shows the JSON with fields like `badgeId` and `status`
- The badge app list shows the new request

> [!IMPORTANT]
> **Quiz in the tutorial:** "The Send Message activity in a Joule skill ..." The completion options were not visible. By step 5 it sends a card back to the user that you design.

## 6.5 What the Design Console tells you

- After step 2 it shows three errors, shown in the screenshot:
  - The **End** output is not connected
  - The skill must contain **at least one activity**
  - You switched off the generated response, so you **must add a Send Message** that describes the end of the skill
- **Why it matters:** these are the rules of a valid skill: connected outputs, at least one activity, and a closing message when Joule's own reply is off

## 6.5a Tutorial 4: filter an action (SJ027)

*Source: SAP Developer tutorial, 20 min, 7 steps (text and all 35 images read).*

- **Goal:** let the user pass a first name, so the action returns only matching business partners
- **Step 1: copy the action project**
  - Take the version published to the library, then **Versions → Save As New Project** (named `FilterBusinessPartners`)
  - On the `GET Retrieves business partner general data` action, **Input** tab: **Add → New Field**, Key and Label `FirstName`
  - Open the `$filter` value → **Condition Editor**: Column `FirstName`, Condition *equal to*, Criteria `${FirstName}`
  - Test with `Jane`, then **Save, Release, Publish**
- **Step 2: new skill** `SearchWithFirstName`
  - Description: retrieve employees with a given first name (John or Jane)
  - **Allow Joule to generate a response:** on
  - Input `FirstName` (required); output `Employees`, type Any, **List** ticked
- **Step 3:** add **Call Action**, choose the filtered action, destination variable `S4HANA_MOCK`, map `FirstName`
- **Step 4:** in **End**, map `Employees` to the action's results list
- **Step 5:** Release (1.0.0), **Show Project Version**, Deploy, map `S4HANA_MOCK`
- **Step 6:** test in standalone Joule, ask if "Jane" is in the system, then correct to John; a list of people appears and you can pick one for details
- **Quiz (step 7):** where do you configure the data mapping for Joule's generated reply? Answer options were not shown; by the tutorial it is the **End** element mapping
- **Why it matters:** the filter lives in the action; the skill only passes the input

> [!TIP]
> The "Choose what happens next" menu offers: Run Process, Call Action, Run Automation, Send Message, Launch Joule Skill, Check Condition.

## 6.5b Tutorial 5: run a process from a skill (SJ028)

*Source: SAP Developer tutorial, 30 min, 10 steps (text and all 46 images read).*

- **Idea:** a skill can start an SAP Build Process Automation process
- **Limit:** you can pass values **in**, but cannot get output **back**: "fire and forget"
- **Must do:** the process must be **released, deployed and published to the library** (publish is done in the Lobby, **Versions** tab → **Publish to Library**)

```mermaid
flowchart LR
  A[Process project] --> B[Release]
  B --> C[Deploy]
  C --> D[Publish to Library]
  D --> E[Skill: Run Process]
  E --> F[Send Message]
```

- **Steps 1–3: the process**
  - Lobby → Create → **Automated Process** → Process; name `InitiateSecurityChecksViaEmail`
  - Process `SendEmailToSecurity`; four required **Process Inputs**: EmployeeID, BadgeStatus, FirstName, LastName
  - Add an **Email** step (To, Subject `Lost Badge`, body built from the inputs by value binding)
  - Needs **email configured for Process Automation**
- **Steps 4–5: the skill** `BadgeSecurity`
  - Switch **off** Allow Joule to generate a response
  - Four required inputs matching the process; no skill outputs
- **Steps 6–7:** **Run Process → Browse All Processes** → add your process → map each input from the Skill Content panel; then **Send Message** with title "Security has been informed" and the parameters mapped in the text
- **Steps 8–9:** Release, Deploy, then Control Tower → Environments → your environment → **Joule** tab → Launch → New Conversation
  - Test sentence: report that the old badge of a named employee has status LOST
  - Check the run in **Monitoring > Process and Workflow Instances**
- **Quiz (step 10):** where do you choose "Publish to Library"? In the **Lobby** (project **Versions** tab)

> [!WARNING]
> If the process is not published to the library, **Browse All Processes** will not show it (you will see "No Process Available").

## 6.6 The rest of the group (not part of this chapter)

*From the group page (read; no images). Group: *Build Your First Joule Skill in Joule Studio, Classic Edition*, beginner, 120 minutes, 5 tutorials.*

| # | Tutorial | Time |
|---|---|---|
| 1 | Setup Environment and Connectivity for Joule Skills (6.2) | 20 min |
| 2 | Create Action Projects (6.3) | 20 min |
| 3 | Create and Deploy a Joule Skill (6.4) | 30 min |
| 4 | Create a Filter in an Action Project (6.5a) | 20 min |
| 5 | Consume an Automated Process in a Joule Skill (6.5b) | 30 min |

- Tutorials 4 and 5 are now covered in 6.5a and 6.5b

## 6.7 Added by Claude, not from the sources

*My own reasoning; the tutorials do not say it.*

- **Debug order when a skill fails:** (1) Design Console, (2) action test tab, (3) destination **Check Connection**, (4) destination properties (the three keys), (5) variable mapping at deploy
- **Naming habit:** use the same name for the destination and the destination variable, so the deploy screen is obvious
- **Release every action project before the skill uses it:** a skill can only pick released and published actions
- **Mock first, real later:** the tutorial's mock services let you learn the screens; swapping to a real system mostly changes the destination and its authentication

## 6.8 Interview corner

**What interviewers listen for:** you can walk the chain environment, destination, action, skill, deploy, and name where each break shows up.

<details class="qa"><summary>🟢 1. What is an action in Joule Studio?</summary>

- A call to an external system (GET, POST and so on), built from an OData service in an action project
- A skill calls actions

*Stronger answer:* actions come from SAP Build Process Automation and must be released and published before use.
</details>

<details class="qa"><summary>🟢 2. Which properties must a destination have for actions?</summary>

- `sap.processautomation.enabled` = true, `sap.applicationdevelopment.actions.enabled` = true, `sap.build.usage` = `odata_gen`

*Stronger answer:* the destination must also be associated with your environment (and Public) in Control Tower.
</details>

<details class="qa"><summary>🟡 3. Why write a good skill description?</summary>

- Joule uses it to choose the skill during a conversation

*Stronger answer:* describe the input it needs ("given the employee's ID") so matching is precise.
</details>

<details class="qa"><summary>🟡 4. What is a destination variable and where is it set?</summary>

- A name used inside the skill; at deploy time you map it to a real destination

*Stronger answer:* this keeps the skill portable between systems and environments.
</details>

<details class="qa"><summary>🔴 5. The Design Console says "you must add a Send Message". Why?</summary>

- You switched off "Allow Joule to generate a response", so the skill must send its own closing message

*Stronger answer:* name the other two checks (End outputs connected, at least one activity).
</details>

<details class="qa"><summary>🔴 6. The skill works in the designer but the standalone assistant cannot find it. What do you check?</summary>

- Was the project released and the released version deployed?
- Was it deployed to the environment you are launching from?
- Are the variables mapped to destinations that are associated with that environment?

*Stronger answer:* check the Joule tab of the environment: it stays empty until a skill is deployed.
</details>

> [!TIP]
> **🧩 Design question**
> HR wants a skill that, given an employee ID, reads the employee from one system and opens a ticket in another.
> - **Sketch:** the environment, the two destinations, the two action projects and the skill steps.
> - **Say out loud:** what you map from the first action into the second, and what the user sees at the end.

## 6.9 Discovery Center missions (links, not read)

- [Set up Joule Studio and start with Joule skills](https://discovery-center.cloud.sap/missiondetail/4651/4940/): the mission the tutorials point to for the tenant prerequisite
- [Build custom Joule skills for SAP and non-SAP systems](https://discovery-center.cloud.sap/missiondetail/4643/)

## 6.10 Cheat sheet

| Topic | Remember |
|---|---|
| Order | Environment, destinations, actions, skill, release, deploy, test |
| Destination keys | `sap.processautomation.enabled`, `sap.applicationdevelopment.actions.enabled`, `sap.build.usage = odata_gen` |
| Associate | Destination to your environment and Public |
| Actions | Output trimmed, tested, released, published |
| Skill | Description, inputs, outputs, actions, Send Message, End |
| Generated response off | Send Message is required |
| Deploy | Map destination variables to real destinations |
| Test | Environment, Joule tab, Launch |

## Screenshots and figures from the sources

*Images saved from the source pages, in the order they appear there.*

### Images: Sales order queries blog (SAP Community)

*Source: [Sales order queries blog (SAP Community)](https://community.sap.com/t5/artificial-intelligence-blogs-posts/building-joule-skills-for-sales-order-queries-in-s-4hana-cloud-part-1/bc-p/14267490)*

![Sales order skill blog, figure 1](images/ch06-s1-salesorderblog-01.png)

![Sales order skill blog, figure 2](images/ch06-s1-salesorderblog-02.png)

![Sales order skill blog, figure 3](images/ch06-s1-salesorderblog-03.png)

![Sales order skill blog, figure 4](images/ch06-s1-salesorderblog-04.png)

![Sales order skill blog, figure 5](images/ch06-s1-salesorderblog-05.png)

![Sales order skill blog, figure 6](images/ch06-s1-salesorderblog-06.png)

![Sales order skill blog, figure 7](images/ch06-s1-salesorderblog-07.png)

### Images: Tutorial: Set up environment and connectivity

*Source: [Tutorial: Set up environment and connectivity](https://developers.sap.com/tutorials/joulestudio-skill-environment-setup)*

![Environment setup tutorial, figure 1](images/ch06-s3-envsetup-01.png)

![Environment setup tutorial, figure 2](images/ch06-s3-envsetup-02.png)

![Environment setup tutorial, figure 3](images/ch06-s3-envsetup-03.webp)

![Environment setup tutorial, figure 4](images/ch06-s3-envsetup-04.webp)

![Environment setup tutorial, figure 5](images/ch06-s3-envsetup-05.webp)

![Environment setup tutorial, figure 6](images/ch06-s3-envsetup-06.webp)

![Environment setup tutorial, figure 7](images/ch06-s3-envsetup-07.webp)

![Environment setup tutorial, figure 8](images/ch06-s3-envsetup-08.webp)

![Environment setup tutorial, figure 9](images/ch06-s3-envsetup-09.webp)

![Environment setup tutorial, figure 10](images/ch06-s3-envsetup-10.webp)

![Environment setup tutorial, figure 11](images/ch06-s3-envsetup-11.webp)

![Environment setup tutorial, figure 12](images/ch06-s3-envsetup-12.webp)

![Environment setup tutorial, figure 13](images/ch06-s3-envsetup-13.webp)

### Images: Tutorial: Filter an action

*Source: [Tutorial: Filter an action](https://developers.sap.com/tutorials/joulestudio-skill-action-filter)*

![Action filter tutorial, figure 1](images/ch06-s5-actionfilter-01.webp)

![Action filter tutorial, figure 2](images/ch06-s5-actionfilter-02.webp)

![Action filter tutorial, figure 3](images/ch06-s5-actionfilter-03.webp)

![Action filter tutorial, figure 4](images/ch06-s5-actionfilter-04.webp)

![Action filter tutorial, figure 5](images/ch06-s5-actionfilter-05.webp)

![Action filter tutorial, figure 6](images/ch06-s5-actionfilter-06.webp)

![Action filter tutorial, figure 7](images/ch06-s5-actionfilter-07.webp)

![Action filter tutorial, figure 8](images/ch06-s5-actionfilter-08.webp)

![Action filter tutorial, figure 9](images/ch06-s5-actionfilter-09.webp)

![Action filter tutorial, figure 10](images/ch06-s5-actionfilter-10.webp)

![Action filter tutorial, figure 11](images/ch06-s5-actionfilter-11.webp)

![Action filter tutorial, figure 12](images/ch06-s5-actionfilter-12.webp)

![Action filter tutorial, figure 13](images/ch06-s5-actionfilter-13.webp)

![Action filter tutorial, figure 14](images/ch06-s5-actionfilter-14.webp)

![Action filter tutorial, figure 15](images/ch06-s5-actionfilter-15.webp)

![Action filter tutorial, figure 16](images/ch06-s5-actionfilter-16.webp)

![Action filter tutorial, figure 17](images/ch06-s5-actionfilter-17.webp)

![Action filter tutorial, figure 18](images/ch06-s5-actionfilter-18.webp)

![Action filter tutorial, figure 19](images/ch06-s5-actionfilter-19.webp)

![Action filter tutorial, figure 20](images/ch06-s5-actionfilter-20.webp)

![Action filter tutorial, figure 21](images/ch06-s5-actionfilter-21.webp)

![Action filter tutorial, figure 22](images/ch06-s5-actionfilter-22.webp)

![Action filter tutorial, figure 23](images/ch06-s5-actionfilter-23.webp)

![Action filter tutorial, figure 24](images/ch06-s5-actionfilter-24.webp)

![Action filter tutorial, figure 25](images/ch06-s5-actionfilter-25.webp)

![Action filter tutorial, figure 26](images/ch06-s5-actionfilter-26.webp)

![Action filter tutorial, figure 27](images/ch06-s5-actionfilter-27.webp)

![Action filter tutorial, figure 28](images/ch06-s5-actionfilter-28.webp)

![Action filter tutorial, figure 29](images/ch06-s5-actionfilter-29.webp)

![Action filter tutorial, figure 30](images/ch06-s5-actionfilter-30.webp)

![Action filter tutorial, figure 31](images/ch06-s5-actionfilter-31.webp)

![Action filter tutorial, figure 32](images/ch06-s5-actionfilter-32.webp)

![Action filter tutorial, figure 33](images/ch06-s5-actionfilter-33.webp)

![Action filter tutorial, figure 34](images/ch06-s5-actionfilter-34.webp)

![Action filter tutorial, figure 35](images/ch06-s5-actionfilter-35.webp)

### Images: Tutorial: Create a skill

*Source: [Tutorial: Create a skill](https://developers.sap.com/tutorials/joulestudio-skill-create)*

![Skill create tutorial, figure 1](images/ch06-s6-skillcreate-01.webp)

![Skill create tutorial, figure 2](images/ch06-s6-skillcreate-02.webp)

![Skill create tutorial, figure 3](images/ch06-s6-skillcreate-03.webp)

![Skill create tutorial, figure 4](images/ch06-s6-skillcreate-04.webp)

![Skill create tutorial, figure 5](images/ch06-s6-skillcreate-05.webp)

![Skill create tutorial, figure 6](images/ch06-s6-skillcreate-06.webp)

![Skill create tutorial, figure 7](images/ch06-s6-skillcreate-07.webp)

![Skill create tutorial, figure 8](images/ch06-s6-skillcreate-08.webp)

![Skill create tutorial, figure 9](images/ch06-s6-skillcreate-09.webp)

![Skill create tutorial, figure 10](images/ch06-s6-skillcreate-10.webp)

![Skill create tutorial, figure 11](images/ch06-s6-skillcreate-11.webp)

![Skill create tutorial, figure 12](images/ch06-s6-skillcreate-12.webp)

![Skill create tutorial, figure 13](images/ch06-s6-skillcreate-13.webp)

![Skill create tutorial, figure 14](images/ch06-s6-skillcreate-14.webp)

![Skill create tutorial, figure 15](images/ch06-s6-skillcreate-15.webp)

![Skill create tutorial, figure 16](images/ch06-s6-skillcreate-16.webp)

![Skill create tutorial, figure 17](images/ch06-s6-skillcreate-17.webp)

![Skill create tutorial, figure 18](images/ch06-s6-skillcreate-18.webp)

![Skill create tutorial, figure 19](images/ch06-s6-skillcreate-19.webp)

![Skill create tutorial, figure 20](images/ch06-s6-skillcreate-20.webp)

![Skill create tutorial, figure 21](images/ch06-s6-skillcreate-21.webp)

![Skill create tutorial, figure 22](images/ch06-s6-skillcreate-22.webp)

![Skill create tutorial, figure 23](images/ch06-s6-skillcreate-23.webp)

![Skill create tutorial, figure 24](images/ch06-s6-skillcreate-24.webp)

![Skill create tutorial, figure 25](images/ch06-s6-skillcreate-25.webp)

![Skill create tutorial, figure 26](images/ch06-s6-skillcreate-26.webp)

![Skill create tutorial, figure 27](images/ch06-s6-skillcreate-27.webp)

![Skill create tutorial, figure 28](images/ch06-s6-skillcreate-28.webp)

![Skill create tutorial, figure 29](images/ch06-s6-skillcreate-29.webp)

![Skill create tutorial, figure 30](images/ch06-s6-skillcreate-30.webp)

![Skill create tutorial, figure 31](images/ch06-s6-skillcreate-31.webp)

![Skill create tutorial, figure 32](images/ch06-s6-skillcreate-32.webp)

![Skill create tutorial, figure 33](images/ch06-s6-skillcreate-33.webp)

![Skill create tutorial, figure 34](images/ch06-s6-skillcreate-34.webp)

![Skill create tutorial, figure 35](images/ch06-s6-skillcreate-35.webp)

![Skill create tutorial, figure 36](images/ch06-s6-skillcreate-36.webp)

![Skill create tutorial, figure 37](images/ch06-s6-skillcreate-37.webp)

![Skill create tutorial, figure 38](images/ch06-s6-skillcreate-38.webp)

![Skill create tutorial, figure 39](images/ch06-s6-skillcreate-39.webp)

![Skill create tutorial, figure 40](images/ch06-s6-skillcreate-40.webp)

![Skill create tutorial, figure 41](images/ch06-s6-skillcreate-41.webp)

![Skill create tutorial, figure 42](images/ch06-s6-skillcreate-42.webp)

![Skill create tutorial, figure 43](images/ch06-s6-skillcreate-43.webp)

### Images: Tutorial: Skill process

*Source: [Tutorial: Skill process](https://developers.sap.com/tutorials/joulestudio-skill-process)*

![Skill process tutorial, figure 1](images/ch06-s7-skillprocess-01.webp)

![Skill process tutorial, figure 2](images/ch06-s7-skillprocess-02.webp)

![Skill process tutorial, figure 3](images/ch06-s7-skillprocess-03.webp)

![Skill process tutorial, figure 4](images/ch06-s7-skillprocess-04.webp)

![Skill process tutorial, figure 5](images/ch06-s7-skillprocess-05.webp)

![Skill process tutorial, figure 6](images/ch06-s7-skillprocess-06.webp)

![Skill process tutorial, figure 7](images/ch06-s7-skillprocess-07.webp)

![Skill process tutorial, figure 8](images/ch06-s7-skillprocess-08.webp)

![Skill process tutorial, figure 9](images/ch06-s7-skillprocess-09.webp)

![Skill process tutorial, figure 10](images/ch06-s7-skillprocess-10.webp)

![Skill process tutorial, figure 11](images/ch06-s7-skillprocess-11.webp)

![Skill process tutorial, figure 12](images/ch06-s7-skillprocess-12.webp)

![Skill process tutorial, figure 13](images/ch06-s7-skillprocess-13.webp)

![Skill process tutorial, figure 14](images/ch06-s7-skillprocess-14.webp)

![Skill process tutorial, figure 15](images/ch06-s7-skillprocess-15.webp)

![Skill process tutorial, figure 16](images/ch06-s7-skillprocess-16.webp)

![Skill process tutorial, figure 17](images/ch06-s7-skillprocess-17.webp)

![Skill process tutorial, figure 18](images/ch06-s7-skillprocess-18.webp)

![Skill process tutorial, figure 19](images/ch06-s7-skillprocess-19.webp)

![Skill process tutorial, figure 20](images/ch06-s7-skillprocess-20.webp)

![Skill process tutorial, figure 21](images/ch06-s7-skillprocess-21.webp)

![Skill process tutorial, figure 22](images/ch06-s7-skillprocess-22.webp)

![Skill process tutorial, figure 23](images/ch06-s7-skillprocess-23.webp)

![Skill process tutorial, figure 24](images/ch06-s7-skillprocess-24.webp)

![Skill process tutorial, figure 25](images/ch06-s7-skillprocess-25.webp)

![Skill process tutorial, figure 26](images/ch06-s7-skillprocess-26.webp)

![Skill process tutorial, figure 27](images/ch06-s7-skillprocess-27.webp)

![Skill process tutorial, figure 28](images/ch06-s7-skillprocess-28.webp)

![Skill process tutorial, figure 29](images/ch06-s7-skillprocess-29.webp)

![Skill process tutorial, figure 30](images/ch06-s7-skillprocess-30.webp)

![Skill process tutorial, figure 31](images/ch06-s7-skillprocess-31.webp)

![Skill process tutorial, figure 32](images/ch06-s7-skillprocess-32.webp)

![Skill process tutorial, figure 33](images/ch06-s7-skillprocess-33.webp)

![Skill process tutorial, figure 34](images/ch06-s7-skillprocess-34.webp)

![Skill process tutorial, figure 35](images/ch06-s7-skillprocess-35.webp)

![Skill process tutorial, figure 36](images/ch06-s7-skillprocess-36.webp)

![Skill process tutorial, figure 37](images/ch06-s7-skillprocess-37.webp)

![Skill process tutorial, figure 38](images/ch06-s7-skillprocess-38.webp)

![Skill process tutorial, figure 39](images/ch06-s7-skillprocess-39.webp)

![Skill process tutorial, figure 40](images/ch06-s7-skillprocess-40.webp)

![Skill process tutorial, figure 41](images/ch06-s7-skillprocess-41.webp)

![Skill process tutorial, figure 42](images/ch06-s7-skillprocess-42.webp)

![Skill process tutorial, figure 43](images/ch06-s7-skillprocess-43.webp)

![Skill process tutorial, figure 44](images/ch06-s7-skillprocess-44.webp)

![Skill process tutorial, figure 45](images/ch06-s7-skillprocess-45.webp)

![Skill process tutorial, figure 46](images/ch06-s7-skillprocess-46.webp)

## Recap

- A skill is built on actions, which are built on destinations, which live in an environment
- The description lets Joule choose your skill
- Design Console errors are the checklist for a valid skill
- Release and deploy before you test in the standalone assistant

## Practice

1. List the three destination properties from memory.
2. Rebuild the chain for a different pair of systems and write down each name.
3. Write the three Design Console errors and the fix for each.
4. Draft a better skill description for the badge skill and say why.

## How this chapter was checked

- **Read fully:** five tutorials (text and all images: 13, 21, 43, 35 and 46) and the group page (no images). I opened all collapsed steps
- **Not read:** workshop parts 2–4 of SJ030 (separate pages), the quiz answer options (they were not shown on the page), the tutorials' linked set-up page and Discovery Center missions, the "related learning" lists
- **Not run:** no tenant or account was used; nothing was built or tested
- **Dated points:** tutorials created July 2025, updated August 2026; screens may differ in a newer edition
- **Omitted on purpose:** a shared demo login printed in step 8 of the skill tutorial (see the caution box)
- **Small text:** some screenshot text was too small to read; I describe only what is readable

## Sources and further reading

- SAP Developer tutorial, *Setup Environment and Connectivity for Joule Skills* (text and images read): https://developers.sap.com/tutorials/joulestudio-skill-environment-setup
- SAP Developer tutorial, *Create Action Projects* (text and images read): https://developers.sap.com/tutorials/joulestudio-skill-action-create
- SAP Developer tutorial, *Use Joule Studio, Classic Edition to Create and Deploy a Joule Skill* (text and images read): https://developers.sap.com/tutorials/joulestudio-skill-create
- SAP Developer group page, *Build Your First Joule Skill in Joule Studio, Classic Edition* (read): https://developers.sap.com/tutorials/group-build-your-first-joule-skill-in-joule-studio-classic-edition
- SAP Developer tutorial, *Create a Filter in an Action Project* (read): https://developers.sap.com/tutorials/joulestudio-skill-action-filter
- SAP Developer tutorial, *Consume an Automated Process in a Joule Skill* (read): https://developers.sap.com/tutorials/joulestudio-skill-process
- SAP Community blog, *Building Joule Skills for Sales Order Queries in S/4HANA Cloud, Part 1* (read): https://community.sap.com/t5/artificial-intelligence-blogs-posts/building-joule-skills-for-sales-order-queries-in-s-4hana-cloud-part-1/bc-p/14267490
- Discovery Center missions: see 6.9

---

*Previous: [Chapter 5: Setting up Joule product by product](05-setting-up-joule-by-product.md)*
*Next: [Chapter 7: Your first Joule agent](07-first-joule-agent.md)*
