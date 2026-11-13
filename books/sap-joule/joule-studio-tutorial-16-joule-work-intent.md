# Joule Studio tutorial 16: drafting a Joule Studio intent inside regular Joule chat

*The only tutorial in this book that never opens Joule Studio at all — a 2-turn conversation in ordinary end-user Joule chat, used as an intent-drafting tool for the agent built in the next tutorial.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** a technique, not a build — using regular end-user **Joule chat** (not Joule Studio) to turn a vague need into a paste-ready Joule Studio Intent Statement, by first hitting a real capability limit and then asking Joule to help articulate what's actually needed
> - **You will build:** nothing yet — this produces the exact Intent Statement paragraph used to start [Joule Studio tutorial 17: the Financial Closing Advisor agent](joule-studio-tutorial-17-financial-closing-advisor-agent.md)
> - **Level:** beginner · **Time:** about 5 minutes
> - **Builds on:** [Joule Studio tutorial 15: an n8n workflow for invoice exceptions](joule-studio-tutorial-15-invoice-exception-n8n-workflow.md). **Leads to:** [Joule Studio tutorial 17: building a Financial Closing Advisor agent](joule-studio-tutorial-17-financial-closing-advisor-agent.md)

> [!WARNING]
> Pre-release Joule Studio — screens and exact flow may differ from general availability. This specific tutorial's screens are all standard Joule chat, not Joule Studio.

**After this tutorial you can:**

- Explain the difference between what happened in turn 1 (a genuine capability limit) and what happened in turn 2 (a drafting request), and why that distinction matters
- Reuse this same technique — stating requirements in plain language, asking Joule to produce a paste-ready Intent Statement — before starting your own Joule Studio agent

## 1. Turn 1: hitting a real capability limit

A user opens a new conversation in regular Joule (not Joule Studio) and describes where she's at, three days into a financial close:

![New Conversation prompt: "Hey Joule — I'm three days into the August close and there's a lot in flight across accruals, journal entries, reconciliations, intercompany, FX, and sub-ledger tie-outs. I have the task list, I know the sequence, I know the mechanics. What I actually need right now is someone who can look at what's actually going on in the numbers and help me figure out where things stand. Can you help with that?"](images/sj212-01-turn1-prompt.png)

Joule hands the request off to an existing **Financial Closing Assistant** skill, visible in the processing trace:

![Processing trace: Analyzing financial close request details, Evaluating financial close assistants, Starting agent request, Handing over to Financial Closing Assistant, SUBMITTED, Analyzing your request, Retrieving conversation context, Classifying request type](images/sj212-01-turn1-response.png)

That assistant responds honestly about what it can and can't do — this is the real limit the next turn is built around:

> "I completely understand how intense the financial close period can be... While I understand the accounting processes and the sequence required for a successful close, I cannot directly analyze your real-time ERP ledger numbers, live account balances, or transactional systems to inspect where things stand due to system limitations. Although I cannot look directly at your live financial figures, I can certainly help you by providing general closing guidance, standard checklist procedures, or explanations of complex accounting..."

## 2. Turn 2: asking Joule to draft the Joule Studio intent

Rather than settling for general guidance, the user states precisely what a dedicated agent would need to do — and asks Joule to turn that into a Joule Studio-ready statement:

![Follow-up prompt: "Thanks — but qualitative guidance or one-off suggestions won't cut it every close cycle. I want my own dedicated agent for this, a Financial Closing Advisor, that actually looks at my live data for the six areas I mentioned, tells me what to work on and why, and ranks it by what's material, what's blocking other steps, what's near deadline, and what looks risky. Keep it in clear tiers, show your evidence, flag anything off or overdue, and admit when data is missing instead of guessing. It should only recommend — never post or execute. And keep it short — end every response with the single next thing I should do. Can you help me shape that into an intent for Joule Studio? Give me both a structured breakdown and, at the end, a single paste-ready paragraph — plain prose, no headings, no bullets — that I can drop into the Intent Statement field."](images/sj212-02-turn2-prompt.png)

Joule produces exactly that: a structured breakdown followed by one paste-ready paragraph, labeled explicitly for reuse:

![Joule Studio Intent Statement, labeled "Copy and paste the paragraph below directly into the Intent Statement field in Joule Studio": "The Financial Closing Advisor agent acts strictly as a read-only analytical assistant to help users monitor and prioritize active financial closing activities across six core areas: accruals, journal entries, reconciliations, intercompany transactions, foreign exchange revaluations, and sub-ledger tie-outs. The agent analyzes live transactional data and closing checklists to provide evidence-based recommendations, ranking outstanding items into clear priority tiers based on materiality, downstream blocking dependencies, upcoming deadlines, and risk profiles. It must explicitly state when required data is missing rather than making assumptions, and it is strictly prohibited from executing postings, modifications, or any transactional write-actions. All responses must be highly concise and conclude with a single, clear next action for the user to take." Next Action: copy the paragraph above and paste it into the Intent Statement field of a new agent draft in Joule Studio](images/sj212-02-turn2-response.png)

> [!TIP]
> Notice what's already baked into this paragraph, purely from the conversation, before Joule Studio has even opened: **read-only, never posts or writes**, an explicit **"state when data is missing, never guess"** rule, and a **concise-response-ending-in-one-next-action** format constraint. All three show up as concrete guardrails in the next tutorial's generated agent — this conversational drafting step is where they actually originate, not something invented later in Joule Studio.

## 3. Added by Claude, not from the sources

- The TIP in section 2, tracing which guardrails originate in this conversational step versus appearing later in Joule Studio, is this book's own cross-reference forward to [Tutorial 17](joule-studio-tutorial-17-financial-closing-advisor-agent.md) — confirmed by comparing this intent paragraph against that tutorial's generated PRD, not asserted by this tutorial alone.
- Not run: this conversation was conducted by the tutorial's own author; nothing was independently re-executed for this book.

## 4. Interview corner

**What interviewers listen for:** you can articulate why turn 1's "I can't do that" response is a genuine capability boundary rather than a failure, and you recognize this whole tutorial as a reusable technique, not a one-off anecdote.

<details class="qa"><summary>1. Why did the Financial Closing Assistant say it couldn't help with the user's original request?</summary>

- It cannot directly analyze real-time ERP ledger numbers, live account balances, or transactional systems — a genuine system limitation of that existing chat-based skill, not a misunderstanding of the request

</details>

<details class="qa"><summary>2. What two things did Joule produce in its turn-2 response, and why does the format matter?</summary>

- A structured breakdown and a single paste-ready plain-prose paragraph with no headings or bullets — the plain-prose form matters because Joule Studio's Intent Statement field expects a single descriptive paragraph, not a formatted document

</details>

<details class="qa"><summary>3. Name 3 guardrails already present in the drafted intent paragraph before Joule Studio is ever opened.</summary>

- Read-only / never posts or executes writes, must explicitly state when data is missing rather than guess, and responses must be concise and end with one clear next action

</details>

> [!TIP]
> **🧩 Design question**
> *"A colleague says they always just type their own Intent Statement directly into Joule Studio — why bother with this two-turn detour through regular Joule chat first?"* Talk about: letting Joule itself surface the gap between a vague ask ("help me figure out where things stand") and a precise, testable set of requirements (six named areas, 4 ranking criteria, 2 explicit guardrails, a response-format constraint) — the conversational back-and-forth is doing real requirements-gathering work before any Studio screen is involved, which tends to produce a tighter Intent Statement than writing one cold.

## Cheat sheet

| Thing | Detail |
|---|---|
| Where this happens | Regular end-user Joule chat — not Joule Studio |
| Turn 1 | Hits a genuine capability limit (can't read live ERP data) |
| Turn 2 | User states precise requirements, asks for a paste-ready Intent Statement |
| Output | One plain-prose paragraph, explicitly labeled for the Joule Studio Intent Statement field |
| Guardrails already present | Read-only/no writes, state-missing-data-don't-guess, concise-with-one-next-action |

## Recap

- This tutorial is a technique, not a build: using ordinary Joule chat to turn a vague need into a precise, paste-ready Joule Studio Intent Statement
- Turn 1 surfaces a genuine system limitation (no live ERP data access) rather than a misunderstanding
- Turn 2's drafted paragraph already encodes the agent's core guardrails — read-only, explicit about missing data, and format-constrained — before Joule Studio is ever opened
- The next tutorial starts directly from this paragraph, pasted into a new agent's Intent Statement field

## Practice

1. Without looking back, explain the capability limit the Financial Closing Assistant hit in turn 1
2. List the 4 criteria the drafted agent ranks outstanding items by
3. Name the 3 guardrails already present in the drafted intent paragraph

## How this chapter was checked

- The full tutorial "Draft a Joule Studio Intent with Joule" (developers.sap.com, Beginner, 5 min) was read in full, 13 Nov 2026.
- 4 images were found and downloaded, all used here; each was opened and the full prompt/response text was transcribed directly from the screenshots rather than paraphrased, since the exact wording is the point of this tutorial.
- Nothing in this chapter was independently re-executed — this conversation was conducted by the tutorial's own author.

## Sources and further reading

- SAP Developers, *Draft a Joule Studio Intent with Joule* — https://developers.sap.com/tutorials/joule-work-intent-drafting (read in full 13 Nov 2026)

Previous: [Joule Studio tutorial 15: an n8n workflow for invoice exceptions](joule-studio-tutorial-15-invoice-exception-n8n-workflow.md) · Next: [Joule Studio tutorial 17: building a Financial Closing Advisor agent](joule-studio-tutorial-17-financial-closing-advisor-agent.md)
