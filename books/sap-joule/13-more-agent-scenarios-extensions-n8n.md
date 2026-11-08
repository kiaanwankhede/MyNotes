# Chapter 13: More Joule Studio scenarios: sales, supply chain, data products, agent extensions and n8n workflows

*Ten more Agent Lab tutorials: three new solution types beyond a plain agent (data product, agent extension, n8n workflow) and five new agent scenarios.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how the same intent-to-deploy pipeline from [Chapter 12](12-intent-based-agents-lab.md) builds sales, supply-chain and billing solutions, how to extend a standard SAP agent, and how Joule Studio builds n8n workflows
> - **Level:** beginner · **Time:** about 40 minutes of reading
> - **Sources:** ten SAP Developer tutorials (SJ069 to SJ078), read 9 November 2026 (text and screenshots)
> - **Builds on:** [Chapter 12](12-intent-based-agents-lab.md) (the pipeline, PRD, guardrails)

**After this chapter you can:**

- Choose between an agent, a data product, an agent extension and an n8n workflow
- Explain Quick Create versus Ideate and Plan
- Name the four extension layers of an agent extension (instructions, MCP tool, pre-hook, post-hook)
- Say why a deterministic engine, not the LLM, picks a cable roll
- Describe the human-in-the-loop step in an n8n workflow

> [!WARNING]
> **What this chapter is**
> - Pre-release Agent Lab content; screens and names may change
> - Educational, not production; the tutorials say production deployment is not done from Joule Studio
> - Several tutorials say "you will not deploy" (agent extensions, n8n, equipment, sales reps, data product); only the supplier-risk, sales-assistant and cable-roll tutorials walk through Deploy
> - Data, customers and numbers are illustrative; I ran nothing

> [!CAUTION]
> **Writes need people**
> - Cable roll: a stock transfer order (STO) in S/4HANA only after planner approval
> - Invoice exception: an invoice is released only after the AP clerk approves in SAP Task Center
> - Sales assistant: reads only; the rep decides

## 13.1 The four solution types on the Create screen

*Sources: SJ071, SJ074, SJ075, SJ076, SJ077, SJ078.*

| Tile | What you get | Tutorial here |
|---|---|---|
| **Agent** | A Python agent with generated MCP servers | SJ069 to SJ073 |
| **Data product** | A data product definition (DPD) built by the Data Product Creation Agent | SJ074 |
| **Agent Extension** | Changes to a pre-delivered SAP agent, no new agent | SJ075, SJ076 |
| **n8n Workflow** | A visual workflow with SAP nodes | SJ077, SJ078 |

- SJ071 also shows an **Application** tile in some screens
- Older screens show three tiles; newer ones show four (as in Chapter 12)

## 13.2 Quick Create or Ideate and Plan

*Source: SJ069 (both tabs of the page were read).*

- **Quick Create (checked):** adds "Fast Track", skips clarifying questions and runs all phases; business goals are still confirmed
- **Ideate and Plan (unchecked):** Joule asks questions and pauses at each phase
  - You type `Create requirements`, then `Create specification`
  - Then choose **Build**, or type `Build the solution`
  - Optionally type `deploy`; deployment record shows status, version and live agent URL, with **Try now** (A2A)
- Test prompt in SJ069: `review all suppliers and their KPI scores`
- The **Traces** panel shows how the agent handled each request

## 13.3 Five agent scenarios

| ID | Agent | Backend | What it recommends or does | Human step |
|---|---|---|---|---|
| SJ069 | Supplier Performance Assistant | simulated procurement data | Monitors supplier KPIs, flags at-risk suppliers, suggests approved alternatives | Not specified in the text I read |
| SJ070 | AI Sales Assistant (discount strategy) | S/4HANA Cloud + SAP Sales Cloud | Discount range, margin impact, risk level, rationale | Rep decides |
| SJ071 | AI Sales Assistant (2 to 3 ranked strategies) | S/4HANA SD | Discount %, rationale, win probability, projected margin | Rep decides |
| SJ072 | Cable Roll Optimizer | S/4HANA PP and MM/WM | Roll or roll combination with least offcut; STO if stock is short | Planner approves any STO |
| SJ073 | Equipment Troubleshooting Agent | S/4HANA (OData) | Equipment history and troubleshooting help for maintenance technicians | Not specified |

### SJ070: discount strategy across two systems

- **Intent (two sentences):** names purpose, source systems, data and user
- **Three scenarios:** repeat customer, new prospect asking a big discount, strategic account mid-cycle
- **Intent fit:** above about 80% is "strong"; lower means one of purpose, systems, data or user is missing
- **Milestones become tests:** data connectivity, context assembly, recommendation, rep interaction, outcome tracked
- **PRD guardrails (four):**
  - No writes to SAP
  - HIGH RISK flag if projected margin falls below the margin floor
  - Partial data handled gracefully
  - Prompt-injection detection
- **MCP servers:** one per OData API, typically 2 to 4 (orders, pricing or simulation, opportunities)
- **Build command:** `execute specification/specification.md`
- **Test prompt:** `Recommend discount strategy for customer Best Run SAP Company`
- **Low temperature:** same inputs give the same recommendation (reproducible, auditable)
- **Evaluation:** "Generate scenarios" creates evaluation scenarios from the intent
- **Failing tests:** injection-resistance patterns may clash with benign inputs; the pricing MCP server is sensitive to pricing configuration and authorisations

### SJ072: cable roll optimisation (the engine-versus-LLM example)

- **Problem:** picking a roll much longer than needed leaves scrap offcut
- **Three cases:** single roll locally, several rolls locally, roll from another location (STO)
- **Five pain points:** no network-wide stock view, habit-based selection, invisible offcuts, reactive transfers, no audit link
- **Key design rule:** a **deterministic cutting-stock engine** chooses the rolls; the **LLM only narrates** and its numbers come from the engine
- **Hybrid automation:** reads and optimisation run alone; STO creation needs planner approval
- **Four guardrails:**
  - No STO without recorded approval
  - Batch certificate and expiry checked before optimising
  - Waste threshold escalation (for example more than 15%)
  - Stock-data freshness check
- **MCP servers:** Production Order (read only) and Batch Stock (read, plus write only for STO)
- **Troubleshooting hints from the text:** storage location codes in `solution.yaml`; `max_rolls_per_order`; authorisation object `M_MSEG_BWA` with movement type 351

### SJ073 and SJ071: the short versions

- Both use Quick Create and let you accept the PRD unchanged
- SJ073: the Idea Board maps the intent to the business process "Acquire to Decommission"; the spec is `specification/equipment-troubleshooting-agent/specification.md`; no deploy unless the instructor says so
- SJ071: after build, check **Testing**, then ask `How can I use this solution?`; no deploy
- Intent fit in the SJ073 screenshots looked like about 90% (small text)

## 13.4 Data product: billing completeness (SJ074)

- **Goal:** combine Sales Orders and Billing Documents into an order-to-cash data foundation
- **Start:** type the prompt in the Joule Work chat, then choose Quick create
- **The Requirement and Specification phases are skipped** because you build the data product directly
- **Result:** a data product definition (DPD) file; ask for a preview with `show a data preview of the first 10 rows in md format`
- **Publish** the data product if asked
- **Test step:** open a pre-deployed solution, "Billing completeness and revenue recognition agent", and choose **Try now**
  - Example skill: breakdown of ordered value by billing completion status (shown as a bar chart)
- Screenshots show a lineage graph of source tables feeding the data product

## 13.5 Agent extensions (SJ075, SJ076)

Extend a **pre-delivered SAP agent** instead of building a new one.

| Tutorial | Agent extended | Extension |
|---|---|---|
| SJ075 | Journal Entry Agent (invoked as `@Financial Closing Assistant ...`) | Instruction extension adding a disclaimer; optional four-layer extension |
| SJ076 | AP Invoice Agent | n8n post-hook that creates a Task Center task; added instructions and an MCP server |

```mermaid
flowchart LR
  U[User request] --> P[Pre-hook: check before posting]
  P --> A[Standard agent + instructions + MCP tool]
  A --> H[Post-hook: after success]
```

- **Four layers (SJ075 step 6):**
  - **Pre-hook:** runs before the action (flag an amount over a limit)
  - **Tool extension:** adds an MCP tool via MCP Hub (read past postings)
  - **Instruction extension:** plain-language business rule (check cost centre, GL account, profit centre and segment combine validly)
  - **Post-hook:** runs after success (HTML summary report)
- **Baseline first (SJ075):** run the standard agent to see it does no checks, flags or reports
- **Journal entry file:** `.xlsx` or `.csv`; up to 999 proposals per file; mandatory fields are journal entry date, posting date, type, company code, currency, G/L account, debit and credit
- **Restrictions:** a deployed extension blocks others from extending the same agent, and lab users cannot deploy it
- **Output:** an `extension.yaml`
- **SJ076 design tab:** "Instructions and Context" injects rules (example: always validate tax on pending invoices; errors are non-approvable, warnings allowed with a note, OK is safe) and "Add Server" adds MCP servers
- **Warning in SJ075:** the optional section may fail if MCP tools or n8n hooks are disabled in your system

> [!IMPORTANT]
> **Secrets and shared logins**
> - The tutorials mention lab logon information or sample files only by name; none is copied here

## 13.6 n8n workflows in Joule Studio (SJ077, SJ078)

| Tutorial | Workflow | Nodes named |
|---|---|---|
| SJ077 | Invoice Exception Agent | webhook trigger from a Joule agent, SAP MCP Client, SAP Agent, SAP Human-in-the-Loop (SAP Task Center), release via MCP client |
| SJ078 | IT Incident Triage and Auto Routing | classifies incidents P1 to P4, root-cause category, routes to workflows; SAP Task Center node for manager approval; SAP Agent node |

- **SJ077 flow:** read blocked invoices → get PO, goods receipt and contract → agent finds the block reason → AP clerk approves in Task Center → release in S/4HANA
- **Guardrails (SJ077):** human approval for every release, no write-back when rejected, always return a response to the webhook
- **Why n8n:** a visual canvas with generated nodes; solution files include `specification.md`, the workflow JSON under `assets`, and `solution.yaml`
- **SJ078:** after build, add intent `Add an SAP Task Center node within the N8N workflow to send workflow approvals to the manager`, then add an **SAP Agent** node (triggers an agent from another solution) and execute the workflow
- **Preview limits (SJ077):** do not choose Execute workflow or Deploy; configuration of the AI node and live runs are not in the preview

## 13.7 What the screenshots add

*Viewed 9 November 2026: SJ069 (32 images, both tabs), SJ070 (read earlier), SJ071 (10), SJ072 (18), SJ073 (12), SJ074 (9), SJ075 (21), SJ076 (15), SJ077 (13), SJ078 (15). Most are small, so I read layout and highlights, not fine print.*

- **SJ071:** Create Agent dialog with the name and intent highlighted; the clarifying question asked even with Quick Create ("Which deployment is the primary source of discount and pricing data?" with options such as On Premise, Cloud Public Edition, Private Edition, Hybrid); chat suggestions for inputs to consider; a spec view with sections such as Basic Setup, MCP Translation Files, Agent Tools, Agent System Prompt, Business Data Instrumentation, MCP Wiring, Agent Extensibility, Testing, Agent Evaluation
- **SJ072:** a placeholder image first; steps, the PRD and architecture views, an agent low-code page with agent configurations, evaluation ("no evaluations generated"), a test overview, a **Try Your Agent** page and a Deploy confirmation; I could not read the numbers on the test overview
- **SJ073:** intent-tools list, a progress bar on the Idea Board, a PRD, the code tab and the **Try** tab; the intent-fit figure was too small to read with certainty
- **SJ074:** a lineage graph of several source nodes feeding the data product, a preview table, the pre-deployed solution page and the bar chart
- **SJ075:** the Joule chat with `@Financial Closing Assistant ...`, a file-upload area, a mapping table with an **Approve Mapping** button, an Agent Catalog pick, and an intent summary whose intent fit looked like about 95% (small text)
- **SJ076:** Agent Extension tile highlighted, an n8n post-hook canvas, the Design tab with Instructions and Context and MCP server catalogue
- **SJ077:** one screenshot shows a different sample solution ("Month-End Financial Close Controller") in an early step; it does not match the invoice scenario, so I did not use it
- **SJ078:** an n8n canvas with many nodes and the SAP Agent node picker

## 13.8 Added by Claude, not from the sources

- **Pattern for all ten:** name the user, the data, the decision and the guardrail in the intent; keep reads automatic and writes human-approved
- **Choosing a type:** new reasoning task → agent; reusable analytics → data product; tweak a standard SAP agent → extension; chained steps with approvals → n8n workflow
- **Engine versus LLM:** use an engine whenever the answer must be the same every time (rolls, totals); use the LLM for wording and classification

## 13.9 Interview corner

**What interviewers listen for:** you pick the right solution type and say where the human sits.

<details class="qa">
<summary>🟢 What is Quick Create?</summary>

- It adds Fast Track so Joule skips clarifying questions and runs all phases; business goals are still confirmed
</details>

<details class="qa">
<summary>🟡 When would you extend a standard agent rather than build one?</summary>

- When SAP already delivers the agent and you only need your own checks, rules, tools or reports (the four layers)
</details>

<details class="qa">
<summary>🟡 Why does the cable roll agent use an engine?</summary>

- Same inputs must give the same, auditable result; the LLM only narrates the engine's numbers
</details>

<details class="qa">
<summary>🔴 An n8n workflow releases invoices. How do you make sure none is released without sign-off?</summary>

- Route the finding through the human-in-the-loop step (Task Center); no write path on rejection; test that the release call is reachable only after approval
</details>

<details class="qa">
<summary>🔴 Your discount agent's tests for the pricing MCP server fail. What do you check?</summary>

- Destination to a tenant with pricing conditions, user authorisations, and whether injection patterns block a benign test input
</details>

**🧩 Design question:** design an extension for the Journal Entry Agent that blocks postings to a closed period. Choose the layer (pre-hook, tool, instruction, post-hook), the data it reads and who is told.

## 13.10 Discovery Center missions (links, not read)

- [Build custom Joule skills for SAP and non-SAP systems](https://discovery-center.cloud.sap/missiondetail/4643/)
- The tutorials also list the missions **Joule Studio Agent Lab** and **2026 SAP TechEd Berlin Dev Garage & Agent Lab**; I did not capture their links, so none is added here

## 13.11 Cheat sheet

| Topic | Remember |
|---|---|
| Quick Create | Fast Track; goals still confirmed |
| Ideate and Plan | Answer questions; `Create requirements`, `Create specification`, `Build the solution` |
| Data product | Skips PRD and spec; DPD file, preview, publish |
| Extension layers | Pre-hook, MCP tool, instructions, post-hook |
| n8n human step | SAP Task Center / Human-in-the-Loop |
| Engine vs LLM | Engine decides, LLM narrates |
| Production | Not deployed from Joule Studio |

## Recap

- Four solution types: agent, data product, extension, n8n workflow
- The pipeline from Chapter 12 still applies
- Extensions add checks to SAP agents without a new build
- Engines decide, LLMs explain
- Human approval before every write

## Practice

1. Pick the solution type for four ideas of your own and say why.
2. Write the four extension layers for an agent you know.
3. For SJ072, list what runs alone and what needs the planner.
4. Draw the SJ077 workflow as boxes.

## How this chapter was checked

- **Read fully (text and screenshots):** SJ069 to SJ078
- **Not read:**
  - fine print inside small screenshots (see 13.7)
  - the "Related learning" lists, videos, linked tutorials and Discovery Center missions
  - the downloadable sample file `agent_lab_journal_entry.xlsx` (SJ075)
- **Not run:** nothing was built or deployed
- **Dated points:** pre-release Agent Lab content (October 2026)
- **Small inconsistencies noted:** SJ072 says all tests pass but no numbers were legible; SJ077's first screenshot shows a different sample solution

## Sources and further reading

- SAP Developer, *Use Joule Studio to Create an Assistant to Monitor Supplier Risk* (read): https://developers.sap.com/tutorials/joule-studio-spend-supplier-assistant
- SAP Developer, *Build an AI Sales Assistant Agent with Joule Studio, SAP Sales Cloud, and SAP S/4HANA Cloud* (read): https://developers.sap.com/tutorials/build-an-ai-sales-assistant-agent
- SAP Developer, *Use Joule Studio to Create an AI Assistant for Sales Reps* (read): https://developers.sap.com/tutorials/joule-studio-cx-agent-create
- SAP Developer, *Optimize Cable Roll Selection for Work Orders with a Custom Joule Agent* (read): https://developers.sap.com/tutorials/cable-roll-optimizer-agent
- SAP Developer, *Use Joule Studio to Create an Assistant for Equipment Troubleshooting* (read): https://developers.sap.com/tutorials/joule-studio-scm-equipment-assistant
- SAP Developer, *Build a Billing Completeness Data Product with Joule Studio* (read): https://developers.sap.com/tutorials/joule-studio-bdc-agent-create
- SAP Developer, *Create an Extension for a Standard Agent* (read): https://developers.sap.com/tutorials/create-agent-extension
- SAP Developer, *Use Joule Studio to Extend the AP Invoice Agent using Agent Extensions* (read): https://developers.sap.com/tutorials/joule-studio-agent-extension
- SAP Developer, *How to create an Invoice Exception Agent with an n8n Workflow* (read): https://developers.sap.com/tutorials/create-invoice-exception-agent-with-n8n
- SAP Developer, *Use Joule Studio to Create an IT Incident Triage and Auto Routing Agent with N8N, SAP Task Center Node and SAP Agent Node* (read): https://developers.sap.com/tutorials/joule-studio-n8n-workflow-create
- Discovery Center missions: see 13.10

---

*Previous: [Chapter 12: Intent-based agents in Joule Studio: ten business scenarios](12-intent-based-agents-lab.md)*
