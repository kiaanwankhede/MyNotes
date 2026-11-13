# Joule Studio tutorial 13: building a Cable Roll Optimizer agent

*A deterministic optimization engine wrapped in an agent — not an LLM guessing at the best cable roll, a real algorithm minimizing offcut waste, with the LLM only presenting the result.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how a generated agent wraps a genuine optimization algorithm (not LLM reasoning) and exposes it through 4 separate MCP servers, one per integrated API
> - **You will build:** a Cable Roll Optimizer that reads work order requirements, batch attributes, and stock levels, runs a deterministic optimization engine to minimize cable offcut waste, and raises a Stock Transfer Order on planner approval
> - **Level:** beginner · **Time:** about 18 minutes
> - **Builds on:** [Joule Studio tutorial 12: building a Sales Goal Advisor agent](joule-studio-tutorial-12-sales-goal-advisor-agent.md). **Leads to:** [Joule Studio tutorial 14: extending a standard agent](joule-studio-tutorial-14-journal-entry-agent-extension.md)

> [!WARNING]
> Pre-release Joule Studio — screens and exact flow may differ from general availability.

**After this tutorial you can:**

- Explain what a deterministic optimization engine is doing inside an otherwise LLM-driven agent, and why it's not just the LLM reasoning about numbers
- Name all 4 MCP servers this agent integrates, one per SAP API, and what each is read for
- Read a generated agent's configurable environment variables and explain what each one tunes

## 1. The business problem

Manufacturing needs cable rolls cut from stock to match production-order length requirements. Picking the wrong roll (or wrong combination) manually wastes material as offcut, and remote-location stock means extra transfer lead time if not caught early.

## 2. Define the intent

![Open Joule Studio](images/sj208-01-open-joule-studio.png)

![Create Agent dialog: Name "Cable Roll Optimizer," intent describing reading work order length/spec requirements, finding the roll or roll combination minimizing offcut waste, ranking by waste/location/expiry, and raising a Stock Transfer Order on planner approval, Quick Create checked](images/sj208-02-enter-agent-details.png)

![Confirm Business Goals](images/sj208-03-confirm-business-goals.png)

## 3. Review the intent

![Intent Summary](images/sj208-04-intent-summary.png)
![Exploring the intent file](images/sj208-05-exploring-intent-file.png)

## 4. The PRD — Solution Architecture

![PRD creation in progress](images/sj208-06-prd-creation-in-progress.png)

The Solution Architecture section names 4 integration points, each tied to a specific read or write:

![Solution Architecture: AI Agent (Python/A2A) deployed on SAP BTP, connecting to S/4HANA via OData to read work orders and batch stock, running an internal optimization engine, presenting recommendations via a planner interface, writing back on approval. Key Components: AI Agent, Optimization Engine (custom algorithm evaluating roll/combination selection against length requirements and waste thresholds), Configuration Store (waste thresholds, location priority rules, batch selection criteria), Planner Approval Interface. Integration Points: Production Order API (API_PRODUCTION_ORDER_2_SRV, read work order requirements), Batch Master API (API_BATCH_SRV, read batch attributes — length, expiry, certificate), Material Stock API (API_MATERIAL_STOCK_SRV, read available stock per location), Stock Transfer Order Approval API (OP_SRVCPARTSSTOAPPROVAL_0001, raise STO on approval)](images/sj208-07-solution-architecture.png)

> [!NOTE]
> This is a genuinely different architecture shape from the other agents in this book: the **Optimization Engine** is described as a custom deterministic algorithm, not an LLM reasoning step. The LLM's role here is narrower than usual — present the optimizer's output and handle the approval conversation, not decide which roll to pick.

## 5. Specification

![Specification Summary](images/sj208-08-specification-summary.png)

## 6. Generate the solution

![Solution fully built — Solution Artifacts panel](images/sj208-09-solution-fully-built-agent.png)
![Agent configuration overview](images/sj208-10-agent-configuration-overview.png)
![Agent evaluation section](images/sj208-11-agent-evaluation-section.png)
![Pro-code view, file tree](images/sj208-12-code-overview.png)

Confirmed directly: the generated solution has exactly **4 MCP server assets, one per SAP API named in the architecture**:

![MCP review: cable-roll-optimizer-agent plus 4 MCP servers — sap-s4-production-order-mcp-server (selected, 14 tools, including get_metadata/batch/list/create/update/delete/get for A_ProductionOrder_2), sap-s4-op-api-batch-srv-mcp-server, sap-s4-reservation-document-mcp...-server, sap-s4-op-srvcpartsstoapproval-m...-server. Right panel summary: 4 MCP Server assets one per SAP API generated from EDMX specs (Production Order API, Batch Master Record API, Stock Transfer Order Approval API, Reservation Document API); runtime skills roll-optimization (optimization algorithm with configurable thresholds, FEFO, location priority) and stock-transfer (approval-gated STO workflow); business instrumentation for all 5 PRD milestones (M1-M5) with structured logging and OpenTelemetry spans; 147 tests all passing (optimizer unit tests, mock MCP tool tests, approval gate tests, end-to-end integration tests); configurable via env vars WASTE_THRESHOLD_PCT, LOCATION_PRIORITY, MIN_SHELF_LIFE_DAYS, REQUIRED_CERTIFICATE_TYPES](images/sj208-13-mcp-review.png)

The same summary spells out exactly what the optimizer does, verbatim from the panel:

- Reads manufacturing work order requirements from SAP S/4HANA (material, required cable length, specification)
- Queries batch stock across all storage locations using the SAP Batch Master Record API
- Runs a deterministic optimization engine (`optimizer.py`) that finds the single roll or multi-roll combination with minimum offcut waste
- Ranks recommendations by waste %, location priority (local first), and FEFO (expiry date)
- Presents the top 3 recommendations to the planner for review
- On approval: raises a Stock Transfer Order via SAP S/4HANA when rolls are at a remote location
- Never writes to SAP without explicit planner confirmation in the conversation

> [!TIP]
> The 4 configurable environment variables (`WASTE_THRESHOLD_PCT`, `LOCATION_PRIORITY`, `MIN_SHELF_LIFE_DAYS`, `REQUIRED_CERTIFICATE_TYPES`) are a concrete example of a generated agent exposing its optimization logic's tuning knobs outside the code itself — a planner or admin can adjust waste tolerance or certificate requirements without touching `optimizer.py`.

## 7. Validate with tests

![Testing Overview: 147 tests](images/sj208-14-tests-overview.png)
![Testing, start of chat](images/sj208-15-testing-start.png)
![Local test results detail](images/sj208-16-local-test-results.png)

## 8. Deploy

![Deploy confirmation](images/sj208-17-deploy-solution.png)

Same governance boundary as every other agent in this family: development/test landscape only from inside Joule Studio.

## 9. Added by Claude, not from the sources

- The section 6 framing ("genuinely different architecture shape... deterministic algorithm, not an LLM reasoning step") is this book's own comparison against the other agents in this family — the underlying architecture description is the source's own screen text.
- The naming difference between the architecture text's "Material Stock API" and the MCP server panel's "Reservation Document" server is presented here exactly as each screen states it, without forcing them to match — it's likely the same integration point described two different ways in two different generated artifacts, but this book doesn't assert that as confirmed fact.
- Not run: the agent described was built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 10. Interview corner

**What interviewers listen for:** you can explain the optimizer-vs-LLM split precisely (deterministic algorithm picks the roll, LLM only narrates/handles approval), and you can name all 4 MCP servers without conflating them.

<details class="qa"><summary>1. What actually decides which cable roll or roll combination to use — the LLM, or something else?</summary>

- A deterministic optimization engine (`optimizer.py`) — a custom algorithm, not the LLM. The LLM presents the optimizer's output and manages the approval conversation, but doesn't make the selection itself

</details>

<details class="qa"><summary>2. What are this agent's 4 MCP servers, and what is each read for?</summary>

- Production Order API (work order length/spec requirements), Batch Master Record API (batch attributes — length, expiry, certificate), a stock-location server (available stock per location), Stock Transfer Order Approval API (raising the STO on approval)

</details>

<details class="qa"><summary>3. Name the 4 configurable environment variables this agent exposes, and what each tunes.</summary>

- `WASTE_THRESHOLD_PCT` (acceptable offcut waste tolerance), `LOCATION_PRIORITY` (local-first ranking rule), `MIN_SHELF_LIFE_DAYS` (expiry/FEFO cutoff), `REQUIRED_CERTIFICATE_TYPES` (which batch certificates qualify)

</details>

> [!TIP]
> **🧩 Design question**
> *"A plant manager asks why this agent needs an LLM at all, if the actual roll-selection decision is made by a plain algorithm."* Talk about: the LLM's role being conversational — reading work order context, presenting the top-3 ranked recommendations in plain language, handling the planner's approval dialogue, and only then triggering the deterministic write — versus the optimization math itself, which stays in auditable, deterministic code precisely because waste-minimization decisions need to be explainable and repeatable, not probabilistic.

## Cheat sheet

| Thing | Detail |
|---|---|
| MCP servers | 4 — Production Order, Batch Master Record, Reservation Document/Material Stock, STO Approval |
| Optimizer | Deterministic `optimizer.py`, not LLM reasoning |
| Ranking order | Waste % → location priority (local first) → FEFO (expiry date) |
| Recommendations shown | Top 3 |
| Env vars | `WASTE_THRESHOLD_PCT`, `LOCATION_PRIORITY`, `MIN_SHELF_LIFE_DAYS`, `REQUIRED_CERTIFICATE_TYPES` |
| Tests | 147/147 passing |

## Recap

- This agent wraps a genuine deterministic optimization engine, not an LLM reasoning step, for its core roll-selection decision
- 4 MCP servers map one-to-one to 4 SAP APIs, following the same naming pattern seen throughout this book
- Recommendations are ranked by waste %, then location priority, then FEFO expiry, with the top 3 shown to the planner
- 4 environment variables let an admin tune the optimizer's thresholds without touching code
- 147 automated tests passed before this agent was considered ready, covering the optimizer, mocked MCP tools, the approval gate, and end-to-end flows

## Practice

1. Without looking back, explain what decides the roll selection — and what the LLM's role actually is
2. Name all 4 MCP servers and what each integrates
3. List the 4 configurable environment variables and what each tunes

## How this chapter was checked

- The full tutorial "Build a Cable Roll Optimization Agent" (developers.sap.com, Beginner, 18 min, 9 steps) was read in full, 13 Nov 2026.
- 17 images were found and downloaded, all used here; each was opened and visually verified against its caption before being written into this chapter, including the Solution Architecture and MCP Servers screenshots, which were transcribed in full rather than paraphrased.
- Nothing in this chapter was independently re-executed — the agent described was built and tested by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Build a Cable Roll Optimization Agent* — https://developers.sap.com/tutorials/cable-roll-optimizer-agent (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 12: building a Sales Goal Advisor agent](joule-studio-tutorial-12-sales-goal-advisor-agent.md) · Next: [Joule Studio tutorial 14: extending a standard agent](joule-studio-tutorial-14-journal-entry-agent-extension.md)
