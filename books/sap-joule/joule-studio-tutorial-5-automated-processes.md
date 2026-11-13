# Joule Studio tutorial 5: consuming an automated process in a Joule Skill

*The last tutorial — and the one with a real, non-obvious limitation worth knowing before you design around it.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how to build a full SAP Build Process Automation process (not just a single Action), its own separate Release → Deploy → Publish-to-Library sequence, and how a Joule Skill consumes it via **Run Process** instead of Call Action
> - **You will build:** an email-sending process, `InitiateSecurityChecksViaEmail`, and a Skill, **BadgeSecurity**, that triggers it when someone reports a lost or stolen badge — tested end to end, with the result confirmed in Monitoring
> - **Level:** intermediate · **Time:** about 22 minutes
> - **Builds on:** [Joule Studio tutorial 3: building and deploying a Joule Skill](joule-studio-tutorial-3-create-deploy-skill.md) (the Skill-building flow, reused here with Run Process instead of Call Action). **Leads to:** nothing specific — this is the last of the 5 linked tutorials

**After this tutorial you can:**

- Build a Process Automation project separately from an Action Project, including a Send Mail activity with real data-bound email content
- Explain why a process needs Release **and** Deploy **and** Publish to Library — three stages, across two different screens — before a Skill can consume it
- State, correctly, the one hard limitation of Run Process: inputs flow in, but the process's own output never flows back into the conversation

## 1. Run Process vs. Call Action

```mermaid
flowchart LR
    S["Joule Skill"] -->|"Call Action\n(Tutorials 2-4)"| A["Action Project\nsynchronous, returns output"]
    S -->|"Run Process\n(this tutorial)"| P["SAP Build Process\nfire-and-forget, no output back"]
```

> [!CAUTION]
> **🔒 Run Process is fire-and-forget: inputs flow in, outputs do not flow back**
> Stated explicitly in the tutorial's own introduction: in the current release, a Joule Skill can pass **inputs** into a triggered process but **cannot** receive the process's **output** back into the conversation. If a design needs the conversation to report what the process actually did, Run Process alone can't do that — the Skill has to compose its own confirmation message instead (section 7 below), not relay anything the process itself returns.

## 2. Create the Process Automation project

From the Lobby, start a new project with a different objective than every previous tutorial — **Automated Process**:

![Lobby showing the existing 2 Joule Skill projects, Create button highlighted](images/sj142-113-lobby-create.png)
![Create Project, Objective step: Application, Automated Process (selected), Joule Agent and Skill, Business Site](images/sj142-114-create-automated-process-tile.png)
![Create Project, Type step: Process tile selected ("Build a business process to automate a workflow... Automating sales orders, invoice management, approval flows"), Skills needed "SAP Build Process Automation"](images/sj142-115-create-process-type.png)

Name it:

![Create Project, Name step: "InitiateSecurityChecksViaEmail", description "When a badge is reported as lost or stolen, contact security via email"](images/sj142-116-name-and-description-initiatesecuritychecks.png)

Review before creating:

![Create Project, Summary step reviewing Objective (Automated Process), Type (Process), Name (InitiateSecurityChecksViaEmail)](images/sj142-117-create-project-process.png)

The project opens empty, same pattern as a Skill project — create the actual process artifact from inside it:

![The InitiateSecurityChecksViaEmail project overview, Create menu open, Name field empty, "There are no entries yet"](images/sj142-118-process-automation-create-process-sendemail.png)

## 3. Define process inputs

Open the process editor's side panel and switch to its Variables tab:

![Side panel collapse/expand control highlighted on the process canvas](images/sj142-119-process-automation-open-side-panel.png)
![Process Details panel: General/Variables/Attributes tabs, Trigger "How do you want to start your process?", Name "SendEmailToSecurity", Subject "SendEmailToSecurity"](images/sj142-120-process-automation-variables-tab.png)

Configure 4 inputs — all required:

![Configure Process Inputs: EmployeeID/employeeid/"Employee ID"/String, FirstName/firstname/"First name"/String, LastName/lastname/"Last name"/String, BadgeStatus/badgestatus/"Badge"/String — all 4 marked Required](images/sj142-121-configure-process-inputs-four-fields.png)

## 4. Add the Send Mail activity

Save first:

![Process canvas: Trigger node connected to End, Save button highlighted](images/sj142-122-process-automation-save.png)

Add a Trigger, then choose what happens next from Process Automation's own, much broader node palette:

![Trigger panel ("How do you want to start your process?" / Add a Trigger) and, below it, the "Choose what happens next" palette: Form, Approval, Controls and Events, Automation, Action, Email (highlighted), Notification, Subprocess, Decision, Variant Template, Script Task, Placeholder](images/sj142-123-select-email-activity.png)

Configure the mail header — **To** and **Subject**, data-bound to the process inputs:

![Send Mail node side panel: Mail Header To field, Subject "Lost Badge," Additional Options, Mail Body section with "Open Mail Body Editor" link](images/sj142-124-configure-email-to-and-subject.png)

Compose the body with real value-binding tokens pulled straight from the process's own inputs:

![Edit Mail Body: Value Binding panel showing Process Inputs (BadgeStatus, EmployeeID, FirstName, LastName), rich text body reading "Hello Security colleagues, [FirstName] [LastName] with ID [EmployeeID] has reported that their badge is [BadgeStatus]. Please take the appropriate measures. Best regards, Front Desk"](images/sj142-125-email-editor-value-binding-process-inputs.png)

The finished, saved flow — Trigger → Send Mail → End:

![The completed process flow: Trigger "How do you want to start your process?" connected to a Send Mail node with Subject "Lost Badge" and Mail Body confirmed to have content, connected to End](images/sj142-126-process-automation-finished-flow.png)

## 5. Release, deploy, and — a step a Skill alone never needed — publish to the library

A **process** needs one more stage than an Action Project or a Skill does. Release and Deploy happen from the Process Automation editor itself, same as before:

![Release Project dialog for InitiateSecurityChecksViaEmail, with an "Optimize for faster execution" checkbox not present on the earlier Skill/Action release dialogs](images/sj142-127-process-automation-release.png)
![Deploy dialog, Choose an Environment: tutorial environment, description "Environment for testing the tutorial for Joule Skills"](images/sj142-128-process-automation-deploy-select-environment.png)
![Deployed confirmation: tutorial_InitiateSecurityChecksViaE... 1.0.0, Deployed, Active](images/sj142-129-process-automation-deployed-confirmation.png)

But a Skill still can't see it yet. Go to the project's **Lobby → Versions tab** — a completely different screen from the process editor — and **Publish to Library** explicitly:

![Lobby's Versions tab for the process project, showing 2 versions and a "Publish to Library" option in the context menu](images/sj142-130-lobby-versions-tab-publish-to-library.png)
![Confirmation that the project has been published](images/sj142-131-lobby-published-confirmation.png)

> [!WARNING]
> **⚠️ Pitfall: Deployed ≠ Published — a Skill can't see an un-published process**
> Release and Deploy make the process *runnable*; **Publish to Library**, done separately from the Lobby's Versions tab, is what actually makes it visible to a Joule Skill's "Browse All Processes" picker. Skipping this step leaves an otherwise-working, deployed process invisible to every Skill that might want to use it.

## 6. Build the Skill that triggers it

Confirm all 3 projects now exist side by side:

![Lobby listing all 3 projects: tutorial_SearchWithName (Joule Skill), tutorial_CreateBadge (Joule Skill), tutorial_InitiateSecurityChecksViaEmail (Process Automation)](images/sj142-132-lobby-create-joule-skill-project.png)

![Create Project, Objective step, Joule Skill tile highlighted](images/sj142-133-create-project-joule-skill-tile.png)
![Create Project, Name step: "tutorial_BadgeSecurity", description "Contact security when a badge is reported lost or stolen"](images/sj142-134-create-project-badgesecurity-name.png)
![Create Project, Summary step reviewing the selections before Create](images/sj142-135-create-project-review.png)

The new project starts empty, same as every previous Skill project:

![tutorial_BadgeSecurity project overview, Create menu, "There are no entries yet"](images/sj142-136-joule-studio-create-joule-skill-menu.png)
![Create Joule Skill popup: Name "BadgeSecurity", Identifier "badgeSecurity", Description "Contact security when a badge is lost or stolen"](images/sj142-137-joule-studio-create-joule-skill-popup-badgesecurit.png)

Once again, this tutorial turns the auto-response toggle **off** — a Send Message step composes the user-facing confirmation, since (per the pitfall in section 1) the process itself can't report back:

![Trigger Parameters: "Allow Joule to generate a response" toggled OFF, "Allow skill to be started directly by a user" ON](images/sj142-138-joule-studio-trigger-disable-generate-response.png)

Configure 4 Skill inputs, matching the process's own 4 inputs:

![Skill Parameters tab, Skill Inputs, Configure highlighted](images/sj142-139-joule-studio-parameters-configure-skill-inputs.png)
![Configure Skill Inputs: Employee ID, BadgeStatus, First Name, Last Name — all 4 required except Last Name](images/sj142-140-joule-studio-configure-skill-inputs-four-fields.png)
![Skill Parameters tab, Skill Inputs section expanded showing all 4 applied: BadgeStatus, Employee ID, First Name, Last Name](images/sj142-141-joule-studio-skill-inputs-applied.png)

This Skill needs **no outputs** — a direct, visible consequence of Run Process's fire-and-forget nature:

![Skill Outputs section: "No Outputs added yet. No outputs have been defined for this skill yet."](images/sj142-142-joule-studio-skill-outputs-empty.png)

## 7. Wire the Run Process step

From the Trigger's `+`, choose **Run Process** this time, not Call Action:

![Choose what happens next palette, Run Process highlighted among Call Action, Run Automation, Send Message, Launch Joule Skill, Check Condition](images/sj142-143-joule-studio-select-run-process-plus.png)

Browse published processes — empty until the process from section 5 has actually gone through Publish to Library:

![Process panel: Browse All Processes link, "No Process Available Yet — Start by creating a Blank Process"](images/sj142-144-joule-studio-browse-all-processes.png)

![Browse library showing exactly 1 published process: SendEmailToSecurity, from project tutorial_InitiateSecurityChecksViaEmail](images/sj142-145-joule-studio-add-sendemailtosecurity-process.png)

Map all 4 of the Skill's inputs into the process's 4 inputs — this is the only data that actually crosses into the process:

![Run Process node, Inputs tab, BadgeStatus field, "Type or select item"](images/sj142-146-joule-studio-inputs-badgestatus-field.png)
![Skill Content panel alongside the Run Process node's Inputs tab, all 4 fields mapped: BadgeStatus, EmployeeID, FirstName, LastName](images/sj142-147-joule-studio-map-inputs-all-fields.png)

## 8. Add the confirmation message

Since the process can't report back anything, the Skill has to tell the user what happened on its own, using only the data it already has:

![Choose what happens next palette, Send Message highlighted, now positioned after the Run Process node](images/sj142-148-joule-studio-select-send-message-plus.png)

![The flow with a Send Message node added after Run Process, its side panel showing "Open Message Editor"](images/sj142-149-joule-studio-open-message-editor.png)

Compose the message, pulling from the Skill's own **inputs** (not any process output, since there is none):

![Message Configuration: Title "Security has been informed", Text "Badge status" with a Data Mapping panel open, showing context → joule_process_sendEmailToSecurity_1 → startEvent → Employee ID / BadgeStatus (highlighted) / First Name / Last Name](images/sj142-150-joule-studio-message-configuration-title-text.png)

Preview the finished card:

![Message Configuration with a live Preview: "Security has been informed — Badge status $(badgeStatus) for employee $(EmployeeId) has been reported to security"](images/sj142-151-joule-studio-message-configured-preview.png)

## 9. Release, deploy, and test

![Release Project dialog for BadgeSecurity, version 1.0.0](images/sj142-152-joule-studio-release-skill.png)
![Released confirmation banner with a "Show project version" link](images/sj142-153-joule-studio-show-project-version-released.png)
![Deploy dialog, Choose an Environment: tutorial environment, with a description confirming "Joule Digital Assistant: Standalone"](images/sj142-154-joule-studio-deploy-select-environment.png)

All 3 capabilities now live in the same environment:

![Environment overview, Joule Digital Assistant Capabilities list showing all 3 deployed versions: tutorial_BadgeSecurity, tutorial_SearchWithName, tutorial_CreateBadge, each 1.0.0](images/sj142-155-environment-joule-tab-launch.png)

A new conversation, with a real front-desk report:

![A fresh Joule conversation](images/sj142-156-joule-new-conversation-start.png)

> *"Please report to security that the old badge of John Doe 1003764 has the status LOST"*

![Joule's response: "Security has been informed — Badge status LOST for employee 1003764 has been reported to security"](images/sj142-157-joule-conversation-badge-reported-lost-response.png)

## 10. Confirm the process actually ran

The conversation confirms what the Skill *said* happened — Monitoring confirms it *actually* happened on the backend:

![Monitoring → Process and Workflow Instances, filtered to Completed status, showing a SendEmailToSecurity instance with Status "Completed," the correct Project and Environment](images/sj142-158-monitoring-process-and-workflow-instances.png)

This closing check matters precisely because of this tutorial's central limitation: the Skill's confirmation message is composed from what it already knew going in, not from anything the process reported back. Monitoring is the only place that independently confirms the process succeeded.

## 11. Added by Claude, not from the sources

- The "Run Process vs. Call Action" Mermaid diagram in section 1 is this book's own visual framing of the fire-and-forget distinction the tutorial's own introduction states directly.
- The closing observation in section 10 (why Monitoring matters specifically *because* of the fire-and-forget limitation) is this book's synthesis connecting section 1's constraint to the actual verification step — the underlying facts are the source's.
- Not run: the process and Skill described were built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 12. Interview corner

**What interviewers listen for:** you state the Run Process limitation confidently and specifically (inputs in, no output back), and you know Publish to Library is a distinct, separate step from Deploy — not a detail you'd guess.

### 🟢 Basic

<details class="qa"><summary>1. What's the one hard limitation of Run Process, stated explicitly by the tutorial itself?</summary>

- A Joule Skill can pass inputs into a triggered process, but cannot receive the process's output back into the conversation

</details>

<details class="qa"><summary>2. A process is Released and Deployed, but a Skill's "Browse All Processes" still shows nothing. What's missing?</summary>

- Publish to Library — a separate step from the Lobby's Versions tab, distinct from Release and Deploy, and required before any Skill can see the process

</details>

### 🟡 Intermediate

<details class="qa"><summary>3. A Skill using Run Process needs to confirm to the user that an action succeeded. How does it do that, given the fire-and-forget limitation?</summary>

- It composes its own confirmation message (via a Send Message step) using data it already has from its own inputs — not from anything the process returns, since nothing comes back
- *Stronger answer:* this means the confirmation message can only ever restate what was *sent* to the process, never report on what the process *did* with it

</details>

<details class="qa"><summary>4. Why does this Skill define zero Skill Outputs, unlike the Skills in Tutorials 3 and 4?</summary>

- Because Run Process provides no output to map into a Skill Output in the first place — defining one would have nothing to bind to

</details>

### 🔴 Senior

<details class="qa"><summary>5. A team wants a Skill that triggers a multi-step approval workflow and reports its final outcome in the same conversation. Where does this design break, and what's the fix?</summary>

- It breaks at the exact same point this tutorial demonstrates: Run Process can't return the workflow's outcome back into the conversation, so the Skill can never truthfully report an outcome it was never told
- *Stronger answer:* the outcome has to reach the user through a separate channel the process itself triggers (e.g. a notification, an email, or a status the user checks later) — not through the Skill that originally started the process

</details>

> [!TIP]
> **🧩 Design question**
> *"A customer wants Joule to kick off a multi-day approval process and tell the requester as soon as it's approved."* Talk about: Run Process being the right mechanism to kick the process off, but structurally unable to report the eventual approval back into that same conversation (section 1's limitation), and why the actual notification has to come from the process itself (e.g. a Send Mail or Notification activity at the point of approval) rather than from the triggering Skill, since the Skill's own conversation has long since ended by the time a multi-day approval resolves.

## Cheat sheet

| Step | Detail |
|---|---|
| Run Process limitation | Inputs flow in; the process's own output never flows back |
| Process publish sequence | Release + Deploy (process editor) **then** Publish to Library (Lobby → Versions tab) — 3 stages, 2 screens |
| Skill Outputs for a Run Process flow | None — there's nothing to map |
| Confirming success to the user | A Send Message step composed from the Skill's own inputs, not the process's output |
| Confirming success actually happened | Monitoring → Process and Workflow Instances |

## Recap

- SAP Build Process Automation projects are built separately from Action Projects, with their own, broader node palette (Form, Approval, Email, Decision, and more)
- A process needs Release, Deploy, **and** Publish to Library — the last one from a different screen entirely — before any Skill can consume it
- Run Process is fire-and-forget: a real architectural limitation, not a bug, and Skills built around it define zero outputs and compose confirmations from their own inputs only
- Monitoring is the independent source of truth for whether a triggered process actually completed — the conversation's own confirmation message can't tell you that
- This closes the 5-tutorial series: environment/connectivity (1), Action Projects (2), a full Skill with chained actions and a manual response (3), a filtered action with auto-generated response and multi-turn correction (4), and consuming a full automated process (5)

## Practice

1. Without looking back, state Run Process's one hard limitation in a single sentence
2. Name the three stages a process needs before a Skill can use it, and which screen each one happens on
3. Explain why this tutorial's Skill defines zero Skill Outputs

## How this chapter was checked

- All 46 images for this tutorial were downloaded and individually opened and visually verified against their captions before being written into this chapter.
- This is part 5 of 5 of the SAP Developers tutorial series "Build Your First Joule Skill in Joule Studio, Classic Edition." Nothing in this chapter is code; nothing was independently executed — the process and Skill described are the tutorial author's own.

## Sources and further reading

- SAP Developers, *Build Your First Joule Skill in Joule Studio, Classic Edition* — https://developers.sap.com/group.joule-studio-first-skill.html, Tutorial 5 of 5 (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 4: filters and the other response mode](joule-studio-tutorial-4-filters-and-responses.md) · Next: [Enabling Joule for SAP S/4HANA Cloud Private Edition](enabling-s4hana-private-edition.md)
