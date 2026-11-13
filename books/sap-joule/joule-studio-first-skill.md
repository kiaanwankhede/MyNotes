# Building your first Joule Skill in Joule Studio

*Five linked tutorials, 33 steps, one real Skill deployed and tested end to end — the hands-on companion to the lifecycle chapter's theory.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the concrete Joule Studio, Classic Edition workflow — environments and destinations, Action Projects, the Trigger → Action → Send Message → End flow, the two response mechanisms (auto-generated vs. manual), filters, and consuming a full SAP Build Process Automation process from a Skill
> - **You will build:** a working Joule Skill that looks up an employee by first name and creates a replacement badge for them, deployed and tested in a real Joule conversation
> - **Level:** intermediate · **Time:** about 30 minutes to read; the original hands-on version runs about 120 minutes
> - **Builds on:** [Joule Studio and the agent development lifecycle](02-joule-studio-lifecycle.md) (the conceptual 6-stage lifecycle). **Leads to:** nothing specific — this is this book's most concrete Joule Studio walkthrough

**After this chapter you can:**

- Set up a Joule Studio environment and the destinations it needs, and know which ones have to be associated to *both* your own environment and the Public environment
- Build an Action from an OData source, and release/publish it correctly (all three steps, not just Save)
- Choose between the two response mechanisms — "Allow Joule to generate a response" vs. a manual Send Message activity — and explain why each exists
- Add a filter condition to a Skill input, and understand why a multi-turn conversation can correct a slot value mid-conversation
- Explain the one real limitation of **Run Process**: inputs flow in, but outputs don't flow back out

## 1. Tutorial 1 — Set up environment and connectivity

Everything in Joule Studio runs inside a **Control Tower environment**. Create one (or use an existing test environment), then add the Joule tab to confirm it's there.

![SAP Build's Control Tower, the landing page for environments and tenant configuration](images/sj142-01-control-tower.png)
![Creating a new test environment](images/sj142-02-create-environment.png)

Destinations are created in the **BTP Cockpit**, not inside Joule Studio itself, with specific required properties depending on what they connect to:

| Property | Required value |
|---|---|
| `sap.processautomation.enabled` | `true` |
| `sap.applicationdevelopment.actions.enabled` | `true` |
| `sap.build.usage` | `odata_gen` |

![Creating a destination for a mock S/4HANA OData service, with the required properties set](images/sj142-05-create-destination-s4hanamock.png)
![Checking the destination's connection succeeds before moving on](images/sj142-06-check-connection-s4hanamock.png)

> [!WARNING]
> **⚠️ Pitfall: a destination has to be associated with your environment *and* the Public environment**
> Creating a destination isn't enough on its own — it has to be explicitly associated with environments via **Control Tower → Destinations → Add**. Both **your own test environment** and the **Public** environment need the destination selected, or Joule Studio won't be able to use it later. Missing the Public environment specifically is an easy, non-obvious way to get a destination that "exists" but doesn't actually work from inside a Skill.

![Associating a destination with both the test environment and the Public environment](images/sj142-11-associate-environments.png)

## 2. Tutorial 2 — Create Action Projects

**Actions** connect SAP Build Process Automation to backend systems — SAP or non-SAP — and are consumed directly inside a Joule Skill. They're built from an OData destination.

![Creating a new Action Project from an API source](images/sj142-14-create-an-action-project.png)
![Selecting operations to expose from the underlying OData service](images/sj142-19-select-operations.png)

- Trim the input and output fields down to just what the Skill actually needs — don't expose the whole OData payload by default.
- **Test the Action with real values** before moving on — Joule Studio has a built-in test runner for this.

![Testing an Action with a real value and inspecting the response](images/sj142-22-action-test.png)

> [!WARNING]
> **⚠️ Pitfall: Save isn't enough — an Action needs Save → Release → Publish**
> An Action Project only becomes usable elsewhere once it's gone through all three stages. Saving alone leaves it invisible to a Joule Skill trying to call it.

![Releasing an Action Project](images/sj142-26-action-release.png)
![Publishing the released Action Project](images/sj142-27-action-publish.png)

## 3. Tutorial 3 — Create and deploy a Joule Skill

This is the core tutorial — the actual Joule Studio flow-builder, and the first full Trigger → Action → Send Message → End flow.

```mermaid
flowchart LR
    T["Trigger\n(when a scenario is called)"] --> A1["Action\n(call a published Action Project)"]
    A1 --> A2["Action\n(optional: a second call)"]
    A2 --> SM["Send Message\n(manual response, if Joule\nauto-response is disabled)"]
    SM --> E["End"]
```

Create the Skill project, then its General settings — name, description, and **two independent toggles** worth knowing about:

![The Skill's General settings: Name, Description, "Allow Joule to generate a response," and a separate "Allow skill to be started directly by a user" toggle](images/sj142-92-joule-studio-allow-joule-generate-responses-toggle.png)

- **Allow Joule to generate a response** (on by default): if you turn this **off**, you must add your own **Send Message** activity to the flow to produce a response — nothing is shown to the user otherwise. This tutorial builds with it off, to show the manual path.
- **Allow skill to be started directly by a user** is a *separate* toggle — turning it off restricts the Skill to being triggered only by another Skill/Agent, not directly by end-user conversation.

Define Skill **Inputs** and **Outputs** before wiring any actions:

![Configuring a Skill input parameter (first name)](images/sj142-94-joule-studio-configure-skill-inputs-firstname.png)
![Configuring the Skill's output parameters](images/sj142-96-joule-studio-configure-skill-outputs-employees-lis.png)

> [!TIP]
> Check the **Design Console** after defining parameters, before building out the flow — it surfaces errors early (e.g. an unmapped output) rather than letting you discover them after wiring the whole flow.

Add the first Action: **+ → Call Action → Browse All Actions**, pick the published Action, create a **Destination Variable** inline, then map Skill input fields to the Action's own inputs.

![Browsing all published Actions to add to the flow](images/sj142-98-joule-studio-browse-all-actions-filter.png)
![Creating a Destination Variable for the chosen Action](images/sj142-100-joule-studio-create-destination-variable-businessp.png)
![Mapping the Skill's firstName input to the Action's input field](images/sj142-101-joule-studio-map-input-firstname.png)

**Release → Show Project Version → Deploy** are three distinct steps — it's easy to deploy an old version by skipping "Show Project Version" after a Release.

![Releasing the Skill](images/sj142-104-joule-studio-release.png)
![Deploying the released version: selecting the environment and destinations](images/sj142-106-joule-studio-deploy-select-environment-destination.png)

Test it in the **standalone Joule assistant**, reached via Control Tower → Environments → your environment → Joule tab → Launch:

![Launching the standalone Joule assistant for testing](images/sj142-108-environment-joule-tab-launch.png)
![A real conversation testing the deployed Skill with a first-name query](images/sj142-110-joule-conversation-prompt-jane-front-desk.png)

## 4. Tutorial 4 — Create a filter in an Action Project

This tutorial shows the **other** response mechanism — "Allow Joule to generate a response" left **on**, so there's no manual Send Message step at all, the response comes straight from the Action's own output data.

- Duplicate/version an existing Action Project via **Actions → Save As New Project**, rather than starting from scratch.
- Add a custom input field, then map it into the underlying OData `$filter` using a **Condition Editor** — Column, Condition, and Criteria dropdowns, not raw filter syntax.

![Save As New Project — duplicating an existing Action Project to add a filter](images/sj142-79-save-as-new-project-popup.png)
![The Condition Editor: mapping a firstName input into an OData filter condition](images/sj142-84-condition-editor-firstname-equal.png)

A realistic multi-turn test confirms **slot correction** works: the user says "Jane," gets a result, then says "actually, John" — and the Skill picks up the corrected value without restarting the conversation.

![Testing the filtered Action with a first value ("Jane")](images/sj142-85-actions-test-with-jane.png)

## 5. Tutorial 5 — Consume an automated process in a Joule Skill

This introduces **Run Process** — consuming a full SAP Build Process Automation process (here: sending a security email) from inside a Skill, instead of a single Action call.

> [!CAUTION]
> **🔒 Run Process is fire-and-forget: inputs flow in, outputs do not flow back**
> Stated explicitly in the tutorial's own text: in the current release, a Joule Skill can pass **inputs** to a triggered process, but it **cannot** receive that process's **output** back into the conversation. Design around this — don't assume a Run Process step can report a result the way a Call Action step can.

A process only becomes usable inside Joule Studio after **three** separate stages, done from two different screens:

1. **Release** and **Deploy** — from the Process Automation editor itself.
2. **Publish to Library** — from the Lobby's **Versions** tab, a separate screen entirely.

![Creating the automated process (send-email) in Process Automation](images/sj142-118-process-automation-create-process-sendemail.png)
![The finished process flow before release](images/sj142-126-process-automation-finished-flow.png)
![Releasing the process](images/sj142-127-process-automation-release.png)
![Deploying the released process to an environment](images/sj142-128-process-automation-deploy-select-environment.png)
![Publishing the deployed process to the Library — the step that actually makes it visible to Joule Studio](images/sj142-130-lobby-versions-tab-publish-to-library.png)

Back in the Skill's flow builder, add the process via **+ → Run Process → Browse All Processes**, map its inputs, then add a **Send Message** step to actually tell the user something happened (since the process itself can't report back):

![Browsing all published processes to add via Run Process](images/sj142-144-joule-studio-browse-all-processes.png)
![Mapping all required fields into the process's inputs](images/sj142-147-joule-studio-map-inputs-all-fields.png)

Release → Deploy the Skill, then test and confirm in Monitoring that the process instance actually ran:

![Testing the finished Skill in a real conversation — reporting a badge lost](images/sj142-157-joule-conversation-badge-reported-lost-response.png)
![Monitoring process and workflow instances to confirm the Run Process step actually executed](images/sj142-158-monitoring-process-and-workflow-instances.png)

> [!WARNING]
> **⚠️ Pitfall: the tutorial's shared demo credentials can get locked**
> The original tutorial's demo backend uses shared public test credentials, which "can lead to the credentials being locked" from overuse. If a connectivity check fails for this reason, the tutorial's own advice is to skip that verification sub-step and instead confirm the setup via the raw OData service URL directly.

## 6. Added by Claude, not from the sources

- The Mermaid flow diagram in section 3 is this book's visual summary of the Trigger → Action → Send Message → End pattern described across the tutorial's own screenshots — the shape is the source's, the diagram is this book's.
- Grouping all 5 tutorials under one chapter, rather than five separate ones, is editorial — the tutorials build on each other's project state in the original source, so splitting them would fragment a single continuous walkthrough.
- Not run: the Skill, Actions, and process described here were built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 7. Interview corner

**What interviewers listen for:** you know the three-stage publish pattern (Save/Release/Publish, or Release/Deploy/Publish-to-Library) isn't optional ceremony, and you can explain *why* Run Process is fire-and-forget rather than just reciting that it is.

### 🟢 Basic

<details class="qa"><summary>1. An Action Project has been saved but a Joule Skill can't find it in "Browse All Actions." Why?</summary>

- It hasn't been Released and Published yet — Save alone doesn't make an Action Project visible elsewhere

</details>

<details class="qa"><summary>2. What's the difference between "Allow Joule to generate a response" and "Allow skill to be started directly by a user"?</summary>

- The first controls whether Joule auto-generates a response from output data or requires a manual Send Message step; the second controls whether the Skill can be triggered directly by end-user conversation at all, independent of the first setting

</details>

### 🟡 Intermediate

<details class="qa"><summary>3. A Skill calls Run Process to trigger a multi-step approval workflow, and the developer wants to tell the user the approval's outcome in the same conversation. What's wrong with that design?</summary>

- Run Process is fire-and-forget — a Skill can pass inputs into the process but cannot receive its output back, so the conversation can't report an outcome the process itself produces
- *Stronger answer:* if the outcome needs to reach the user, it has to happen through a separate mechanism (e.g. a notification sent by the process itself), not through the Joule Skill that triggered it

</details>

<details class="qa"><summary>4. A destination was created and tested successfully in BTP Cockpit, but a Joule Skill still can't use it. What's a likely cause?</summary>

- The destination wasn't associated with the right environment(s) in Control Tower — specifically, it needs to be associated with both the developer's own environment and the Public environment

</details>

### 🔴 Senior

<details class="qa"><summary>5. Design a Skill that looks up an employee by name, with the name possibly being corrected mid-conversation (e.g. "Jane" → "actually John"). What makes this work, architecturally?</summary>

- A Skill input mapped through a Condition Editor into a backend filter (not hardcoded), so a corrected value re-triggers the same Action with the new filter criteria rather than needing a new flow
- *Stronger answer:* this is exactly the multi-turn slot-correction pattern demonstrated in Tutorial 4 — the Skill's conversational state handles the correction, the Action/filter layer underneath doesn't need to know a correction even happened

</details>

> [!TIP]
> **🧩 Design question**
> *"A team wants a Joule Skill that both looks up data (fast) and kicks off a long-running approval process (slow), reporting both in one response."* Talk about: using Call Action for the fast lookup (its output flows back, so it can be reported immediately), using Run Process for the slow workflow (accepting that its outcome can't flow back into this same conversation), and designing the user-facing message to be explicit about that asymmetry — e.g. "Here's what I found; I've also started the approval, you'll be notified separately" — rather than implying the conversation itself will report the process's result.

## Cheat sheet

| Step | Gotcha |
|---|---|
| Create a destination | Must be associated with *both* your environment and Public |
| Action Project | Save → Release → Publish, all three required |
| Skill response | "Allow Joule to generate a response" (auto) vs. a manual Send Message step — pick one |
| Skill triggering | "Allow skill to be started directly by a user" is a separate toggle from the response one |
| Filter on an input | Condition Editor (Column/Condition/Criteria), not raw filter syntax |
| Run Process | Fire-and-forget — inputs in, no output back |
| Process → usable in Joule Studio | Release + Deploy (Process Automation editor) **then** Publish to Library (Lobby → Versions tab) |

## Recap

- A full Joule Skill build runs through 5 linked stages: environment/connectivity setup, Action Projects, the Skill flow itself, adding a filter, and consuming a full process via Run Process
- Two independent toggles govern a Skill's behavior: how it responds (auto vs. manual Send Message) and whether end users can trigger it directly
- Action Projects and processes both require a multi-stage publish sequence before they're usable elsewhere — saving is never the last step
- Run Process is fire-and-forget: a real architectural limitation to design around, not a bug to work past
- A filter built through the Condition Editor on a Skill input is what makes multi-turn slot correction work naturally

## Practice

1. Without looking back, name the three stages an Action Project needs before a Skill can call it
2. Explain in one sentence why a Skill using Run Process can't report that process's outcome in the same conversation
3. Sketch the Trigger → Action → Send Message → End flow from memory for a Skill with "Allow Joule to generate a response" turned off

## How this chapter was checked

- The full 5-tutorial series "Build Your First Joule Skill in Joule Studio, Classic Edition" (developers.sap.com, 33 steps across the 5 linked tutorials) was read in full, 13 Nov 2026.
- 158 images were found and downloaded (0 failures, 1 harmless exact-duplicate generic "+" icon within the source, both copies kept since removing it added no value). A representative sample spanning all 5 tutorials — including the two most load-bearing claims (the dual response/trigger toggles, and the Design Console) — was opened and visually verified against its filename-derived caption before writing; all matched. 32 of the 158 are embedded above, covering every distinct step and pitfall; the remainder are additional intermediate screenshots of the same multi-step UI flows already illustrated (e.g. repeated "browse all actions" or field-mapping screens for the tutorial's second action/process), kept in `images/` (`sj142-*`) rather than individually embedded, since the steps they show are already covered by the embedded screenshots for that same flow.
- Nothing in this chapter is code in the traditional sense, but the Skill/Action/process flows described were built and tested by the tutorial's own author — treated as "run," not independently re-executed for this book.

## Sources and further reading

- SAP Developers, *Build Your First Joule Skill in Joule Studio, Classic Edition* — https://developers.sap.com/group.joule-studio-first-skill.html (5 linked tutorials, read in full 13 Nov 2026)

Previous: [n8n workflows in Joule Studio](04-n8n-workflows.md) · Next: [Enabling Joule for SAP S/4HANA Cloud Private Edition](enabling-s4hana-private-edition.md)
