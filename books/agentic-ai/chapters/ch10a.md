# Streaming agent output
> lead: How to show an agent's work while it runs: step updates, live tokens, custom progress, reasoning, tool-call fragments, and the newer typed "event streaming" API. From the LangChain documentation.

meta: LangChain docs | read 30 Oct 2026 | 25 min read | Not covered in class

:::note This chapter comes from the docs, not the class
The course did not teach streaming. This chapter is built from the LangChain "Streaming" and "Event streaming" pages. Version numbers matter here because the API changed recently, so each one is stated next to the feature.
:::

## Why it matters

An agent can take many seconds, because it loops over model calls and tools. Without streaming the user stares at a blank screen. Streaming lets you show **what step the agent is on**, **tokens as they arrive**, and **progress from long tools**. In interviews it comes up as "how would you build a responsive agent UI".

## Core ideas

### 1. Two streaming APIs

| API | Call | Output | Use |
| --- | --- | --- | --- |
| Stream modes | `agent.stream(..., stream_mode=...)` | Chunks you branch on by mode | Lower level, works everywhere |
| Event streaming | `agent.stream_events(..., version="v3")` | A run object with typed projections | The docs' recommendation for new apps (introduced in LangChain v1.3) |

Agents run on LangGraph, so they share its streaming machinery.

### 2. The three stream modes

| Mode | What you get |
| --- | --- |
| `updates` | The state update after each agent step (one event per step) |
| `messages` | `(token, metadata)` pairs from any node that calls an LLM |
| `custom` | Anything you write yourself from a tool or node |

The docs' mode table does not list `values` or `debug`; they point to the LangGraph streaming docs for those. You can pass several modes as a list, for example `["updates", "custom"]`.

```python
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "Weather in Paris?"}]},
    stream_mode="updates",
):
    print(chunk)
```

For one tool call, `updates` shows three events: the **model node** (the tool-call request), the **tools node** (the `ToolMessage`), then the **model node** again (the final answer).

### 3. Live tokens with `messages`

```python
for chunk in agent.stream(inputs, stream_mode="messages", version="v2"):
    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
```

`metadata["langgraph_node"]` tells you which node produced the token. The chunks also carry `tool_call_chunk` entries holding partial JSON arguments.

:::key version="v2" gives every chunk the same shape
Requires LangGraph 1.1 or later. Each chunk is a dict with `type`, `ns` and `data`, so you branch on `chunk["type"]` instead of unpacking tuples. With `invoke(..., version="v2")` the result is a `GraphOutput` with `.value` (the state) and `.interrupts` (empty if none).
:::

### 4. Custom progress from a tool

```python
from langgraph.config import get_stream_writer

@tool
def lookup(city: str) -> str:
    """Look up data for a city."""
    writer = get_stream_writer()
    writer(f"Looking up data for city: {city}")
    return "..."
```

Consume it with `stream_mode="custom"`. The writer works only inside a LangGraph execution, so calling the tool by hand outside an agent fails.

### 5. Multiple modes at once

Pass `stream_mode=["updates", "custom"]`. Each chunk is a `StreamPart` dict (`type`, `ns`, `data`) and you branch on `chunk["type"]`.

### 6. Streaming reasoning

Filter content blocks for `type == "reasoning"`. The model must have reasoning switched on; the docs' example uses `ChatAnthropic` with `thinking={"type": "enabled", "budget_tokens": 5000}`. LangChain normalises each provider's format into one `reasoning` block type (Chapter 3 lists the block types).

### 7. Streaming tool calls: partial vs complete

- **Partial arguments** arrive as `tool_call_chunks` in `messages` mode.
- **Completed calls** need `stream_mode=["messages", "updates"]`, or you aggregate the chunks yourself.

To aggregate, add the chunks together with `+` and treat the one with `chunk_position == "last"` as final. Then read `full_message.tool_calls`.

### 8. Human-in-the-loop while streaming

The pause appears as an `__interrupt__` entry in `updates` mode. Build one decision per interrupt (order must match the action requests), then resume with `agent.stream(Command(resume=decisions), config=config, ...)`. A checkpointer and `thread_id` are still required (Chapter 10).

### 9. Sub-agents: who is speaking?

Give each agent a `name=` in `create_agent`; it appears in message metadata as `lc_agent_name`. Pass `subgraphs=True` to `stream()` so nested agents' output reaches you. Reading `lc_agent_name` tells your UI which agent is emitting tokens.

### 10. Turning streaming off

`ChatOpenAI(..., streaming=False)` disables token streaming for that model. For integrations without a `streaming` argument use `disable_streaming=True`, which is on the base chat model class. The docs suggest this for models whose output should not reach the client on a LangSmith deployment.

## Event streaming (the recommended API)

```python
stream = agent.stream_events({"messages": [...]}, config=config, version="v3")
for kind, item in stream.interleave("messages", "tool_calls"):
    ...
final_state = stream.output
```

Instead of one mixed stream you get **separate iterators per projection**, so each part of your UI reads only what it needs.

| Projection | What it gives you |
| --- | --- |
| `stream.messages` | One `ChatModelStream` per model call |
| `message.text` | Text deltas, plus the final text |
| `message.reasoning` | Reasoning deltas, if the model emits them |
| `message.tool_calls` | Argument chunks as they arrive; `.get()` returns parsed calls |
| `message.output` | The final AI message (read usage from `message.output.usage_metadata`) |
| `stream.values` | State snapshots |
| `stream.output` | The final agent state |
| `stream.tool_calls` | Tool lifecycle: `tool_name`, `input`, `output_deltas`, `output`, `error` |
| `stream.subagents` | Handles for named `create_agent` sub-agents (`.messages`, `.values`, `.tool_calls`, `.output`, `.name`, `.cause`) |
| `stream.subgraphs` | All nested graph runs, including plain subgraphs |
| `stream.extensions` | Custom projections, keyed by name |

:::tip Sync and async
Sync: `stream.interleave("messages", "tool_calls", "values")` yields `(name, item)` pairs in arrival order. Async: `await agent.astream_events(..., version="v3")`, then consume `stream.messages` and `stream.tool_calls` together with `asyncio.gather`.
:::

:::note Version gate for tool-call chunks
Delta-only tool-call chunks need `langchain-core>=1.6.13`. Earlier versions send the cumulative arguments in every chunk, so concatenating them would repeat text.
:::

### Custom transformers (the advanced part)

When you need a projection that does not exist, for example retrieval progress, write a **transformer** and pass `transformers=[...]`; read it back from `stream.extensions[name]`. A middleware class can ship its own by setting a `transformers` attribute (needs `langchain>=1.3.2`). The order is built-in tool-call transformer first, then middleware transformers in middleware order, then the ones you pass to `create_agent`.

:::key Why PII redaction must touch the stream too
`after_model` redaction changes saved state, but a live reader could still see raw text as it streamed. `PIIMiddleware(..., apply_to_output=True)` also registers a transformer that redacts text deltas, tool arguments, tool outputs and state snapshots **before** they reach a live reader (needs `langchain>=1.3.2`). This links Chapters 8 and 10a.
:::

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Using `get_stream_writer()` in a tool you call directly | Fails outside a LangGraph run | Only rely on it inside an agent run |
| Forgetting `subgraphs=True` with sub-agents | Inner tokens never arrive | Pass it and read `lc_agent_name` |
| Concatenating tool-call chunks on an old `langchain-core` | Repeated or garbled arguments | Upgrade, or aggregate and use `chunk_position == "last"` |
| Streaming HITL without a checkpointer | Cannot resume | Add a checkpointer and reuse the thread id |
| Expecting `stream_mode` tables to list `values` | Not found in the agent page | See the LangGraph streaming docs |

## Hands-on lab

1. Run one agent with `stream_mode="updates"` and write down the three events for a single tool call.
2. Switch to `messages` and print only the text tokens.
3. Add a tool that calls `get_stream_writer()` and watch `custom` mode.
4. Try `["updates", "custom"]` with `version="v2"` and branch on `chunk["type"]`.
5. Enable reasoning on a model that supports it and print only `reasoning` blocks.
6. Rewrite the loop with `stream_events(..., version="v3")` and iterate `stream.messages`.
7. Add `PIIMiddleware("email", apply_to_output=True)` and compare what a live reader sees.

## Interview corner

:::pitch
I choose between stream modes and event streaming. For new apps I use event streaming with typed projections so my UI reads messages, tool calls and state independently. For lower-level control I use `updates` for step progress, `messages` for tokens and `custom` for progress my tools write. With sub-agents I name each agent and enable subgraph streaming, and with human-in-the-loop I watch for the interrupt and resume with a `Command`.
:::

### Basics

:::qa What are the three stream modes in the LangChain agents docs?
`updates` (state after each step), `messages` (token plus metadata from any LLM node) and `custom` (data your own code writes with the stream writer).
:::

:::qa How do you stream tokens?
`stream_mode="messages"`. Each item has the token and metadata, and `metadata["langgraph_node"]` says where it came from.
:::

:::qa How does a tool report progress?
It calls `get_stream_writer()` and writes values, which arrive in `custom` mode. It only works inside a LangGraph run.
:::

### Intermediate

:::qa What does `version="v2"` change?
Every chunk becomes a dict with `type`, `ns` and `data`, so you branch on `type` instead of unpacking tuples. `invoke(version="v2")` returns a `GraphOutput` with `.value` and `.interrupts`. Needs LangGraph 1.1 or later.
:::

:::qa How do you stream a sub-agent's output and know who is speaking?
Set `name=` on each agent, pass `subgraphs=True` to `stream()`, and read `lc_agent_name` from the metadata.
:::

:::qa How do you get complete tool calls while streaming?
Use `["messages", "updates"]`, or add the `tool_call_chunk`s together and finish when `chunk_position == "last"`, then read `tool_calls`.
:::

### Tricky

:::qa Why is event streaming "typed projections" better than stream modes?
Each projection (messages, tool calls, values, sub-agents) is its own iterator, so a component consumes only what it needs without branching on mode strings. You can also drain a projection to get the final value, or interleave several in arrival order.
:::

:::qa A user's email appears in a live stream even though you redact in `after_model`. Why?
Redacting state does not touch tokens already sent to a live reader. Use `PIIMiddleware` with `apply_to_output=True`, which also registers a stream transformer so streamed text, tool arguments, outputs and snapshots are redacted before they are delivered.
:::

:::qa When would you write a custom transformer?
When you need a projection the built-ins do not offer, for example retrieval progress or artifacts. Pass it in `transformers=[...]` or ship it from middleware, then read `stream.extensions[...]`.
:::

## Quick revision

- [ ] I can name the three stream modes and what each emits
- [ ] I can stream tokens and read the source node
- [ ] I can write progress from a tool with the stream writer
- [ ] I can explain `version="v2"` and `version="v3"`
- [ ] I can list the event-streaming projections
- [ ] I can stream sub-agents and identify the speaker
- [ ] I can explain why output PII redaction needs a stream transformer

<!-- docs31e -->
## From the docs: a voice agent built on streaming

*From the LangChain tutorial [Build a voice agent with LangChain](https://docs.langchain.com/oss/python/langchain/voice-agent), read in full on 31 Oct 2026.*

Every voice agent does three things: **listen** (capture and transcribe audio), **think** (interpret and reason) and **speak** (generate audio and stream it back). Two architectures:

| | Sandwich (STT, agent, TTS) | Speech-to-speech |
| --- | --- | --- |
| Idea | Speech-to-text, a text LangChain agent, then text-to-speech | One multimodal model takes audio in and gives audio out |
| Good | Full control of each part, swap providers, newest text-model features, transparent | Simpler, often lower latency for simple turns, captures tone |
| Bad | Orchestrating several services, and speech to text loses tone and emotion | Few model options, lock-in risk, features lag, less control |

The page builds the sandwich (it says it can reach under 700 ms latency with some providers) for a sandwich-shop order agent, with AssemblyAI for speech-to-text and Cartesia for text-to-speech; a full reference app is in the `voice-sandwich-demo` repository. A browser captures microphone audio as PCM and streams it over a WebSocket to a Python server (the same design adapts to telephony such as Twilio or to WebRTC).

- **Speech-to-text stage:** a producer-consumer pattern. One task pumps audio chunks to the provider while another yields events: `stt_chunk` (partial) and `stt_output` (final transcript, which triggers the agent).
- **Agent stage:** a normal `create_agent` with two tools (`add_to_order`, `confirm_order`), an `InMemorySaver` and a fresh thread id per call for memory. The system prompt says to avoid emojis, special characters and markdown because a speech engine reads the reply. It streams with `agent.astream_events(..., version="v3")` and `stream.messages`, yielding each token as an `agent_chunk` so synthesis can start at once.
- **Text-to-speech stage:** merges two async streams, the upstream events (sending agent text to the provider) and the audio chunks coming back. Cartesia starts synthesising as soon as it gets text, so playback begins before the agent finishes.
- **Composition:** the three stages are `RunnableGenerator`s chained with `|`, and `pipeline.atransform(audio_stream)` runs them concurrently inside a FastAPI WebSocket endpoint. Each stage starts as soon as its input arrives, which is where the low latency comes from.
<!-- /docs31e -->

## Sources and further reading

- [Streaming (LangChain docs)](https://docs.langchain.com/oss/python/langchain/streaming)
- [Event streaming (LangChain docs)](https://docs.langchain.com/oss/python/langchain/event-streaming)
- [Models: streaming and token usage (LangChain docs)](https://docs.langchain.com/oss/python/langchain/models)
