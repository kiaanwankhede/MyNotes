# Joule Studio tutorial 1: environment and connectivity setup

*Everything after this tutorial assumes a Control Tower environment and two working destinations already exist — this is where they come from.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how to create a Control Tower environment for Joule Studio, build two destinations from scratch with the exact properties Joule Studio needs, and associate each destination with both your own environment and the shared Public environment
> - **You will build:** a test environment named `tutorial`, plus `tutorial_S4HANA_MOCK` and `tutorial_Badge_Service` destinations, ready for the Action Projects built in the next tutorial
> - **Level:** intermediate · **Time:** about 10 minutes
> - **Builds on:** [Joule Studio and the agent development lifecycle](02-joule-studio-lifecycle.md). **Leads to:** [Joule Studio tutorial 2: Action Projects](joule-studio-tutorial-2-action-projects.md)

**After this tutorial you can:**

- Create a Control Tower environment and confirm the Joule Digital Assistant tab actually appears inside it
- Build a destination from scratch with the 3 additional properties Joule Studio specifically requires
- Explain why a destination has to be associated with the Public environment, not just your own

## 1. Create the environment

```mermaid
flowchart LR
    E["1. Create environment\n(Control Tower)"] --> D1["2. Create destination\n(S4HANA_MOCK)"]
    D1 --> D2["3. Create destination\n(Badge_Service)"]
    D2 --> A["4. Associate both destinations\nwith your environment AND Public"]
```

Everything in Joule Studio runs inside a **Control Tower environment**.

![SAP Build's Lobby, with Control Tower highlighted in the left sidebar, showing Tenant Configuration tiles including Environments](images/sj142-01-control-tower.png)

Open **Environments** and create a new one:

![Create Environment dialog: Environment Name "tutorial", Identifier "tutorial", Color, Description "Environment for testing the tutorial for Joule Skills"](images/sj142-02-create-environment.png)

Confirm the **Joule** tab now appears inside the environment — this is where the Joule Digital Assistant for this environment will live once a Skill is deployed to it:

![The new environment's detail page with a Joule Digital Assistant tab visible](images/sj142-03-joule-tab-environment.png)

## 2. Create the first destination: a mock S/4HANA OData service

Destinations are created in BTP's **Connectivity** area, not inside Joule Studio itself — reached from Control Tower via **Create Destination → From Scratch**:

![The Create New Destination menu, showing From Scratch, From File, and Service Instance options](images/sj142-04-destination-from-scratch.png)

| Field | Value |
|---|---|
| Name | `tutorial_S4HANA_MOCK` |
| Type | HTTP |
| Proxy Type | Internet |
| URL | the mock S/4HANA OData service URL |
| Authentication | NoAuthentication |

Three **Additional Properties** are required — this is the detail easiest to miss, since the destination will otherwise look complete without them:

| Key | Value |
|---|---|
| `sap.processautomation.enabled` | `true` |
| `sap.applicationdevelopment.actions.enabled` | `true` |
| `sap.build.usage` | `odata_gen` |

![Create Destination form fully filled in for tutorial_S4HANA_MOCK, with all 3 additional properties set, numbered steps 1 through 7](images/sj142-05-create-destination-s4hanamock.png)

Check the connection before moving on:

![Check Connection succeeded for tutorial_S4HANA_MOCK, confirmed via an HTTP request without authentication](images/sj142-06-check-connection-s4hanamock.png)

## 3. Create the second destination: the badge service

A second destination, same shape, pointing at a third-party badge-issuing service used later in Tutorial 3:

![Create Destination form for tutorial_Badge_Service, same 3 additional properties pattern as the first destination](images/sj142-07-badge-service-destination.png)

![Check Connection succeeded for tutorial_Badge_Service](images/sj142-08-check-connection-badgeservice.png)

## 4. Associate both destinations with the right environments

Before either destination is usable, both the destinations list and Control Tower itself need to show them:

![Control Tower's Destinations list, searched for "tutorial," showing "No results found" before association is complete](images/sj142-09-controltower-destinations.png)

Use **Add Destination** from Control Tower. Step 1 picks which destination:

![Add Destination wizard, Select Destination step, listing tutorial_Badge_Service and tutorial_S4HANA_MOCK](images/sj142-10-select-destination.png)

Step 2 associates it with an environment — here, the `tutorial` environment:

![Add Destination wizard, Associate Environments step, with the tutorial environment checked under Specific Environments](images/sj142-11-associate-environments.png)

> [!CAUTION]
> **🔒 A destination also has to be associated with the Public environment, not just your own**
> Repeat the association step a second time, this time checking **Public** instead of (or in addition to) your own environment. Skipping this is a real, easy-to-miss way to end up with a destination that looks fully configured but doesn't actually work once an Action Project or Skill tries to use it.

![Add Destination wizard, second pass, with the Public environment checked instead](images/sj142-12-add-destinations.png)

Confirm both destinations now show up, each associated with 2 environments:

![Final Destinations list showing tutorial_Badge_Service and tutorial_S4HANA_MOCK, each associated with 2 environments (Public + tutorial)](images/sj142-13-lobby-check.png)

## 5. Added by Claude, not from the sources

- The explicit "don't skip the Public environment" framing in section 4 is this book's own emphasis, written because the tutorial's own flow repeats this step without calling out why it matters — the underlying requirement is the source's.
- Not run: this chapter documents the tutorial author's own setup; nothing was independently executed for this book.

## 6. Interview corner

**What interviewers listen for:** you know a destination needs two separate environment associations (your own + Public), not just one, and you can name the three additional properties a Joule Studio destination specifically needs.

<details class="qa"><summary>1. What three additional properties does a destination need for Joule Studio to use it?</summary>

- `sap.processautomation.enabled=true`, `sap.applicationdevelopment.actions.enabled=true`, `sap.build.usage=odata_gen`

</details>

<details class="qa"><summary>2. A destination checks connection successfully but an Action Project built from it still can't find it. What's the likely cause?</summary>

- It wasn't associated with the Public environment — only associating it with your own environment isn't enough
- *Stronger answer:* re-run the Add Destination flow a second time, this time selecting Public under Specific Environments

</details>

## Cheat sheet

| Step | Detail |
|---|---|
| Create environment | Control Tower → Environments → Create |
| Required destination properties | `sap.processautomation.enabled`, `sap.applicationdevelopment.actions.enabled`, `sap.build.usage=odata_gen` |
| Environment associations needed | Your own environment **and** Public — both, not either |

## Recap

- A Control Tower environment is the prerequisite container everything else in Joule Studio runs inside
- A destination built for Joule Studio needs 3 specific additional properties, not just a URL and authentication type
- Every destination needs to be associated with both your own environment and the Public environment — missing the second one is a common, hard-to-diagnose gap

## Practice

1. Without looking back, name the three additional properties a Joule Studio destination needs
2. Explain in one sentence why a destination needs to be associated with the Public environment specifically

## How this chapter was checked

- All 13 images for this tutorial were downloaded and individually opened and visually verified against their captions before being written into this chapter — not captioned from filename or DOM order alone.
- This is part 1 of 5 of the SAP Developers tutorial series "Build Your First Joule Skill in Joule Studio, Classic Edition." Nothing in this chapter is code; nothing was independently executed — the environment and destinations described are the tutorial author's own.

## Sources and further reading

- SAP Developers, *Build Your First Joule Skill in Joule Studio, Classic Edition* — https://developers.sap.com/group.joule-studio-first-skill.html, Tutorial 1 of 5 (read in full 13 Nov 2026)

Previous: [n8n workflows in Joule Studio](04-n8n-workflows.md) · Next: [Joule Studio tutorial 2: Action Projects](joule-studio-tutorial-2-action-projects.md)
