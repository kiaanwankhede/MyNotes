# Joule Studio tutorial 6: building an agent from the command line (Local/CLI flow)

*Every tutorial so far used Joule Studio's web UI. This one builds the same kind of agent entirely from VS Code and a terminal — the `jl` CLI plus a coding agent, not a browser.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the Joule Studio Local/CLI flow — `jl` CLI setup and login, initializing a project with a coding agent (OpenCode), and the same Intent → PRD → Specification → Solution lifecycle driven entirely through chat with a local coding agent instead of a web UI
> - **You will build:** a Supplier Disruption Response Agent for SAP S/4HANA Public Cloud — given a real supplier production-halt scenario, it retrieves at-risk purchase orders and scheduling agreements, scores them HIGH/MEDIUM/LOW, and produces a risk-scored, fully labeled assessment report
> - **Level:** intermediate · **Time:** about 25 minutes
> - **Builds on:** [Joule Studio and the agent development lifecycle](02-joule-studio-lifecycle.md) (the 6-stage lifecycle this tutorial walks through concretely) and [n8n workflows in Joule Studio](04-n8n-workflows.md). **Leads to:** [Joule Studio tutorial 7: building a supplier performance agent](joule-studio-tutorial-7-supplier-performance-agent.md)

**After this tutorial you can:**

- Set up and authenticate the `jl` CLI from VS Code, and initialize a Joule Studio project for a specific coding agent
- Explain what "Intent-Based Development" (IBD) means concretely — the same clarifying-question pattern from the web UI, now happening in a terminal chat
- Recognize the labeling discipline this agent enforces on its own output: every claim marked `[Confirmed Fact]`, `[Assumption]`, or `[Recommendation]`
- Read a generated agent's file tree and know what each piece (MCP server, `asset.yaml`, milestone logging) is for

## 1. The CLI flow, end to end

```mermaid
flowchart LR
    S["Set up VS Code\n+ jl CLI + login"] --> I["jl init\n(pick coding agent)"]
    I --> IN["Enter intent\n(IBD clarifying Q&A)"]
    IN --> P["Review intent.md\n→ PRD → Specification"]
    P --> G["Generate & review code\n(Code Hunt)"]
    G --> D["Deploy & test\n(jl a2a message)"]
```

## 2. Set up the environment

Open an empty project folder in VS Code:

![VS Code opened with no folder loaded](images/sj205-01-vscode-open-no-folder.png)
![Creating a new folder on the Desktop for the project](images/sj205-02-new-folder-dialog-desktop.png)
![The empty project folder open in VS Code's Explorer](images/sj205-03-empty-project-folder-explorer.png)

Open a terminal inside that folder and confirm the `jl` CLI is available:

![Terminal opened inside the project folder](images/sj205-04-terminal-open-project-folder.png)

```console
jl --help
```

![Output of `jl --help`: Solution Management CLI, listing asset types (agent, agent-extension, cap-app, domain-model-extension, mcp-server) and commands (init, login, logout, build, deploy, status, verify, help)](images/sj205-05-jl-help-command-output.png)

```console
jl version
```

![Output of `jl version`](images/sj205-06-jl-version-output.png)

## 3. Log in from Joule Studio's Develop tab

The CLI authenticates against your Joule Studio account, not a separate credential:

![Joule Studio home: "What can I help move forward today?"](images/sj205-07-joule-studio-home.png)
![User menu open, Settings option visible](images/sj205-08-user-menu-settings.png)

Settings → **Develop** tab shows the **CLI Authentication** sign-in URL to copy:

![Develop tab: CLI Authentication setup, "In order to connect with the Command Line Interface (CLI), please copy/paste the following URL"](images/sj205-09-develop-tab-signin-url.png)

```console
jl login '<sign-in URL>'
```

![Terminal confirming jl login completed, Solution Management CLI help text visible with login now authenticated](images/sj205-10-jl-login-completed.png)

## 4. Initialize the project and launch the coding agent

```console
jl init opencode
```

![jl init output: skills tree being initialized, OpenCode MCP config initialized](images/sj205-11-jl-init-complete-skills-tree.png)

```console
opencode
```

![OpenCode launched inside the project folder](images/sj205-12-opencode-launched.png)
![OpenCode's own startup screen: "Ask anything... What is the tech stack of this project?" with Build/auto mode and Claude Opus 4.6 Anthropic as the active model](images/sj205-13-opencode-auto-approve.png)

> [!NOTE]
> The coding agent driving this flow (OpenCode here, shown running **Claude Opus 4.6**) is a separate, swappable piece from Joule Studio itself — `jl init` supports other compatible coding agents too, not just OpenCode.

## 5. Enter the intent, in chat

The real intent prompt given to the agent, verbatim:

> *"I am a procurement manager at a manufacturing company using SAP S/4HANA Cloud. Our key supplier in Taiwan has just announced that a production halt due to a factory fire this morning. I need an agent that: 1. Retrieves all open purchase orders and scheduling agreements linked to affected suppliers in SAP S/4HANA. 2. Scores each item HIGH / MEDIUM / LOW based on delivery proximity, open value, and geographic overlap. Rules the agent must follow: — Every output must be labeled [Confirmed Fact], [Assumption], or [Recommendation]. I'll start by analyzing your intent to build this supplier disruption assessment agent. Let me kick off the intent analysis skill first."*

![The intent prompt entered in the terminal chat, agent announcing it will run the "intent-analysis" skill](images/sj205-14-ibd-skill-analysis-running.png)

The agent asks clarifying questions one at a time — just like the web UI's IBD flow, but through chat:

![Agent response after analyzing available SAP S/4HANA Cloud Public Edition APIs for Purchase Orders, Scheduling Agreements, Business Partners, Supplier Lists, Inbound Deliveries, Locations — noting some APIs (CE_SUPPLIERLIST_0002, API_BUSINESS_PARTNER) are NOT registered on this tenant — then asking who the primary users are besides the procurement manager](images/sj205-15-ibd-success-metrics-question.png)

![A second clarifying question: target users, supplier scope, risk scoring rules, operation mode](images/sj205-16-ibd-review-answers-prompt.png)

> [!TIP]
> One real, API-availability-driven gap surfaced mid-conversation: the agent explicitly flagged that `CE_SUPPLIERLIST_0002` and `API_BUSINESS_PARTNER` were **not registered on this tenant**, and said the agent would need MCP translation files generated from the API specs instead of relying on pre-built MCP servers. This is a concrete example of the agent reasoning about its own backend constraints *during* intent clarification, not after.

![Answers confirmed: Target users Procurement + Supply Chain, Supplier scope "User specifies at runtime," Risk scoring rules "Use reasonable defaults," Operation mode "On-demand + recommendations"](images/sj205-17-ibd-confirm-goals-table.png)

Business Goals & Success Criteria, mandatory for every AI Agent solution:

![Agent asking for Business Goals — "Faster time-to-assessment, Minimize revenue impact, Better decision quality"](images/sj205-18-ibd-confirm-goals-details.png)
![Agent asking for concrete metric targets: Metric targets, Revenue impact target, Decision quality target](images/sj205-19-intent-md-open-in-vscode.png)

The answers given: *"2 days → 30 min"* (time-to-assessment), *"Reduce by 20%+"* (revenue impact), *"100% coverage of at-risk POs"* (decision quality).

## 6. Review the generated intent.md

Once confirmed, the agent writes `intent.md` to the project and opens it:

![intent.md open in VS Code: Supplier Disruption Risk Assessment Agent — Business Challenge, Business Goals & Success Criteria table, Key Milestones](images/sj205-20-intent-md-terminal-review.png)

![The terminal confirming the intent analysis is complete, summarizing what was captured](images/sj205-21-intent-reviewed-continue-with-prd.png)

## 7. PRD, specification, and API discovery

Typed into chat: `Continue with PRD`

![intent.md's full content reviewed in the terminal — Business Architecture, Process Hierarchy, Fit Gap Analysis table with Requirement/Standard asset(s) found/MCP Server ID/MCP Server Version columns](images/sj205-22-prd-overview.png)

The agent confirms the solution shape before writing the PRD: *"Solution: Pro-code Python AI agent... Core capability: Retrieve open POs/scheduling agreements... APIs identified: API_PURCHASEORDER..., API_SCHED_AGRMT_PROCESS_SRV, ... Would you like to proceed to Product Requirements Document (PRD) generation?"*

![The PRD overview: Title, Date, Owner, Solution Category "AI Agent," Purpose & Value Proposition, Business Need, Expected Impact](images/sj205-23-prd-reviewed-create-spec-command.png)

Typed into chat: `Create specification`

![Specification overview file tree: guidelines.md, api-discovery-results.md, specification.md, with a checklist of setup/asset-implementation items to complete](images/sj205-24-specification-overview.png)

The agent runs **API discovery** before writing the spec — confirming exactly which OData services it will actually call:

![Terminal output: "API integrations: 7 OData APIs — all specs downloaded via EDMX, ready for MCP translation file generation," "Instrumentation: 5 milestones (M1-M5) with structured logging and OpenTelemetry spans"](images/sj205-25-spec-api-discovery-execute-command.png)

## 8. The finished project structure

```console
execute specification/supplier-disruption-agent/specification.md
```

![Final confirmation panel: Agent Wiring (7 MCP server requires entries in agent's asset.yaml), Unit Tests (14 tests: milestone tracking, system prompt, agent creation, runtime skill), Integration Test (4 tests), mcp-mock.json "Background generation in progress" — plus the full generated solution structure: solution-architecture (1 agent + 7 servers), specification/ (specs + 7 EDMX API specs + 7 MCP translations), assets/supplier-disruption-agent/ (asset.yaml, agent.py, agent_executor.py, instrumentation.py, main.py, tests/, 7 mcp-*-server/ folders)](images/sj205-26-spec-complete-file-structure.png)

> [!NOTE]
> This final structure is the concrete answer to "what does a generated Joule agent actually look like on disk" — one `agent.py` plus `agent_executor.py` and `instrumentation.py`, a dedicated MCP server folder per integrated API (7 here, matching the "one MCP server per integration point" pattern already documented in [the lifecycle chapter](02-joule-studio-lifecycle.md)), and both unit and integration test suites generated alongside the implementation, not bolted on afterward.

## 9. Added by Claude, not from the sources

- The "CLI flow, end to end" Mermaid diagram in section 1 is this book's visual summary of the tutorial's own narrative — the steps themselves are the source's.
- The cross-reference to "one MCP server per integration point" in section 8 connects this tutorial's concrete file tree back to a pattern this book already documented from other sources — the observation is this book's synthesis.
- Not run: the agent described was built by the tutorial's own author via a live chat session; nothing was independently re-executed for this book, and the exact coding-agent conversation (clarifying-question answers, generated file contents) will vary between runs since it's LLM-driven.

## 10. Interview corner

**What interviewers listen for:** you can name the CLI's actual commands (`jl init`, `jl login`, `jl a2a message`) without guessing, and you understand that IBD's clarifying-question flow is the same mechanism whether it's happening in a web UI or a terminal chat.

<details class="qa"><summary>1. What's the practical difference between building an agent via Joule Studio's web UI versus the Local/CLI flow?</summary>

- The CLI flow runs entirely in VS Code and a terminal, using the `jl` CLI plus a coding agent (e.g. OpenCode) to drive the same Intent → PRD → Specification → Solution lifecycle through chat, instead of clicking through a web interface
- *Stronger answer:* the underlying lifecycle and artifacts (intent.md, PRD, specification, generated Python agent with MCP servers) are the same either way — CLI is a different interface onto the same process, not a different process

</details>

<details class="qa"><summary>2. During intent clarification, the agent flagged that two APIs weren't registered on the tenant. What did it do about that, concretely?</summary>

- It noted the agent would need MCP translation files generated directly from the API specs, rather than relying on pre-built MCP servers for those two APIs

</details>

<details class="qa"><summary>3. What are the three labels every output of this agent is required to carry, and why does that matter for a risk-assessment tool?</summary>

- `[Confirmed Fact]`, `[Assumption]`, `[Recommendation]` — this was a hard requirement stated in the original intent, not something Joule Studio added on its own
- *Stronger answer:* for a disruption-response tool feeding real procurement decisions, conflating a confirmed PO status with an assumption or a recommendation would be a real governance risk — the labeling discipline is itself a guardrail, enforced at the output layer

</details>

> [!TIP]
> **🧩 Design question**
> *"A developer wants to build a Joule agent but prefers working in their own editor with a coding agent they already use daily, rather than a web UI."* Talk about: the Local/CLI flow as the answer (`jl init` supports multiple coding agents, not just OpenCode), the lifecycle staying identical (Intent/PRD/Specification/Solution) so skills transfer between the two interfaces, and why `jl login` against the Develop tab's sign-in URL is still required even in a fully local workflow — the CLI is local, the authentication and the generated solution's lifecycle management are not.

## Cheat sheet

| Command | Does |
|---|---|
| `jl --help` | Lists available asset types and commands |
| `jl version` | Confirms CLI version |
| `jl login '<url>'` | Authenticates the CLI against your Joule Studio account (URL from Settings → Develop) |
| `jl init opencode` | Initializes a project for a specific coding agent |
| `jl a2a message "..."` | Sends a test message to a deployed agent over A2A |

## Recap

- The Local/CLI flow runs Joule Studio's same Intent → PRD → Specification → Solution lifecycle through `jl` plus a coding agent in VS Code, not a web UI
- `jl login` ties the CLI to your Joule Studio account via a sign-in URL from the Develop tab — login is still centralized even though the build itself is local
- The agent surfaced a real backend constraint (2 unregistered APIs) during intent clarification and adjusted its plan accordingly, rather than discovering it later
- The final generated structure: one agent implementation plus one MCP server folder per integrated API (7 here), with both unit and integration tests generated alongside

## Practice

1. Without looking back, list the 5 `jl` commands covered in this tutorial and what each does
2. Explain in one sentence why the agent needed to generate MCP translation files for 2 of its 7 APIs instead of using pre-built MCP servers
3. Name the three required output labels this agent's intent mandated, and why they matter

## How this chapter was checked

- The full tutorial "Build a Supplier Disruption Response Agent on SAP S/4HANA" (developers.sap.com, Intermediate, 40 min, 9 steps) was read in full, 13 Nov 2026.
- 26 images were found and downloaded, all used here; each was opened and visually verified against its caption before being written into this chapter, including the final file-structure screenshot confirming the coding-agent model (Claude Opus 4.6) and full generated solution tree.
- Nothing in this chapter was independently re-executed — the agent, its generated code, and the chat conversation are the tutorial author's own live session; LLM-driven conversations like this one will vary between runs.

## Sources and further reading

- SAP Developers, *Build a Supplier Disruption Response Agent on SAP S/4HANA* — https://developers.sap.com/tutorials/build-a-supplier-disruption-response-agent-on-sap (read in full 13 Nov 2026)

Previous: [n8n workflows in Joule Studio](04-n8n-workflows.md) · Next: [Joule Studio tutorial 7: building a supplier performance agent](joule-studio-tutorial-7-supplier-performance-agent.md)
