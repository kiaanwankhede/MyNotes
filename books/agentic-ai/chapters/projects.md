# Mini-project ideas
> lead: Eight small projects that each exercise a block of the course, with a stretch goal and the interview story it gives you. Build one at a time.
meta: Practice | Each takes a weekend or less

:::note About the domain
Examples lean towards clinical education and research, because a project in a field you know well is easier to judge and easier to explain. **Never use real patient data** with any model or tool. Use synthetic or fully de-identified examples, and keep a human in the loop for anything clinical. Swap in any domain you like.
:::

## How to pick

Choose the project that matches the block you want to master. Then write a **two-sentence story** you can say in an interview: the problem, the design choice (and the alternative you rejected), and one thing that failed and how you fixed it.

| # | Project | Builds on | Chapters |
| --- | --- | --- | --- |
| 1 | Guideline Q&A with RAG | Retrieval, grounding | [20](#agentic-ai-ch20), [1](#agentic-ai-ch1) |
| 2 | Exam question generator | Structured output | [4](#agentic-ai-ch4) |
| 3 | Manuscript checklist reviewer | Structured output, tools | [4](#agentic-ai-ch4), [5](#agentic-ai-ch5) |
| 4 | Study buddy with memory | Memory and store | [6](#agentic-ai-ch6), [10](#agentic-ai-ch10) |
| 5 | Safe-action assistant | Middleware and HITL | [7](#agentic-ai-ch7), [8](#agentic-ai-ch8), [10](#agentic-ai-ch10) |
| 6 | Your own MCP server | FastMCP, deployment | [11](#agentic-ai-ch11) to [16](#agentic-ai-ch16) |
| 7 | MCP-powered agent | MCP in LangChain | [18](#agentic-ai-ch18) |
| 8 | Parallel reviewer panel | Multi-agent router | [19](#agentic-ai-ch19) |

## 1. Guideline Q&A with RAG

**Goal:** upload a handful of public guideline PDFs and answer questions using **only** their content.

- Chunk with overlap, embed, store, retrieve the top three, answer from them.
- The prompt must say "I do not know" when the answer is not in the documents. Test it with a question that is not covered.
- **Stretch:** compare `similarity`, `multiquery` and `contextual` retrieval on the same ten questions and record which wins.
- **Interview story:** how you stopped the model making things up, and what the retrieval comparison showed.

## 2. Exam question generator

**Goal:** turn a topic into multiple-choice questions with a guaranteed shape.

- Pydantic schema: stem, four options, correct answer, explanation, difficulty (`Literal`).
- Constrain the number of options and the answer index with `Field(ge=..., le=...)`.
- **Stretch:** add a second pass that checks each question against its source text, and reject any it cannot support.
- **Interview story:** why a schema beats "please reply in JSON", and how validation errors fed back and fixed a bad question.

## 3. Manuscript checklist reviewer

**Goal:** check a draft against a reporting checklist and return structured findings.

- Tools: a section extractor and a checklist lookup. Output: item, status (present, missing, unclear), evidence quote.
- Use a `Union` schema if findings come in more than one type.
- **Stretch:** add a todo list so the agent works through the checklist item by item.
- **Interview story:** when you chose tools versus plain code, and the cost of a vague tool description.

## 4. Study buddy with memory

**Goal:** an assistant that remembers your weak topics across sessions.

- A checkpointer and `thread_id` for each session, plus a **store** for long-term facts ("weak on topic X").
- Read the store with `ToolRuntime`, and pass the user id through **context**.
- **Stretch:** summarise old history with `SummarizationMiddleware` and compare token usage.
- **Interview story:** the difference between saver, store and state, and which you chose for each fact.

## 5. Safe-action assistant

**Goal:** an agent that can draft and send an email or cancel a booking, but only with approval.

- `HumanInTheLoopMiddleware` on the risky tool only, with `approve`, `edit`, `reject`.
- A conditional interrupt: ask only when a value passes a threshold.
- Add a tool call limit, PII redaction on input, and a retry with backoff on a flaky tool.
- **Stretch:** write one custom middleware (for example an audit log in `after_model`) and prove the hook order with print statements.
- **Interview story:** why a prompt rule is not a control, and how the missing-tool approach is stronger.

## 6. Your own MCP server

**Goal:** wrap a small API or database as an MCP server and put it on a public URL.

- FastMCP with at least one tool, one resource and one prompt. Test in Inspector.
- Mount it in FastAPI (`path="/"`, lifespan at construction), keep the database path in an environment variable, deploy a clean repo to Horizon.
- **Stretch:** compare `FastMCP.from_fastapi` with hand-written tools, and make database calls async.
- **Interview story:** auto-convert versus manual, and the deployment bug you hit.

## 7. MCP-powered agent

**Goal:** an agent that uses two MCP servers: one yours, one public.

- `MCPAdapter` with a client group. Call a tool directly first, then hand the tools to `create_agent`.
- Gate destructive tools with HITL built from annotations, and **test that the filter really selects them**.
- **Stretch:** add bearer-token auth to your server.
- **Interview story:** transport failure versus tool failure, and what the client group solved.

## 8. Parallel reviewer panel

**Goal:** several specialist reviewers (for example method, statistics, ethics) that read the same document at once.

- A router: classify, `Send` to specialists in parallel, a reducer to merge, a synthesis step.
- Compare latency with a sequential version, and write down the model-call counts.
- **Stretch:** a handoffs-style follow-up chat that keeps state after the report.
- **Interview story:** why you chose a router over subagents, with numbers.

## A weekly rhythm

1. Pick one project and write its two-sentence interview story **before** you start.
2. Build the smallest version that works end to end.
3. Break it on purpose (bad input, a failing tool, a long conversation) and fix it.
4. Add one stretch item.
5. Update your story with what failed. That detail is what makes it sound real.
