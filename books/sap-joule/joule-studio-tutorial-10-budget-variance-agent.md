# Joule Studio tutorial 10: automating budget variance management

*A cost-center budgeting agent that doesn't just detect variance — it drafts a comparison chart and an approval email, and only writes the revised budget back after a human signs off.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the same Joule Studio flow again, this time generating a Chart Generation Module as part of the agent's own architecture — not just text output
> - **You will build:** a Budgeting Agent for Cost Center Increases that detects spot/sustained/cascade cost disruptions, proposes a revised budget with a visual comparison chart, and drafts an approval email
> - **Level:** beginner · **Time:** about 15 minutes
> - **Builds on:** [Joule Studio tutorial 9: balance confirmation workflows](joule-studio-tutorial-9-balance-confirmation-agent.md). **Leads to:** [Joule Studio tutorial 11: building an agent to handle demand spikes](joule-studio-tutorial-11-demand-spike-agent.md)

> [!WARNING]
> Pre-release Joule Studio — screens and exact flow may differ from general availability.

**After this tutorial you can:**

- Name the 3 categories of cost disruption this agent is designed to classify, with a real example of each
- Read a Solution Architecture section that includes a non-obvious component (a chart generator) and explain why it's there
- State exactly where the autonomous/human-approval boundary sits for this agent

## 1. Three disruption categories

| Category | Example |
|---|---|
| Spot increase | An emergency supplier surcharge |
| Sustained increase | A new energy tariff |
| Cascade increase | A shared-infrastructure cost rippling through the cost-center hierarchy |

Pain points driving this agent: no automated detection, manual hierarchy traversal, spreadsheet recalculation, manual approval communications, and no consolidated audit trail.

## 2. Define the intent

![Open Joule Studio landing screen](images/sj202-01-open-joule-studio.png)

![Create Agent dialog: Name "Budgeting Agent for Cost Center Increases," full intent statement (detect cost increases, validate, identify affected cost centers, propose revised plan with charts, draft approval emails, apply on approval, log for audit, configurable thresholds/scenarios/granularity), Quick Create checked](images/sj202-02-create-agent-dialog.png)

![Confirm Business Goals screen](images/sj202-03-confirm-business-goals.png)

## 3. Review the intent

![Intent Summary](images/sj202-04-intent-summary.png)
![Intent file in the File tree](images/sj202-05-intent-file.png)

Recommended solution: a Python agent using the **Agent-to-Agent (A2A)** protocol.

![Intent Fit score shown before proceeding](images/sj202-06-intent-fit-score.png)

## 4. The PRD

![PRD, low-code view](images/sj202-07-product-requirements-document.png)
![PRD raw Markdown file](images/sj202-08-prd-file.png)
![Requirements section: user stories + acceptance criteria](images/sj202-09-requirements-section.png)

**Automation boundary, stated explicitly:** detecting cost anomalies against configured thresholds is autonomous; **writing a revised budget back to S/4HANA always requires human approval.**

The architecture names a component not obvious from the intent statement alone — a dedicated chart generator:

![Solution Architecture: AI Agent (Python/A2A) as the core reasoning engine, SAP S/4HANA OData APIs, Generative AI Hub (LLM) for drafting, a Chart Generation Module producing an embedded comparison chart (original plan vs. revised plan vs. forecast) as an inline image in the approval email, an Audit Log Store, a Configuration Store for thresholds/scenarios/granularity, and named Integration Points including the Cost Center API (CE_COSTCENTER_0001)](images/sj202-10-solution-architecture.png)

> [!NOTE]
> The **Chart Generation Module** produces an actual embedded image — a plan-vs-revised-plan-vs-forecast comparison chart inlined directly into the approval email — not just a text summary. This is a concrete example of a generated agent producing structured visual output as part of its normal workflow, not only conversational text.

## 5. Specification

![Specification review](images/sj202-11-specification-review.png)
![Specification folder, file tree](images/sj202-12-specification-folder.png)

> [!NOTE]
> This tutorial's chat trigger phrase is **"Build the solution"** — a different wording from Tutorial 9's `execute specification`. Both trigger the same generation step; the exact phrase to type varies slightly between these tutorials, worth knowing so you're not thrown if a different one is suggested elsewhere.

## 6. Generate the solution

![Build the solution trigger, typed into chat](images/sj202-13-build-the-solution.png)
![Preview panel](images/sj202-14-preview-agent.png)
![LLM configuration and MCP server config](images/sj202-15-llm-mcp-config.png)
![Evaluation section](images/sj202-16-evaluation.png)

## 7. Validate with tests

![Testing Overview](images/sj202-17-testing-overview.png)

A **Test Solution** button lets you explicitly re-run the test suite — "sometimes it finds something new":

![Test Solution button](images/sj202-18-test-solution.png)
![Testing chat, further interaction](images/sj202-19-testing-chat.png)

## 8. Deploy

![Deploy, step 1](images/sj202-20-deploy-step1.png)
![Deploy, step 2 confirmation](images/sj202-21-deploy-step2.png)

Same governance boundary as every other agent in this family: **production deployment is never done from inside Joule Studio.** Deploying here reaches a SAP-managed development/test service; once there, the agent becomes auto-discoverable to Joule without end users needing to know its name.

## 9. Added by Claude, not from the sources

- The explicit callout on the Chart Generation Module in section 4 highlights a component the tutorial's own architecture text names but doesn't dwell on — worth surfacing since it's a genuinely distinct capability (structured visual output) not seen in Tutorials 7–9.
- Not run: the agent described was built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 10. Interview corner

**What interviewers listen for:** you can name all 3 disruption categories with their examples, and you know the chart-generation capability is a real architectural component, not just a chat-response formatting choice.

<details class="qa"><summary>1. What are the 3 disruption categories this agent classifies, with one example each?</summary>

- Spot increase (emergency supplier surcharge), Sustained increase (new energy tariff), Cascade increase (shared-infrastructure cost rippling through the hierarchy)

</details>

<details class="qa"><summary>2. What does the Chart Generation Module actually produce, and where does it end up?</summary>

- A comparison chart (original plan vs. revised plan vs. forecast), embedded as an inline image directly in the approval email — not just described in text

</details>

<details class="qa"><summary>3. Where exactly is the autonomous/human-approval line drawn for this agent?</summary>

- Detecting cost anomalies against configured thresholds is autonomous; writing a revised budget back to S/4HANA always requires human approval

</details>

> [!TIP]
> **🧩 Design question**
> *"A finance director asks why the agent sends an approval email with a chart instead of just auto-applying the revised budget when confidence is high."* Talk about: the hard architectural boundary (budget writes always need human approval, regardless of confidence), the chart existing specifically to make that approval decision fast and visual rather than requiring the approver to dig into numbers themselves, and why "high confidence" is not treated as grounds to skip the human step in this design.

## Cheat sheet

| Thing | Detail |
|---|---|
| Disruption categories | Spot, Sustained, Cascade |
| Chart Generation Module | Produces a plan-vs-revised-vs-forecast chart, embedded in the approval email |
| Autonomous | Cost-anomaly detection against thresholds |
| Always human-approved | Any write of a revised budget back to S/4HANA |
| Trigger phrase | "Build the solution" (vs. other tutorials' `execute specification`) |

## Recap

- This agent classifies cost disruptions into 3 categories (spot, sustained, cascade) and proposes revised budgets accordingly
- Its architecture includes a dedicated Chart Generation Module producing a real embedded comparison chart in the approval email, not just text
- Budget writes to S/4HANA always require human approval — detection and proposal generation are the only autonomous parts
- The exact chat phrase to trigger solution generation varies between tutorials in this family — "Build the solution" here, `execute specification` elsewhere

## Practice

1. Without looking back, name the 3 disruption categories and one example of each
2. Explain in one sentence what the Chart Generation Module produces and where it appears
3. State the exact autonomous/human-approval boundary for this agent

## How this chapter was checked

- The full tutorial "Automate Budget Variance Management for Cost Centers with a Custom Joule Agent" (developers.sap.com, Beginner, 20 min, 9 steps) was read in full, 13 Nov 2026.
- 21 images were found and downloaded, all used here; each was opened and visually verified against its caption before being written into this chapter, including the Solution Architecture screenshot confirming the Chart Generation Module detail.
- Nothing in this chapter was independently re-executed — the agent described was built and tested by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Automate Budget Variance Management for Cost Centers with a Custom Joule Agent* — https://developers.sap.com/tutorials/budget-variance-agent (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 9: balance confirmation workflows](joule-studio-tutorial-9-balance-confirmation-agent.md) · Next: [Joule Studio tutorial 11: building an agent to handle demand spikes](joule-studio-tutorial-11-demand-spike-agent.md)
