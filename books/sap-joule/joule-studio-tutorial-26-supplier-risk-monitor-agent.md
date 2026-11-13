# Joule Studio tutorial 26: a Supplier Performance Monitor agent, the second simulated-data agent in this book

*A risk-scoring agent built, like Tutorial 23's HR assistant, entirely on simulated data — because no SAP API integration exists for this scenario at all, not because the real system isn't live yet.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** a second, distinct reason an agent might be built with zero MCP servers — not "not live yet" (as in [Tutorial 23](joule-studio-tutorial-23-hr-onboarding-assistant-agent.md)) but "no SAP API integration exists for this at all"
> - **You will build:** a Supplier Performance Monitor Agent that scores 15 suppliers' risk from KPI breaches, surfaces pre-approved alternatives for at-risk ones, and produces a natural-language advisory report
> - **Level:** beginner · **Time:** about 15 minutes
> - **Builds on:** [Joule Studio tutorial 25: an Equipment Troubleshooting agent](joule-studio-tutorial-25-equipment-troubleshooting-agent.md). **Leads to:** [Joule Studio tutorial 27: a Joule Work trial walkthrough](joule-studio-tutorial-27-joule-work-trial.md)

> [!WARNING]
> Pre-release Joule Studio — screens and exact flow may differ from general availability.

**After this tutorial you can:**

- State the exact risk-scoring rule this agent uses (how many KPI breaches map to low/medium/high risk)
- Explain the difference between this agent's reason for using simulated data and Tutorial 23's reason
- Name the 4 files the build summary highlights and what each is responsible for

## 1. Create the agent

![Open new solution dialog](images/sj221-01-open-new-solution-dialog.png)
![Create Agent, Quick Create mode](images/sj221-02-create-agent-quick-create-mode.png)
![Create Agent, Ideate and Plan mode](images/sj221-03-create-agent-ideate-and-plan-mode.png)
![Quick Create intent generation](images/sj221-04-quick-create-intent-generation.png)

## 2. One clarifying question

![Clarifying question: "Which user roles should the agent primarily serve?" Options: Procurement Manager, Category Manager, Supply Chain Analyst, All of the above, Other](images/sj221-05-clarifying-questions.png)

![Intent created](images/sj221-06-intent-created.png)
![Idea Board](images/sj221-07-idea-board.png)
![Entering "create requirements" in chat](images/sj221-08-enter-create-requirements-in-chat.png)

## 3. The PRD and the real-time risk scoring rule

![PRD: Title "Supplier Performance Monitor Agent," Date 2026-05-04, Owner "Procurement Excellence Team," Solution Category "AI Agent." Elevator Pitch — "Procurement teams are flying blind when it comes to supplier risk. This agent autonomously monitors supplier KPIs, flags at-risk suppliers before disruptions occur, and surfaces pre-approved alternatives — turning reactive firefighting into proactive supply chain management." Business Need: manual supplier performance reviews are slow, infrequent, and miss early warning signals; when a supplier is flagged, buyers spend hours searching for qualified alternatives. Product Objectives: automatically classify supplier risk levels based on configurable KPI thresholds; surface ranked, pre-approved alternative suppliers for every at-risk supplier identified; deliver a structured advisory report summarizing findings and recommended next actions. Requirements: R1 Supplier KPI Retrieval — user story and acceptance criteria (agent returns on-time delivery rate, quality score, complaint count, and order fulfillment rate per supplier from the simulated dataset), Priority Rank 1; R2 Risk Classification](images/sj221-09-prd-overview.png)

The risk-scoring rule, confirmed directly: the agent flags at-risk suppliers using a risk scoring engine where KPI breaches map to severity — **1 KPI breach = low risk, 2 = medium, 3+ = high.**

> [!NOTE]
> The build log states the same reasoning seen in [Tutorial 23](joule-studio-tutorial-23-hr-onboarding-assistant-agent.md), but for a different underlying cause: **"No SAP API integration exists (using simulated data), so no MCP tools needed."** Tutorial 23's HR assistant used simulated data because its real target system (SuccessFactors HXM) was planned but not yet live — an integration that *will* exist eventually. Here, the stated reason is that no SAP API integration exists for this scenario *at all* — a different kind of gap, not a timing one.

## 4. Specification and generation

![Entering "create specification" in chat](images/sj221-10-enter-create-specification-in-chat.png)
![Specification creation](images/sj221-11-spec-creation.png)
![Specification ready](images/sj221-12-spec-ready.png)
![Build the solution](images/sj221-13-build-the-solution.png)
![Solution creation in progress](images/sj221-14-solution-creation-in-progress.png)

The finished solution, confirmed directly — 4 key files:

| File | Purpose |
|---|---|
| `app/data/suppliers.py` | 15 simulated suppliers across 3 categories |
| `app/scoring.py` | KPI threshold engine with configurable thresholds |
| `app/tools.py` | 4 agent tools registered |
| `app/agent.py` | Agent with full milestone instrumentation |

What the agent does, confirmed directly:

- Retrieves KPIs — on-time delivery, quality score, complaint count, and lead time
- Flags at-risk suppliers using the risk scoring engine (1 breach = low, 2 = medium, 3+ = high)
- Retrieves approved alternatives per category from the supplier registry, ranked by composite score
- Generates a risk summary broken down by severity and category
- Produces a natural-language advisory report via SAP AI Core (LLM)

![Solution code view](images/sj221-15-solution-code.png)

## 5. Try the agent: a real 15-supplier breakdown

![Try Your Agent chat](images/sj221-16-try-your-agent.png)

![Agent response: "Supplier Performance Review - Complete KPI Analysis. I've reviewed all 15 suppliers across three categories. Here's the comprehensive breakdown: OVERALL SUMMARY. Total Suppliers: 15. Performing Well: 9 suppliers (60%). At Risk: 6 suppliers (40%)." Right panel, Key files created table and Test results: "50/50 tests passing | 87% code coverage | test_report.json generated." Ready to deploy? "Just say 'deploy' and I'll walk you through deploying this agent to SAP BTP." Traces panel: Agent Run (17ms) → Create Agent Agent (16ms) → get_all_supplier_scores (2ms)](images/sj221-17-agent-response.png)

> [!TIP]
> 6 of 15 suppliers (40%) flagged at risk in this test run is a meaningfully large fraction — a useful sanity check (similar to [Tutorial 19's](joule-studio-tutorial-19-billing-completeness-data-product.md) billing-completeness numbers) that the simulated dataset has real, distributed variation rather than being tuned to always look clean.

## 6. Testing and deployment

![Testing overview](images/sj221-18-testing-overview.png)
![Deploy the agent](images/sj221-19-deploy-the-agent.png)
![Deployment complete](images/sj221-20-deployment-complete.png)
![Try the deployed agent](images/sj221-21-try-the-deployed-agent.png)

## 7. Added by Claude, not from the sources

- The NOTE in section 3 contrasting this agent's "no integration exists" reasoning with Tutorial 23's "not yet live" reasoning is this book's own comparison across tutorials — both stated reasons are transcribed directly from each tutorial's own build log.
- The TIP in section 5 reading the 40% at-risk figure as a realistic-data signal is this book's own interpretation, drawing the same pattern noted in Tutorial 19's chart.
- Not run: the agent described was built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 8. Interview corner

**What interviewers listen for:** you can state the exact breach-to-risk-level mapping without hesitation, and you can articulate the difference between this agent's "no integration exists" and Tutorial 23's "not live yet" reasons for using simulated data.

<details class="qa"><summary>1. What is this agent's exact risk-scoring rule?</summary>

- 1 KPI breach = low risk, 2 KPI breaches = medium risk, 3 or more KPI breaches = high risk

</details>

<details class="qa"><summary>2. This is the second agent in this book built with zero MCP servers. How does its stated reason differ from Tutorial 23's HR Virtual Assistant?</summary>

- This agent's build log states "no SAP API integration exists" for this scenario — a capability gap, not a timing one. Tutorial 23's reason was that its real target system (SuccessFactors HXM Suite) was "planned but not yet live" — an integration that will exist eventually, just not yet

</details>

<details class="qa"><summary>3. Name the 4 key files in this agent's solution and what each is responsible for.</summary>

- `suppliers.py` (15 simulated suppliers across 3 categories), `scoring.py` (configurable KPI threshold engine), `tools.py` (4 registered agent tools), `agent.py` (the agent itself, with full milestone instrumentation)

</details>

> [!TIP]
> **🧩 Design question**
> *"A procurement director asks whether this agent's recommendations can be trusted the same way as one backed by live SAP data."* Talk about: the agent's reasoning and risk-scoring logic being fully real and testable (50/50 tests passing, a genuine threshold engine) even though the underlying supplier data is simulated — the distinction to make clear is between "the logic is sound" (yes, demonstrably) and "the specific numbers reflect your actual suppliers today" (no, not until this is wired to a real data source) — the same distinction worth raising for Tutorial 23's HR assistant.

## Cheat sheet

| Thing | Detail |
|---|---|
| Why simulated data | "No SAP API integration exists" for this scenario — different reason from Tutorial 23's "not yet live" |
| Risk scoring | 1 breach = low, 2 = medium, 3+ = high |
| Suppliers | 15, across 3 categories |
| Key files | `suppliers.py`, `scoring.py`, `tools.py`, `agent.py` |
| Tests | 50/50 passing, 87% code coverage |
| Test result | 9/15 (60%) performing well, 6/15 (40%) at risk |

## Recap

- This is the second agent in this book built entirely against simulated data with zero MCP servers, for a different stated reason than Tutorial 23's HR assistant — no integration exists here, versus not yet live there
- The risk-scoring rule is concrete and stated directly: 1/2/3+ KPI breaches map to low/medium/high risk
- The finished agent's test run flagged 6 of 15 simulated suppliers (40%) as at-risk, a realistic, non-trivial distribution
- 50/50 tests passed at 87% code coverage before deployment

## Practice

1. Without looking back, state the exact KPI-breach-to-risk-level mapping
2. Explain the difference between this agent's reason for simulated data and Tutorial 23's
3. Name the 4 key files in this agent's solution

## How this chapter was checked

- The full tutorial "Build a Supplier Performance Monitor Agent" (developers.sap.com, Beginner, 15 min) was read in full, 13 Nov 2026.
- 21 images were found and downloaded, all used here; each was opened and visually verified against its caption before being written into this chapter, including the full PRD, the build summary's key files table, and the live test response, all transcribed directly.
- Nothing in this chapter was independently re-executed — the agent described was built and tested by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Build a Supplier Performance Monitor Agent* — https://developers.sap.com/tutorials/supplier-performance-monitor-agent (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 25: an Equipment Troubleshooting agent](joule-studio-tutorial-25-equipment-troubleshooting-agent.md) · Next: [Joule Studio tutorial 27: a Joule Work trial walkthrough](joule-studio-tutorial-27-joule-work-trial.md)
