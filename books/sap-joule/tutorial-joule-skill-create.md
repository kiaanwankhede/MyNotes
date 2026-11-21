# Tutorial: Create and deploy a Joule skill

*Build a skill that chains two API calls: it looks up an employee in the SAP system, creates a badge for them in a second system, and confirms with a custom message.*

> [!NOTE]
> **📍 At a glance**
> - **SAP tutorial:** [Use Joule Studio, Classic Edition to Create and Deploy a Joule Skill](https://developers.sap.com/tutorials/joulestudio-skill-create.html) (part 3 of 5)
> - **You will build:** the skill *CreateBadge* with inputs, two actions, a message card and outputs, deployed to your environment
> - **You need:** the destinations from [tutorial 5](tutorial-joule-skill-setup.md) and the published action projects from [tutorial 6](tutorial-joule-action-projects.md)
> - **Level:** beginner · **Time:** about 30 minutes (SAP's estimate)
> - **Concepts:** [Joule Studio Classic](joule-studio-classic.md), 3.4 and 3.8
> - **Last checked:** 21 Nov 2026

**After this tutorial you can:**

- Define a skill's inputs and outputs, and switch off Joule's own reply
- Chain two actions, each with its own destination variable, and map data between them
- Release, deploy and test a skill in the standalone Joule assistant

## 7.1 What you build

```mermaid
flowchart LR
    T["Trigger<br/>inputs: EmployeeID*, Status, CommunityID"] --> A1["Action 1 · S4HANA_MOCK<br/>get business partner"]
    A1 -- "success" --> A2["Action 2 · Badge_Service<br/>createBadge"]
    A2 -- "success" --> M["Send Message<br/>'Badge has been created for …'"]
    M --> E["End<br/>outputs: Badge, Employee ID, Employee Name"]
```

## 7.2 Steps

*Steps and screenshots adapted from SAP's tutorial (© SAP SE, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)). Steps reworded; screenshots resized; personal data blurred in two of them.*

### Step 1: Create the project and the skill

1. Open the **SAP Build lobby** and choose **Create**.

    ![SAP Build lobby (Welcome to SAP Build): Lobby selected and the Create button](images/t23-01-lobby.png)

2. Under *Objective*, select the Joule tile and choose **Next**.
   - SAP's text calls it *Joule Skill*; newer screens show *Joule Agent and Skill*.

    ![Create Project, step Objective: four tiles, with Joule Agent and Skill selected, then Next](images/t23-02-lobby-create.png)

3. Enter the project name `CreateBadge` and the description "Create a badge for an employee given the employee's ID". Choose **Review**, then **Create**.

    ![Create Project, step Name: project name and description, then Review](images/t23-03-create-project.png)

4. Joule Studio opens on the project's *Overview*. Choose **Create → Joule Skill**.
   - The same menu offers *Joule Agent* (tutorial 10) and *Data Type*.

    ![Project overview with no artifacts yet; the Create menu open, with Joule Skill marked](images/t23-04-create-skill.png)

5. Enter the skill name `CreateBadge` and the same description, then choose **Create**.
   - **The description matters most.** Joule reads it to decide which skill fits the user's request.

    ![Create Joule Skill dialog: name CreateBadge, identifier createBadge, description, then Create](images/t23-05-create-skill-2.png)

6. The editor shows the empty skill: a **Trigger** ("When a scenario is called") and an **End**.

    ![The new skill in the editor: a Trigger node joined to an End node](images/t23-06-create-new.png)

### Step 2: Define the inputs and outputs

1. Click **Trigger** (or **<<** at the right) to open the side panel.
2. On the *General* tab, switch off **Allow Joule to generate a response**.
   - This skill sends its own message card instead (step 5).
   - *Allow skill to be started directly by a user* stays on, as in SAP's screenshot.

    ![Trigger side panel, General tab: Allow Joule to generate a response switched off; direct start by a user left on](images/t23-07-trigger.png)

3. Open the **Parameters** tab and choose **Configure** next to *Skill Inputs*.

    ![Parameters tab: Skill Inputs (none yet) with its Configure button, and Skill Outputs below](images/t23-08-parameters.png)

4. Choose **Add Input** three times and fill in the rows, then choose **Apply**:

    | Name | Description | Required |
    |---|---|---|
    | `EmployeeID` | Employee ID | yes |
    | `Status` | Status | no |
    | `CommunityID` | Community ID | no |

    ![Configure Skill Inputs: EmployeeID (required), Status and CommunityID, then Apply](images/t23-09-inputs-configure.png)

5. Choose **Configure** next to *Skill Outputs*, choose **Add Output** three times, fill in the rows, then **Apply**:

    | Name | Description | Type | Required |
    |---|---|---|---|
    | `Badge` | Badge | Number | yes |
    | `Employee ID` | Employee ID | String | yes |
    | `Employee Name` | Employee name | String | yes |

    ![Configure Skill Outputs: Badge (Number), Employee ID and Employee Name (String), all required, then Apply](images/t23-10-outputs-configure.png)

6. Expand **Skill Outputs** to check the three outputs, then close the side panel and choose **Save**.

    ![Parameters tab: Skill Outputs expanded, showing Badge, Employee ID and Employee Name, each marked required](images/t23-11-outputs-configured.png)

7. Open the **Design Console** at the bottom. It lists two errors and a warning; this is expected for now:
   - the End step's outputs are not connected
   - the skill has no activity yet
   - the generated response is off, so a *Send Message* step is needed

    ![Design Console: two errors (End output not connected; no activity) and one warning (add a send-message step)](images/t23-12-errors.png)

8. Close the Design Console.

### Step 3: Add the first action (look up the employee)

1. Choose the **+** between *Trigger* and *End*, then **Call Action**.

    ![Choose what happens next: Run Process, Call Action (marked), Run Automation, Send Message, Launch Joule Skill, Check Condition](images/t23-13-firstaction1.png)

2. Choose **Browse All Actions**.

    ![The Action panel: Browse All Actions marked, Browse All RFC Actions below, and no actions added yet](images/t23-14-firstaction2.png)

3. Find **GET Retrieves business partner data by using business partner number** and choose **Add** next to it.

    ![Browse library: the published actions from both projects; the single-partner GET action marked](images/t23-15-firstaction3.png)

4. In the action's side panel, open **Destination Variable** and choose **+ Create Destination Variable**.

    ![The action step's side panel: Destination Variable is empty (Must not be empty), with Create Destination Variable marked](images/t23-16-firstaction4.png)

5. Enter the identifier `S4HANA_MOCK` and a description such as "BusinessPartner API", then **Create**.
   - The variable is only a placeholder. You pick the real destination when you test or deploy.

    ![Create Destination Variable: identifier S4HANA_MOCK, description BusinessPartner API, type Destination, then Create](images/t23-17-firstaction5.png)

6. Select `S4HANA_MOCK` as the step's destination variable.

    ![The action step's General tab with S4HANA_MOCK selected as destination variable](images/t23-18-firstaction6.png)

7. Open the **Inputs** tab and click the `BusinessPartner` field. In the *Skill Content* pane, under *Skill Inputs*, choose **EmployeeID**.

    ![Inputs tab: BusinessPartner mapped to EmployeeID, picked from Skill Inputs in the Skill Content pane](images/t23-19-firstaction7.png)

8. Open the **Outputs** tab and expand the tree: `result → A_BusinessPartnerType` with `BusinessPartner`, `FirstName`, `LastName`.
9. Close the panel and choose **Save**.

    ![Outputs tab of the first action: result > A_BusinessPartnerType with the three fields; close, then Save](images/t23-20-firstaction8.png)

### Step 4: Add the second action (create the badge)

1. Choose the **+** between the first action and *End*, then **Call Action**.

    ![The flow with the first action in place; Choose what happens next opened below it, Call Action marked](images/t23-21-secondaction2.png)

2. Choose **Browse All Actions**.

    ![Call Action panel: Browse All Actions marked; the two business partner actions listed as available](images/t23-22-secondaction3.png)

3. Find **POST Invoke action createBadge** and choose **Add** next to it.

    ![Browse library with POST Invoke action createBadge marked](images/t23-23-secondaction3b.png)

4. Open **Destination Variable** and choose **+ Create Destination Variable**.

    ![createBadge step's side panel: destination list shows S4HANA_MOCK, and Create Destination Variable is marked](images/t23-24-secondaction4.png)

5. Enter the identifier `Badge_Service` and a description such as "Third-party badge service", then **Create**. Select it for this step.

    ![Create Destination Variable: identifier Badge_Service, description Third-party badge service, then Create](images/t23-25-secondaction5.png)

6. Open the **Inputs** tab, click `businesspartnerId`, and map all five inputs from the *Skill Content* pane:

    | createBadge input | Comes from |
    |---|---|
    | `businesspartnerId` | first action → `BusinessPartner` |
    | `communityId` | skill input `CommunityID` |
    | `firstname` | first action → `FirstName` |
    | `lastname` | first action → `LastName` |
    | `status` | skill input `Status` |

    ![Inputs of createBadge mapped: three fields from the first action's result, two from the skill inputs](images/t23-26-secondaction6.png)

7. Open **Outputs** and expand `result`: it includes `ID`, `badgeId` (a number, as set in tutorial 6), the names and timestamps.
8. Close the panel and choose **Save**.

    ![Outputs tab of createBadge: result with ID, badgeId (#, a number), businesspartnerId, names and timestamps](images/t23-27-secondaction7.png)

### Step 5: Add the message card

1. Choose the **+** between the second action and *End*, then **Send Message**.

    ![Choose what happens next after createBadge, with Send Message marked](images/t23-28-sendmessage.png)

2. In the step's side panel, choose **Open Message Editor**.

    ![Send Message step selected in the flow; its side panel with the Open Message Editor button](images/t23-29-sendmessage-2.png)

3. The editor shows *Message Configuration* on the left and a live *Preview* on the right. The message type is *Illustrated Message*.

    ![Edit User Interaction: Illustrated Message type, empty Title and Text, an illustration list, and Add Button](images/t23-30-messageeditor.png)

4. **Title:** `Badge Request`.
5. **Text:** type "Badge has been created for". Use the **<>** button (data mapping) to insert:
   - `badgeId` from the createBadge result, after the word "Badge"
   - `firstname` from the createBadge result, at the end

    ![Data Mapping open from the Text field: badgeId and firstname marked under the createBadge result](images/t23-31-message-firstname.png)

6. **Illustration:** pick one that fits, for example *Add People*.
7. Choose **Add Button**. Title `Go to Badge System`; URL: the badge-system address given on SAP's page.
8. Check the preview, then choose **Save**. Close the side panel and choose **Save** again.

    ![Finished message: title, text with the two mapped values, Add People illustration, and a Go to Badge System button in the preview](images/t23-32-message-finished.png)

### Step 6: Map the outputs at End

1. Click **End**. For each skill output, click the field and pick the value from the createBadge result:

    | Skill output | Value |
    |---|---|
    | `Badge` | `badgeId` |
    | `Employee ID` | `businesspartnerId` |
    | `Employee Name` | `firstname` |

2. Close the side panel and choose **Save**.

    ![End step: Badge, Employee ID and Employee Name mapped from the createBadge result, then Save](images/t23-33-end-configuration.png)

### Step 7: Release and deploy

1. Choose **Release** at the top, then **Release** in the dialog (version 1.0.0).

    ![Release Project dialog over the skill: version 1.0.0 and the Release button](images/t23-34-project-release.png)

2. In the green message, choose **Show project version** to switch to the released version.

    ![Message: CreateBadge 1.0.0 released, with the Show project version link](images/t23-35-project-released.png)

3. Choose **Deploy**, select your environment, and choose **Deploy**.

    ![Released project: Deploy, then Choose an Environment with tutorial selected (Joule Digital Assistant: Standalone)](images/t23-36-project-deploy-environment.png)

4. In *Define Variables*, choose the real destination for each variable, then **Deploy**:
   - `Badge_Service` → your `Badge_Service` destination
   - `S4HANA_MOCK` → your `S4HANA_MOCK` destination

    ![Define Variables: a real destination chosen for Badge_Service and for S4HANA_MOCK, then Deploy](images/t23-37-project-deploy-variables.png)

5. The project now shows **Deployed** and **Active**.

    ![Project overview: version 1.0.0 Deployed and Active, with the CreateBadge skill listed](images/t23-38-project-deployed.png)

### Step 8: Test in the standalone assistant

1. In the lobby choose **Control Tower → Environments**, open your environment and its **Joule** tab.
   - `CreateBadge` 1.0.0 is now listed under *Environment Capabilities*. Choose **Launch**.

    ![The environment's Joule tab now lists CreateBadge 1.0.0; the Launch button is marked](images/t23-39-assistant-launch.png)

2. The standalone Joule opens with a new conversation.

    ![Standalone Joule: How can I help you?, and the message box (the user's name is blurred)](images/t23-40-conversation-start.png)

3. Send: *"Please create a badge for the employee with the ID 1003764. The badge status is NEW and his community ID is john.doe@bestrunsap.com"*.
4. Joule runs the skill and shows your message card with the new badge number.

    ![Joule's reply: the Badge Request card with badge 50671 for John, and the Go to Badge System button](images/t23-41-conversation-end.png)

5. **Check the badge without logging on:** open this address in a browser, with your badge ID in place of `34`:
   - `https://badges.cfapps.eu10.hana.ondemand.com/service/BadgeRequests/Badges?$filter=badgeId%20eq%2034`
   - It returns the badge record from the OData service.

    ![Example OData result for one badge: createdAt, ID, badgeId (arrow), names, businesspartnerId and status](images/t23-42-checkbadgeodata.png)

6. **Or open the badge system** with *Go to Badge System*. SAP's page gives a shared demo login for it, which is not copied here.
   - SAP warns that the shared login can get locked; if it is, use the OData check above.

    ![Access Pro Systems badge app: badge requests for john.doe, the new one with Badge ID 50671 marked (a photo in the header is blurred)](images/t23-43-accessprosystems.png)

## 7.3 Why it works

- **Inputs** come from the chat as text; Joule fills them in the *resolving input slots* step, and asks for `EmployeeID` because it is required (3.4).
- **Two destination variables** keep the skill independent of real systems; you choose them at test and deploy time.
- **Outputs** make the skill usable by agents and other skills. The message card is only for users who call the skill directly; inside an agent it does not run (3.5).

> [!NOTE]
> **Your own message, or Joule's?**
> - This tutorial switches off *Allow Joule to generate a response* and writes a fixed message card.
> - The lecturer called that a process-automation habit. For skills that agents will use, leave it on, since agents read only the outputs anyway.
> - Tutorial 8 shows the other way, with Joule writing the reply.

## 7.4 Common mistakes (seen in class)

| What you see | Why | Fix |
|---|---|---|
| Action 2 cannot find the business partner fields | Action 2 was added on the error (4XX) branch of action 1 | Delete it and add it on the success branch, or just above End |
| 404 from the badge service | The two destinations were swapped when testing | `S4HANA_MOCK` for the business partner action, `Badge_Service` for createBadge |
| *result* cannot be bound in End | The output type does not match the action's success schema | Pick the schema of the same action, ending in `200` |
| *Test* is missing | You are looking at the released version | Switch the version back to *editable* |
| A field cannot be mapped (greyed out) | Text input into a number field | *Apply formula* and convert, for example string to number |

- **In class**, learners skipped release and deploy and used *Test* from the editable version, picking the destinations there. Deployment came later.

## 7.5 The same steps with Northwind (Lecture 11)

- *Get Orders:* one action, no inputs, the output bound to the orders schema.
- *Get customer by key:* a required `CustomerID` input mapped to the action's key, so Joule asked for the ID when it was missing.
- *Top N:* an optional "number of orders to return" input, converted to a number and mapped to `$top`.

> [!IMPORTANT]
> **🏭 In production**
> - Skills that create data should run inside an agent with *Require user confirmation* switched on (3.5), so a person sees the badge request before it is sent.
> - Keep one action per skill where you can; chained calls are harder to test and to reuse.
>
> *Added by Claude*

## Check yourself

<details class="qa"><summary>Why does the skill ask for the employee ID when you leave it out?</summary>

- `EmployeeID` is a required input, so Joule must fill it before running
- It asks the user in a follow-up question

</details>

<details class="qa"><summary>Why add the second action on the success path?</summary>

- Only the success path carries the business partner data that action 2 needs
- The error path carries the error payload

</details>

## How this page was checked

- **SAP tutorial read in full on 21 Nov 2026** (last updated by SAP on 21 Aug 2026).
- **Steps rebuilt on 21 Nov 2026** from the tutorial's source file, with all 43 of its screenshots.
  - Every screenshot was checked for personal data. Two were blurred: a user's first name on the Joule start screen, and a person's photo in the badge app's header.
  - SAP's page has a *Test yourself* heading, but its public source contains no questions, so none were taken over.
- **Lecture 12 recording:** captions 0:56 to 1:45 (building, testing and fixing the skill). **Lecture 11:** 0:34 to 1:00 and 1:31 to 1:53 (Northwind skills, inputs, `$top`).
- Not run by me: there is no SAP Build tenant in this workspace. The OData check address in step 8 is SAP's and was not opened.

## Sources

- SAP Developer Center, *Use Joule Studio, Classic Edition to Create and Deploy a Joule Skill*: https://developers.sap.com/tutorials/joulestudio-skill-create.html
- Tutorial source and screenshots: https://github.com/sap-tutorials/sap-build-process-automation (© SAP SE, licensed CC BY 4.0)
- SAP Help, *Create a Joule Skill*: https://help.sap.com/docs/joule-studio-classic/joule-studio-classic-edition/create-joule-skill
- Mentors Pool course, Lecture 11 Part A (BT023) and Lecture 12 (BT025) recordings

Previous: [Tutorial: Create action projects](tutorial-joule-action-projects.md) · Next: [Tutorial: Filter an action and let Joule write the reply](tutorial-joule-action-filter.md)
