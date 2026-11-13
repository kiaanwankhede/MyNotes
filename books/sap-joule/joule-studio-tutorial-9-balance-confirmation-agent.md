# Joule Studio tutorial 9: automating balance confirmation workflows

*A Financial Accounting scenario — and a clean example of the "autonomous reads, human-approved exceptions" boundary that shows up across this entire tutorial family.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the same Joule Studio web flow as Tutorials 7–8, applied to a Financial Accounting process — and a clear split between what the agent does autonomously versus what it routes to a human
> - **You will build:** an "Automated Processing of Balance Confirmations" agent that retrieves business-partner and GL open-item data from S/4HANA, generates compliant confirmation letters, and routes disputes or high-balance cases to human review
> - **Level:** beginner · **Time:** about 22 minutes
> - **Builds on:** [Joule Studio tutorial 8: AI Sales Assistant](joule-studio-tutorial-8-ai-sales-assistant-agent.md). **Leads to:** [Joule Studio tutorial 10: automating budget variance management](joule-studio-tutorial-10-budget-variance-agent.md)

> [!WARNING]
> Pre-release Joule Studio — screens and exact flow may differ from general availability.

**After this tutorial you can:**

- State precisely which 2 OData APIs this agent integrates with, and why it needs exactly 2 MCP servers, not more
- Read a generated milestone list (M1–M5) and explain what each one actually gates
- Name the specific conditions that route a case to human review instead of fully-autonomous letter dispatch

## 1. Three request types, five pain points

| Request type | What it means |
|---|---|
| Verification | Confirm a single balance on request |
| Balance list | Produce a list of balances across a set of partners |
| Exception-only | Surface only discrepancies, not routine confirmations |

Pain points driving this agent: constant tool-switching, slow manual lookups, inconsistent letter wording, a fragmented audit trail, and manual partner follow-up load.

## 2. Define the intent

![Create a new agent dialog](images/sj201-01-create-new-agent-dialog.png)

![Agent details entered: Name "Automated Processing of Balance Confirmations," Intent Statement describing processing balance confirmations and generating compliant letters, Quick Create checked](images/sj201-02-enter-agent-details.png)

Even with Quick Create checked, Business Goals & Success Criteria confirmation still runs:

![Business Goals clarifying question in chat](images/sj201-03-business-goals-clarifying-questions.png)

## 3. Review the intent

![Intent Summary tab](images/sj201-04-intent-summary.png)
![Recommended Solution: Python agent with a reconciliation engine kept separate from the LLM narration layer](images/sj201-05-recommended-solution.png)

> [!NOTE]
> The recommended solution explicitly keeps the **reconciliation logic** (deterministic) separate from the **LLM narration layer** (the part that writes the actual letter text) — the same split seen across every agent in this tutorial family: deterministic code decides *what happened*, the LLM only explains it in writing.

## 4. The PRD

![PRD requirements, low-code view](images/sj201-06-prd-requirements.png)

The PRD's Solution Architecture section is the one worth reading closely — it names exactly 2 integration points, not more:

![Solution Architecture: Architecture Overview, Key Components (Balance Confirmation Agent, S/4HANA MCP Tools wrapping Business Partner + GL Line Items APIs, Letter Generation Skill, Audit Logger), Integration Points (Business Partner API, GL Account Line Items API)](images/sj201-07-solution-architecture.png)

- 4 autonomous actions, including read-only S/4HANA data fetch
- 2 human-review triggers: a discrepancy over a configured threshold, or a dispute indicator on the account

## 5. Specification

![Specification inspection: file tree with core agent folder plus MCP server folders](images/sj201-08-inspect-specification.png)

## 6. Generate the solution

![Generated Solution Artifacts panel](images/sj201-09-generated-solution-artifacts.png)
![Agent configuration, low-code view](images/sj201-10-agent-configuration.png)
![Evaluation section](images/sj201-11-evaluation.png)
![Pro-code file tree view](images/sj201-12-code-overview.png)

Exactly **2 MCP servers**, confirmed directly in the generated solution — not 3:

![MCP Servers panel: api_business_partner (MCP server for the api_business_partner service) and cds_api_glaccountlineitem (MCP server for the cds_api_glaccountlineitem service); right panel confirms "Balance Confirmation Agent — Implementation Complete," listing the Python AI Agent, Letter-Generation Runtime Skill, Business Partner MCP Server, and GL Account Line Items MCP Server as the 4 built components](images/sj201-13-mcp-servers-review.png)

The same panel gives the real test numbers and milestone breakdown:

- **Test results: 135/135 passed, 83% coverage**
- **M1** — Classifies incoming balance confirmation requests
- **M2** — Retrieves live S/4HANA business partner + open item data via MCP tools
- **M3** — Generates legally compliant response letters using the `letter-generation` skill
- **M4** — Routes disputed items, unidentifiable partners, or high-balance cases to human review
- **M5** — Full audit trail via structured logs + OpenTelemetry spans for all 5 milestones

> [!TIP]
> This milestone list is a concrete, inspectable answer to "what does this agent actually do, step by step" — more useful than the PRD's prose summary, since each milestone maps directly to a logged, auditable event.

## 7. Validate with tests

![Testing Overview results](images/sj201-14-tests-overview.png)
![Preview chat test with the agent](images/sj201-15-test-agent-chat.png)
![Local test results detail](images/sj201-16-local-test-results.png)

## 8. Deploy

![Deploy confirmation dialog](images/sj201-17-deploy-solution.png)

Production flow once live: Ingestion → Classification → Data retrieval (both MCP servers) → Reconciliation → Letter generation → Routing (auto-dispatch vs. human review) → Audit logging.

## 9. Added by Claude, not from the sources

- The "deterministic reconciliation vs. LLM narration" framing in section 3 restates the tutorial's own Recommended Solution text, with this book's emphasis on it being a recurring pattern across the family.
- A real correction made during review: an earlier read of this tutorial's content (via a background research pass) claimed 3 MCP servers; opening the actual MCP Servers screenshot directly showed exactly 2 (Business Partner, GL Account Line Items) — the architecture text confirms this. The chapter reflects what the screenshot actually shows, not the initial research summary.
- Not run: the agent described was built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 10. Interview corner

**What interviewers listen for:** you give the exact MCP server count (2) and name both, rather than a rounded-up guess, and you can state the 2 specific human-review triggers rather than a vague "exceptions get escalated."

<details class="qa"><summary>1. How many MCP servers does this agent use, and what does each wrap?</summary>

- 2 — one wrapping the Business Partner API, one wrapping the GL Account Line Items API

</details>

<details class="qa"><summary>2. What are the 2 specific conditions that route a balance confirmation case to human review instead of automatic dispatch?</summary>

- A discrepancy over a configured threshold, or a dispute indicator present on the account

</details>

<details class="qa"><summary>3. Why does the architecture keep reconciliation logic separate from the LLM narration layer?</summary>

- So the actual financial determination (does the balance match, is there a discrepancy) is deterministic and auditable code, while the LLM's role is limited to composing the letter text explaining that determination — not deciding the financial facts itself

</details>

> [!TIP]
> **🧩 Design question**
> *"An auditor asks how they can trust a letter this agent sent wasn't based on a hallucinated balance."* Talk about: the reconciliation engine being deterministic code reading live S/4HANA data via the 2 MCP servers (not LLM-generated), the LLM's role being strictly to narrate an already-computed result, and the M5 audit trail (structured logs + OpenTelemetry spans) giving a traceable record of exactly what data was retrieved and what determination was made before any letter was drafted.

## Cheat sheet

| Thing | Detail |
|---|---|
| MCP servers | 2 — Business Partner API, GL Account Line Items API |
| Human-review triggers | Discrepancy over threshold, or dispute indicator present |
| Test results | 135/135 passed, 83% coverage |
| Milestones | M1 Classify → M2 Retrieve data → M3 Generate letter → M4 Route to human if needed → M5 Audit trail |

## Recap

- This agent integrates with exactly 2 S/4HANA OData APIs (Business Partner, GL Account Line Items) via 2 MCP servers — not 3, a correction made after directly verifying the screenshot rather than trusting an initial summary
- The architecture deliberately keeps deterministic reconciliation separate from LLM-generated letter narration
- 2 specific conditions route a case to human review: an over-threshold discrepancy, or a dispute indicator
- A 5-milestone structured log (M1–M5) gives a concrete, auditable trace of what the agent did on every run
- 135/135 tests passed at 83% coverage before this agent was considered ready

## Practice

1. Without looking back, name the 2 MCP servers this agent uses and what each wraps
2. List the 2 specific conditions that send a case to human review
3. Explain in one sentence why reconciliation logic and letter narration are kept as separate layers

## How this chapter was checked

- The full tutorial "Automate Balance Confirmation Workflows in Financial Accounting with a Custom Joule Agent" (developers.sap.com, Beginner, 30 min, 9 steps) was read in full, 13 Nov 2026.
- 17 images were found and downloaded (4 further images were commenter/author avatars, correctly excluded), all 17 used here; each was opened and visually verified against its caption before being written into this chapter — this caught and corrected a real discrepancy (an initial research pass claimed 3 MCP servers; the actual screenshot shows 2, confirmed by the architecture text too).
- Nothing in this chapter was independently re-executed — the agent described was built and tested by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Automate Balance Confirmation Workflows in Financial Accounting with a Custom Joule Agent* — https://developers.sap.com/tutorials/balance-confirmation-agent (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 8: AI Sales Assistant agent](joule-studio-tutorial-8-ai-sales-assistant-agent.md) · Next: [Joule Studio tutorial 10: automating budget variance management](joule-studio-tutorial-10-budget-variance-agent.md)
