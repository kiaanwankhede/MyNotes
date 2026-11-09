# Chapter 10: Pro-code agents and the A2A protocol

*How custom code-based agents plug into Joule: the integration pattern, three ways around the 60-second limit, securing the agent, and a CLI build of a supplier-disruption agent.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** how low-code and pro-code agents connect to Joule, what A2A is, the three integration options and their limits, how to secure an agent with IAS tokens, and how the Joule Studio CLI flow builds an agent from an intent
> - **Level:** intermediate · **Time:** about 60 minutes of reading plus the 40-minute tutorial
> - **Sources:** one SAP Architecture Center page, two SAP Community blogs, one SAP Developer tutorial, and one SAP concept index page, read 8 November 2026 with their images
> - **Builds on:** [Chapter 8](08-agents-hands-on.md) (agents and MCP in Joule Studio)

**After this chapter you can:**

- Explain how Joule calls a low-code agent versus a pro-code agent
- Name the A2A steps and Joule's time limits
- Choose between three integration options for slow agents
- Describe how IAS tokens protect an agent endpoint
- Walk through the intent-based development flow with the `jl` CLI

> [!WARNING]
> **What this chapter is**
> - Parts of the architecture are **not yet generally available** (the Architecture Center page says so); two-way links to third-party agents through the Agent Gateway are not supported yet
> - The blogs are written by SAP staff and show sample code from their repositories, not product documentation
> - Dates matter: constraints in the blog (March 2026) were partly changed by a June 2026 update
> - I ran nothing

> [!CAUTION]
> **Credentials**
> - The IAS blog shows client IDs, secrets and tenant URLs as placeholders. Use your own, and keep them out of code and notes

## 10.1 How Joule reaches an agent (SJ044)

*Source: SAP Architecture Center, "Integrating AI Agents with Joule (Outbound A2A)", updated 26 October 2026 (text and diagram read).*

- **Joule is the front door:** its orchestrator decides whether to use a built-in skill, fetch information, or hand the task to a custom agent
- **Low-code agents (Joule Studio):**
  - Deploying the agent creates the Joule artifacts for you: a **Joule scenario** and a **dialog function**
  - The scenario is registered in the scenario catalog
  - At runtime Joule calls the dialog function, which runs the agent in the **managed runtime on SAP AI Core**
- **Pro-code agents (bring your own agent):**
  - The agent must be an **A2A server**: an HTTP endpoint following the Agent2Agent protocol (the page names version 0.3.0)
  - You create a **Joule scenario** by hand, add a **dialog function** whose action is of type `agent-request`, and point it at the agent's A2A endpoint
  - Joule acts as the **A2A client**, sends `message/send` with the user's text, waits, and shows the result

| Agent type | How it connects | Traits |
|---|---|---|
| Low-code | Automatic at deployment | No manual set-up; tied to SAP Build lifecycle |
| Pro-code | Manual, A2A protocol | Open standard; most flexible |

- **Three capabilities for pro-code agents:**
  - **Synchronous:** Joule expects an answer within **60 seconds**
  - **Asynchronous:** for long tasks, the agent notifies a Joule webhook through push notifications
  - **Multi-turn:** context and task IDs from the agent can be reused in later requests
- **Security:** an **IAS app-to-app trust** must exist between Joule and the agent server
- **Diagram (read):** the Business AI Platform holds Joule Work (Joule Studio with custom agents and agent extensions, the Joule orchestrator with skills), managed runtimes and an **Agent Gateway** (discovery and invocation, speaking A2A and MCP); a customer subaccount holds custom agents and SAP Integration Suite (MCP gateway, A2A connectivity); third parties (MCP servers, APIs, other clouds' agents) sit across the network; **SAP Cloud Identity Services** provides trust; the Autonomous Suite holds the domain apps

```mermaid
flowchart LR
  U[User] --> J[Joule orchestrator]
  J -->|low-code: deployed scenario| R[Managed runtime on AI Core]
  J -->|pro-code: agent-request over A2A| A[Your A2A agent endpoint]
  I[IAS trust] -.-> J
  I -.-> A
```

## 10.2 Three ways to integrate a code-based agent (SJ045)

*Source: SAP Community blog, "Integrating Joule with Code-based Agents: Three Paths Forward" (text and all 8 images read).*

- **Three constraints in the base pattern:**
  - **60-second clock** on synchronous calls; slower agents give the user an error. The blog adds a 30 June 2026 update: **asynchronous A2A with push notifications** is now available
  - **Agent Builder (low-code) had no native A2A support** as of March 2026; direct A2A only worked from the Joule Studio **Code Editor** (pro-code). A2A is said to be on the roadmap
  - **No live status** reaches the user while the remote agent works

| | Option 1: direct A2A | Option 2: async REST | Option 3: A2A client proxy |
|---|---|---|---|
| Path | Code Editor → A2A → agent | Agent Builder → Build Process Automation → REST → agent | Either tool → A2A client service → A2A → agent |
| Timeout | about 60 s | about 5 min | no hard limit |
| Streaming | No | No | Yes |
| Complexity | Low | Medium | Medium |
| Best for | Fast agents | 1–5 minute jobs, low-code | Best user experience |

- **The sample use case:** a Deep Research Agent (an orchestrator plus parallel research sub-agents, built with a LangGraph-based SDK, adapted to SAP Generative AI Hub, deployed on Cloud Foundry). It is slow on purpose, to stress all three options
- **Option 1 detail:**
  - The agent exposes an **agent card** at `/.well-known/agent.json`
  - Joule reaches it through a named **BTP destination**, so no credentials sit in code
  - To fit 60 seconds, lower research depth and parallelism (two environment variables); this costs quality
  - **Limits:** hard timeout; no streaming
- **Option 2 detail:**
  - The agent has a REST API: one synchronous endpoint, one to **submit a job** (returns a job ID at once) and one to **poll a job**
  - A **Build Process Automation** process submits the job, then loops, waiting about a minute between polls, until the status is *completed*; the skill returns the report
  - **Parts:** an action project (two REST actions), the process, the skill; sample archives are provided for import
  - **Limits:** "fire and wait", no partial output; about 5 minutes. The full async callback model needs the agent to use the **same IAS** as Joule
- **Option 3 detail:**
  - A small **stateless proxy** (TypeScript on Cloud Foundry) turns REST calls into A2A calls: a synchronous endpoint, a raw stream, and a **normalised stream** whose chunks Joule can read with a JSON path
  - Joule's *Streamed Message Action* shows the text as it arrives; for Agent Builder, the synchronous endpoint is exposed as an action project
  - The target agent and its authentication come from a **BTP destination** at request time (basic, client credentials or JWT-bearer)
  - **Limit:** through Agent Builder, the normal action quotas still apply (1 minute connection, 3 minutes socket)
- **Rule of thumb from the blog:** fast agent → option 1; long but low-code → option 2; best experience or both tools → option 3

```mermaid
flowchart TD
  Q{How long does your agent run?} -->|under 60 s| O1[Option 1: direct A2A]
  Q -->|1 to 5 min and low-code| O2[Option 2: async REST plus process]
  Q -->|any length, want live progress| O3[Option 3: A2A client proxy with streaming]
```

## 10.3 Securing the agent with IAS (SJ046)

*Source: SAP Community blog, "Joule A2A: Secure Code Based Agents with IAS" (text and both images read).*

- **Problem:** the first A2A set-up had **no authentication**, so anyone on the internet could call the agent
- **Scope of the fix:** **app-to-app** authentication with the OAuth2 **client credentials** flow. The token identifies the **application**, not the end user
  - To call backends **as the user**, you need **principal propagation**, a different pattern (covered in a separate blog, not read)
- **IAS side:** an application with a provided API scope (the blog uses `api_read_access`) and client credentials with that permission
- **Token checks:** a JWT is a signed token; the middleware checks
  - **issuer** (your IAS tenant), **audience** (your client), **expiry**, and the **scope** list
  - the **signature**, using IAS's public keys fetched from its key-set endpoint
- **Middleware:** about 50 lines of Python for the A2A web server
  - lets the **discovery path** (`/.well-known/`) stay public
  - returns **401** for a missing or invalid bearer token
  - one line adds it to the server; issuer and audience come from environment variables in the deployment manifest
- **Test in three calls:** public agent card works; a call without a token fails with 401; a call with a token fetched from IAS succeeds and returns the answer
- **Connect Joule:** in a BTP destination use **OAuth2ClientCredentials** with the client ID, secret and IAS token URL
  - **Pitfall:** Joule **caches destination contents**. After changing the destination, delete and redeploy the capability (`joule delete`, `joule deploy`)

```mermaid
sequenceDiagram
  participant J as Joule
  participant I as IAS
  participant A as Agent (middleware)
  J->>I: client credentials
  I-->>J: JWT with scope
  J->>A: message/send + bearer token
  A->>A: check signature, issuer, audience, expiry, scope
  A-->>J: answer (or 401)
```

## 10.4 Build an agent from an intent with the CLI (SJ047)

*Source: SAP Developer tutorial, "Build a Supplier Disruption Response Agent on SAP S/4HANA", 40 min, 9 steps, created October 2026 (text and all 30 images read; four images are plain placeholder graphics and several terminal screenshots are too small to read).*

- **Two modes in Joule Studio:** **Web** (visual builder for developers and analysts) and **Local / CLI** (the `jl` command line plus a coding agent such as OpenCode, for developers)
- **Core idea: Intent-Based Development (IBD):** you describe the goal in plain language; the engine produces a **PRD**, a **specification** and an implementation, which you review and deploy
- **Scenario:** a supplier announces a factory fire; the agent finds at-risk **purchase orders and scheduling agreements** in S/4HANA Public Cloud, scores each **HIGH / MEDIUM / LOW**, and reports
  - Scoring uses **delivery proximity, open value and geographic overlap**
  - **Every claim is labelled** `[Confirmed Fact]` (from SAP), `[Assumption]` (thresholds) or `[Recommendation]`
- **Four milestones:** signal intake → SAP data retrieval → risk assessment → consolidated report
- **Targets:** at-risk POs found in under 15 minutes; full triage in under 30; 100% of claims labelled
- **MCP servers:** two read-only servers are generated from SAP OData specs with the MCP Builder, for purchase orders and scheduling agreements; a third source (preferred supplier list) is also allowed. Other APIs are **not registered on the tutorial tenant** and fail at deployment
- **Steps:**
  - **Set up:** VS Code, a new working folder, terminal; `jl --help`, `jl version`; **`jl login`** with the personal sign-in URL taken from Joule Studio → Settings → Develop → CLI authorization (a 401 means log in again)
  - **Initialise:** `jl init opencode` fetches the IBD skills into a skills folder and writes config files. **Do not edit the generated skills**; customise through the agent's own code
  - **Intent:** paste an intent prompt (role, system, supplier country, the two data sets, scoring factors and the labelling rule); answer the clarifying questions; IBD maps it to the **Source to Pay** reference architecture, checks fit and gaps, finds APIs, and gives an **intent fit score** (target at least 0.7). A low score usually means the system or APIs were not named. Adding "FastTrack." skips the questions
  - **Review three documents:** `intent.md`, the PRD, the specification; type "Continue with PRD", "Create specification", "Execute specification". If the spec lists an unregistered API, tell the coding agent to remove it
  - **Implementation (10–20 minutes):** a "code hunt" through the generated project: the model setting exposed by a decorator, milestone logging, risk-scoring thresholds read from environment variables (labelled assumptions), labelling functions, a thin `mcp_tools` wrapper that tests patch so they run offline, and generated tests
  - **Generated layout:** a solution manifest at the root; an asset folder for the agent (manifest, mock file, tests, app code, skills, tools, MCP provider) and one per MCP server (translation file and API spec)
  - **Deploy:** set an environment variable in the asset manifest to run on **mock data**, then ask the coding agent to deploy (about 1–2 minutes). Test through the web UI, the coding agent, or `jl a2a message`
  - **Run the scenario:** send the factory-fire message and tick off milestones M1–M4; use the **Tracing** tab for spans if a milestone is skipped
- **Guardrails in the PRD:** read-only SAP access, externally configurable thresholds, full provenance labels, and **human in the loop** (the agent assesses, the manager decides)
- **Variance warning:** every IBD run differs; judge by the checklists, not the screenshots
- **Prerequisites listed:** Joule Work and Joule Studio access, VS Code, the `jl` CLI, a compatible coding agent. No starter repository

```mermaid
flowchart LR
  A[Intent prompt] --> B[intent.md]
  B --> C[PRD]
  C --> D[Specification]
  D --> E[Generated agent plus MCP servers plus tests]
  E --> F[Deploy to managed runtime]
  F --> G[Test M1 to M4 with tracing]
```

## 10.5 The MCP concept page (SJ042)

- The SAP concept page "MCP Server Integration" is an **index**: it lists related tutorials, docs, videos, samples and prerequisite concepts, with no teaching text of its own
- Its two tutorials are already in this book (Chapter 8's sub-agent tutorial and a Devtoberfest session page not read)
- Handled as **no teaching content**; nothing new was added from it

## 10.6 Added by Claude, not from the sources

*My own reasoning; the sources do not say it.*

- **Check the date of every constraint:** the 60-second limit and "no A2A in Agent Builder" are time-bound; SJ045 itself was partly updated in June 2026
- **Pick by user experience first:** if a user may wait minutes, streaming (option 3) is the only one that shows progress
- **Do not put secrets in code or notes:** use destinations, as every source here does
- **Labelling outputs by provenance** is a good habit for any agent that mixes data and assumptions, not only this scenario

## 10.7 Interview corner

**What interviewers listen for:** you know the two integration paths, the time limits and how the agent is secured.

<details class="qa">
<summary>🟢 How does Joule call a pro-code agent?</summary>

- As an A2A client: a scenario with a dialog function of type `agent-request` points to the agent's A2A endpoint
</details>

<details class="qa">
<summary>🟡 Your agent needs 3 minutes. What are your options?</summary>

- Async A2A with push notifications (needs the same IAS), async REST with a Build Process Automation polling loop (up to about 5 minutes), or an A2A client proxy with streaming
</details>

<details class="qa">
<summary>🟡 What does the IAS middleware verify, and what stays public?</summary>

- Signature, issuer, audience, expiry and scope; the `/.well-known/` agent card stays public
</details>

<details class="qa">
<summary>🔴 You updated the destination but Joule still fails. Why?</summary>

- Joule caches destination contents; delete and redeploy the capability
</details>

<details class="qa">
<summary>🔴 App-to-app or user identity: which does client credentials give you?</summary>

- App identity only. To act as the user in a backend, you need principal propagation
</details>

**🧩 Design question:** a research agent takes 4 minutes and the business wants live progress. Choose a path, name the pieces, and say how you secure it.

## 10.8 Discovery Center missions (links, not read)

- [Build custom Joule skills for SAP and non-SAP systems](https://discovery-center.cloud.sap/missiondetail/4643/)

## 10.9 Cheat sheet

| Topic | Remember |
|---|---|
| Low-code agent | Joule scenario and dialog function created on deploy; runs on AI Core |
| Pro-code agent | A2A server; manual scenario with `agent-request` |
| Sync limit | about 60 s |
| Long jobs | async A2A (same IAS), async REST (about 5 min), or streaming proxy |
| Securing | IAS client credentials, JWT checks, agent card public |
| Destination change | Redeploy the capability (cache) |
| CLI flow | `jl login`, `jl init`, intent, PRD, spec, execute, deploy |
| Labels | Confirmed Fact, Assumption, Recommendation |

## Screenshots and figures from the sources

*Images saved from the source pages, in the order they appear there.*

### Images: Tutorial: Supplier disruption response agent

*Source: [Tutorial: Supplier disruption response agent](https://developers.sap.com/tutorials/build-a-supplier-disruption-response-agent-on-sap)*

![Supplier disruption agent tutorial, figure 1](images/ch10-s5-supplierdisruption-01.webp)

![Supplier disruption agent tutorial, figure 2](images/ch10-s5-supplierdisruption-02.webp)

![Supplier disruption agent tutorial, figure 3](images/ch10-s5-supplierdisruption-03.webp)

![Supplier disruption agent tutorial, figure 4](images/ch10-s5-supplierdisruption-04.webp)

![Supplier disruption agent tutorial, figure 5](images/ch10-s5-supplierdisruption-05.webp)

![Supplier disruption agent tutorial, figure 6](images/ch10-s5-supplierdisruption-06.webp)

![Supplier disruption agent tutorial, figure 7](images/ch10-s5-supplierdisruption-07.webp)

![Supplier disruption agent tutorial, figure 8](images/ch10-s5-supplierdisruption-08.webp)

![Supplier disruption agent tutorial, figure 9](images/ch10-s5-supplierdisruption-09.webp)

![Supplier disruption agent tutorial, figure 10](images/ch10-s5-supplierdisruption-10.webp)

![Supplier disruption agent tutorial, figure 11](images/ch10-s5-supplierdisruption-11.webp)

![Supplier disruption agent tutorial, figure 12](images/ch10-s5-supplierdisruption-12.webp)

![Supplier disruption agent tutorial, figure 13](images/ch10-s5-supplierdisruption-13.webp)

![Supplier disruption agent tutorial, figure 14](images/ch10-s5-supplierdisruption-14.webp)

![Supplier disruption agent tutorial, figure 15](images/ch10-s5-supplierdisruption-15.webp)

![Supplier disruption agent tutorial, figure 16](images/ch10-s5-supplierdisruption-16.webp)

![Supplier disruption agent tutorial, figure 17](images/ch10-s5-supplierdisruption-17.webp)

![Supplier disruption agent tutorial, figure 18](images/ch10-s5-supplierdisruption-18.webp)

![Supplier disruption agent tutorial, figure 19](images/ch10-s5-supplierdisruption-19.webp)

![Supplier disruption agent tutorial, figure 20](images/ch10-s5-supplierdisruption-20.webp)

![Supplier disruption agent tutorial, figure 21](images/ch10-s5-supplierdisruption-21.webp)

![Supplier disruption agent tutorial, figure 22](images/ch10-s5-supplierdisruption-22.webp)

![Supplier disruption agent tutorial, figure 23](images/ch10-s5-supplierdisruption-23.webp)

![Supplier disruption agent tutorial, figure 24](images/ch10-s5-supplierdisruption-24.webp)

![Supplier disruption agent tutorial, figure 25](images/ch10-s5-supplierdisruption-25.webp)

![Supplier disruption agent tutorial, figure 26](images/ch10-s5-supplierdisruption-26.webp)

## Recap

- Low-code agents are wired to Joule for you; pro-code agents speak A2A
- A 60-second sync limit shapes the design; three options get around it
- Secure the endpoint with IAS tokens; keep the discovery card public
- The `jl` CLI turns an intent into a reviewed, tested, deployed agent

## Practice

1. Draw how Joule reaches a low-code agent and a pro-code agent.
2. Fill the three-option table from memory.
3. Write the five token checks the middleware makes.
4. Write an intent prompt for a different scenario, naming the system, data and rules.

## How this chapter was checked

- **Read fully:** the text and images of SJ044, SJ045, SJ046 and SJ047; SJ042 (an index page)
- **Not read:** the linked blogs (A2A async push, principal propagation, the first A2A blog, the IAS basics blog), the Joule development guide, sample repositories, the demo video, quiz-like items, the "related" lists, Discovery Center missions
- **Not run:** nothing was built, deployed or called
- **Small text:** four images in SJ047 are plain placeholder graphics, and some terminal screenshots were too small to read
- **Dated points:** SJ045 describes March 2026 limits with a June 2026 update; the Architecture Center page lists features not yet generally available

## Sources and further reading

- SAP Architecture Center, *Integrating AI Agents with Joule (Outbound A2A)* (read): https://architecture.learning.sap.com/docs/ref-arch/ae6821
- SAP Community blog, *Integrating Joule with Code-based Agents: Three Paths Forward* (read): https://community.sap.com/t5/technology-blog-posts-by-sap/integrating-joule-with-code-based-agents-three-paths-forward/ba-p/14370520
- SAP Community blog, *Joule A2A: Secure Code Based Agents with IAS* (read): https://community.sap.com/t5/technology-blog-posts-by-sap/joule-a2a-secure-code-based-agents-with-ias/ba-p/14367792
- SAP Developer tutorial, *Build a Supplier Disruption Response Agent on SAP S/4HANA* (read): https://developers.sap.com/tutorials/build-a-supplier-disruption-response-agent-on-sap
- SAP Developer concept page, *MCP Server Integration* (index, read): https://developers.sap.com/concepts/mcp-server-integration/
- Discovery Center missions: see 10.8

---

*Previous: [Chapter 9: An MCP server for mobile development](09-mdk-mcp.md)*

*Next: [Chapter 11: Joule in SAP Build Code, for ABAP developers, and in Joule Work](11-joule-build-code-and-developers.md)*
