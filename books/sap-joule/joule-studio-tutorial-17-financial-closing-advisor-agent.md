# Joule Studio tutorial 17: building a Financial Closing Advisor agent

*The agent drafted conversationally in the previous tutorial, now built — plus the clearest Fit-Gap Analysis table in this book, showing exactly which requirements SAP's standard product already covers and which need custom agent logic.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how to read a full Fit-Gap Analysis table — requirement by requirement, each tagged No/Maybe/Yes for "is this a gap requiring custom agent logic" — before any code is generated
> - **You will build:** a Financial Closing Advisor that reads SAP Advanced Financial Closing (AFC) task data, resolves the dependency chain, diagnoses why tasks are blocked, and recommends the next closing activity with reasoning — advisory only, no writes
> - **Level:** beginner · **Time:** about 20 minutes
> - **Builds on:** [Joule Studio tutorial 16: drafting a Joule Studio intent with Joule chat](joule-studio-tutorial-16-joule-work-intent.md). **Leads to:** [Joule Studio tutorial 18: an AP Invoice Agent Extension](joule-studio-tutorial-18-ap-invoice-agent-extension.md)

> [!WARNING]
> Pre-release Joule Studio — screens and exact flow may differ from general availability.

**After this tutorial you can:**

- Read a Fit-Gap Analysis table and explain what "No," "Maybe," and "Yes" mean in the Gap column
- Name the 3 runtime skills this agent registers and what each is responsible for
- Explain why this agent talks to AFC via direct REST calls wrapped as custom MCP tools, instead of a pre-built MCP server

## 1. Create the agent

![Create new solution](images/sj211-02-create-solution.png)

![Create Agent dialog: Name "Financial Closing Advisor," Intent Statement — "Please create an agent. The agent should support financial controllers during the financial closing cycle by monitoring the status, priority, and sequence of all closing tasks and workflows. It retrieves the current status of each closing activity from the SAP Financial Closing Cockpit, identifies completed, in-progress, blocked, and pending tasks, evaluates the dependency chain and priority of each task, and recommends to the controller the next financial closing activities to be actioned — in the correct sequence and with clear reasoning. Where tasks are blocked by errors, missing data, or incomplete upstream activities, the agent identifies the root cause and suggests corrective actions. The agent supports configuration for closing calendar, task ownership, escalation thresholds, and deadline proximity alerts," Quick Create checked](images/sj211-02-create-agent-dialog.png)

![Business Goals confirmation](images/sj211-02-business-goals-confirmation.png)
![Business Goals & success metrics](images/sj211-02-business-goals-metrics.png)

> [!NOTE]
> This typed intent statement is close in substance to the paste-ready paragraph drafted in [Tutorial 16](joule-studio-tutorial-16-joule-work-intent.md), but not word-for-word identical — it's written in the third person about "financial controllers" rather than first person, and names the SAP Financial Closing Cockpit specifically. The underlying requirements (status/priority/sequence monitoring, blocked-task root-cause diagnosis, configurable thresholds) carry through unchanged.

## 2. Review the intent: a full Fit-Gap Analysis

![Intent Summary](images/sj211-03-intent-summary.png)

This is the most detailed Fit-Gap Analysis table in this book — each requirement checked against SAP's standard product before deciding what needs custom agent logic:

![Fit Gap Analysis table, 7 rows: Retrieve closing task list/statuses → SAP Advanced Financial Closing, API sap.afc:apiResource:SSPIV1:v1, Gap No. Query task activities/metadata → AFC/S4HANA, TaskProviderV2:v1, Gap No. Evaluate task dependency chain/sequence → AFC, SSPIV1:v1, Gap Maybe ("dependency reasoning logic must be built in agent"). Recommend next closing activities with reasoning → None (standard), Gap Yes ("requires AI reasoning layer — custom agent capability"). Identify root cause of blocked tasks → None (standard), Gap Yes ("custom agent logic needed to correlate errors and upstream failures"). Escalation threshold and deadline proximity alerts → AFC (partial), SSPIV1:v1, Gap Maybe ("AFC has scheduling; configurable alert logic must be built in agent"). Closing calendar and task ownership configuration → AFC, SCIMV2:v1, Gap No. Key findings: AFC is the primary standard product and key data source; no MCP servers exist for AFC APIs, so the agent integrates via direct REST calls wrapped as custom MCP tools; the intelligent advisory layer is a genuine gap requiring a custom AI agent; S/4HANA Finance Task Activity API provides supplementary data; industry variants may need domain-specific extensions](images/sj211-03-fit-gap-analysis.png)

| Gap value | Meaning |
|---|---|
| **No** | Standard SAP product (AFC) already covers this requirement directly |
| **Maybe** | AFC provides the underlying data, but reasoning/alert logic on top must be built into the agent |
| **Yes** | No standard capability exists at all — this requires genuine custom AI agent reasoning |

Recommended solution: a pro-code Python AI agent (A2A protocol) connecting to AFC via REST APIs — **Recommended solution category: AI Agent, Intent fit: 88%.**

## 3. The PRD and specification

![Requirements, low-code view](images/sj211-04-requirements-lowcode-view.png)
![Requirements file tree](images/sj211-04-requirements-file-tree.png)
![Specification, low-code view](images/sj211-05-specification-lowcode-view.png)
![Specification file tree](images/sj211-05-specification-file-tree.png)

## 4. Generate the solution

![Generated agent, low-code view](images/sj211-06-solution-agent-lowcode-view.png)
![Generated agent.py Python code](images/sj211-06-agent-python-code.png)

The build summary, confirmed directly — **all 49 specification items complete**:

![Build summary: "All 49 specification items marked complete." Solution Structure — solution.yaml, 3-asset solution: agent + 2 MCP servers. Agent (assets/financial-closing-advisor-agent/): app/agent.py (LangGraph-based agent, full system prompt — advisory-only guardrails, pagination limits, AFC unavailability handling), app/agent_executor.py (all 5 business milestones instrumented with OpenTelemetry spans and structured logs, M1–M5), asset.yaml (registered with dependencies on both MCP servers). Runtime Skills table: closing-task-analysis (dependency chain resolution, task classification, next-action recommendations), blocker-diagnosis (4-type blocker classification — missing data/upstream/system error/config — corrective action templates), escalation-management (deadline threshold evaluation, severity scoring CRITICAL/HIGH/MEDIUM/LOW, alert summaries). MCP Servers: sap-afc-scheduling-spi-mcp-server (15 tools, Scheduling SPI), sap-afc-task-provider-spi-mcp-server (25 tools, Task Provider SPI), mcp-mock.json (40 tools mocked with realistic AFC data for offline testing). Tests: 71 business logic tests all pass; 94.05% overall test score (168 total, 158 pass); test_report.json generated](images/sj211-06-solution-what-was-built.png)

> [!NOTE]
> **Why direct REST calls wrapped as custom MCP tools, not a pre-built MCP server:** the Fit-Gap findings state it plainly — no MCP servers exist yet for AFC's APIs. Joule Studio generates `sap-afc-scheduling-spi-mcp-server` and `sap-afc-task-provider-spi-mcp-server` itself, wrapping the Scheduling SPI and Task Provider SPI REST APIs, the same pattern seen in [Tutorial 8](joule-studio-tutorial-8-ai-sales-assistant-agent.md) when no pre-built server existed for an integration.

## 5. Validate with tests, preview, and deploy

![Preview chat with the agent](images/sj211-07-solution-preview-chat.png)
![Testing Overview, build complete](images/sj211-07-testing-overview-built.png)
![Testing Overview detail: 71 business logic tests, 94.05% overall score, 168 total/158 passed](images/sj211-07-testing-overview-detail.png)
![Deploy confirmation](images/sj211-08-deploy-confirmation.png)

Same governance boundary as every other agent in this family: development/test landscape only from inside Joule Studio.

## 6. Added by Claude, not from the sources

- The Gap-value interpretation table in section 2 (No/Maybe/Yes meanings) is this book's own synthesis of the pattern visible across the Fit-Gap Analysis table's 7 rows — each individual Gap value and note is transcribed directly from the source screenshot.
- The NOTE in section 2 comparing this typed intent statement to Tutorial 16's drafted paragraph is this book's own cross-reference, made by directly comparing the two screenshots' text.
- Not run: the agent described was built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 7. Interview corner

**What interviewers listen for:** you can explain a Fit-Gap Analysis table to someone who's never seen one, and you know why this particular agent needed Joule Studio to generate its own MCP servers rather than reuse existing ones.

<details class="qa"><summary>1. In a Fit-Gap Analysis, what does a "Maybe" in the Gap column mean, using this agent's own example?</summary>

- The standard product (AFC) already provides the underlying data, but the reasoning or alerting logic built on top of that data doesn't exist yet and must be built into the custom agent — e.g. AFC exposes scheduling data, but configurable escalation-alert logic still has to be custom

</details>

<details class="qa"><summary>2. Name the 3 runtime skills this agent registers and what each does.</summary>

- `closing-task-analysis` (dependency chain resolution, task classification, next-action recommendations), `blocker-diagnosis` (4-type blocker classification with corrective action templates), `escalation-management` (deadline threshold evaluation, severity scoring, alert summaries)

</details>

<details class="qa"><summary>3. Why does this agent integrate with AFC via direct REST calls wrapped as custom MCP tools instead of an existing MCP server?</summary>

- The Fit-Gap findings state no MCP servers exist yet for AFC's APIs, so Joule Studio generates its own (`sap-afc-scheduling-spi-mcp-server`, `sap-afc-task-provider-spi-mcp-server`) wrapping the Scheduling SPI and Task Provider SPI REST APIs directly

</details>

> [!TIP]
> **🧩 Design question**
> *"A finance director asks why this agent only recommends and never actually clears a blocked closing task itself, when it clearly understands the root cause."* Talk about: the intent statement's own framing (support the controller, recommend the next activity "with clear reasoning") never describing a write action at all — this agent's entire value is diagnostic and advisory, consistent with the "advisory-only guardrails" named explicitly in `app/agent.py`'s system prompt, and with the pattern across this book that closing-task corrections (unlike, say, a budget revision or STO release) stay entirely in human hands.

## Cheat sheet

| Thing | Detail |
|---|---|
| Intent fit | 88% |
| Solution structure | Agent + 2 MCP servers (3-asset solution) |
| MCP servers | Scheduling SPI (15 tools), Task Provider SPI (25 tools) — both custom-generated, no pre-built server existed |
| Runtime skills | `closing-task-analysis`, `blocker-diagnosis`, `escalation-management` |
| Tests | 71 business logic tests, all pass; 94.05% overall (168 total, 158 pass) |
| Write access | None — advisory only, by design |

## Recap

- This agent's Fit-Gap Analysis is the clearest example in this book of distinguishing "standard product already covers this" from "this needs custom agent reasoning" — 3 of 7 requirements were tagged Yes or Maybe
- No pre-built MCP server existed for AFC, so Joule Studio generated 2 of its own, wrapping the Scheduling SPI and Task Provider SPI REST APIs directly
- 3 runtime skills handle dependency analysis, blocker diagnosis, and escalation management respectively
- The agent is advisory-only by design — it recommends and diagnoses, but never writes back to AFC
- 71 business logic tests passed, with an overall test score of 94.05% across 168 total tests

## Practice

1. Without looking back, explain what "No," "Maybe," and "Yes" mean in a Fit-Gap Analysis Gap column, using one example of each from this agent
2. Name the 2 MCP servers this agent uses and how many tools each exposes
3. Explain why this agent never writes back to SAP Advanced Financial Closing

## How this chapter was checked

- The full tutorial "Build a Financial Closing Advisor Agent" (developers.sap.com, Beginner, 20 min) was read in full, 13 Nov 2026.
- 17 images were found and downloaded, all used here; each was opened and visually verified against its caption before being written into this chapter, including the full Fit-Gap Analysis table and the final build summary, both transcribed in detail rather than paraphrased.
- Nothing in this chapter was independently re-executed — the agent described was built and tested by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Build a Financial Closing Advisor Agent* — https://developers.sap.com/tutorials/financial-closing-advisor-agent (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 16: drafting a Joule Studio intent with Joule chat](joule-studio-tutorial-16-joule-work-intent.md) · Next: [Joule Studio tutorial 18: an AP Invoice Agent Extension](joule-studio-tutorial-18-ap-invoice-agent-extension.md)
