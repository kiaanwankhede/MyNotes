# Joule Studio tutorial 8: building an AI Sales Assistant agent

*Same 9-stage flow as Tutorial 7, a different business problem — and the one place in this pair where Joule Studio has to generate its own API translation layer from scratch.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the same Joule Studio web flow as Tutorial 7, this time watching it handle APIs with **no pre-built MCP servers available**, generating translation files directly from API specs instead
> - **You will build:** a Discount Strategy Suggestion Agent for sales reps, correlating SAP S/4HANA order history and margin data with SAP Sales Cloud opportunity/pipeline data into a structured discount recommendation
> - **Level:** beginner · **Time:** about 18 minutes
> - **Builds on:** [Joule Studio tutorial 7: Supplier Performance Assistant](joule-studio-tutorial-7-supplier-performance-agent.md) (identical flow, different scenario). **Leads to:** [Joule Studio tutorial 9: automating balance confirmation workflows](joule-studio-tutorial-9-balance-confirmation-agent.md)

> [!WARNING]
> This tutorial also runs on a pre-release version of Joule Studio — screens and exact flow may differ from general availability.

**After this tutorial you can:**

- Recognize when Joule Studio has to generate API translation files from scratch instead of reusing pre-built MCP servers, and why that happens
- Read a real risk guardrail tied to a numeric threshold (margin floor) rather than a vague policy statement
- Name the specific MCP server tool count and what a 65-tool count on one server actually implies

## 1. What's different from Tutorial 7

```mermaid
flowchart LR
    A["Signal APIs\n(S/4HANA + Sales Cloud)"] --> B{"Pre-built MCP\nserver exists?"}
    B -->|"Yes (Tutorial 7)"| C["Reuse existing server"]
    B -->|"No (this tutorial)"| D["Generate MCP translation\nfiles from API specs directly"]
```

## 2. Create the solution and define the intent

![Joule Studio's "Create a new solution" screen, same 4-tile layout as Tutorial 7](images/sj207-01-create-new-solution.png)

![Create Agent dialog: Name "AI Sales Assistant," Intent Statement "AI-powered discount strategy suggestion agent that analyzes customer orders, pipeline and margin targets from SAP Sales Cloud and SAP S/4HANA Cloud, providing sales reps with contextualized discount recommendations," Quick Create checked](images/sj207-02-create-agent-dialog.png)

![Business Goals question in chat: "Improve margins by 2%"](images/sj207-03-business-goals-question-chat.png)

## 3. Review the intent

![Intent Summary: "Discount Strategy Suggestion Agent" — Business challenge, Business Goals & Success Criteria table, Key Milestones: 1. Data connectivity established, 2. Context assembly, 3. Discount recommendation generated](images/sj207-04-intent-summary.png)

This intent has **5 milestones**, one more than Tutorial 7's agent — the extra two (Rep interaction, Outcome tracked) reflect the conversational, iterative nature of a discount negotiation versus a one-shot risk score:

![Recommendations panel: Executive Summary — "Python AI agent reasoning across Sales Cloud and S/4HANA data to recommend contextualized discounts" — Recommended Solution, Intent fit](images/sj207-05-recommendations-intent-fit.png)

## 4. The PRD

![PRD: Title "AI-Powered Discount Suggestion Agent," Product Purpose & Value Proposition, Elevator Pitch — "Sales reps waste time manually cross-referencing order history and margin data... this agent gives them a ready-to-use recommendation in seconds"](images/sj207-06-prd-header-value-proposition.png)

![Expected Value, Product Objectives, Business Metrics table — "Improve margins by 2%," "Reduce time spent on pricing decisions"](images/sj207-07-expected-value-objectives-metrics.png)

> [!NOTE]
> A real guardrail from this PRD, concrete rather than vague: a **HIGH RISK flag triggers when projected margin drops below a configured floor** — a numeric threshold baked into the agent's logic, not a policy statement left to the LLM's judgment.

## 5. Specification — where this tutorial diverges from Tutorial 7

![Specification overview: Guidelines, Solution Setup checklist — "Create asset directory," "Invoke 'skill-assets/specification'"](images/sj207-08-specification-overview.png)

The specification phase explicitly notes: **no pre-built MCP servers exist for the Sales Cloud/S/4HANA APIs this agent needs** — Joule generates the translation files directly from the APIs' own specs instead of wiring up an existing server.

## 6. Generate the solution

![Agent LLM Configuration: Select Model, Creativity (Temperature) slider](images/sj207-09-agent-llm-configuration.png)

![Generated agent.py code, imports and LangGraph setup visible in the file explorer](images/sj207-10-agent-code-agentpy.png)

The generated MCP server, confirmed directly: **65 tools** on a single server, internal name `discount-strategy-agent`:

![sap-s4-sales-order-simulation-srv-mcp-server detail: Overview, Name, Description "MCP server for the a_salesorderprocess.cds service," Server Content Tools (65), plus a right-hand chat panel showing live generation commentary ("I'll select only the most relevant tools for discount strategy... read-only, order/opportunity/simulation focused")](images/sj207-11-mcp-server-tools.png)

> [!TIP]
> 65 tools on one server is a lot — and the live generation commentary captured in this screenshot shows Joule actively **narrowing** that surface down to only the relevant, read-only subset for this specific agent, rather than exposing all 65 to the LLM. The tool count reflects what the underlying OData service *offers*, not what the agent actually *uses*.

![Evaluation tab: "No evaluations were generated," Generate scenarios button](images/sj207-12-evaluation-scenarios.png)

## 7. Validate with tests

![Testing Overview: 124 Total Tests, 124 Passed, 0 Failed, 100% Score](images/sj207-13-testing-overview.png)

Canonical test prompt used: *"Recommend discount strategy for customer Best Run SAP Company."*

![Try Your Agent preview, interacting with the agent before deployment — "Everything is in place, here's a complete summary of what was built," Discount Strategy Suggestion Agent Complete, Traces panel visible](images/sj207-14-try-your-agent-preview.png)

## 8. Added by Claude, not from the sources

- The "what's different from Tutorial 7" Mermaid diagram in section 1 is this book's own framing of the no-pre-built-server detail the tutorial states directly — the underlying fact is the source's.
- The observation in section 6 about the 65-tool count being the *offered* surface versus the *used* subset is this book's interpretation of the generation commentary visible in the screenshot, not a claim the tutorial makes explicitly in its own prose.
- Not run: the agent described was built and tested by the tutorial's own author; nothing was independently re-executed for this book.

## 9. Interview corner

**What interviewers listen for:** you can explain what happens when no pre-built MCP server exists for an API Joule Studio needs, and you don't conflate a server's total tool count with how many tools the agent actually calls.

<details class="qa"><summary>1. What happens when an agent needs an API that has no pre-built MCP server available?</summary>

- Joule Studio generates the MCP translation files directly from the API's own specification, rather than reusing an existing server

</details>

<details class="qa"><summary>2. A generated MCP server lists 65 tools. Does the agent actually call all 65?</summary>

- No — the generation process narrows the exposed tool surface down to only what's relevant for the specific agent (here: read-only, order/opportunity/simulation-focused), even though the underlying service offers 65

</details>

<details class="qa"><summary>3. What's the concrete guardrail in this agent's PRD, and why is it more useful than a vague "be careful with margins" instruction?</summary>

- A HIGH RISK flag triggers when projected margin drops below a specific configured floor — a numeric threshold the deterministic logic can enforce, not something left to LLM judgment at runtime

</details>

> [!TIP]
> **🧩 Design question**
> *"A sales ops lead asks why this agent needed 5 milestones when the Supplier Performance agent in Tutorial 7 only needed 4."* Talk about: the extra milestones (Rep interaction, Outcome tracked) reflecting that a discount recommendation is the start of a back-and-forth negotiation, not a one-shot classification — the milestone count in each PRD tracks the actual shape of the business process, not a fixed template.

## Cheat sheet

| Thing | Detail |
|---|---|
| No pre-built MCP server | Joule generates translation files from the API spec directly |
| Guardrail example | Numeric margin-floor threshold, not a vague policy |
| MCP tool count ≠ tools used | A server can expose far more tools than the agent is scoped to call |
| Test result | 124/124 passing, 100% score |

## Recap

- This tutorial follows the identical 9-stage flow as Tutorial 7, with a genuinely different wrinkle: no pre-built MCP server existed for its APIs, so Joule Studio generated translation files from the API specs directly
- A real numeric guardrail (margin-floor threshold) shows up in the PRD, not just a policy statement
- The generated MCP server exposes 65 tools, but the live generation process narrows what the agent actually uses down to a relevant, read-only subset
- 124 automated tests passed at 100% before this agent was considered ready

## Practice

1. Without looking back, explain what happens when Joule Studio needs an API with no pre-built MCP server
2. Name the specific guardrail from this agent's PRD and explain why it's concrete rather than vague
3. Explain the difference between a server's total tool count and the tools an agent actually calls

## How this chapter was checked

- The full tutorial "Build an AI Sales Assistant Agent with Joule Studio, SAP Sales Cloud, and SAP S/4HANA Cloud" (developers.sap.com, Beginner, 25 min, 9 steps) was read in full, 13 Nov 2026.
- 14 images were found and downloaded, all used here; each was opened and visually verified against its caption before being written into this chapter, including the MCP server tools screenshot confirming the 65-tool count and generation commentary.
- Nothing in this chapter was independently re-executed — the agent described was built and tested by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Build an AI Sales Assistant Agent with Joule Studio, SAP Sales Cloud, and SAP S/4HANA Cloud* — https://developers.sap.com/tutorials/build-an-ai-sales-assistant-agent (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 7: Supplier Performance Assistant](joule-studio-tutorial-7-supplier-performance-agent.md) · Next: [Joule Studio tutorial 9: automating balance confirmation workflows](joule-studio-tutorial-9-balance-confirmation-agent.md)
