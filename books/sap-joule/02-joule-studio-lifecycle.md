# Joule Studio and the agent development lifecycle

*Intent in, agent out — but every stage in between is a reviewable artifact, not a black box.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** where Joule Studio sits in the SAP Business AI Platform, the three principles SAP designs "trusted" agents around, and the six-stage lifecycle every agent goes through — illustrated with a real worked example's actual generated files
> - **You will build:** nothing yet — but you'll see a complete generated agent's file tree, its `asset.yaml`, and its real test coverage breakdown
> - **Level:** beginner · **Time:** about 21 minutes
> - **Builds on:** [What Joule actually is](01-what-is-joule.md) (Skill/Agent/Assistant/Work, the three zones). **Leads to:** [Document grounding, analytics, and developer tooling](joule-advanced-capabilities.md)

**After this chapter you can:**

- Place Joule Studio correctly inside the SAP Business AI Platform's three pillars, and name its actual tool ecosystem
- Name the six stages an agent moves through in Joule Studio, in order, and what each one produces
- Explain the difference between Quick Create and the Iterative Track, and when you'd pick each
- Read a real generated agent's file tree and `asset.yaml`, and know what `kind: a2a` means there
- Say what Joule Studio tests before letting you deploy, and what "framework modules" means for coverage targets

## 2.1 Where Joule Studio sits

The SAP Business AI Platform has three pillars, and Joule Studio is only one piece of the first:

| Pillar | What it does | Key pieces |
|---|---|---|
| **Creation** | Build and extend AI-powered applications | **Joule Studio**, SAP Integration Suite |
| **Context and Analysis** | Give AI access to unified, high-quality business data | Business Data Fabric (SAP Datasphere) |
| **Governance** | Manage the AI lifecycle at scale | SAP AI Core, SAP AI Launchpad |

- If you've read the [SAP AI book](../sap-ai/README.md), AI Core and AI Launchpad will already be familiar — they're the governance pillar underneath both Joule and your own custom AI Core workloads.
- Inside Joule specifically: **Joule Work** is where business users consume AI capability through natural language; **Joule Studio** is where you build and extend it. Same platform, different door.

SAP's own ecosystem diagram names real, specific tools at every layer — this is worth more than the pillar table above, because it's concrete:

![SAP Business AI Platform ecosystem: Joule on top of SAP Autonomous Domains, Partner Agents (KPMG, Accenture, Deloitte, IBM, PwC, EY, Capgemini, NTT) and Third-party AI Agents (NVIDIA NemoClaw); below, Build (Joule Studio, n8n, Vercel, Claude Code, Cursor, SAP Integration Suite), Contextualize & Reason (SAP Knowledge Graph, SAP & Non-SAP Models including OpenAI, Mistral AI, Cohere, Perplexity, PRIOR), and Govern (SAP AI Agent Hub, Value Realization, Joule Studio Runtime, Identity/Access/Security), all on SAP Business Data Cloud (SAP, Databricks, Microsoft, Google Cloud, Snowflake)](images/02-platform-ecosystem.png)

- **You are not locked into SAP's own models or tools.** The diagram names OpenAI, Mistral AI, Cohere, Perplexity and "PRIOR" as usable models alongside SAP's own, and Databricks, Microsoft, Google Cloud and Snowflake as Business Data Cloud partners.
- **Partner and third-party agents are first-class, not an afterthought.** KPMG, Accenture, Deloitte, IBM, PwC, EY, Capgemini and NTT appear as named "Partner Agents"; NVIDIA NemoClaw appears as a named "Third-party AI Agent" — all governed through the same AI Agent Hub as your own agents ([What Joule actually is](01-what-is-joule.md), 1.6).
- The **Agent Gateway** ([What Joule actually is](01-what-is-joule.md), 1.2) sits literally in the middle of this diagram, between the SAP Autonomous Suite above and the Business AI Platform below — it's the thing every one of these integrations actually routes through.

## 2.2 Three principles, because "it compiles" isn't enough

An agent that reasons well isn't automatically safe to run against a live business process. SAP frames this as a **trust gap**, and designs Joule Studio around three principles to close it:

- **Context** — the agent needs business objectives, domain knowledge, enterprise data and process awareness, not just a system prompt.
- **Open and enterprise grade** — the solution has to integrate with what you already run, follow standards, and be tested against exceptions and edge cases, not just the golden path.
- **Governance** — identity and access controls, secure execution, and a traceable record of what the agent decided and why, plus visibility into cost and value delivered.

None of these three is unique to SAP — they're the same questions you'd ask of any production agent. What's specific to Joule Studio is that each one maps to a concrete capability in the sections below, instead of staying a slide-ware principle.

## 2.3 The six-stage lifecycle, on a real agent

Every agent — new or extended — moves through the same six stages:

![The six-stage Joule Studio development lifecycle: Business intent analysis, PRD, Specification, Solution, Testing, Deployment](images/02-dev-lifecycle.png)

```mermaid
flowchart LR
    I["Business intent\n(plain language)"] --> P["PRD\n(reviewable requirements)"]
    P --> S["Specification\n(implementation blueprint)"]
    S --> C["Solution\n(generated code + config)"]
    C --> T["Testing\n(end-to-end + behavior eval)"]
    T --> D["Deployment\n(SAP-managed runtime)"]
```

SAP's own course material walks a second full worked example through all six stages — a manufacturing agent called the **Cable Roll Optimizer**. It's reproduced here because every screen is a real generated artifact, not a mockup.

**Stage 1 — Business intent.** You describe the outcome, not the implementation, in the Create Agent dialog:

![Create Agent dialog: Solution, Name "Cable Roll Optimizer", a full intent statement, and the Quick Create checkbox](images/02-cro-1-intent.png)

> **Intent statement (in full):** "Create an agent that should optimize cable roll selection for manufacturing work orders to minimize offcut waste. It reads work order requirements from SAP S/4HANA — including cable material, required length, and specification — and checks available batch stock across all storage locations. Based on this data, the agent applies an optimization engine to recommend the single roll or combination of rolls that fulfills the work order with minimum waste. Where local stock is insufficient, the agent identifies available rolls at other locations and recommends raising a stock transfer order accordingly. All recommendations are presented to the planner for review and approval before any SAP data is modified. The agent supports configuration for acceptable waste thresholds, location priority rules, and batch selection criteria such as expiry date and certificate status."

- Notice **"All recommendations are presented to the planner for review and approval before any SAP data is modified"** — same pattern as [Extending an SAP-delivered agent](03-extending-a-standard-agent.md)'s "preserve the agent's standard functionality" clause: state your human-in-the-loop boundary in the intent itself, don't leave it implicit.
- **Quick Create: Skip clarifying questions and start directly building the solution** is a checkbox right in this dialog — confirming it's a one-step opt-in, not a separate mode.

**Stage 2 — PRD.**

![Generated PRD: title, owner, Solution Category "AI Agent (Python, A2A protocol)", elevator pitch, business need](images/02-cro-2-prd.png)

- The PRD's own title line states the architecture before a single file is generated: **Solution Category: AI Agent (Python, A2A protocol)**. Every PRD in this course — this one and the n8n example in [n8n workflows in Joule Studio](04-n8n-workflows.md) — names the implementation language and protocol up front, not as an implementation detail discovered later.

**Stage 3 — Specification.**

![Specification stage: guideline files listed (guidelines.md, guidelines-agent.md, guidelines-agent-python.md, guidelines-agent-skills.md, guidelines-agent-mcp.md) and generation of mcp-mock.json](images/02-cro-3-spec.png)

- The Specification stage generates its own **guideline files** before any implementation code: `guidelines.md` (universal execution rules), `guidelines-agent.md` (universal agent patterns), `guidelines-agent-python.md` (Python implementation details), `guidelines-agent-skills.md` (runtime skills patterns), `guidelines-agent-mcp.md` (MCP integration patterns). These are instructions the *generator* reads before writing code — a form of guardrail that exists before Stage 4, not bolted on after.
- It also generates an `mcp-mock.json` — a mocked MCP configuration used so the agent can be tested without live SAP connections (see Stage 5).

**Stage 4 — Solution** (this is the UI's own name for the stage — confirmed consistently across every screenshot in this chapter, not "Code"):

![File Explorer and generated asset.yaml for the Cable Roll Optimisation Agent, with Claude Code, Cursor, and Cline shown as IDE handover options](images/02-cro-4-solution.png)

The real generated file tree:

```text
app/
  mcp_providers/
  skills/
  __init__.py
  agent_executor.py
  agent.py
  circuit_breaker.py
  config_loader.py
  config.yaml
  load_skill_resources...
  main.py
  optimisation_engine.py
  prompt_injection_detector.py
  util.py
prebuilt_tests/
tests/
asset.yaml
conftest.py
coverage.json
mcp-mock.json
pytest.ini
README.md
requirements-test.txt
```

And the real `asset.yaml`:

```yaml
apiVersion: asset.sap/v1
kind: Asset

metadata:
  name: cable-roll-optimisation-agent
  version: "1.0.0"

agentCard:
  name: Cable Roll Optimisation Agent
  version: "1.0.0"
  description: Optimises cable roll selection for manufacturing work orders by
    minimising offcut waste using combinatorial bin-packing, enforcing
    expiry/certificates, and raising stock transfer orders with priority
  capabilities:
    skills:
      - name: roll-optimisation
        description: Select optimal cable rolls for a work order with...
      - name: stock-transfer
        description: Raise stock transfer orders for cross-location

provides:
  apis:
    - name: cable-roll-optimisation-agent
      kind: a2a
      ordId: customer.build.apiResource:cable-roll-optimisation-8b8...
```

> [!IMPORTANT]
> **🏭 In production: the generated scaffold ships its own resilience and security modules by default**
> `circuit_breaker.py` and `prompt_injection_detector.py` are not something you add later — Joule Studio generates them as part of the standard agent scaffold. A circuit breaker for calls to external systems, and a prompt-injection detector as framework-level infrastructure, come for free with every generated agent. This matters for Testing in Stage 5: these are counted as *framework* modules, not business logic, so don't expect (or chase) business-logic-level test coverage on them.
>
> *Added by Claude; the course's screenshots show this but don't name the pattern explicitly.*

- `kind: a2a` on the `provides.apis` entry confirms what the PRD already said: this agent's API is exposed as an **A2A** endpoint, the same protocol from [What Joule actually is](01-what-is-joule.md), 1.7 and the post-hook in [Extending an SAP-delivered agent](03-extending-a-standard-agent.md).
- Skills are declared in the `agentCard` as a list with `name` + `description` — this is the Joule Skill concept from [What Joule actually is](01-what-is-joule.md), 1.1, now visible as literal YAML.
- The IDE handover options shown here are more complete than a short list: **Claude Code, Cursor, Cline, Open Code, Codex, "and more"** — see 2.4.

**Stage 5 — Testing.**

![Testing Overview for the Cable Roll Optimizer: 150 total tests, 150 passed, 0 failed, 100% score, with per-module coverage breakdown](images/02-cro-5-testing.png)

- Per-module coverage, read from the actual chat trace: **`agent.py` 69%, `config_loader.py` 96%, `optimisation_engine.py` 81%** — the genuine business logic. Against that: **`mcp_providers/agw.py` 23%** (flagged as "network infrastructure, cannot be unit tested offline") and **`prompt_injection_detector.py` 0%** (flagged as "security infrastructure... framework modules that don't need to be covered by agent-specific tests"). This is the live version of the pitfall above: don't read a low number on a framework module as a quality problem.
- This example also deploys with **4 SAP-connected MCP servers** alongside the agent — `sap-s4-production-order-mcp-server`, `sap-s4-batch-master-record-mcp-...`, `sap-s4-material-stock-mcp-server`, `sap-s4-stock-transport-order-mcp-...` — the same "one MCP server per integration point" pattern from [n8n workflows in Joule Studio](04-n8n-workflows.md)'s n8n example, now confirmed on an agent too.

**Stage 6 — Deployment.**

![Deployment summary: all 5 assets running on SAP BTP, with a real agent endpoint URL and a one-time authorization step](images/02-cro-6-deploy.png)

- **"Deployment Complete — All 5 assets are running on SAP BTP"** (the agent plus its 4 MCP servers), with a real endpoint format: `https://<id>.dev-eu1.ca.ai.cloud.sap`.
- **"To make the agent available to your production planners and manufacturing engineers, a one-time authorization setup is required."** — deployment and user-facing availability are two separate steps; don't assume one implies the other.
- **Preview Your Agent with Mock Data** is a distinct pre-deployment step, letting you converse with the agent before it touches real SAP data — using the `mcp-mock.json` generated back in Stage 3.

![Fast track vs Iterative track side by side: Fast track goes from intent to spec instantly for clear requirements; Iterative track refines intent through guided clarifying questions before generating a validated spec](images/02-fasttrack-vs-iterative.png)

> [!TIP]
> **💡 Quick Create vs Iterative Track**
> When your intent is already well-specified, enable **Quick Create** and Joule Studio skips straight to generation. When it isn't, the **Iterative Track** asks targeted clarification questions first. Both produce the same downstream artifacts — the difference is only how much Joule Studio has to ask before it starts generating. Default to Iterative Track unless you've genuinely already thought through the edge cases yourself.

## 2.4 How you actually build

Joule Studio deliberately doesn't lock you into its own web UI:

![Six ways Joule Studio integrates with how you already work: generate specs, open IDE, create via AI, edit and push to Git, connect via MCP/A2A, test and deploy to SAP Business AI Platform](images/02-mcp-a2a-integration.png)

![Open ecosystem of coding tools you can hand off to: Claude Code, Cursor, Cline, Open Code, Codex, and more, all keeping teams synced through your Git provider of choice](images/02-ide-ecosystem.png)

- **Three surfaces**: the Joule Studio web interface, your own **IDE**, or a **CLI**. The real tool list is wider than a token example suggests: **Claude Code, Cursor, Cline, Open Code, Codex** — "and more."

Who does what, at each stage, through which entry point — stated explicitly rather than left implicit:

![Entry points and per-stage responsibilities: business users work through Joule Studio only; developers work through Joule Studio, IDE or CLI, with a row for each of the six lifecycle stages](images/02-roles-raci.png)

- Notice **Specification has no business-user row at all** — it's the one stage that's entirely a developer activity. Business users re-enter at Solution ("give feedback through solution preview") and Testing ("confirm the solution meets business needs"), but don't touch the technical spec itself.
- **Git is the shared foundation.** Every generated artifact can be pushed to Git, through the Git provider of your choice — version control, code review, and team collaboration work the way they already do for the rest of your code, not some Joule-specific workflow.
- **Enterprise integration runs through MCP and A2A.** This confirms the "open protocols" flagged as unresolved in [What Joule actually is](01-what-is-joule.md), 1.7 — Joule Studio names both explicitly: **MCP** for connecting tools and services, **A2A** for agent interoperability, and the worked example above shows both as literal file content (`mcp-mock.json`, `kind: a2a`), not just slideware. If you know the [MCP book](../mcp/01-why-mcp-exists.md), this is not new ground, just a new place it's wired in.
- Business context during generation is pulled from **SAP LeanIX** (landscape/architecture), **SAP Signavio** (process intelligence), the **SAP Knowledge Graph / domain models** (application semantics) — and one more named here for the first time: **SAP RPT-1**, described as a predictive-AI source ("Anticipate... Predictions"). SAP Business Data Cloud fills out the picture as the facts source.
- SAP's own product page groups that same context into four categories, which is a cleaner mental model than the tool-name list above: **landscape insights** (architecture, a central agent repository, compliance policies, identity controls), **application context** (data models, object relationships, functionality, KPIs), **process insights** (bottlenecks, gaps, improvement recommendations), and **best practices** (process templates, development guidelines, benchmarks). Note the **"central agent repository"** sitting inside landscape insights — a discoverable inventory of what's already been built, separate from (but feeding) the AI Agent Hub in 2.5.

Generated agent code is not a mystery framework — the product page's own promotional screenshot of `main.py` shows exactly what it's built on:

![A generated agent's main.py: class SampleAgent with SUPPORTED_CONTENT_TYPES, a cache_control_injection block, and _build_llm returning a ChatLiteLLM instance — next to a "Recommended Solution" panel (Create requirements, Review PRD, Generate code, Deploy solution)](images/02-litellm-code.png)

- The model call is `ChatLiteLLM(model=model, temperature=self...)` — **generated agents use LiteLLM** as the model-abstraction layer. That single line explains how one agent can target OpenAI, Mistral, Cohere, or SAP's own models (the ecosystem diagram in 2.1) without separate integration code per provider — LiteLLM is exactly the library that normalizes those APIs.
- The scaffold also shows a `cache_control_injection` block and a `thread_ttl_seconds` setting — prompt-caching and conversation-lifetime controls, generated into the agent by default rather than something you'd wire up yourself.
- This panel's own shorthand for the lifecycle — "Create requirements, Review PRD, Generate code, Deploy solution" — calls the Solution stage **"Generate code"**, yet another naming variant alongside "Solution" (the UI's consistent name, 2.3) and "Code" (the course's occasional prose). Three names, one stage — pick "Solution" as the one that matches the actual product UI, and don't be thrown by the other two.

A second full example, from the same page, confirming the "several MCP servers per solution" pattern once again:

![The Create Agent dialog over a Solutions list showing "Discount Pricing Agent" tagged 1 Agent + 5 MCP Servers, and a "Tariff Disruption Response Agent" intent statement about tariff and supply-chain disruption](images/02-tariff-agent-example.jpg)

- **Discount Pricing Agent: 1 Agent, 5 MCP Servers** — a fifth data point (after the Sourcing extension, the n8n PO workflow, the Cable Roll Optimizer, and the AR Collection Email solution in [Extending an SAP-delivered agent](03-extending-a-standard-agent.md)) for the same rule: a solution's MCP-server count tracks its number of external integration points, and that count is often more than one.

### 2.4a Two builders, and connecting Joule Studio across subaccounts

![Joule Studio's place in the wider SAP BTP architecture: inside SAP Build alongside Process Automation, Apps, Code, and Work Zone, trusting SAP Cloud Identity Services, reaching SAP AI Core/Document Grounding and SAP Cloud Solutions, and connecting outward to on-premise systems and 3rd-party APIs](images/sj144-01-joule-studio-sap-build-architecture-diagram.png)

Joule Studio, Classic Edition actually has **two distinct builders**, both GA:

| Builder | For | Cost |
|---|---|---|
| **Skill Builder** | A single predefined task (the Trigger → Action → Send Message → End shape) | No additional orchestration cost, no AI Units consumed |
| **Agent Builder** | Autonomous, multi-step agents that plan their own path through a task | Billed in AI Units once its promotional free-execution window ends |

Agent Builder is activated via **Control Tower → AI Agent Builder Activation**.

> [!WARNING]
> **⚠️ Pitfall: don't trust a specific promo end-date for Agent Builder — it has already moved twice**
> Three SAP sources disagree with each other on when Agent Builder's free-execution promo ends: one blog says "through Dec 31, 2026," a later one corrects that to "May 31, 2026," and the activation screen's own UI banner said "at least January 31, 2026." All three dates have already passed as of this chapter's own check. The pattern, not the date, is the lesson: **verify current billing status directly in the Control Tower before assuming a custom Joule Agent is still free to run** — don't cite any blog's stated date as current.

If **Joule and SAP Build Process Automation live in separate global accounts**, they can still be connected — the one hard requirement is both being federated under the **same SAP Cloud Identity Services tenant** (the "golden thread" that makes this work at all, consistent with the unified-instance rule in [the identity foundation chapter](btp-identity-foundation.md)). Concretely: BTP Cockpit → System Landscape → **Formations** → select the "Integration with Joule" formation → **Include Systems** → pick the SBPA subaccount → check **Enable Capability Deployment** → wait for Formation Status to reach **Ready**.

> [!WARNING]
> **⚠️ Pitfall: the documented role-collection name may not match what actually works**
> The documented requirement is role collections `joule_extensibility` and `end_user` on the Joule subaccount. A real reported case needed `extensibility_developer` instead of `joule_extensibility` to actually get things working — an unresolved discrepancy between two SAP sources. If Joule Studio doesn't appear after an otherwise-correct split-account setup, try both role collection names rather than assuming the documented one is simply wrong to use.

- **If Joule Studio doesn't appear after the Booster at all**, the usual suspects, in order: mismatched IAS tenants between the two subaccounts, SAP Build Process Automation still on the legacy "standard" plan instead of **build-default**, a missing or wrong Joule SKU, or missing role collections (see the pitfall above). If the Formation itself won't reach Ready, that points to an IdP trust error — log an SAP BTP Technical Advisory request rather than keep retrying the same formation action.

## 2.5 Testing and governance, beyond one agent

The per-agent testing in 2.3 is only half the picture — once deployed, agents are governed centrally:

![SAP AI Agent Hub's AI Agent Discovery Inbox: a real inventory of agents (Procurement Invoice Agent, Billing Creation Agent 2.3.5 Production, Classification Agent, Vendor Risk Evaluator) with status and a usage-analytics detail panel showing session counts and a sessions-over-time chart](images/02-ai-agent-hub.png)

- This is the **AI Agent Hub** from [What Joule actually is](01-what-is-joule.md), 1.6, shown as a real screen rather than a description: a searchable **Discovery Inbox** of every agent in the landscape (here: 52 total results), each tagged by classification (SAP AI Agent, etc.) and status (**Action Needed** / **Linked**), with an **Approval gate** ("Reject" / "Add to Inventory") before anything goes into inventory.
- The detail panel for one agent shows real **usage analytics**: Total Sessions, First/Last Active dates, and a Sessions Over Time chart — this is the "visibility into cost and value delivered" principle from 2.2, made concrete.
- Identity and access control specifically runs through **SAP Cloud Identity Services** — named explicitly on SAP's own product page as the mechanism behind the "identity and access controls" line in 2.2's governance principle.

The runtime underneath all of this:

![SAP-managed runtime capabilities: deploy, securely run with identity/security/compliance, scale across business, with NVIDIA OpenShell named for secure isolation — alongside a real agent's Testing Overview panel](images/02-runtime-openshell.png)

- **NVIDIA OpenShell** is named explicitly as the isolation technology behind the SAP-managed runtime's "secure isolation and enterprise scale" claim — this is the specific product name behind what [What Joule actually is](01-what-is-joule.md) described only generically as "the SAP-managed runtime."
- The testing panel shown alongside it (a different example, "Cable Roll Optimizer" again, 150/150/0 at a **different point in development**) reflects a live tool trace: "Called 3 tools," "Called 6 tools," including a **deployment quota check** and **file validation** before the agent actually ships — the generation process itself uses tools, the same way the agent it's generating will.

> [!WARNING]
> **⚠️ Pitfall: "testing" here means behavioral evaluation, not just execution**
> A generated agent can execute successfully and still fail its actual job — e.g. return a technically valid but business-wrong recommendation. Treat Joule Studio's testing stage as closer to an LLM eval suite than a traditional CI test run, and budget review time accordingly before you deploy, especially the first time you extend a given agent.

## 2.6 An older entry point: Joule Studio inside SAP Build

Everything so far shows Joule Studio as its own destination. A community write-up (basic in its own text, but carrying three screenshots worth more than the prose around them) shows a second, older entry point: **Joule Studio reached from inside SAP Build**, SAP's existing low-code platform.

![SAP Build's "Create Project" dialog: four project types — Application, Automated Process, "AI Agent and Joule Skill" (use Joule Studio to create and deploy AI Agents and Joule Skills with drag-and-drop simplicity), and Business Site](images/02-sapbuild-create-project.jpg)

- In SAP Build's own project-creation flow, **"AI Agent and Joule Skill"** sits alongside Application, Automated Process, and Business Site as a fourth project type — a different (likely earlier) front door into the same Joule Studio capability described in the rest of this chapter.

Opening an agent built this way surfaces a configuration screen not shown anywhere in the official course material:

![SAP Build's agent config screen for a "Logistics Agent": a Thinking Steps selector (Small/Medium/Large), an LLM Provider row (Anthropic, Google, MistralAI, OpenAI), separate Base Model and Advanced Model dropdowns, and a Tools table with Name/Description/Resource columns](images/02-sapbuild-agent-config.jpg)

- **LLM Provider is an explicit, visible choice**: Anthropic, Google, MistralAI, OpenAI — not an abstraction you only infer from the `ChatLiteLLM` code in 2.4, but a literal dropdown.
- **Two model slots, not one**: a *Base Model* (here `GPT4o Mini`) and an *Advanced Model* (here `GPT4o`) — implying cheaper/faster vs. more capable models are selected separately, presumably for different parts of an agent's reasoning.
- **Thinking Steps: Small / Medium / Large** — a reasoning-effort control, the same shape as the `temperature`/reasoning-effort knobs you'd set by hand in a framework like LangChain, exposed here as a simple three-way UI choice.
- The **Tools table** (Name, Description, Resource, each editable) is the UI-level view of what the generated `agentCard.capabilities.skills` YAML in 2.3 represents in config form — a real example tool here is "Unified Risk and Weather Retrieval: real-time weather forecast APIs to gather climatic conditions along the transportation path."

A Joule Skill itself has its own visual canvas, distinct from both the agent config above and the n8n canvas in [n8n workflows in Joule Studio](04-n8n-workflows.md):

![A Joule Skill's flow canvas: Trigger ("When skill is called") -> Transportation Process -> Fetch Tracking Status -> Confirmation Message -> End](images/02-sapbuild-skill-canvas.jpg)

- Every skill flow starts with a fixed **Trigger: "When skill is called"** node and ends at an **End** node, with business logic steps in between (here: a process step, a data-fetch step, and a message-composition step) — a simpler, more constrained canvas than n8n's, appropriate for what a Skill is meant to be ([What Joule actually is](01-what-is-joule.md), 1.1): atomic and deterministic, not an open-ended workflow.

> [!WARNING]
> **⚠️ Pitfall: don't follow this blog's access instructions literally**
> The blog post this came from tells readers to "go into SAP Build and access Joule Studio" as the way in. That may have been accurate when it was written (per its own screenshots), but it predates the dedicated Joule Studio launcher and the SAP-Managed Joule activation path from [What Joule actually is](01-what-is-joule.md), 1.4. Treat the SAP Build entry point as *a* way in that still appears to exist, not necessarily *the* current recommended one — confirm against current docs before telling someone else how to get started.

## 2.7 Added by Claude, not from the sources

- The explicit confirmation that "Solution" (not "Code") is the UI's own stage name was reached by cross-checking every screenshot in this chapter — the course's own prose is looser than its own UI, but the UI is consistent everywhere it appears.
- The framing of MCP/A2A as "resolving" [What Joule actually is](01-what-is-joule.md)'s open question is this book's own continuity, not something the course states.
- The 🏭 box on `circuit_breaker.py` / `prompt_injection_detector.py` as default scaffold modules is a pattern this book names; the course's screenshots show it but don't call it out as a design principle.
- Reading `ChatLiteLLM` as confirmation that Joule Studio uses LiteLLM for model abstraction is a direct read of the generated code shown in SAP's own product-page screenshot — not an inference, but also not something SAP states in prose anywhere on that page.
- SAP's product page also cites customer and analyst proof points not reproduced here in detail: Accenture (25% faster full-stack app development), Florida Crystals (a customer story), and a Constellation Research benchmark claiming Joule Studio is "5.5x faster" than traditional development across three scenarios. These are marketing claims from named sources, not independently verified — cite the source and the claimed number together if you ever repeat them, never the number alone.
- Not run: this chapter's worked example is reproduced from the course's own screenshots; nothing here was independently executed, since it requires a Joule Studio tenant this book doesn't have access to.

## 2.8 Interview corner

**What interviewers listen for:** you can name the six lifecycle stages in order, you know Quick Create is a shortcut through clarification (not through testing or review), you don't conflate "code executes" with "agent behaves correctly," and you can read a real `asset.yaml` without flinching.

### 🟢 Basic

<details class="qa"><summary>1. What are the six stages of the Joule Studio agent lifecycle?</summary>

- Business intent → PRD → Specification → Solution → Testing → Deployment

</details>

<details class="qa"><summary>2. What's the difference between Quick Create and the Iterative Track?</summary>

- Quick Create skips the clarification questions and generates directly from the stated intent; the Iterative Track asks clarifying questions first to refine requirements before generating anything

</details>

### 🟡 Intermediate

<details class="qa"><summary>3. Which two open protocols does Joule Studio use for enterprise integration, and what does each do?</summary>

- MCP connects an agent to tools and services; A2A lets agents interoperate with other agents
- *Stronger answer:* this is the same split as the rest of the agentic-AI ecosystem — MCP is model↔tools, A2A is agent↔agent — Joule Studio didn't invent a third mechanism, and the generated `asset.yaml`'s `kind: a2a` is literal proof of it

</details>

<details class="qa"><summary>4. In the Cable Roll Optimizer example, `prompt_injection_detector.py` shows 0% test coverage. Is that a problem?</summary>

- No — it's flagged as a framework/security-infrastructure module, not business logic, and isn't expected to carry agent-specific test coverage
- *Stronger answer:* the real signal to check is whether your *business logic* modules (here, `agent.py`, `config_loader.py`, `optimisation_engine.py`) are well covered — a low number on infrastructure doesn't mean the same thing as a low number on your own code

</details>

<details class="qa"><summary>5. Is an agent built in Joule Studio locked to one LLM provider?</summary>

- No — the SAP Build-hosted agent config screen shows an explicit LLM Provider choice (Anthropic, Google, MistralAI, OpenAI) and even separates a Base Model from an Advanced Model
- *Stronger answer:* this is consistent with the `ChatLiteLLM` call seen in the generated code elsewhere in this chapter — LiteLLM is exactly the kind of library that makes a provider dropdown like this possible without per-provider integration code

</details>

### 🔴 Senior

<details class="qa"><summary>6. A business user hands you a one-line intent and wants an agent by end of day. Walk through your approach.</summary>

- Resist Quick Create by default — a one-line intent is exactly the under-specified case the Iterative Track exists for
- Use the clarification questions to surface edge cases and constraints before anything is generated, since fixing a wrong PRD is cheaper than fixing a wrong deployed agent
- *Stronger answer:* push back on the deadline if the PRD review step gets skipped — that's the one human checkpoint standing between a plausible-sounding intent and a production agent making real business decisions

</details>

> [!TIP]
> **🧩 Design question**
> *"Your team ships an agent through Quick Create, it passes Testing, and three weeks later it's recommending something your PRD never asked for."* Talk about: PRD drift (did the generated solution actually match the reviewed PRD, or did it generate something the business never confirmed), whether behavior evaluation covered this exact scenario, and what AI Agent Hub's session/usage trace would show you about when the behavior changed.

## Cheat sheet

| Stage | Produces | Who reviews it |
|---|---|---|
| Business intent | A plain-language problem statement | Business user |
| PRD | Structured requirements + named architecture (e.g. "AI Agent, Python, A2A") | Business user + developer |
| Specification | Technical blueprint + generated guideline files | Developer |
| Solution | Generated code/config (`asset.yaml`, skills, `kind: a2a` APIs) | Developer |
| Testing | End-to-end + per-module coverage (business logic vs. framework modules) | Developer |
| Deployment | Agent + MCP servers running on SAP BTP, one-time auth to go live | Developer + AI Agent Hub |

## Recap

- Joule Studio is the **Creation** pillar of the SAP Business AI Platform; Context/Analysis (Datasphere) and Governance (AI Core, AI Launchpad) are the other two — and the real ecosystem includes named non-SAP tools (OpenAI, Mistral AI, Cohere, Databricks, Microsoft, Google Cloud, Snowflake) and named partner/third-party agents
- Six lifecycle stages, always in order: **Business intent → PRD → Specification → Solution → Testing → Deployment** — confirmed as the UI's own naming across every screenshot
- A real generated agent is a Python/A2A solution with a standard scaffold that includes `circuit_breaker.py` and `prompt_injection_detector.py` by default, and one MCP server per SAP integration point (five such examples across this book so far)
- Generated agents call models through **LiteLLM** (`ChatLiteLLM`) — the actual mechanism behind "any model, one interface" — and identity/access control runs through **SAP Cloud Identity Services**
- **Quick Create** skips clarification questions; it does not skip review or testing
- Build in the **web UI, an IDE** (Claude Code, Cursor, Cline, Open Code, Codex), **or a CLI** — Git ties them together
- Testing means **behavioral evaluation against the PRD**, not just successful execution — and low coverage on a framework module (like the prompt-injection detector) isn't the same signal as low coverage on your own business logic
- AI Agent Hub's Discovery Inbox is a real approval gate with per-agent usage analytics, not just a concept
- Joule Studio can also be reached through **SAP Build**'s own "Create Project" flow (an older entry point); agent config there shows an explicit LLM provider choice (Anthropic, Google, MistralAI, OpenAI), separate Base/Advanced model slots, and a Thinking Steps (Small/Medium/Large) reasoning control — and a Skill has its own Trigger→steps→End flow canvas, distinct from the n8n canvas in [n8n workflows in Joule Studio](04-n8n-workflows.md)
- **Skill Builder** (single predefined tasks, no AI-Unit cost) and **Agent Builder** (autonomous multi-step agents, billed once its promo ends) are two distinct, separately-activated builders — and Joule/SAP Build Process Automation can live in separate global accounts as long as both share one Cloud Identity Services tenant

## Practice

1. Without looking back, list the six lifecycle stages and say in one sentence who reviews each one
2. Sketch an `asset.yaml` for an agent you're familiar with: name, version, one or two skills, and whether its API would be `kind: a2a`
3. Explain out loud why 0% coverage on `prompt_injection_detector.py` isn't a red flag, but 0% coverage on your own business logic module would be

## How this chapter was checked

- All 7 lessons and all 4 unit quizzes of "Introducing Joule Studio" (learning.sap.com/courses/introducing-joule-studio) were read in full, 9 Nov 2026. The "End-to-End Demo" video was not watched.
- The SAP Joule Studio product page (sap.com) was read in full 10 Nov 2026, including all 5 FAQ accordion answers expanded.
- 43 images appeared across the "Introducing Joule Studio" course's lessons; all 14 used in earlier revisions remain, covering the platform ecosystem diagram, the six-stage lifecycle diagram, the Fast track/Iterative track diagram, the MCP/A2A integration diagram, the IDE ecosystem diagram, the AI Agent Hub screenshot, the runtime/NVIDIA OpenShell screenshot, and all 6 stages of the Cable Roll Optimizer worked example. Per this book's "skip no images" rule, every other image from that course was re-checked; none carried further unused product or diagram content beyond what's already covered in this chapter or Chapters 3-4.
- 2 further images are used from the product page (saved to `images/`, never hotlinked): the generated `main.py` / ChatLiteLLM screenshot, and the Tariff Disruption Response Agent / Discount Pricing Agent example. The page's other visible image (a hero background pattern) is decorative with no content.
- A community blog post, "Gamechanger Alert: Meet SAP Joule Studio for Real-World Impact" (community.sap.com), was read in full 10 Nov 2026. Its own text is non-technical and written by a self-described SAP newcomer (generic HR/IT use cases, no code or architecture) — but all 3 of its embedded screenshots are used here (saved to `images/`, never hotlinked), since they show a SAP Build entry point and a configuration UI (explicit LLM provider choice, dual model slots, a Skill flow canvas) not documented anywhere else in this chapter.
- Nothing in this chapter is code yet, so nothing was run — the file tree, `asset.yaml`, `main.py`, and coverage numbers are transcribed directly from source screenshots, not independently executed.
- Section 2.4a was added 13 Nov 2026 from two further sources, discovered via a partner resource hub and judged ~90% commercial/licensing (SKUs, TDD pricing, Fair Use Limits — correctly out of scope per this book's standing rule) but each contributing one genuinely non-commercial technical fact: the Skill Builder/Agent Builder distinction, and the Formations/role-collections mechanics for a split-account Joule Studio setup. 4 images were found across both (3 byte-identical between the two sources, cross-referenced rather than re-downloaded); 1 unique architecture diagram is used here, opened and visually verified before captioning.

## Sources and further reading

- SAP Learning, *Introducing Joule Studio* — https://learning.sap.com/courses/introducing-joule-studio (all 7 lessons + 4 quizzes, read in full 9 Nov 2026)
- SAP, *Joule Studio product page* — https://www.sap.com/products/artificial-intelligence/joule-studio.html (read in full, all FAQs expanded, 10 Nov 2026)
- Chetannagpal, *Gamechanger Alert: Meet SAP Joule Studio for Real-World Impact* — https://community.sap.com/t5/human-capital-management-blog-posts-by-members/gamechanger-alert-meet-sap-joule-studio-for-real-world-impact/ba-p/14133749 (read in full, 10 Nov 2026; used for its 3 screenshots, not its text)
- SAP Community, *How to Get Started with Joule Studio, Classic Edition* — https://community.sap.com/t5/application-development-and-automation-blog-posts/how-to-get-started-with-joule-studio/ba-p/14152855 (read in full 13 Nov 2026)
- SAP Community, *Setting Up Joule Studio, Classic Edition for All Partner Flows and Entitlement Levels* — https://community.sap.com/t5/technology-blog-posts-by-sap/setting-up-joule-studio-for-all-partner-flows-and-entitlement-levels/ba-p/14282498 (read in full 13 Nov 2026)

Previous: [What Joule actually is](01-what-is-joule.md) · Next: [Document grounding, analytics, and developer tooling](joule-advanced-capabilities.md)
