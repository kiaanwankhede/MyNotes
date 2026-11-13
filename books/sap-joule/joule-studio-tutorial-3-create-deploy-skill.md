# Joule Studio tutorial 3: building and deploying a Joule Skill

*The core tutorial — Trigger, two chained actions, a manually-composed response, and a real deployed Skill you can talk to.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the Trigger → Action → Send Message → End flow shape, how to wire two actions together (the second consuming the first's output), the Design Console's validation, and the Release → Show Project Version → Deploy sequence
> - **You will build:** a working Joule Skill, **CreateBadge**, that looks up an employee by ID and creates a replacement badge for them — deployed and tested in a real conversation, with the badge confirmed in a mock third-party system
> - **Level:** intermediate · **Time:** about 20 minutes
> - **Builds on:** [Joule Studio tutorial 2: Action Projects](joule-studio-tutorial-2-action-projects.md) (both Action Projects built there are consumed here). **Leads to:** [Joule Studio tutorial 4: filters and the other response mode](joule-studio-tutorial-4-filters-and-responses.md)

**After this tutorial you can:**

- Build a full Skill flow: Trigger, two chained Call Action steps, a Send Message step, End
- Explain what the **Design Console** actually catches, with a real example
- Distinguish the "Allow Joule to generate a response" toggle from the separate "Allow skill to be started directly by a user" toggle
- Walk through Release → Show Project Version → Deploy as three distinct steps, not one

## 1. The flow shape

```mermaid
flowchart LR
    T["Trigger\n(when a scenario is called)"] --> A1["Call Action\nlook up business partner"]
    A1 --> A2["Call Action\ncreate badge"]
    A2 --> SM["Send Message\n(manual response)"]
    SM --> E["End"]
```

## 2. Create the Skill project

From the Lobby, start a new project:

![SAP Build's Lobby, "Welcome to SAP Build," All Projects list, Create button highlighted](images/sj142-35-lobby.png)

Choose **Joule Agent and Skill** as the objective:

![Create Project, step 1 Objective: Application, Automated Process, Joule Agent and Skill (selected), Business Site](images/sj142-36-select-joule-skill.png)

Name it:

![Create Project, step 2 Name: "tutorial_CreateBadge", description "Create a badge for an employee given the employee's ID"](images/sj142-37-enter-name-and-description.png)

The project opens empty — create the actual Skill artifact from inside it:

![The tut_CreateBadge project overview, Artifacts tab empty, with a Create menu showing Joule Agent / Joule Skill / Data Type options](images/sj142-38-joule-studio-classic-create.png)

![Create Joule Skill popup: Name "CreateBadge", Identifier "createBadge", Description "Create a badge for an employee given the employee's ID"](images/sj142-39-joule-studio-classic-create-popup.png)

A fresh Skill starts as just a Trigger and an End, connected by nothing:

![A fresh CreateBadge Skill canvas: a Trigger node ("When a scenario is called") and an End node, not yet connected to anything](images/sj142-40-joule-studio-classic-fresh-project.png)

## 3. Configure the Trigger and the two response toggles

Open the Trigger's side panel:

![The Trigger side panel open, showing the canvas behind it](images/sj142-41-open-side-panel-for-trigger.png)

Two independent toggles live on the Trigger's **Parameters** tab, and this tutorial turns one of them **off**:

![Trigger Parameters: "Allow Joule to generate a response" toggled OFF, with the hint "If you deactivate this feature, you need to use the 'Send Message' step to configure a response" — and a separate "Allow skill to be started directly by a user" toggle, left ON](images/sj142-42-choose-parameters.png)

> [!NOTE]
> These are **two separate settings**, easy to conflate. "Allow Joule to generate a response" controls whether a response is auto-composed from output data or has to be built manually via a Send Message step (this tutorial's choice). "Allow skill to be started directly by a user" controls whether end users can trigger this Skill directly in conversation at all, versus only via another Skill/Agent calling it.

## 4. Define Skill Inputs and Outputs

Configure 3 inputs — EmployeeID (required), Status, and CommunityID:

![Configure Skill Inputs: EmployeeID/employeeid/Employee ID (required), Status/status/Status, CommunityID/communityid/Community ID](images/sj142-43-configure-inputs.png)

And 3 outputs — Badge (Number), Employee ID (String), Employee Name (String), all marked Required:

![Configure Skill Outputs: Badge/badge/Badge (Number, required), Employee ID/employeeid/Employee ID (String, required), Employee Name/employeeName/Employee name (String, required)](images/sj142-44-configure-outputs.png)

![The Skill's Parameters tab, Skill Outputs section expanded, showing Badge/Employee ID/Employee Name as defined outputs](images/sj142-45-output-parameters.png)

## 5. The Design Console catches real problems early

With the response toggle off but no Send Message step added yet, and the flow not wired, the **Design Console** flags exactly what's wrong:

![Design Console showing 3 issues: 2 errors ("Your EndEvent output isn't connected", "Your Joule skill must contain at least one activity") and 1 warning ("You have deactivated the generated response, so you need to add a send message step before the end of the skill")](images/sj142-46-design-console-errors.png)

This is worth checking right after defining parameters — it surfaces exactly this kind of gap before you've built out the whole flow around a mistake.

## 6. Wire the first action: look up the business partner

Add the first node from the Trigger's `+`:

![Choose what happens next palette: Run Process, Call Action, Run Automation, Send Message, Launch Joule Skill, Check Condition — Call Action highlighted](images/sj142-47-add-first-action-plus.png)

Browse published actions — initially empty until an action has actually been published (confirming the Release→Publish requirement from Tutorial 2 is real, not optional):

![Action panel: Browse All Actions / Browse All RFC Actions, search empty, "No Action Available Yet — Start by creating a Blank Action"](images/sj142-48-choose-call-action.png)

![Browse library showing 7 published actions across 3 projects, including the two business-partner lookup actions from tutorial_API_BUSINESS_PARTNER](images/sj142-49-browse-all-actions.png)

Select the single-record lookup action:

![The flow with the business-partner action added, Destination Variable field not yet set, "Must not be empty" validation visible](images/sj142-50-select-business-partner-action.png)

Create a **Destination Variable** — this is how the action's underlying destination gets bound at the Skill level:

![Create Destination Variable dialog: Identifier "S4HANA_MOCK", Description "BusinessPartner API", Type "Destination"](images/sj142-51-create-destination-variable.png)

![The action's General tab showing the Destination Variable field now set to S4HANA_MOCK](images/sj142-52-select-destination-variable.png)

Map the Skill's `EmployeeID` input to the action's `BusinessPartner` field:

![Action Inputs tab, with EmployeeID mapped into the BusinessPartner input field via the Skill Content panel](images/sj142-53-map-input-businesspartner-to-employeeid.png)

Inspect the action's output tree — this is what the second action and the Send Message step will both draw from:

![Action Outputs tab, output tree expanded showing $.{uuid}.result.A_BusinessPartnerType with BusinessPartner/FirstName/LastName fields](images/sj142-54-inspect-output-tree.png)

## 7. Wire the second action: create the badge

Add a second node after the first:

![Choose what happens next palette shown again from the second node's +](images/sj142-55-add-second-action-plus.png)

![Browsing all actions again from the Call Action panel, this time with results already available](images/sj142-56-browse-all-actions-second.png)

![Browse library search "tutorial," with the createBadge POST action from tutorial_BadgeRequestsService highlighted](images/sj142-57-select-createbadge-action.png)

A second, distinct Destination Variable is needed for this action — its Destination Variable dropdown starts empty (S4HANA_MOCK is visible as an existing option, but it's the wrong one for a badge-service call):

![Invoke action createBadge, General tab, Destination Variable dropdown open showing "Must not be empty," S4HANA_MOCK listed, and a "+ Create Destination Variable" option](images/sj142-58-create-destination-variable-badge.png)

![Create Destination Variable dialog: Identifier "Badge_Service", Description "Third-party badge service"](images/sj142-59-select-badge-service-variable.png)

Map all 4 inputs this action needs — note these come from **both** the Skill's own inputs (CommunityID, Status) and the **first action's output** (FirstName, LastName), demonstrating actions chaining off each other within one flow:

![Second action's Inputs tab, mapped: businesspartnerId, communityId, firstname, lastname — firstname/lastname drawn from the first action's output, not the Skill's raw inputs](images/sj142-60-map-inputs-second-action.png)

![Second action's Outputs tab, output tree expanded showing badgeId, businesspartnerId, communityId, createdAt, firstname, lastname, modifiedAt, processInstanceId, status, and a User's unique ID field](images/sj142-61-inspect-outputs-second-action.png)

## 8. Add the Send Message step

Since the auto-response toggle is off, a manual response step is required:

![Choose what happens next palette, Send Message highlighted](images/sj142-62-add-send-message-activity.png)

Open its message editor:

![The flow with a Send Message node added, its side panel showing an "Open Message Editor" link](images/sj142-63-open-message-editor.png)

Compose the message with real data-mapping tokens pulled from the action chain's output:

![Edit User Interaction: Message Type "Illustrated Message", Title "Badge Request", Text "Badge ${context.action_post_createBadge_1.result.badgeId} has been create for ${firstname}", Illustration "Add People"](images/sj142-64-message-editor-title-and-text.png)

The **Data Mapping** panel shows exactly which fields are available to insert, traced back through the whole action chain:

![Data Mapping panel open inside the message editor, showing the full output tree available for insertion: id, status, badgeId, lastname, createdAt, User's unique ID, firstname (highlighted), modifiedAt, communityId, businesspartnerId, processInstanceId](images/sj142-65-data-mapping-in-message-editor.png)

Add an **Action Button** that links out to the badge system itself, and preview the finished card:

![Message Configuration with an Action Button "Go to Badge System" linking to a real URL, and a live Preview panel showing the "Badge Request" illustrated card](images/sj142-66-edited-and-previewed-message-with-button.png)

## 9. Map the Skill's own outputs at the End node

Before the flow is complete, the Skill's own declared Outputs (badge, businesspartnerId, firstname) need to be mapped from the action chain's results at the **End** node:

![The End node's Outputs tab, mapped: badge from the createBadge action's badgeId, businesspartnerId, and firstname fields highlighted in the full output tree](images/sj142-67-mapped-data-to-skill-outputs-at-end.png)

## 10. Release, show version, deploy

Three distinct steps — skipping the middle one is an easy way to deploy a stale version:

![Release Project dialog: Release Version 1.0.0, Release Notes](images/sj142-68-choose-release.png)
![Confirmation banner: "tutorial_CreateBadge 1.0.0 released" with a "Show project version" link](images/sj142-69-released-confirmation.png)

Click through to the released version, **then** deploy it:

![Deploy dialog, Choose an Environment: searching "tutorial," the tutorial environment selected, with its description "Environment for testing the tutorial for Joule Skills"](images/sj142-70-deploy-select-environment.png)
![Define Variables step: Badge_Service and S4HANA_MOCK destination variables each mapped to their real tutorial_* destinations, Deploy button highlighted](images/sj142-71-select-destinations-for-deploy.png)
![The deployed project overview, now showing a Deployed badge and Active status](images/sj142-72-deployed-confirmation.png)

## 11. Test it in a real conversation

Launch the standalone Joule assistant from the environment's Joule tab:

![Environment overview with the Joule tab selected and a Launch button](images/sj142-73-joule-tab-launch-assistant.png)

![A fresh Joule conversation, "Hello Martin, How can I help you?"](images/sj142-74-new-conversation-in-standalone-assistant.png)

A real prompt — *"Please create a badge for the employee with the ID 1003764. The badge status is NEW and his community ID is john.doe@bestrunsap.com"* — produces the exact card composed in section 8, with a real badge ID:

![Joule's response: "Employee Badge Creation Request Completed," a Badge Request card reading "Badge 50671 has been create for John," with a Go to Badge System button](images/sj142-75-conversation-result-with-badge-created.png)

Confirm the badge actually exists on the backend, not just in the chat:

![Raw OData service response confirming the created badge record: badgeId 34, firstname Jane, lastname Smith, businesspartnerId BP002, communityId C002, status Submitted](images/sj142-76-badge-in-odata-service-response.png)

![The mock third-party "Access Pro Systems" badge system, listing badge requests by community ID, with the newly-created Badge ID 50671 visible for John Doe](images/sj142-77-badge-system-list-of-badges.png)

## 12. Added by Claude, not from the sources

- The flow-shape Mermaid diagram in section 1 and the toggle-distinction note in section 3 are this book's own synthesis of what the tutorial's screenshots show — the underlying mechanics are the source's.
- Not run: the CreateBadge Skill described was built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 13. Interview corner

**What interviewers listen for:** you can describe the full Trigger→Action→Action→Send Message→End shape without missing a step, and you know Design Console errors are a real pre-flight check, not decoration.

### 🟢 Basic

<details class="qa"><summary>1. What does the Design Console actually check?</summary>

- Structural completeness of the flow — e.g. an unconnected EndEvent output, a skill with no activities, or a deactivated auto-response with no Send Message step added yet

</details>

<details class="qa"><summary>2. Why does the second action (createBadge) need its own separate Destination Variable from the first?</summary>

- Each action is bound to a different backend destination (S4HANA_MOCK vs. Badge_Service) — one Destination Variable per distinct backend connection

</details>

### 🟡 Intermediate

<details class="qa"><summary>3. The second action in a chain needs a field that only the first action's output provides. How is that wired?</summary>

- Map the second action's input directly from the first action's output in the Skill Content/data-mapping panel, not from the Skill's own raw inputs — this is exactly how firstname/lastname flow from the business-partner lookup into the createBadge call

</details>

<details class="qa"><summary>4. What's the practical risk of treating Release and Deploy as one step?</summary>

- Deploy pulls from a specific **version** of the project — without explicitly going through "Show project version" after a Release, it's possible to deploy an older version than the one just released

</details>

### 🔴 Senior

<details class="qa"><summary>5. A Skill's Send Message step references `${context.action_post_createBadge_1.result.badgeId}`. What does this token structure tell you about how Joule Studio exposes action results?</summary>

- Each action step's results are namespaced by its step identifier (`action_post_createBadge_1`) under a shared `context` object, with the action's own response shape (`result.badgeId`) nested underneath — this is what lets the Data Mapping panel offer the full output tree from every prior step in the flow, not just the immediately preceding one

</details>

> [!TIP]
> **🧩 Design question**
> *"A Skill needs to look up a record, then take an action on it, then tell the user exactly what happened, including a clickable link to view the result."* Talk about: chaining two Call Action steps (lookup, then action), turning off auto-generated response in favor of a Send Message step for full control over the message text and an Action Button, and using the Data Mapping panel's full output tree (not just the last action's output) to compose a message that references data from earlier in the chain.

## Cheat sheet

| Step | Detail |
|---|---|
| Flow shape | Trigger → Call Action → Call Action → Send Message → End |
| Two response toggles | "Allow Joule to generate a response" (auto vs. manual) is separate from "Allow skill to be started directly by a user" |
| Design Console | Checks for unconnected EndEvent, missing activities, missing Send Message when auto-response is off |
| Destination Variable | One per distinct backend destination an action in the flow uses |
| Deploy sequence | Release → Show Project Version → Deploy (3 steps) |

## Recap

- A full Skill flow chains a Trigger, one or more Call Action steps, and either an auto-generated response or a manual Send Message step, ending at End
- The Design Console is a real pre-flight check — it caught an unconnected output and a missing Send Message step in this exact build
- A second action in a chain can consume the first action's output directly, not just the Skill's own raw inputs
- Release → Show Project Version → Deploy are three distinct steps; skipping the middle one risks deploying a stale version
- The finished CreateBadge Skill was tested end to end: a real conversation prompt produced a real badge, confirmed both in the OData response and in the mock third-party badge system's own UI

## Practice

1. Without looking back, sketch the full Trigger-to-End flow shape this tutorial builds
2. Explain in one sentence the difference between the two response-related toggles on the Trigger
3. Name the three Design Console issues this tutorial encountered and what each one meant

## How this chapter was checked

- All 43 images for this tutorial were downloaded and individually opened and visually verified against their captions before being written into this chapter.
- This is part 3 of 5 of the SAP Developers tutorial series "Build Your First Joule Skill in Joule Studio, Classic Edition." Nothing in this chapter is code; nothing was independently executed — the CreateBadge Skill described was built and tested by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Build Your First Joule Skill in Joule Studio, Classic Edition* — https://developers.sap.com/group.joule-studio-first-skill.html, Tutorial 3 of 5 (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 2: Action Projects](joule-studio-tutorial-2-action-projects.md) · Next: [Joule Studio tutorial 4: filters and the other response mode](joule-studio-tutorial-4-filters-and-responses.md)
