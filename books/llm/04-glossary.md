# Chapter 4: Glossary

**After this chapter you can:**

- Look up any course term in one line and jump to the chapter that teaches it
- Tell apart look-alike terms (guardrail and middleware, state and runtime, saver and store)

- 140 entries from the whole course, A to Z. Each has a one-line meaning and a link to where it is taught
- Definitions are reworded, not copied. Terms from the source glossaries are all here
- Where the books use a different name from the class, the book's chapter is the link

## A

- **A2A (agent-to-agent).** A protocol for separate agent systems to talk to each other. The roadmap places it beside MCP and LangGraph. [LLM, Ch 1](../llm/01-course-roadmap-and-prerequisites.md)
- **Agent.** Orchestration code that joins a brain (the model), memory (the history) and tools so the model can act, not only talk. The code is not itself intelligent. [Python, Ch 3](../python/03-anatomy-of-an-agent.md)
- **Agentic loop.** Send messages and tool schemas, run any tool the model asks for, append the result, call again, stop on plain text. [LLM, Ch 2](../llm/02-the-agentic-loop-in-pure-python.md)
- **Agent = model + harness.** LangChain's own definition: the model plus everything wrapped around it. [Langchain, Ch 1](../langchain/01-introduction-to-langchain.md) · [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **AgentOps.** Deploying and monitoring agents in production. Taught after the fundamentals and framework phases. [LLM, Ch 1](../llm/01-course-roadmap-and-prerequisites.md)
- **AgentState.** The typed dictionary an agent runs on: the `messages` list plus any custom fields. Extend it by subclassing. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **AI message.** The model's reply object. It holds text, content blocks, an id and any tool calls, not just a string. [Langchain, Ch 3](../langchain/03-models-messages-and-parameters.md)
- **AI model, chatbot, agent.** Three layers. A model makes one stateless prediction, a chatbot adds history, an agent adds tools it can choose. [Python, Ch 3](../python/03-anatomy-of-an-agent.md)
- **`*args` and `**kwargs`.** Collect positional and keyword arguments. A decorator's wrapper uses them to pass any call through. [Python, Ch 2](../python/02-python-refresher.md)
- **`args_schema`.** A Pydantic model attached to a tool for richer argument rules than type hints: ranges, patterns, nested fields. [Langchain, Ch 5](../langchain/05-tools.md)
- **`artifact` (on `ToolMessage`).** An extra field for rich tool output such as links or ids. The application reads it; the model never sees it. [Langchain, Ch 5](../langchain/05-tools.md)

## B

- **`BaseModel`.** The Pydantic class that checks every field's type when you create an object and raises at once on bad data. [Pydantic, Ch 1](../pydantic/01-why-pydantic-and-basemodel.md)
- **Batching (`.batch()`).** Send several independent requests together so they run in parallel. `batch_as_completed()` returns each as it finishes. [Langchain, Ch 3](../langchain/03-models-messages-and-parameters.md)
- **`before_agent` and `after_agent`.** Hooks that fire once per run, at the start and end. A natural place to open and close a resource. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **`before_model` and `wrap_model_call`.** `before_model` observes state. `wrap_model_call` receives the outgoing request and can rewrite the model, tools or prompt. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **`bind_tools()`.** Tells a model which tools exist. It does not run them; the model can only request a call. [Langchain, Ch 5](../langchain/05-tools.md)
- **Brain, memory, tools.** The mental model every agent framework maps onto. [Python, Ch 3](../python/03-anatomy-of-an-agent.md)

## C

- **Capability negotiation.** Each side of an MCP connection declares what it can do during the handshake, so neither assumes more than the other supports. [MCP, Ch 3](../mcp/03-lifecycle-json-rpc-and-capability-negotiation.md)
- **Chain (LangChain Classic).** The older fixed sequence of steps, replaced by agents that decide their own steps. [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **Chatbot.** A model plus history. See "AI model, chatbot, agent". [Python, Ch 3](../python/03-anatomy-of-an-agent.md)
- **Checkpointing.** Saving a conversation's state by `thread_id` so a later call resumes it. Without a checkpointer an agent forgets between calls. [Langchain, Ch 6](../langchain/06-agents-and-memory.md)
- **Class-based middleware.** Middleware written as an `AgentMiddleware` subclass with hook methods. Better once it needs state, several hooks or reuse. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **`Command`.** The object that resumes a paused run (`Command(resume=...)`) or updates state and routes from a tool. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **Conditional interrupt (`when`).** Pause for human approval only when the call's data meets a rule, such as a refund over a set amount. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **Connectors and the config file.** Connectors are the easy way to add a hosted MCP server. The config file is what powers both and gives full control. [MCP, Ch 5](../mcp/05-building-mcp-servers.md)
- **Context (in `ToolRuntime`).** Fixed configuration passed at invoke time, readable in a tool, invisible to the model. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **`context_schema`.** Declares the shape of per-run information an agent expects, passed in with `context=`. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **Context window.** The model's fixed-size whiteboard. When it fills, the oldest content is dropped. Not the same as memory. [LLM, Ch 3](../llm/03-inside-the-model.md)
- **`create_agent()`.** LangChain's single entry point that joins a model, tools, a prompt and middleware into a runnable agent. [Langchain, Ch 6](../langchain/06-agents-and-memory.md)
- **Custom middleware.** Middleware you write for rules no built-in one covers, using hooks. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)

## D

- **DAG (the loop is not one).** A directed acyclic graph cannot cycle. The agent loop does (model, tool, model), so it is not a DAG. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **Dataclass.** Generates `__init__` from typed fields. It does not check types at run time, unlike `BaseModel`. [Python, Ch 2](../python/02-python-refresher.md) · [Pydantic, Ch 1](../pydantic/01-why-pydantic-and-basemodel.md)
- **Decorator.** A function that wraps another to add behaviour around it. `@tool` is built on the idea. [Python, Ch 2](../python/02-python-refresher.md)
- **Decorator-based middleware.** A single hook defined by decorating a plain function. Best for one hook at a time. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **Deep Agents.** The batteries-included layer on top of LangChain agents: context compression, a virtual file system, sub-agents. The least control. [Langchain, Ch 1](../langchain/01-introduction-to-langchain.md) · [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **Dynamic tool loading.** Changing the tools an agent can see at run time, for example hiding a VIP-only tool. [Langchain, Ch 7](../langchain/07-middleware.md)

## E

- **Elicitation.** An MCP server asking the user for more information mid-task, through the client. Differs from human-in-the-loop, which approves an action. [MCP, Ch 7](../mcp/07-legacy-vs-modern-mcp.md) · [Langchain, Ch 12](../langchain/12-mcp-in-langchain.md)
- **`EmailStr`, `HttpUrl`, `SecretStr`.** Pydantic special types: check an email, check a URL, hide a secret when printed. [Pydantic, Ch 2](../pydantic/02-field-and-special-types.md)
- **Embeddings.** See "Vector embeddings". [LLM, Ch 3](../llm/03-inside-the-model.md)
- **Exponential backoff.** Retry delays that grow each time: `initial_delay` times `backoff_factor` to the power of the retry number. [Langchain, Ch 9](../langchain/09-guardrails-to-do-lists-and-tool-resilience.md)

## F

- **FastMCP.** The library that turns a plain Python function into an MCP tool with a decorator. Unrelated to FastAPI. [MCP, Ch 5](../mcp/05-building-mcp-servers.md)
- **`FastMCP.from_fastapi()`.** Converts every FastAPI route into an MCP tool in one line. Fast, but with no prompts and rough tool names. [MCP, Ch 5](../mcp/05-building-mcp-servers.md)
- **Few-shot prompting.** Show the model a few example question and answer pairs before the real question, instead of a bloated system prompt. [Langchain, Ch 3](../langchain/03-models-messages-and-parameters.md)
- **`Field()`.** Adds limits on the value, such as `gt=0` or `min_length=2`, not just the type. [Pydantic, Ch 2](../pydantic/02-field-and-special-types.md)
- **`field_validator` and `model_validator`.** One checks a single field. The other runs after all fields and sees the whole model, so it can compare fields. [Pydantic, Ch 3](../pydantic/03-validators.md)
- **Forward-Deployed Engineer (FDE).** A role the course covers alongside Harness Engineering. [LLM, Ch 1](../llm/01-course-roadmap-and-prerequisites.md)
- **f-string.** A string written `f"..."` where `{ }` is replaced by a value. [Python, Ch 1](../python/01-setup-and-api-basics.md)
- **Function calling (before MCP).** The 2023 ability of a model to request a call to a described tool. It worked, but each app wired tools its own way. [MCP, Ch 1](../mcp/01-why-mcp-exists.md)
- **`functools.wraps`.** Keeps the original function's name when you wrap it in a decorator. [Python, Ch 2](../python/02-python-refresher.md)

## G

- **Groq.** A fast, free provider (not Elon Musk's "Grok") that hosts open models behind an OpenAI-compatible API. [Python, Ch 3](../python/03-anatomy-of-an-agent.md)
- **Guardrail.** The goal of keeping an agent from doing something unwanted. Middleware is one mechanism for it. [Langchain, Ch 8](../langchain/08-prebuilt-middleware-limits-fallback-and-pii.md)

## H

- **Harness.** Everything wrapped around a raw model: prompt, tools, memory, middleware, guardrails. [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **Harness engineering.** The discipline of doing that wrapping well. Tools such as Claude Code are examples. [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **Headless tools.** Tools defined on the server but run on the user's own device, such as clipboard or location, through an interrupt. [Langchain, Ch 6](../langchain/06-agents-and-memory.md)
- **HITL decisions.** Four answers to a human-in-the-loop pause: `approve`, `edit`, `reject`, `respond`. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **Hooks (six).** `before_agent`, `before_model`, `wrap_model_call`, `after_model`, `wrap_tool_call`, `after_agent`. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **Horizon.** The hosting service from Prefect that FastMCP's docs recommend. Connect a GitHub repo and get a public URL. [MCP, Ch 6](../mcp/06-deployment-and-building-a-client.md)
- **`HostExecutionPolicy`.** Gives the shell tool direct access to the host machine. For trusted sandboxes only. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **Host (MCP).** The app a person uses, such as Claude Desktop. It starts one client per server. [MCP, Ch 2](../mcp/02-primitives-and-architecture.md)
- **Human-in-the-loop (HITL).** Middleware that pauses before a sensitive tool call so a person can approve, edit or reject it. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)

## I

- **`init_chat_model`.** One entry point to any provider: change the `"provider:model"` string and nothing else. [Langchain, Ch 3](../langchain/03-models-messages-and-parameters.md)
- **Initialization handshake.** The three-step MCP opening: `initialize` request, the server's reply, then the client's `initialized` notice. [MCP, Ch 3](../mcp/03-lifecycle-json-rpc-and-capability-negotiation.md)
- **`InMemorySaver`.** A checkpointer that keeps history in RAM by `thread_id`. Lost when the process ends. [Langchain, Ch 6](../langchain/06-agents-and-memory.md)
- **`InMemoryStore`.** A dictionary-like store that persists across conversations, for things such as saved preferences. [Langchain, Ch 6](../langchain/06-agents-and-memory.md)

## J

- **JSON-RPC 2.0.** The message format MCP uses: either side can start a request, and notifications need no reply. [MCP, Ch 3](../mcp/03-lifecycle-json-rpc-and-capability-negotiation.md)
- **JSON-schema tools.** A tool defined by a JSON schema instead of a Python function. Valid, but Pydantic is more practical. [Langchain, Ch 5](../langchain/05-tools.md)

## K

- **Knowledge cutoff.** The date a model's training data ends. It knows nothing later, so agents need search tools. [LLM, Ch 2](../llm/02-the-agentic-loop-in-pure-python.md)

## L

- **LangChain.** The middle layer of the family: a customisable harness (`create_agent`) built on LangGraph. [Langchain, Ch 1](../langchain/01-introduction-to-langchain.md)
- **LangChain Classic.** LangChain before v1.0 (October 2025). Most online tutorials still teach it; it is legacy. [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **LangFuse.** An independent open-source observability tool. Despite the name it is not part of the LangChain family. [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **LangGraph.** The low-level foundation: total control of every step and the steepest learning curve. [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **LangSmith.** An observability platform that records every model call, tool call and decision. Not for building agents. [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **LLM.** A large language model. It predicts the next token from patterns in text. [LLM, Ch 3](../llm/03-inside-the-model.md)
- **`LLMToolEmulator`.** Middleware that has a model invent a plausible tool result without running the tool. For testing. [Langchain, Ch 9](../langchain/09-guardrails-to-do-lists-and-tool-resilience.md)
- **`LLMToolSelectorMiddleware`.** Uses a cheaper model to pick the tools relevant to the query before the main call. Filters by query, not by user state. [Langchain, Ch 9](../langchain/09-guardrails-to-do-lists-and-tool-resilience.md)
- **Luhn algorithm.** The checksum real card numbers pass. The PII credit-card detector uses it, so a random digit string is not flagged. [Langchain, Ch 8](../langchain/08-prebuilt-middleware-limits-fallback-and-pii.md)

## M

- **`max_tokens` and `max_turns`.** `max_tokens` caps output length. `max_turns` caps how many times the loop may call the model. [LLM, Ch 2](../llm/02-the-agentic-loop-in-pure-python.md)
- **MCP client.** The part a host creates to talk to exactly one server. Five servers means five clients. [MCP, Ch 2](../mcp/02-primitives-and-architecture.md)
- **MCP Inspector.** A browser tool that connects to a server and lets you call its tools, resources and prompts directly. [MCP, Ch 3](../mcp/03-lifecycle-json-rpc-and-capability-negotiation.md) · [MCP, Ch 5](../mcp/05-building-mcp-servers.md)
- **MCP lifecycle.** Three phases in order: initialization, operation, shutdown. [MCP, Ch 3](../mcp/03-lifecycle-json-rpc-and-capability-negotiation.md) · [MCP, Ch 4](../mcp/04-operation-transports-and-shutdown.md)
- **MCP (Model Context Protocol).** An open standard so any AI host can use any compliant server's tools, resources and prompts. [MCP, Ch 1](../mcp/01-why-mcp-exists.md)
- **MCP primitives.** What a server can offer: tools (do), resources (read), prompts (a form to fill in). [MCP, Ch 2](../mcp/02-primitives-and-architecture.md)
- **MCP server.** The side that offers capabilities. Often a wrapper around APIs that already existed. [MCP, Ch 2](../mcp/02-primitives-and-architecture.md) · [MCP, Ch 5](../mcp/05-building-mcp-servers.md)
- **Memory saver, store, cache, database.** Four different things: a saver resumes one thread, a store holds cross-conversation facts, a cache avoids repeating calls, a database is for everything else. [Langchain, Ch 6](../langchain/06-agents-and-memory.md) · [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **Middleware.** Code that intercepts an agent at set points (around the model and tools) for cross-cutting control. [Langchain, Ch 7](../langchain/07-middleware.md)
- **Middleware execution order.** `before_*` hooks run in declared order, `after_*` hooks in reverse, and `wrap_*` hooks nest with the first one outermost. A stack. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **MIME type.** Tells a client what kind of content a resource holds (text, PDF, audio). [MCP, Ch 4](../mcp/04-operation-transports-and-shutdown.md)
- **Model call limit.** Middleware that caps model calls in one run. The formal version of `max_turns`. [Langchain, Ch 8](../langchain/08-prebuilt-middleware-limits-fallback-and-pii.md)
- **Model fallback.** Switches to a backup model when the primary fails hard. A failure fallback, not a smart router. [Langchain, Ch 8](../langchain/08-prebuilt-middleware-limits-fallback-and-pii.md)
- **`model.profile`.** Looks up what a model supports (structured output, tools, multimodal) before you rely on it. [Langchain, Ch 4](../langchain/04-structured-output.md)

## N

- **Nested models.** A Pydantic model used as a field's type, matching nested JSON. [Pydantic, Ch 4](../pydantic/04-nested-models-and-inheritance.md)
- **ngrok (tunnelling).** Exposes a local port as a public URL without deploying. [MCP, Ch 5](../mcp/05-building-mcp-servers.md)

## O

- **Open-Meteo.** A free, keyless weather API used for the first real tool in TripMate. [Langchain, Ch 6](../langchain/06-agents-and-memory.md)
- **OpenRouter.** One endpoint and one key for models from many providers, with exact token counts. [LLM, Ch 3](../llm/03-inside-the-model.md)
- **Operation phase.** The MCP phase where the client discovers (`tools/list`) and then calls (`tools/call`). [MCP, Ch 4](../mcp/04-operation-transports-and-shutdown.md)

## P

- **Parameters.** The billions of fixed weights set in training. Not the same as tokens. [LLM, Ch 3](../llm/03-inside-the-model.md)
- **`PIIMiddleware`.** Detects personal data (email, card, custom ids) before it reaches the model and applies a strategy. [Langchain, Ch 8](../langchain/08-prebuilt-middleware-limits-fallback-and-pii.md)
- **PII strategies.** Four ways to handle detected personal data: `block`, `redact`, `mask`, `hash`. [Langchain, Ch 8](../langchain/08-prebuilt-middleware-limits-fallback-and-pii.md)
- **Primitive functions.** Tools have `list` and `call`; resources have `list` and `read`; prompts have `list` and `get`. [MCP, Ch 2](../mcp/02-primitives-and-architecture.md) · [MCP, Ch 4](../mcp/04-operation-transports-and-shutdown.md)
- **Prompt injection.** An attempt to override instructions through the message itself. A field limit can stop its effect. [Langchain, Ch 1](../langchain/01-introduction-to-langchain.md)
- **Provider strategy and tool strategy.** Two ways to get structured output: the provider's native feature, or a synthetic tool call that works almost anywhere. [Langchain, Ch 4](../langchain/04-structured-output.md)
- **Pydantic.** A library that checks type and value at run time and raises `ValidationError` on bad input. [Pydantic, Ch 1](../pydantic/01-why-pydantic-and-basemodel.md)
- **`pyproject.toml`.** The project file that records Python version and dependencies so another machine rebuilds the same environment. [Python, Ch 1](../python/01-setup-and-api-basics.md)

## R

- **ReAct.** "Reason plus Act", the first general agent pattern. The model reasons and acts instead of following a fixed chain. [Langchain, Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)
- **Retriever and RAG.** Find the relevant text first, then answer from it. Used in the Meridian project. [Projects, Ch 3](../projects/03-meridian-ai-learner.md)
- **`return_direct`.** Sends a tool's output straight to the user, skipping the model's rewording. [Langchain, Ch 5](../langchain/05-tools.md)
- **Runtime.** Information that travels with the agent but is not the conversation: `context`, `store`, `stream_writer`, `execution_info`, `server_info`. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)

## S

- **`SecretStr`.** See `EmailStr`, `HttpUrl`, `SecretStr`. [Pydantic, Ch 2](../pydantic/02-field-and-special-types.md)
- **Server-side (provider) tools.** Tools such as web search that run on the provider's side, not in your code. [Langchain, Ch 5](../langchain/05-tools.md) · [Langchain, Ch 6](../langchain/06-agents-and-memory.md)
- **`ShellToolMiddleware`.** Gives an agent a persistent real shell. The mechanism behind how coding agents edit files. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)
- **`state` (in `ToolRuntime`).** Short-term memory inside a tool: the messages and mutable data of this conversation. [Langchain, Ch 5](../langchain/05-tools.md)
- **Stateless.** A raw model call remembers nothing. The whole history is resent each time. [LLM, Ch 3](../llm/03-inside-the-model.md) · [Python, Ch 3](../python/03-anatomy-of-an-agent.md)
- **State versus runtime.** State is mutable and persists across calls in a conversation. Runtime context is fixed for the run. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **STDIO (transport).** Client and server as parent and child processes on one machine. Fast and private, local only. [MCP, Ch 4](../mcp/04-operation-transports-and-shutdown.md)
- **`store` (in `ToolRuntime`).** Long-term memory inside a tool that persists across separate conversations. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **Streamable HTTP.** The MCP transport for servers anywhere on the internet: JSON-RPC over POST to one `/mcp` URL. Replaced HTTP+SSE. [MCP, Ch 4](../mcp/04-operation-transports-and-shutdown.md)
- **Streaming (`.stream()`).** Returns output chunk by chunk. It does not make the answer faster, only the wait shorter. [Langchain, Ch 3](../langchain/03-models-messages-and-parameters.md)
- **`stream_writer`.** Lets a tool send live progress updates while it runs. [Langchain, Ch 11](../langchain/11-runtime-and-human-in-the-loop.md)
- **Structured output.** Making a reply fit a defined shape (a Pydantic model) instead of free text. [Langchain, Ch 4](../langchain/04-structured-output.md) · [Pydantic, Ch 5](../pydantic/05-validating-llm-output.md)
- **`SummarizationMiddleware`.** Condenses older history once a token, message or percent trigger is hit, keeping recent messages in full. [Langchain, Ch 7](../langchain/07-middleware.md)
- **System, user, assistant messages.** The three roles sent on every call: rules (optional), what the person said, the model's earlier replies. [LLM, Ch 2](../llm/02-the-agentic-loop-in-pure-python.md)

## T

- **Thread id.** The key a checkpointer uses to find a conversation's saved history. The application decides when a new thread starts. [Langchain, Ch 6](../langchain/06-agents-and-memory.md)
- **To-do list middleware.** Gives an agent a persisted plan it updates turn by turn. [Langchain, Ch 9](../langchain/09-guardrails-to-do-lists-and-tool-resilience.md)
- **Token.** The unit a model reads, writes and bills in, about three quarters of a word. Output costs more than input. [LLM, Ch 3](../llm/03-inside-the-model.md)
- **Tool.** A function the model can choose to call, given only its name, description and schema. [Langchain, Ch 5](../langchain/05-tools.md) · [Python, Ch 1](../python/01-setup-and-api-basics.md)
- **Tool call limit.** Caps tool calls: a run limit (one invoke) or a thread limit (the whole conversation). [Langchain, Ch 8](../langchain/08-prebuilt-middleware-limits-fallback-and-pii.md)
- **Tool error middleware.** Turns a tool's exception into a readable tool message so the run continues. [Langchain, Ch 9](../langchain/09-guardrails-to-do-lists-and-tool-resilience.md)
- **`ToolMessage`.** Feeds a tool result back to the model, with a `tool_call_id` matching the request. [Langchain, Ch 5](../langchain/05-tools.md)
- **Tool retry middleware.** Retries a failed tool with exponential backoff up to `max_retries`. [Langchain, Ch 9](../langchain/09-guardrails-to-do-lists-and-tool-resilience.md)
- **`ToolRuntime`.** A parameter that gives a tool access to state, context, store and more, all hidden from the model. [Langchain, Ch 5](../langchain/05-tools.md)
- **Tool schema.** The name, description and parameters sent to the model. It never sees the function. [LLM, Ch 2](../llm/02-the-agentic-loop-in-pure-python.md)
- **Transport layer.** How an MCP client and server are connected: STDIO locally, Streamable HTTP over the internet. [MCP, Ch 4](../mcp/04-operation-transports-and-shutdown.md)

## U

- **Union types (multi-intent).** Pass `Union[A, B]` as the schema so the model picks the shape that fits. [Langchain, Ch 4](../langchain/04-structured-output.md)
- **UV.** One tool for Python versions, environments and dependencies, replacing `pip`, `venv` and `conda`. [Python, Ch 1](../python/01-setup-and-api-basics.md)

## V

- **`ValidationError`.** The error Pydantic raises when data fails a check. [Pydantic, Ch 1](../pydantic/01-why-pydantic-and-basemodel.md)
- **Vector embeddings.** A word or idea as a point in a high-dimensional space where similar meanings are close. [LLM, Ch 3](../llm/03-inside-the-model.md)
- **Version negotiation.** The client proposes its latest version; the server accepts it or answers with its own latest. [MCP, Ch 3](../mcp/03-lifecycle-json-rpc-and-capability-negotiation.md)
- **Vibe coding.** Letting AI write most of an app. It gets you most of the way, but the code still needs a security and data review. _not written up in the books_
- **VS Code and Google Colab.** Colab for learning step by step; VS Code for real multi-file projects. [LLM, Ch 1](../llm/01-course-roadmap-and-prerequisites.md)

## W

- **`wrap_tool_call`.** One hook that sees a tool call before it runs. It replaces a separate before and after pair. [Langchain, Ch 10](../langchain/10-shell-tools-and-custom-middleware.md)

## Look-alike terms

- **Guardrail vs middleware.** A guardrail is the goal (stop something bad). Middleware is one way to build it
- **State vs runtime.** State changes and lasts through a conversation. Runtime context is fixed for the run
- **Saver vs store.** A saver (checkpointer) resumes one thread. A store keeps facts across threads
- **Host vs client vs server (MCP).** The host is the app. It starts one client per server. The client talks to the server
- **Tool vs primitive.** A tool is one kind of MCP primitive. The others are resources and prompts
- **Token vs parameter.** Tokens flow through the model. Parameters are what the model is
- **Context window vs memory.** The window is per call and fixed. Memory is a separate, lasting mechanism
- **Provider strategy vs tool strategy.** Native structured output, or a synthetic tool call that fakes it

## Interview corner

**Q1. Guardrail or middleware?**
- A guardrail is the aim. Middleware is a mechanism that can implement it, along with retries, fallbacks and logging

**Q2. State or runtime context?**
- State is mutable and persists across calls in a conversation. Runtime context is set when you invoke and does not change

**Q3. Checkpointer or store?**
- A checkpointer resumes one conversation by `thread_id`. A store holds data across conversations

**Q4. What does "stateless" mean for an LLM call?**
- The model remembers nothing between calls. The history is resent every time

**Q5. Tool schema or tool function?**
- The schema (name, description, parameters) goes to the model. The function stays in your code

**Q6. What are the three MCP primitives?**
- Tools (do), resources (read), prompts (a form to fill in)

**Q7. Why is the agent loop not a DAG?**
- It cycles back (model, tool, model again)

**Q8. What does `wrap_model_call` do that `before_model` cannot?**
- It receives the outgoing request and can change the model, tools or prompt. `before_model` only observes

## Added by Claude, not from the sources

- **One term added:** "Retriever and RAG" (retrieve first, then answer) comes from the Meridian project, not the source glossaries
- **One fix to the source wording:** the class glossary says `wrap_tool_call` "stays in declared order" for after-hooks. [Langchain Ch 10](../langchain/10-shell-tools-and-custom-middleware.md) tested this: wrap hooks **nest**, so a wrap hook exits in reverse. The execution-order entry follows that
- **One term not written up:** "Vibe coding" appears in the source glossary but no book chapter teaches it, so it has no link
- **Names change:** `langchain-mcp-adapters` and `langchain.mcp` are two different packages (see [Langchain Ch 12](../langchain/12-mcp-in-langchain.md)). The glossary uses the class's wording
- **Study tip:** read one letter a day and say each entry aloud without looking at the definition

## Recap

- 140 entries, A to Z, each linked to its teaching chapter
- The look-alike list is the fastest revision for interviews
- If a term is missing, search the book that owns the topic and add it here

## Practice

1. Pick ten entries at random and explain each without looking
2. Use the look-alike list: write one sentence that separates each pair
3. Find a term you use at work that is missing here and write its entry

## How this chapter was checked

- **Terms and meanings** come from the two source glossaries (about 141 entries, some only pointing to another entry, a few merged here into one line). Definitions were reworded
- **Links:** every chapter link was checked to point to a file that exists in this repository. The chapter chosen for each term was picked by searching the books for the term and checking the best match. A few were set by hand
- **Not checked:** each link was not opened to confirm the section; the chapter is the target, not the section
- The `wrap` hook order follows the tested result in the Langchain book

## Sources and further reading

- Live-Class-2026, `GLOSSARY.md` (a short table with links to the class summaries)
- Live-Class-2026, `classes_transcription_summary/glossary.md` (about 140 entries). The source glossaries link to a different GitHub repository; those links are not reused here

Previous: [Chapter 3, Inside the model](03-inside-the-model.md)
