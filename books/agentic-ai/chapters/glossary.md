# Glossary
> lead: Key terms from the whole course in one line each, grouped by theme, with the chapter where each is explained. Use the search box to jump to a term.
meta: About 100 terms | Links go to the chapter

## Agent basics

| Term | One line | Chapter |
| --- | --- | --- |
| **Agent** | An LLM that decides which tool to call, in a loop, with memory kept as a message list | [Foundations](#foundations-f3) |
| **Agentic loop** | Model decides, tool runs, result goes back to the model, repeat until a plain-text answer. Once called ReAct | [Foundations](#foundations-f3), [6](#agentic-ai-ch6) |
| **Harness** | Everything around the model: system prompt, tools, memory, middleware. Agent = Model + Harness | [1](#agentic-ai-ch1), [2](#agentic-ai-ch2) |
| **Harness engineering** | The skill of wrapping a raw model so it becomes useful | [2](#agentic-ai-ch2), [16](#agentic-ai-ch16) |
| **Stateless LLM** | Each call remembers nothing; memory is history you resend | [Foundations](#foundations-f3) |
| **ReAct** | Reason plus Act: the 2022 pattern behind the first general agents | [2](#agentic-ai-ch2) |
| **`max_turns`** | A cap on loop iterations to prevent runaway cost | [Foundations](#foundations-f3) |
| **Tool schema** | Name, description and parameters that tell the model how to call a tool | [Foundations](#foundations-f3), [5](#agentic-ai-ch5) |
| **Token** | The billing unit of a model call; input and output are counted | [3](#agentic-ai-ch3) |
| **Context window** | The amount of text a model can consider at once | [7](#agentic-ai-ch7) |

## The LangChain family

| Term | One line | Chapter |
| --- | --- | --- |
| **LangChain** | A configurable agent harness (`create_agent`) built on LangGraph | [1](#agentic-ai-ch1), [2](#agentic-ai-ch2) |
| **LangGraph** | Low-level orchestration: state, persistence, durable execution. The foundation | [2](#agentic-ai-ch2) |
| **Deep Agents** | Batteries included: planning, virtual file system, sub-agents | [2](#agentic-ai-ch2) |
| **LangSmith** | Observability: traces of every model and tool call | [2](#agentic-ai-ch2) |
| **LangFuse** | An independent observability tool, not part of the LangChain family | [2](#agentic-ai-ch2) |
| **LangChain Classic** | Pre-v1 LangChain (`AgentExecutor` and friends), now `langchain-classic` | [2](#agentic-ai-ch2), [20](#agentic-ai-ch20) |
| **`create_agent()`** | The entry point that builds an agent from a model, tools, prompt and middleware | [1](#agentic-ai-ch1) |
| **`init_chat_model()`** | Universal model constructor using a `"provider:model"` string | [2](#agentic-ai-ch2), [3](#agentic-ai-ch3) |
| **`uv`** | The fast Python package and project manager used throughout | [1](#agentic-ai-ch1) |
| **`.env` and `.env.example`** | Real keys (never committed) and a safe template (committed) | [1](#agentic-ai-ch1) |

## Models and messages

| Term | One line | Chapter |
| --- | --- | --- |
| **`SystemMessage`** | Instructions for behaviour | [2](#agentic-ai-ch2) |
| **`HumanMessage`** | What the user said | [2](#agentic-ai-ch2) |
| **`AIMessage`** | What the model said, with `.tool_calls`, `.usage_metadata`, `.content_blocks` | [3](#agentic-ai-ch3) |
| **`ToolMessage`** | A tool's result, tied to the request by `tool_call_id`; can carry an `artifact` and `status` | [3](#agentic-ai-ch3), [5](#agentic-ai-ch5) |
| **Few-shot prompting** | Example input and output pairs as prior messages before the real question | [3](#agentic-ai-ch3) |
| **`temperature`** | Randomness of the output | [3](#agentic-ai-ch3) |
| **`max_tokens`, `timeout`, `max_retries`** | Output cap, wait time and retry count (default 6) | [3](#agentic-ai-ch3) |
| **`.invoke()`, `.stream()`, `.batch()`** | One answer, progressive chunks, many independent calls | [3](#agentic-ai-ch3) |
| **`AIMessageChunk`** | A streamed piece; chunks add with `+` into a full message | [3](#agentic-ai-ch3) |
| **`batch_as_completed`** | Batching that yields each result as it finishes | [3](#agentic-ai-ch3) |
| **`.bind_tools()`** | Tells a model which tools exist. Does not run them | [3](#agentic-ai-ch3), [5](#agentic-ai-ch5) |
| **Open vs closed source** | Open: weights available, self-hostable. Closed: API only | [2](#agentic-ai-ch2) |

## Structured output

| Term | One line | Chapter |
| --- | --- | --- |
| **Structured output** | Forcing a reply into a validated shape | [4](#agentic-ai-ch4) |
| **`with_structured_output()`** | Wraps a model so it returns a schema object | [3](#agentic-ai-ch3), [4](#agentic-ai-ch4) |
| **Pydantic `BaseModel`** | Strictly validated schema (vs `TypedDict`, no validation) | [4](#agentic-ai-ch4) |
| **`Literal`** | Restricts a field to an exact set of values | [4](#agentic-ai-ch4) |
| **`ProviderStrategy`** | Uses the provider's native structured output. Fast, only where supported | [4](#agentic-ai-ch4) |
| **`ToolStrategy`** | Forces structure with a synthetic tool call. Works almost anywhere | [4](#agentic-ai-ch4) |
| **`model.profile`** | Shows a model's capabilities, such as native structured output | [4](#agentic-ai-ch4) |
| **`Union` schema** | Several schemas; the model picks one from the intent | [4](#agentic-ai-ch4) |
| **Prompt template** | Reusable prompt with `{variables}` (`ChatPromptTemplate`) | [4](#agentic-ai-ch4) |

## Tools

| Term | One line | Chapter |
| --- | --- | --- |
| **`@tool`** | Wraps a function so an agent can call it; name from the function, description from the docstring | [5](#agentic-ai-ch5) |
| **`args_schema`** | A Pydantic schema with descriptions and constraints for a tool's arguments | [5](#agentic-ai-ch5) |
| **Reserved names** | `config` and `runtime` cannot be tool arguments; the failure shows at runtime | [5](#agentic-ai-ch5) |
| **Server-side tool** | Runs on the model provider's servers (web search, code interpreter) | [5](#agentic-ai-ch5) |
| **Headless tool** | Definition on the server, implementation on the user's device | [6](#agentic-ai-ch6) |
| **`return_direct`** | A tool's raw output skips the model's final pass | [5](#agentic-ai-ch5) |
| **`ToolRuntime`** | Hidden tool access to state, context, store and stream writer | [5](#agentic-ai-ch5), [10](#agentic-ai-ch10) |
| **Dynamic tool loading** | Changing the available tools at runtime | [6](#agentic-ai-ch6) |
| **Tavily** | A third-party web search service wrapped by a LangChain tool | [5](#agentic-ai-ch5), [6](#agentic-ai-ch6) |

## Memory and state

| Term | One line | Chapter |
| --- | --- | --- |
| **Checkpointer** | Saves a conversation's state (for example `InMemorySaver`) | [1](#agentic-ai-ch1), [6](#agentic-ai-ch6) |
| **`thread_id`** | The id that selects which conversation to restore | [6](#agentic-ai-ch6) |
| **Memory store** | Long-term facts across conversations | [5](#agentic-ai-ch5), [6](#agentic-ai-ch6) |
| **`AgentState`** | The mutable conversation state, extendable with custom fields | [6](#agentic-ai-ch6), [10](#agentic-ai-ch10) |
| **Runtime** | Information that travels with the agent but is not conversation | [10](#agentic-ai-ch10) |
| **`context` and `context_schema`** | Immutable per-run data and its declared shape | [10](#agentic-ai-ch10) |
| **Cache TTL** | How long a cached result stays valid | [1](#agentic-ai-ch1) |

## Middleware and guardrails

| Term | One line | Chapter |
| --- | --- | --- |
| **Middleware** | Code that hooks into the agent loop | [6](#agentic-ai-ch6), [7](#agentic-ai-ch7) |
| **Guardrail** | The goal of controlling agent behaviour. Middleware is one mechanism | [7](#agentic-ai-ch7), [8](#agentic-ai-ch8) |
| **The six hooks** | `before_agent`, `before_model`, `wrap_model_call`, `after_model`, `wrap_tool_call`, `after_agent` | [9](#agentic-ai-ch9) |
| **`wrap_model_call`** | Rewrites the actual model request (tools, model, messages) | [9](#agentic-ai-ch9) |
| **`SummarizationMiddleware`** | Condenses long history; `trigger` and `keep` | [7](#agentic-ai-ch7) |
| **`HumanInTheLoopMiddleware`** | Pauses for approve, edit, reject or respond | [7](#agentic-ai-ch7), [10](#agentic-ai-ch10) |
| **`Command(resume=...)`** | The answer that resumes a paused run | [10](#agentic-ai-ch10) |
| **Call limits** | Run limit (one invoke) and thread limit (whole conversation) | [8](#agentic-ai-ch8) |
| **`ModelFallbackMiddleware`** | Switches to a backup model when the primary fails | [7](#agentic-ai-ch7) |
| **`PIIMiddleware`** | Detects personal data. Strategies `block`, `redact`, `mask`, `hash` | [7](#agentic-ai-ch7), [8](#agentic-ai-ch8) |
| **Luhn algorithm** | The checksum real card numbers satisfy | [8](#agentic-ai-ch8) |
| **`TodoListMiddleware`** | A maintained structured plan for multi-step work | [8](#agentic-ai-ch8) |
| **`LLMToolSelectorMiddleware`** | Filters tools by the current query | [8](#agentic-ai-ch8) |
| **Tool retry and backoff** | `delay = initial_delay × backoff_factor ^ retry_number` | [8](#agentic-ai-ch8) |
| **`LLMToolEmulator`** | A model fakes tool results for testing | [8](#agentic-ai-ch8) |
| **`ShellToolMiddleware`** | A persistent shell for the agent. How coding assistants edit files | [9](#agentic-ai-ch9) |
| **`@dynamic_prompt`** | A system prompt rebuilt each call from runtime values | [10](#agentic-ai-ch10) |
| **Conditional interrupt** | Pause only when arguments meet a condition (a `when` callable) | [10](#agentic-ai-ch10) |

## MCP

| Term | One line | Chapter |
| --- | --- | --- |
| **MCP** | Open protocol connecting AI apps to tools and data | [11](#agentic-ai-ch11) |
| **Host, client, server** | The app, its 1:1 connector, and the tool provider | [11](#agentic-ai-ch11), [12](#agentic-ai-ch12) |
| **Primitives** | Tools (do), resources (read), prompts (template) | [11](#agentic-ai-ch11), [12](#agentic-ai-ch12) |
| **JSON-RPC 2.0** | The message format: `id`, `method`, `params`, `result` or `error` | [12](#agentic-ai-ch12) |
| **Notification** | A JSON-RPC message with no `id` and no reply | [12](#agentic-ai-ch12) |
| **Lifecycle** | Initialization, operation, shutdown | [12](#agentic-ai-ch12), [14](#agentic-ai-ch14) |
| **Initialization handshake** | `initialize`, response, `initialized` | [12](#agentic-ai-ch12) |
| **Capability negotiation** | Each side declares what it can do | [13](#agentic-ai-ch13) |
| **Roots, sampling, elicitation** | Client capabilities: file access, borrowing the client's model, asking the user | [13](#agentic-ai-ch13), [17](#agentic-ai-ch17) |
| **Discovery** | `tools/list` and friends. Automatic and free | [13](#agentic-ai-ch13) |
| **STDIO** | Local transport over stdin and stdout | [14](#agentic-ai-ch14) |
| **Streamable HTTP** | Remote transport: POST to `/mcp`. Replaced HTTP plus SSE | [14](#agentic-ai-ch14) |
| **FastMCP** | The popular Python library for building servers (`@mcp.tool`) | [14](#agentic-ai-ch14) |
| **MCP Inspector** | A browser tool for trying any MCP server | [11](#agentic-ai-ch11) |
| **Wiretap** | A relay that prints the real JSON-RPC conversation | [13](#agentic-ai-ch13) |
| **Prefect Horizon** | Free hosting for MCP servers from a GitHub repo | [15](#agentic-ai-ch15), [16](#agentic-ai-ch16) |
| **`Mcp-Session-Id`** | The legacy session header | [15](#agentic-ai-ch15), [17](#agentic-ai-ch17) |
| **Stateless MCP** | The 2026-07-28 spec: every request self-contained | [17](#agentic-ai-ch17) |
| **`mode="legacy"`** | Client option restoring the classic handshake | [17](#agentic-ai-ch17) |
| **`MCPAdapter`** | LangChain's built-in (beta) way to use MCP servers as tools | [18](#agentic-ai-ch18) |
| **`ClientGroup`** | Independent connections to several servers | [18](#agentic-ai-ch18) |
| **MCP gateway** | One entry point aggregating several MCP servers | [16](#agentic-ai-ch16) |

## Multi-agent and projects

| Term | One line | Chapter |
| --- | --- | --- |
| **Subagents** | A supervisor agent calls agents as tools | [19](#agentic-ai-ch19) |
| **Handoffs** | One agent's prompt and tools change with state | [19](#agentic-ai-ch19) |
| **Skills** | Specialised content loaded on demand (progressive disclosure) | [19](#agentic-ai-ch19) |
| **Router** | Classify once, fan out in parallel, synthesise | [19](#agentic-ai-ch19) |
| **Custom workflow** | A hand-built LangGraph graph | [19](#agentic-ai-ch19) |
| **`Send`** | LangGraph primitive that dispatches to branches in parallel | [19](#agentic-ai-ch19) |
| **RAG** | Retrieve relevant chunks, then answer from them | [20](#agentic-ai-ch20) |
| **Embeddings** | Numbers that capture meaning; similar text sits close | [20](#agentic-ai-ch20) |
| **Chunk overlap** | Shared characters between neighbouring chunks | [20](#agentic-ai-ch20) |
| **A2A** | Agent-to-agent protocol for connecting separate agent systems | [9](#agentic-ai-ch9) |
