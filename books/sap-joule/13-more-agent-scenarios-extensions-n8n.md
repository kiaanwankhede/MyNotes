# Chapter 13: More Joule Studio scenarios: sales, supply chain, data products, agent extensions and n8n workflows

*Ten more Agent Lab tutorials: three new solution types beyond a plain agent (data product, agent extension, n8n workflow) and five new agent scenarios.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how the same intent-to-deploy pipeline from [Chapter 12](12-intent-based-agents-lab.md) builds sales, supply-chain and billing solutions, how to extend a standard SAP agent, and how Joule Studio builds n8n workflows
> - **Level:** beginner · **Time:** about 40 minutes of reading
> - **Sources:** ten SAP Developer tutorials (SJ069 to SJ078) and two partner blogs and three news items (SJ079, SJ082, SJ086, SJ088, SJ089), read 9 November 2026 (text and screenshots)
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

## 13.7 Real-world examples and market context (SJ079, SJ082, SJ086, SJ088, SJ089)

*Sources: SJ079 (sovanta blog, with Endress+Hauser), SJ082 (Mindset Consulting blog), SJ086 (SAP News), SJ088 (SAPinsider) and SJ089 (CX Today). Blogs and press are partner, vendor or trade-press views, not SAP documentation; SAP's own claims in them are not independently verified.*

### SJ079: purchasing anomaly agent (sovanta and Endress+Hauser)

- **Problem:** sales reps cannot see changes in a customer's buying pattern across a large product range
  - Examples: a sudden rise or fall in one product area, a shift to unexpected measuring principles, recent orders of products heading for order stop
- **Built with:** the agent builder in Joule Studio (the "classic" low-code builder with skills)
- **Data sources:** a SAP HANA Cloud operational data hub and a product knowledge base reached through an internal RAG tool
- **Text-to-SQL pipeline:** the agent is grounded (document grounding in SAP AI Core) with the database schema, example SQL queries and background documentation
- **Two custom Joule skills:** one runs a SQL query through a proxy connector; one reads the product knowledge base
- **Workaround:** SAP Build Actions did not fully support dynamic outputs, so the team handled changing query results themselves
- **Flow:** question in plain language → agent chooses the source → writes SQL from schema and examples → result enriched from product documentation → plain-language summary → follow-ups
- **Extra value:** it also finds successor products for items in order stop and compares old and new product
- **Their outlook:** agent-to-agent collaboration, and a native database tool that could replace the Text-to-SQL workaround
- **Architecture diagram (viewed):** natural-language question → Joule agent in Joule Studio (SAP Build) → two skills via SAP Build Process Automation actions → destination → proxy connector in a Cloud Foundry space → HANA Cloud; the knowledge base is reached over HTTPS; AI models and document grounding sit in SAP AI Core; a model named "MistralAI" is labelled on the diagram
- **Second image:** a Joule test chat showing a measuring-principle anomaly answer and a list of products in order stop (customer names blurred)

### SJ082: twenty Joule agents on a real BTP tenant (Mindset Consulting)

- **What it is:** an opinion and overview post by the company's CEO ahead of SAP Sapphire 2026; the detail sits in linked posts and a catalogue I did not open
- **Claims in the post:** twenty agents built on a real BTP tenant with real MCP and S/4HANA, running live; the team trained 40+ people
- **Points about the market (author's view):**
  - Joule Studio, MCP support and an MCP gateway in Integration Suite are positioned as the route for non-SAP agents
  - An SAP API policy (named v.4.2026a in the post) says agent calls to SAP APIs should go through SAP-endorsed paths such as Joule or Integration Suite; the author thinks many customers are not compliant yet
  - Business Data Cloud matters because agents quote wrong numbers when the data is untrusted
- **"Mindset stack":** journey and discovery, pipes (trust and architecture), data, and experience
- **Not in this post:** the "157 MCP tools" and "human approval on writes" points that my master noted; they are not on the page I read (likely in the linked posts, not read)
- **Images:** two author photos only

### SJ086: Joule in S/4HANA Cloud and supply chain (SAP News, December 2024)

- **Not Joule Studio:** an announcement that Joule is available in S/4HANA Cloud Public Edition (November 2024 release) and in supply-chain applications (Integrated Business Planning, product data management); Asset Performance Management is early access
- **Joule uses named:** quick navigation to apps, instant insights (for example purchase orders, outbound deliveries), and pointers to enablement content
- **Claim quoted from "a recent study":** AI-powered tools cut administrative time by 30% (SAP's wording; the study is not named)
- **Customers:** AGILITA AG (a GROW with SAP customer, found apps and help documentation faster) and TE Connectivity (activated Joule in Integrated Business Planning; first tests used help documentation; wants plan explanations and scenario comparison later)
- **Date warning:** the master link `?p=230358` redirects to this 2024 post; it describes early use, not agents
- **Image:** one decorative banner

### SJ088: Joule agents for Ariba and Fieldglass (SAPinsider)

- **Planned for June 2026 general availability:** a Joule agent in Ariba Intake Management (routes requests across SAP and non-SAP systems, checks policy, categorises spend), AI-assisted contract creation in Ariba Contracts, and gate-pass time capture in Fieldglass
- **Runtime:** the Joule Agent Runtime is free until 31 December 2026 for Ariba and Fieldglass customers
- **Also stated:** next-generation Ariba available since March 2026; at least 60% of agentic capabilities to be back-ported to current-generation Ariba; an 11-assistant rollout (five in June, six in September 2026); 70% less manual time for AI-assisted statement-of-work creation (SAP's figure)
- **Wording check:** the article says "planned"; it is not proof the features are live
- **Images:** six stock or logo pictures, no diagrams

### SJ089: a sceptical view (CX Today, 28 July 2026)

- **Argument:** at SAP's Q2 2026 earnings call, evidence of AI agents was mostly in finance, procurement and ERP, with little proof for customer service
- **Facts reported:** Joule Work to launch in Q3; an "AI Agent Hub" to govern SAP and non-SAP agents and MCP servers; beta programs oversubscribed
- **SAP examples cited (SAP's claims):** an Amadeus agent clearing about 40,000 incorrect transactions; Lemvigh-Müller over 90% touchless processing and 98% matching accuracy; PwC cutting a billing task from 35 to 5 minutes; up to 30% lower ERP migration cost
- **Pricing:** SAP said agents would be priced on value (an intent, not a model with disclosed results)
- **Use for learning:** treat vendor numbers as claims; ask for the baseline and who measured
- **Image:** one stock photo of an SAP office

## 13.8 What the screenshots add

*Viewed 9 November 2026: SJ069 (32 images, both tabs), SJ070 (read earlier), SJ071 (10), SJ072 (18), SJ073 (12), SJ074 (9), SJ075 (21), SJ076 (15), SJ077 (13), SJ078 (15). Most are small, so I read layout and highlights, not fine print.*

- **SJ071:** Create Agent dialog with the name and intent highlighted; the clarifying question asked even with Quick Create ("Which deployment is the primary source of discount and pricing data?" with options such as On Premise, Cloud Public Edition, Private Edition, Hybrid); chat suggestions for inputs to consider; a spec view with sections such as Basic Setup, MCP Translation Files, Agent Tools, Agent System Prompt, Business Data Instrumentation, MCP Wiring, Agent Extensibility, Testing, Agent Evaluation
- **SJ072:** a placeholder image first; steps, the PRD and architecture views, an agent low-code page with agent configurations, evaluation ("no evaluations generated"), a test overview, a **Try Your Agent** page and a Deploy confirmation; I could not read the numbers on the test overview
- **SJ073:** intent-tools list, a progress bar on the Idea Board, a PRD, the code tab and the **Try** tab; the intent-fit figure was too small to read with certainty
- **SJ074:** a lineage graph of several source nodes feeding the data product, a preview table, the pre-deployed solution page and the bar chart
- **SJ075:** the Joule chat with `@Financial Closing Assistant ...`, a file-upload area, a mapping table with an **Approve Mapping** button, an Agent Catalog pick, and an intent summary whose intent fit looked like about 95% (small text)
- **SJ076:** Agent Extension tile highlighted, an n8n post-hook canvas, the Design tab with Instructions and Context and MCP server catalogue
- **SJ077:** one screenshot shows a different sample solution ("Month-End Financial Close Controller") in an early step; it does not match the invoice scenario, so I did not use it
- **SJ078:** an n8n canvas with many nodes and the SAP Agent node picker

## 13.9 Added by Claude, not from the sources

- **Pattern for all ten:** name the user, the data, the decision and the guardrail in the intent; keep reads automatic and writes human-approved
- **Choosing a type:** new reasoning task → agent; reusable analytics → data product; tweak a standard SAP agent → extension; chained steps with approvals → n8n workflow
- **Engine versus LLM:** use an engine whenever the answer must be the same every time (rolls, totals); use the LLM for wording and classification

## 13.10 Interview corner

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

## 13.11 Discovery Center missions (links, not read)

- [Build custom Joule skills for SAP and non-SAP systems](https://discovery-center.cloud.sap/missiondetail/4643/)
- The tutorials also list the missions **Joule Studio Agent Lab** and **2026 SAP TechEd Berlin Dev Garage & Agent Lab**; I did not capture their links, so none is added here

## 13.12 Cheat sheet

| Topic | Remember |
|---|---|
| Quick Create | Fast Track; goals still confirmed |
| Ideate and Plan | Answer questions; `Create requirements`, `Create specification`, `Build the solution` |
| Data product | Skips PRD and spec; DPD file, preview, publish |
| Extension layers | Pre-hook, MCP tool, instructions, post-hook |
| n8n human step | SAP Task Center / Human-in-the-Loop |
| Engine vs LLM | Engine decides, LLM narrates |
| Production | Not deployed from Joule Studio |

## Screenshots and figures from the sources

*Images saved from the source pages, in the order they appear there.*

### Images: Tutorial: AI sales assistant agent

*Source: [Tutorial: AI sales assistant agent](https://developers.sap.com/tutorials/build-an-ai-sales-assistant-agent)*

![AI sales assistant, figure 1](images/ch13-s2-aisalesassistant-01.webp)

![AI sales assistant, figure 2](images/ch13-s2-aisalesassistant-02.webp)

![AI sales assistant, figure 3](images/ch13-s2-aisalesassistant-03.webp)

![AI sales assistant, figure 4](images/ch13-s2-aisalesassistant-04.webp)

![AI sales assistant, figure 5](images/ch13-s2-aisalesassistant-05.webp)

![AI sales assistant, figure 6](images/ch13-s2-aisalesassistant-06.webp)

![AI sales assistant, figure 7](images/ch13-s2-aisalesassistant-07.webp)

![AI sales assistant, figure 8](images/ch13-s2-aisalesassistant-08.webp)

![AI sales assistant, figure 9](images/ch13-s2-aisalesassistant-09.webp)

![AI sales assistant, figure 10](images/ch13-s2-aisalesassistant-10.webp)

![AI sales assistant, figure 11](images/ch13-s2-aisalesassistant-11.webp)

![AI sales assistant, figure 12](images/ch13-s2-aisalesassistant-12.webp)

![AI sales assistant, figure 13](images/ch13-s2-aisalesassistant-13.webp)

![AI sales assistant, figure 14](images/ch13-s2-aisalesassistant-14.webp)

### Images: Tutorial: Cable roll optimizer agent

*Source: [Tutorial: Cable roll optimizer agent](https://developers.sap.com/tutorials/cable-roll-optimizer-agent)*

![Cable roll optimizer, figure 1](images/ch13-s3-cableroll-01.webp)

![Cable roll optimizer, figure 2](images/ch13-s3-cableroll-02.webp)

![Cable roll optimizer, figure 3](images/ch13-s3-cableroll-03.webp)

![Cable roll optimizer, figure 4](images/ch13-s3-cableroll-04.webp)

![Cable roll optimizer, figure 5](images/ch13-s3-cableroll-05.webp)

![Cable roll optimizer, figure 6](images/ch13-s3-cableroll-06.webp)

![Cable roll optimizer, figure 7](images/ch13-s3-cableroll-07.webp)

![Cable roll optimizer, figure 8](images/ch13-s3-cableroll-08.webp)

![Cable roll optimizer, figure 9](images/ch13-s3-cableroll-09.webp)

![Cable roll optimizer, figure 10](images/ch13-s3-cableroll-10.webp)

![Cable roll optimizer, figure 11](images/ch13-s3-cableroll-11.webp)

![Cable roll optimizer, figure 12](images/ch13-s3-cableroll-12.webp)

![Cable roll optimizer, figure 13](images/ch13-s3-cableroll-13.webp)

![Cable roll optimizer, figure 14](images/ch13-s3-cableroll-14.webp)

![Cable roll optimizer, figure 15](images/ch13-s3-cableroll-15.webp)

![Cable roll optimizer, figure 16](images/ch13-s3-cableroll-16.webp)

![Cable roll optimizer, figure 17](images/ch13-s3-cableroll-17.webp)

### Images: Tutorial: Create an agent extension

*Source: [Tutorial: Create an agent extension](https://developers.sap.com/tutorials/create-agent-extension)*

![Agent extension, figure 1](images/ch13-s4-createagentext-01.webp)

![Agent extension, figure 2](images/ch13-s4-createagentext-02.webp)

![Agent extension, figure 3](images/ch13-s4-createagentext-03.webp)

![Agent extension, figure 4](images/ch13-s4-createagentext-04.webp)

![Agent extension, figure 5](images/ch13-s4-createagentext-05.webp)

![Agent extension, figure 6](images/ch13-s4-createagentext-06.webp)

![Agent extension, figure 7](images/ch13-s4-createagentext-07.webp)

![Agent extension, figure 8](images/ch13-s4-createagentext-08.webp)

![Agent extension, figure 9](images/ch13-s4-createagentext-09.webp)

![Agent extension, figure 10](images/ch13-s4-createagentext-10.webp)

![Agent extension, figure 11](images/ch13-s4-createagentext-11.webp)

![Agent extension, figure 12](images/ch13-s4-createagentext-12.webp)

![Agent extension, figure 13](images/ch13-s4-createagentext-13.webp)

![Agent extension, figure 14](images/ch13-s4-createagentext-14.webp)

![Agent extension, figure 15](images/ch13-s4-createagentext-15.webp)

![Agent extension, figure 16](images/ch13-s4-createagentext-16.webp)

![Agent extension, figure 17](images/ch13-s4-createagentext-17.webp)

![Agent extension, figure 18](images/ch13-s4-createagentext-18.webp)

![Agent extension, figure 19](images/ch13-s4-createagentext-19.webp)

![Agent extension, figure 20](images/ch13-s4-createagentext-20.webp)

![Agent extension, figure 21](images/ch13-s4-createagentext-21.webp)

### Images: Tutorial: Invoice exception agent with n8n

*Source: [Tutorial: Invoice exception agent with n8n](https://developers.sap.com/tutorials/create-invoice-exception-agent-with-n8n)*

![Invoice exception n8n, figure 1](images/ch13-s5-invoiceexcn8n-01.webp)

![Invoice exception n8n, figure 2](images/ch13-s5-invoiceexcn8n-02.webp)

![Invoice exception n8n, figure 3](images/ch13-s5-invoiceexcn8n-03.webp)

![Invoice exception n8n, figure 4](images/ch13-s5-invoiceexcn8n-04.webp)

![Invoice exception n8n, figure 5](images/ch13-s5-invoiceexcn8n-05.webp)

![Invoice exception n8n, figure 6](images/ch13-s5-invoiceexcn8n-06.webp)

![Invoice exception n8n, figure 7](images/ch13-s5-invoiceexcn8n-07.webp)

![Invoice exception n8n, figure 8](images/ch13-s5-invoiceexcn8n-08.webp)

![Invoice exception n8n, figure 9](images/ch13-s5-invoiceexcn8n-09.webp)

![Invoice exception n8n, figure 10](images/ch13-s5-invoiceexcn8n-10.webp)

![Invoice exception n8n, figure 11](images/ch13-s5-invoiceexcn8n-11.webp)

![Invoice exception n8n, figure 12](images/ch13-s5-invoiceexcn8n-12.webp)

![Invoice exception n8n, figure 13](images/ch13-s5-invoiceexcn8n-13.webp)

### Images: Tutorial: Joule Studio agent extension

*Source: [Tutorial: Joule Studio agent extension](https://developers.sap.com/tutorials/joule-studio-agent-extension)*

![Studio agent extension, figure 1](images/ch13-s6-studioagentext-01.webp)

![Studio agent extension, figure 2](images/ch13-s6-studioagentext-02.webp)

![Studio agent extension, figure 3](images/ch13-s6-studioagentext-03.webp)

![Studio agent extension, figure 4](images/ch13-s6-studioagentext-04.webp)

![Studio agent extension, figure 5](images/ch13-s6-studioagentext-05.webp)

![Studio agent extension, figure 6](images/ch13-s6-studioagentext-06.webp)

![Studio agent extension, figure 7](images/ch13-s6-studioagentext-07.webp)

![Studio agent extension, figure 8](images/ch13-s6-studioagentext-08.webp)

![Studio agent extension, figure 9](images/ch13-s6-studioagentext-09.webp)

![Studio agent extension, figure 10](images/ch13-s6-studioagentext-10.webp)

![Studio agent extension, figure 11](images/ch13-s6-studioagentext-11.webp)

![Studio agent extension, figure 12](images/ch13-s6-studioagentext-12.webp)

![Studio agent extension, figure 13](images/ch13-s6-studioagentext-13.webp)

![Studio agent extension, figure 14](images/ch13-s6-studioagentext-14.webp)

![Studio agent extension, figure 15](images/ch13-s6-studioagentext-15.webp)

### Images: Tutorial: BDC agent

*Source: [Tutorial: BDC agent](https://developers.sap.com/tutorials/joule-studio-bdc-agent-create)*

![BDC agent, figure 1](images/ch13-s7-bdcagent-01.png)

![BDC agent, figure 2](images/ch13-s7-bdcagent-02.png)

![BDC agent, figure 3](images/ch13-s7-bdcagent-03.png)

![BDC agent, figure 4](images/ch13-s7-bdcagent-04.png)

![BDC agent, figure 5](images/ch13-s7-bdcagent-05.png)

![BDC agent, figure 6](images/ch13-s7-bdcagent-06.png)

![BDC agent, figure 7](images/ch13-s7-bdcagent-07.png)

![BDC agent, figure 8](images/ch13-s7-bdcagent-08.png)

![BDC agent, figure 9](images/ch13-s7-bdcagent-09.png)

### Images: Tutorial: CX agent

*Source: [Tutorial: CX agent](https://developers.sap.com/tutorials/joule-studio-cx-agent-create)*

![CX agent, figure 1](images/ch13-s8-cxagent-01.webp)

![CX agent, figure 2](images/ch13-s8-cxagent-02.png)

![CX agent, figure 3](images/ch13-s8-cxagent-03.png)

![CX agent, figure 4](images/ch13-s8-cxagent-04.png)

![CX agent, figure 5](images/ch13-s8-cxagent-05.png)

![CX agent, figure 6](images/ch13-s8-cxagent-06.png)

![CX agent, figure 7](images/ch13-s8-cxagent-07.png)

![CX agent, figure 8](images/ch13-s8-cxagent-08.png)

![CX agent, figure 9](images/ch13-s8-cxagent-09.png)

![CX agent, figure 10](images/ch13-s8-cxagent-10.png)

### Images: Tutorial: n8n workflow

*Source: [Tutorial: n8n workflow](https://developers.sap.com/tutorials/joule-studio-n8n-workflow-create)*

![n8n workflow, figure 1](images/ch13-s9-n8nworkflow-01.png)

![n8n workflow, figure 2](images/ch13-s9-n8nworkflow-02.png)

![n8n workflow, figure 3](images/ch13-s9-n8nworkflow-03.png)

![n8n workflow, figure 4](images/ch13-s9-n8nworkflow-04.png)

![n8n workflow, figure 5](images/ch13-s9-n8nworkflow-05.png)

![n8n workflow, figure 6](images/ch13-s9-n8nworkflow-06.png)

![n8n workflow, figure 7](images/ch13-s9-n8nworkflow-07.png)

![n8n workflow, figure 8](images/ch13-s9-n8nworkflow-08.png)

![n8n workflow, figure 9](images/ch13-s9-n8nworkflow-09.png)

![n8n workflow, figure 10](images/ch13-s9-n8nworkflow-10.png)

![n8n workflow, figure 11](images/ch13-s9-n8nworkflow-11.png)

![n8n workflow, figure 12](images/ch13-s9-n8nworkflow-12.png)

![n8n workflow, figure 13](images/ch13-s9-n8nworkflow-13.png)

![n8n workflow, figure 14](images/ch13-s9-n8nworkflow-14.png)

![n8n workflow, figure 15](images/ch13-s9-n8nworkflow-15.png)

### Images: Tutorial: SCM equipment assistant

*Source: [Tutorial: SCM equipment assistant](https://developers.sap.com/tutorials/joule-studio-scm-equipment-assistant)*

![SCM equipment assistant, figure 1](images/ch13-s10-scmequipment-01.png)

![SCM equipment assistant, figure 2](images/ch13-s10-scmequipment-02.png)

![SCM equipment assistant, figure 3](images/ch13-s10-scmequipment-03.png)

![SCM equipment assistant, figure 4](images/ch13-s10-scmequipment-04.png)

![SCM equipment assistant, figure 5](images/ch13-s10-scmequipment-05.png)

![SCM equipment assistant, figure 6](images/ch13-s10-scmequipment-06.png)

![SCM equipment assistant, figure 7](images/ch13-s10-scmequipment-07.png)

![SCM equipment assistant, figure 8](images/ch13-s10-scmequipment-08.png)

![SCM equipment assistant, figure 9](images/ch13-s10-scmequipment-09.png)

![SCM equipment assistant, figure 10](images/ch13-s10-scmequipment-10.png)

![SCM equipment assistant, figure 11](images/ch13-s10-scmequipment-11.png)

![SCM equipment assistant, figure 12](images/ch13-s10-scmequipment-12.png)

### Images: Tutorial: Spend supplier assistant

*Source: [Tutorial: Spend supplier assistant](https://developers.sap.com/tutorials/joule-studio-spend-supplier-assistant)*

![Spend supplier assistant, figure 1](images/ch13-s11-spendsupplier-01.webp)

![Spend supplier assistant, figure 2](images/ch13-s11-spendsupplier-02.png)

![Spend supplier assistant, figure 3](images/ch13-s11-spendsupplier-03.png)

![Spend supplier assistant, figure 4](images/ch13-s11-spendsupplier-04.png)

![Spend supplier assistant, figure 5](images/ch13-s11-spendsupplier-05.png)

![Spend supplier assistant, figure 6](images/ch13-s11-spendsupplier-06.png)

![Spend supplier assistant, figure 7](images/ch13-s11-spendsupplier-07.png)

![Spend supplier assistant, figure 8](images/ch13-s11-spendsupplier-08.png)

![Spend supplier assistant, figure 9](images/ch13-s11-spendsupplier-09.png)

![Spend supplier assistant, figure 10](images/ch13-s11-spendsupplier-10.png)

![Spend supplier assistant, figure 11](images/ch13-s11-spendsupplier-11.png)

![Spend supplier assistant, figure 12](images/ch13-s11-spendsupplier-12.png)

![Spend supplier assistant, figure 13](images/ch13-s11-spendsupplier-13.png)

![Spend supplier assistant, figure 14](images/ch13-s11-spendsupplier-14.png)

![Spend supplier assistant, figure 15](images/ch13-s11-spendsupplier-15.png)

![Spend supplier assistant, figure 16](images/ch13-s11-spendsupplier-16.png)

![Spend supplier assistant, figure 17](images/ch13-s11-spendsupplier-17.png)

![Spend supplier assistant, figure 18](images/ch13-s11-spendsupplier-18.png)

![Spend supplier assistant, figure 19](images/ch13-s11-spendsupplier-19.png)

![Spend supplier assistant, figure 20](images/ch13-s11-spendsupplier-20.png)

![Spend supplier assistant, figure 21](images/ch13-s11-spendsupplier-21.png)

### Images: Beyond PoC: Sovanta purchasing anomalies

*Source: [Beyond PoC: Sovanta purchasing anomalies](https://community.sap.com/t5/technology-blog-posts-by-members/beyond-poc-how-sovanta-detects-purchasing-anomalies-with-a-custom-joule/ba-p/14257926)*

![Sovanta blog, figure 1](images/ch13-s1-sovanta-01.png)

![Sovanta blog, figure 2](images/ch13-s1-sovanta-02.png)

### Images: SAP News: Joule in S/4HANA Cloud and Supply Chain

*Source: [SAP News: Joule in S/4HANA Cloud and Supply Chain](https://news.sap.com/2024/12/joule-available-sap-s4hana-cloud-supply-chain-management/)*

![SAP News article, figure 1](images/ch13-s12-newssap-01.jpg)

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

- **Read fully (text and screenshots):** SJ069 to SJ079, SJ082, SJ086, SJ088, SJ089, SJ086, SJ088, SJ089
- **Not read:**
  - fine print inside small screenshots (see 13.8)
  - the "Related learning" lists, videos, linked tutorials and Discovery Center missions
  - SJ080, SJ081, SJ083, SJ084 and SJ085: PDFs I could not open (not in this chapter); SJ087: page gone (410)
  - linked catalogue and team posts from SJ082
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
- sovanta, *Beyond PoC: How sovanta Detects Purchasing Anomalies with a Custom Joule Agent* (read): https://community.sap.com/t5/technology-blog-posts-by-members/beyond-poc-how-sovanta-detects-purchasing-anomalies-with-a-custom-joule/ba-p/14257926
- Mindset Consulting, *Twenty Joule Agents. Sapphire 2026.* (read): https://www.mindsetconsulting.com/twenty-joule-agents-sapphire-2026/
- SAP News, *Joule in SAP S/4HANA Cloud and Supply Chain* (read): https://news.sap.com/2024/12/joule-available-sap-s4hana-cloud-supply-chain-management/
- SAPinsider, *SAP Joule Agents Reach Ariba and Fieldglass* (read): https://sapinsider.org/blogs/sap-delivers-joule-agents-across-ariba-and-fieldglass-in-june-2026/
- CX Today, *SAP Talks Up AI Agents, but Where Are the CX Wins?* (read): https://cxtoday.com/sap-ai-agents-customer-service-wins
- Discovery Center missions: see 13.11

---

*Previous: [Chapter 12: Intent-based agents in Joule Studio: ten business scenarios](12-intent-based-agents-lab.md)*

---

*Next: [Chapter 14: Troubleshooting Joule setup and Joule Studio](14-troubleshooting-joule-setup-and-studio.md)*
