# Joule Studio tutorial 4: filtering an action, and the other response mode

*Tutorial 3 built a Skill that composes its own message by hand. This one flips that choice — and adds a real filter condition along the way.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how to duplicate and extend an existing Action Project with a custom filter field via the Condition Editor, and how a Skill behaves with **"Allow Joule to generate a response" turned on** instead of off
> - **You will build:** a filtered Action Project (`tutorial_FilterBusinessPartners`) and a new Skill, **SearchWithFirstName**, tested with a real multi-turn conversation that corrects itself mid-conversation
> - **Level:** intermediate · **Time:** about 18 minutes
> - **Builds on:** [Joule Studio tutorial 2: Action Projects](joule-studio-tutorial-2-action-projects.md) (the business-partner action duplicated here) and [Joule Studio tutorial 3](joule-studio-tutorial-3-create-deploy-skill.md) (the Skill-building flow, now with the other toggle setting). **Leads to:** [Joule Studio tutorial 5: consuming an automated process](joule-studio-tutorial-5-automated-processes.md)

**After this tutorial you can:**

- Duplicate an existing Action Project with Save As New Project, rather than starting from scratch
- Add a custom input field to an action and wire it into an OData filter via the Condition Editor
- Explain what changes in a Skill's behavior when "Allow Joule to generate a response" is left on
- Recognize multi-turn slot correction when a user corrects themselves mid-conversation

## 1. Two paths to a response

```mermaid
flowchart TD
    A["Trigger fires, action(s) run"] --> B{"Allow Joule to\ngenerate a response?"}
    B -->|"Off (Tutorial 3)"| C["Manual Send Message step\nfull control over the message"]
    B -->|"On (this tutorial)"| D["Joule auto-composes a response\nfrom the action's output data"]
```

## 2. Duplicate the business-partner action, with a twist

Rather than building a new Action Project from scratch, **Save As New Project** from the existing one built in Tutorial 2:

![The existing tutorial_API_BUSINESS_PARTNER project's Actions menu, "Save As New Project" option visible](images/sj142-78-actions-save-as-new-project.png)

![Save As New Project dialog: Project Name "tutorial_FilterBusinessPartners", description "This is to give Joule access to information about business partners. An extra input field is added to simplify the use of the filter."](images/sj142-79-save-as-new-project-popup.png)

Confirm the new, separate project exists alongside the original:

![Actions list showing both tutorial_FilterBusinessPartners and tutorial_API_BUSINESS_PARTNER as distinct projects](images/sj142-80-new-filterbusinesspartners-project.png)

## 3. Add a custom input field

Open the general-data action (the one returning a collection) and add a brand-new field, not present on the original OData entity:

![The action's Input tab, Add Input highlighted](images/sj142-81-actions-add-input.png)

![Add New Field dialog: Key "FirstName", Mandatory No, Parameter "custom", Type "string", Label "FirstName", Static No](images/sj142-82-actions-add-new-field-firstname.png)

## 4. Apply a filter with the Condition Editor

Open **Apply Filters** and build a condition against the new field — note the dialog offers both a **Condition Editor** (point-and-click) and a **Text Expression** (raw syntax) tab:

![Apply Filters dialog, Condition Editor tab selected, a FirstName filter condition row being built](images/sj142-83-filter-value-popup.png)

The finished condition: **Column** FirstName, **Condition** "equal to", **Criteria** bound to the new `${FirstName}` input field:

![Condition Editor: Group row with Column=FirstName, Condition=equal to, Criteria=${FirstName}](images/sj142-84-condition-editor-firstname-equal.png)

Test it with a real value before publishing:

![Test tab with FirstName=Jane as a Test Input Value, returning a filtered Test Preview result](images/sj142-85-actions-test-with-jane.png)

Publish the filtered action the same way as any other — Release, then Publish:

![The action project showing Published status, 2 actions](images/sj142-86-actions-published-filter.png)

## 5. Build a new Skill around the filtered action

![Lobby, creating a new project, Create button highlighted](images/sj142-87-lobby-create-skill.png)
![Create Project, Objective step, Joule Skill tile highlighted](images/sj142-88-create-project-joule-skill-type.png)
![Create Project, Name step: "tutorial_SearchWithName", description "Uses an Action containing a mapped condition to filter on the FirstName"](images/sj142-89-create-project-searchwithname.png)

Inside the new project, create the actual Skill:

![Create menu inside the project, Joule Skill option highlighted](images/sj142-90-joule-studio-create-joule-skill-menu.png)
![Create Joule Skill popup: Name "SearchWithFirstName", Identifier "searchWithFirstName", Description "Retrieve information about employees with a given first name. Usually John or Jane is used"](images/sj142-91-create-joule-skill-popup-searchwithfirstname.png)

## 6. Leave auto-generated response turned on

This is the deliberate difference from Tutorial 3 — **both** toggles stay on:

![Trigger Parameters: "Allow Joule to generate a response" ON, "Allow skill to be started directly by a user" ON — both toggles enabled, unlike Tutorial 3](images/sj142-92-joule-studio-allow-joule-generate-responses-toggle.png)

With no manual Send Message step needed, the rest of the build is just inputs, outputs, and one action:

![Skill Parameters tab, Skill Inputs section, Configure highlighted](images/sj142-93-joule-studio-parameters-configure-skill-inputs.png)
![Configure Skill Inputs: FirstName/firstname/"First name of employee", required](images/sj142-94-joule-studio-configure-skill-inputs-firstname.png)
![Skill Parameters tab, Skill Outputs section, Configure highlighted](images/sj142-95-joule-studio-parameters-configure-skill-outputs.png)
![Configure Skill Outputs: Employees/employees/Employees, Type "Any", marked as a List](images/sj142-96-joule-studio-configure-skill-outputs-employees-lis.png)

## 7. Wire the filtered action

![Choose what happens next palette, Call Action highlighted](images/sj142-97-joule-studio-select-action-plus.png)
![Browse All Actions panel, empty initially](images/sj142-98-joule-studio-browse-all-actions-filter.png)

Browse library confirms multiple candidate actions by the same name across different projects — the filtered one from `tutorial_FilterBusinessPartners` is the one actually needed here:

![Browse library listing 9 actions, with "Retrieves business partner general data" from tutorial_FilterBusinessPartners selected for Add](images/sj142-99-joule-studio-add-action-filterbusinesspartners.png)

Create its Destination Variable, then map the Skill's `FirstName` input directly into the action's custom filter field:

![Create Destination Variable for the business-partner destination](images/sj142-100-joule-studio-create-destination-variable-businessp.png)
![Action Inputs tab, FirstName mapped from the Skill's own firstname input](images/sj142-101-joule-studio-map-input-firstname.png)

Inspect the action's output, then map the Skill's `Employees` output directly from it at the End node — no Send Message step needed anywhere in this flow:

![Action Outputs tab preview, showing the filtered results array structure](images/sj142-102-joule-studio-outputs-tab-preview.png)
![End node's Outputs tab, Employees list mapped from the action's results](images/sj142-103-joule-studio-configure-end-employees-list.png)

## 8. Release and deploy

![Release Project dialog for SearchWithFirstName, version 1.0.0](images/sj142-104-joule-studio-release.png)
![Released confirmation banner with a "Show project version" link](images/sj142-105-joule-studio-show-project-version.png)
![Deploy dialog, Choose an Environment: tutorial environment selected](images/sj142-106-joule-studio-deploy-select-environment-destination.png)
![Deployed confirmation: tutorial_SearchWithFirstName 1.0.0, Deployed, Active](images/sj142-107-joule-studio-deployed-confirmation.png)

## 9. Test it — and watch it correct itself mid-conversation

![Environment's Joule tab, both SearchWithFirstName and CreateBadge listed as deployed capabilities](images/sj142-108-environment-joule-tab-launch.png)

Start a fresh conversation:

![A new Joule conversation panel, "New Conversation" started](images/sj142-109-joule-conversation-new.png)

A realistic front-desk scenario — a security-verification prompt, not a direct "search for" query:

![A new Joule conversation: "I am at the front desk in the reception area. A person claiming to be an employee is here. Can you check if Jane is in the system?"](images/sj142-110-joule-conversation-prompt-jane-front-desk.png)

With the auto-response toggle on, Joule composes the Employee Information card directly from the action's output — no Send Message step was built for this:

![Joule's auto-generated response: an "Employee Information" card for Jane, showing First Name Jane, Last Name Roe, Business Partner ID 1003765](images/sj142-111-joule-conversation-message-response-jane.png)

A follow-up message, mid-conversation, corrects the name entirely:

> *"Thanks, I meant you to check if John is in the system."*

![Joule's follow-up response: an Employee List showing multiple Johns (John Doe, John Smith, John Lara, John Price), and a detail panel confirming John Doe's Business Partner ID 1003764 once selected](images/sj142-112-joule-conversation-follow-up-john-correction.png)

This is **slot correction** working as designed: the Skill's own conversational state handled the name change and re-ran the same filtered action with the new value — nothing in the flow itself needed to know a correction had happened.

## 10. Added by Claude, not from the sources

- The "two paths to a response" Mermaid diagram in section 1 is this book's own comparison between this tutorial's toggle setting and Tutorial 3's — the underlying mechanics are the source's.
- The "slot correction" framing in section 9 is this book's own name for the behavior the tutorial's screenshots demonstrate; the tutorial itself doesn't use that term.
- Not run: the Action Project and Skill described were built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 11. Interview corner

**What interviewers listen for:** you can state precisely what changes in a Skill's flow when auto-response is left on (no Send Message step needed) versus off, and you recognize multi-turn correction as a conversational-state behavior, not something the flow itself has to implement.

<details class="qa"><summary>1. With "Allow Joule to generate a response" left on, what's missing from this Skill's flow compared to Tutorial 3's?</summary>

- A Send Message step — the response is composed automatically from the action's output data instead

</details>

<details class="qa"><summary>2. Why duplicate an existing Action Project with Save As New Project instead of editing the original in place?</summary>

- The original (unfiltered) action is still needed elsewhere (e.g. by the CreateBadge Skill from Tutorial 3) — duplicating preserves it unchanged while creating a separate, filterable version

</details>

<details class="qa"><summary>3. A user says "check if Jane is in the system," gets an answer, then says "I meant John." What makes the Skill handle this correctly without restarting the conversation?</summary>

- The Skill's input mapping is driven by conversational state, not a one-shot parse — a corrected value simply re-triggers the same flow with the new FirstName input, re-running the same filtered action

</details>

## Cheat sheet

| Thing | Detail |
|---|---|
| Duplicate an Action Project | Actions menu → Save As New Project |
| Add a custom filter field | Action's Input tab → Add Input → New Field (type, label, etc.) |
| Build the filter | Apply Filters → Condition Editor (Column / Condition / Criteria) |
| Auto-response on | No Send Message step needed; map outputs directly at End |
| Multi-turn correction | Handled by conversational state, not explicit flow logic |

## Recap

- An existing Action Project can be duplicated via Save As New Project rather than rebuilt from scratch
- A custom input field plus the Condition Editor turns a plain OData action into a filterable one
- With "Allow Joule to generate a response" left on, a Skill needs no Send Message step — outputs map straight through to End
- The finished SearchWithFirstName Skill handled a real mid-conversation correction (Jane → John) without any special-case logic in the flow itself

## Practice

1. Without looking back, name the three fields the Condition Editor uses to build a filter condition
2. Explain in one sentence what's structurally different between this tutorial's flow and Tutorial 3's
3. Describe what happened when the test conversation said "I meant John" instead of "Jane"

## How this chapter was checked

- All 35 images for this tutorial were downloaded and individually opened and visually verified against their captions before being written into this chapter.
- This is part 4 of 5 of the SAP Developers tutorial series "Build Your First Joule Skill in Joule Studio, Classic Edition." Nothing in this chapter is code; nothing was independently executed — the Action Project and Skill described are the tutorial author's own.

## Sources and further reading

- SAP Developers, *Build Your First Joule Skill in Joule Studio, Classic Edition* — https://developers.sap.com/group.joule-studio-first-skill.html, Tutorial 4 of 5 (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 3: building and deploying a Joule Skill](joule-studio-tutorial-3-create-deploy-skill.md) · Next: [Joule Studio tutorial 5: consuming an automated process](joule-studio-tutorial-5-automated-processes.md)
