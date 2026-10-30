# Cheat sheet
> lead: The key patterns on one page, for the night before an interview. Every item links back to the chapter that explains it.
meta: Quick reference | Code is condensed. See the chapters for the full versions

## The agent in one picture

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-5.5",              # "provider:model", any model you can access
    tools=[get_weather],                 # functions or @tool functions
    system_prompt="You are a helpful assistant",
    checkpointer=InMemorySaver(),        # memory (needs a thread_id when invoking)
    middleware=[...],                    # control (call limits, HITL, PII, custom)
    response_format=MySchema,            # structured final answer
    context_schema=MyContext,            # immutable per-run data
    store=my_store,                      # long-term memory
)
agent.invoke({"messages": [("user", "Weather in Delhi?")]},
             config={"configurable": {"thread_id": "t1"}},
             context=MyContext(user_id="u1"))
```

**Agent = Model + Harness.** An agent is a model calling tools in a loop until the task is done. The model never runs a tool; the agent does. ([Ch 1](#agentic-ai-ch1), [Ch 2](#agentic-ai-ch2))

## The raw loop

```python
for _ in range(max_turns):
    msg = model.invoke(messages)                   # with tools bound
    if not msg.tool_calls: return msg.content      # plain text = final answer
    messages.append(msg)
    for call in msg.tool_calls:                    # the CODE runs the tool
        messages.append(ToolMessage(content=str(tools[call["name"]](**call["args"])),
                                    tool_call_id=call["id"]))
```

## Models and messages ([Ch 3](#agentic-ai-ch3))

| Need | Use |
| --- | --- |
| A model | `init_chat_model("openai:gpt-5.5", temperature=0.5, max_tokens=1000, timeout=30, max_retries=6)` |
| Messages | `SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage` |
| One answer / progress / many | `.invoke()` / `.stream()` / `.batch()` (`batch_as_completed` for results as they finish) |
| Exact cost | `response.usage_metadata` |
| Show a tool, do not run it | `model.bind_tools([f])`, then read `response.tool_calls` (empty `content`) |
| Teach by example | Few-shot: prior Human and AI message pairs |

Batching does **not** save tokens. It saves cost and time (provider batch APIs, fewer round trips).

## Structured output ([Ch 4](#agentic-ai-ch4))

```python
class Booking(BaseModel):
    action: Literal["book", "cancel"]
    seats: int = Field(default=1, ge=1, le=10, description="Number of seats")

model.with_structured_output(Booking)                    # on a model
create_agent(..., response_format=ToolStrategy(schema=Union[A, B]))   # several intents
```

| | ProviderStrategy | ToolStrategy |
| --- | --- | --- |
| How | The provider's native feature | A synthetic tool call |
| Where | Supported models only | Almost any tool-calling model |

Validation errors go back to the model, which retries. A raw model cannot do tools and a schema together; an agent can.

## Tools ([Ch 5](#agentic-ai-ch5))

```python
@tool(args_schema=Input)             # docstring is the description the model reads
def book_seats(...): ...

@tool
def f(x: str, runtime: ToolRuntime) -> str:      # hidden from the model
    runtime.context.user_id; runtime.store.get(...); runtime.state
```

- Never name an argument `config` or `runtime` (fails at runtime).
- `return_direct` skips the model's final pass.
- Server-side tools run on the provider; headless tools run on the user's device.

## Memory ([Ch 6](#agentic-ai-ch6), [Ch 10](#agentic-ai-ch10))

| Need | Use |
| --- | --- |
| One conversation | Checkpointer plus `thread_id` |
| Facts across conversations | Store |
| Mutable data that persists in a thread | **State** (custom `AgentState` fields) |
| Immutable per-run data | **Context** |
| Repeated expensive calls | Cache with a TTL by data volatility |

## Middleware ([Ch 7](#agentic-ai-ch7) to [Ch 9](#agentic-ai-ch9))

| Hook | Runs | Use |
| --- | --- | --- |
| `before_agent` / `after_agent` | Once | Setup / teardown |
| `before_model` / `after_model` | Every loop pass | Observe or change state; redact input, check output |
| `wrap_model_call` | Every loop pass | Rewrite the request: filter tools, swap model |
| `wrap_tool_call` | Every loop pass | Wrap a tool execution |

**Before and wrap hooks run in declared order. After hooks run in reverse.**

| Built-in | Remember |
| --- | --- |
| `SummarizationMiddleware` | `model` (can be cheaper), `trigger`, `keep` |
| `HumanInTheLoopMiddleware` | Needs a checkpointer. `approve`, `edit`, `reject`, `respond`. Resume with `Command(resume={"decisions": [...]})` |
| `ToolCallLimitMiddleware` | `run_limit` (one invoke), `thread_limit` (conversation) |
| `ModelFallbackMiddleware` | Switches only on hard failure |
| `PIIMiddleware` | `block`, `redact`, `mask`, `hash`; custom detector with a regex or function |
| `TodoListMiddleware` | A maintained structured plan |
| `LLMToolSelectorMiddleware` | Filters tools by the query; `always_include` |
| Tool retry | `delay = initial_delay × backoff_factor ^ retry_number`; `max_retries` counts retries **after** the first call |
| `LLMToolEmulator` | Fake tool results for testing |

Guardrail is the **goal**. Middleware is the **mechanism**.

## MCP ([Ch 11](#agentic-ai-ch11) to [Ch 17](#agentic-ai-ch17))

```python
from fastmcp import FastMCP
mcp = FastMCP("Server")

@mcp.tool
def add(a: int, b: int) -> int: """Add two numbers."""; return a + b
@mcp.resource("file://notes")
def notes() -> str: ...
@mcp.prompt
def template(x: str) -> str: ...

mcp.run()                                   # STDIO (local)
mcp_app = mcp.http_app(path="/")            # HTTP: path "/" because mount adds the prefix
app = FastAPI(lifespan=mcp_app.lifespan)    # lifespan at construction
app.mount("/mcp", mcp_app)
```

| Topic | Remember |
| --- | --- |
| Architecture | Host, then one **client per server** (1:1), then server |
| Primitives | Tools (do), resources (read only), prompts (template). Each has `list` |
| Message format | JSON-RPC 2.0. `id` matches response to request. No `id` means notification |
| Lifecycle | Initialization, operation, shutdown |
| Handshake | `initialize` (id), response (same id), `initialized` (no id) |
| Negotiation | Each side declares capabilities. Latest version only, never a list |
| Operation | Discovery `tools/list` (automatic, free), calling `tools/call` (name plus arguments) |
| Shutdown | **No JSON-RPC.** STDIO: stop input, terminate, kill. HTTP: close the connection |
| Transports | STDIO (local, fast, secure) and Streamable HTTP (POST `/mcp`, remote) |
| Auto-convert an API | `FastMCP.from_fastapi(app)`. No prompts, resources or custom descriptions |
| Deploy | Clean repo (`main.py`, `database.py`, `pyproject.toml`, `uv.lock`), entry point `main.py:mcp` |
| Install in Claude Desktop | `uv run fastmcp install claude-desktop server.py` (use `which uv` for the full path) |

**Legacy vs modern (2026-07-28):** legacy remembers you with a session; modern is stateless and every message carries its context. Sampling is deleted (call the provider directly). Elicitation and ping need `mode="legacy"`. Deprecated means at least 12 months before removal is eligible. ([Ch 17](#agentic-ai-ch17))

**In LangChain** ([Ch 18](#agentic-ai-ch18)):

```python
async with MCPAdapter(transport_or_url_or_client_or_group) as adapter:
    tools = await adapter.list_tools()
    agent = create_agent(model, tools)          # use the agent INSIDE the block
```

Tool errors (`isError`) become `status="error"` messages. Transport failures raise. Elicitation becomes an `interrupt()`. Auth goes on the `Client`.

## Multi-agent ([Ch 19](#agentic-ai-ch19))

| Situation | Pattern |
| --- | --- |
| A central agent coordinates distinct domains | **Subagents** |
| Behaviour changes as a task progresses | **Handoffs** (state field plus `wrap_model_call`, tools return `Command`) |
| Many optional specialisations | **Skills** (`load_skill`) |
| Independent sources, query at once | **Router** (`Send`, reducer, synthesise) |
| None of these | **Custom workflow** (`StateGraph`) |

Default to one agent. Handoffs and skills are cheaper on repeats (about 5 vs 8 calls). Subagents and router win on parallel topics.

## Interview one-liners

- **Why LangChain?** A harness: tool schemas, messages, the loop and provider switching, so I focus on behaviour.
- **bind_tools?** Makes the model aware. Does not execute.
- **Why a schema?** Free text is not a contract.
- **Why filter tools in middleware, not the prompt?** A prompt can be talked around. A missing tool is not an option.
- **State vs context?** State is mutable and persists. Context is immutable per run.
- **Why MCP?** One server maintained by the provider instead of every team rewriting the same wrapper.
- **Why JSON-RPC?** Lightweight, transport-agnostic, two-way, notifications built in.
- **Does shutdown use JSON-RPC?** No. It is the transport's job.
- **Who calls the tool?** The client or agent. Never the model.
- **When multi-agent?** Only when tools, context, teams or latency demand it.
