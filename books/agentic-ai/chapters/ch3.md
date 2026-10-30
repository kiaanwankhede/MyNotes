# Inside the model
> lead: Everything LangChain exposes around a single model call: parameters, messages, the full response object, streaming, batching, tool binding and structured output.
meta: Class 08 | 19 July | 35 min read | Code: Weekend 04

## Why it matters

Anyone can run a five-minute quickstart. Real engineering means understanding every knob around the model: the **input** (messages), **parameters** (temperature, max tokens), **tools** and **structured output**. Interviews probe exactly these, especially "what does `bind_tools` actually do?" and "does batching save tokens?"

:::key Under every framework, it is just an API call
LangChain, OpenRouter, Claude and the raw `chat.completions` code from the primer are all a standard API request and a standard API response. No framework adds magic. Knowing this makes any new framework easier to learn.
:::

## Core ideas

### 1. Model parameters

```python
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "openai:gpt-5.5",
    temperature=0.5,
    max_tokens=1000,
    timeout=30,
    max_retries=6,
)
```

| Parameter | What it controls | Notes |
| --- | --- | --- |
| `model` | Which LLM to use | The only required field |
| `api_key` | Credentials | Optional: LangChain reads the standard environment variable |
| `temperature` | Randomness and creativity | Lower is steadier, higher is more varied |
| `max_tokens` | Cap on output length | Raising it fixes the common OpenRouter error where a reply exceeds the limit |
| `timeout` | How long to wait for a reply | In seconds |
| `max_retries` | Retries before giving up | Default is 6 |

These are passed as **keyword arguments**, explicit `key=value` pairs next to the model name.

:::note Free tiers have real limits
OpenRouter's free tier showed a limit of about 20 requests a minute and 50 a day in class. Groq hosts mostly open-source models and pays the hosting itself, which is why access is free or cheap. Free models generally trail flagship quality; that gap is the price.
:::

### 2. Messages, and few-shot prompting

The message types are System, Human and AI (plus Tool, in Chapter 2). A few facts that come up:

- A single "hi" to Claude actually sends **thousands of tokens**, because the hidden system message goes with it.
- In a finished product like the Claude app, the provider fixes the system message. When **you** build an agent, you control it. That is the point of building your own harness.
- Messages can be dictionaries (`{"role": "system", "content": ...}`) or classes. They behave the same. The instructor prefers classes for readability.

:::analogy A real debugging story: examples beat essays
A co-pilot style chatbot performed poorly despite a strong system message. Instead of adding more instructions, the instructor inserted a few **example exchanges** as separate prior messages: a sample user message, then a sample AI reply, before the real question. Output improved noticeably. A senior colleague named it: **few-shot prompting**.
:::

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="You are a helpful support assistant."),
    HumanMessage(content="Example question..."),
    AIMessage(content="Example ideal answer..."),
    HumanMessage(content="Actual user question here"),
]
response = model.invoke(messages)
```

:::tip Rule of thumb
Keep the system message short. If the model is inconsistent, show it two or three examples before piling on more rules.
:::

### 3. Anatomy of the response

Every call returns an `AIMessage`, with far more than the text.

| Field | What it holds |
| --- | --- |
| `.text` | The reply as a plain string |
| `.content` | Raw content: usually the same as text, but can be a list of blocks |
| `.content_blocks` | LangChain's standard structure for rich content (text, reasoning, citations, images) across providers |
| `.tool_calls` | Tool requests the model made (empty list if none) |
| `.id` | Unique id of this message |
| `.usage_metadata` | **Exact** token counts: input, output, total |
| `.response_metadata` | Provider extras: which model answered, why it stopped |

```python
response = model.invoke("Hello!")
print(response.usage_metadata)
# input_tokens, output_tokens, total_tokens, plus finer breakdowns such as cached or reasoning tokens
```

:::tip Track spend without extra libraries
`usage_metadata` carries the exact billed numbers. Sum it across a conversation to track cost per user or per session. No third-party counter needed.
:::

**Restoring history.** You can build an `AIMessage("...")` yourself and place it in the list; the model treats it as if it said it. That is legitimate for restoring a saved conversation or setting up a test. Using it to fake agreement the model never gave can mislead its later reasoning.

### 4. Streaming

```python
for chunk in model.stream("Why do parrots have colorful feathers?"):
    print(chunk.text, end="", flush=True)
```

A 2,000-word answer takes about 5 to 7 seconds, but text appearing piece by piece **feels** faster. That matters in real products: nobody ships a screen frozen for seven seconds. It is built in; just swap `.invoke()` for `.stream()`.

Each piece is an `AIMessageChunk`, and chunks add together with `+` into a full message of the same shape `.invoke()` returns:

```python
full = None
for chunk in model.stream("Write one short sentence about the ocean."):
    full = chunk if full is None else full + chunk
```

### 5. Batching

```python
responses = model.batch([Q1, Q2, Q3])           # parallel, returns all at once
for r in model.batch_as_completed([Q1, Q2, Q3]):  # yields each as it finishes
    print(r)
```

Requests in a batch must be **independent**. A company Q&A portal could collect questions for 15 seconds to a minute and batch them, instead of one call per question.

:::trap "Batching saves tokens"
It does not. Every request in a batch still carries its own full system message and context. What it saves is **cost and time**, from two places: (1) provider batch APIs (OpenAI's, for example, runs jobs asynchronously at roughly half price, which is a pricing decision, not token reduction), and (2) infrastructure, since fewer round trips and connections are needed.
:::

| Method | Use when |
| --- | --- |
| `.invoke()` | One call, wait for the whole answer |
| `.stream()` | One call, show progress |
| `.batch()` | Many independent calls, want all results together |
| `.batch_as_completed()` | Many independent calls, handle each as it finishes (batching plus streaming feel) |

### 6. Binding tools

:::key Binding makes the model aware. It does not run anything.
`bind_tools` tells the model which tools exist and what they do. Calling `.invoke()` afterwards only asks the model to **decide** whether and how to call one. Your code still has to run the function.
:::

```python
def get_weather(location: str) -> str:
    """Get the current weather at a given location."""
    return f"It's sunny in {location}"

model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("What is the weather in Delhi?")

print(response.content)       # '' (empty: the model chose a tool, not text)
print(response.tool_calls)    # [{'name': 'get_weather', 'args': {'location': 'Delhi'}, 'id': '...'}]
```

When the model chooses a tool, `content` is **empty** and everything useful is in `tool_calls`: the tool name, its arguments and an id. Binding takes a list, so more tools (for example a `set_password` function) can sit beside it; the model picks by name and docstring. A plain function works because the `ChatOpenAI` wrapper builds the schema for you.

**Resolving the call by hand** (this is exactly what `create_agent` automates):

1. Read `response.tool_calls` and pick the call.
2. Run `get_weather(location=...)` yourself.
3. Wrap the result in a **`ToolMessage`** with the same `tool_call_id`, not a bare string.
4. Send the message list back to the model for the final answer.

```python
from langchain_core.messages import ToolMessage

tool_message = ToolMessage(
    content="Sunny in Delhi",
    tool_call_id=response.tool_calls[0]["id"],
    name="get_weather",
    artifact={"source": "weather-api"},     # app-only data, never sent to the model
)
```

`ToolMessage` can also carry an **`artifact`** (extra data for your app, hidden from the model, such as a document id for a citation link) and a **`status`** (success or failure), useful later for observability.

### 7. Structured output

Having learned Pydantic, a model should be able to reply in that validated shape instead of free text.

```python
from pydantic import BaseModel, Field

class Email(BaseModel):
    subject: str = Field(description="The email subject line")
    body: str = Field(description="The email body")

structured_model = model.with_structured_output(Email)
response = structured_model.invoke("Write a leave email to my manager")
print(type(response))        # <class 'Email'>, a real object, not a string
```

If your code depends on getting an `Email`, it will not break on a malformed string. Chapter 4 goes much deeper.

### 8. Free and local models

The interface does not change when you go free. Ollama runs on your own machine with no API key:

```python
# first: install Ollama and run `ollama pull llama3.2`
free_model = init_chat_model("ollama:llama3.2")
```

Free of API cost is not free of hardware cost: a model like `llama3.2` needs real RAM, ideally a GPU, and quality differs from a frontier model. Good for development, testing, no internet or tight budgets.

## Questions from class worth knowing

:::qa How do I route a query to the right agent among several specialised ones?
Treat each agent like a **tool**: give the router only a short name and description for each, never their full knowledge files. The router can be an `if` statement or a small LLM call that only classifies, depending on how distinct the domains are. If the descriptions themselves are too big, treat it as a small retrieval problem over agent metadata.
:::

:::qa How do I avoid resending a whole project's context every day?
Keep a running summary file (for example `memory.md`) that the AI updates after each session, and read only that next time. The trade-off, stated honestly in class: summarising saves tokens but can lose detail, so full context and minimal tokens cannot both be maximised. That is why human oversight still matters.
:::

:::qa Does `create_agent` resolve a tool call in one `invoke`?
Normally yes. By default the whole loop completes within a single `invoke`.
:::

:::qa Is a system message the same as a skill?
No. They are different concepts.
:::

<!-- docs-add -->
## From the docs: models in depth

*Added from the LangChain Models page (read 30 Oct 2026).*

**Initialising.** `init_chat_model("openai:gpt-5.5")` or `init_chat_model("gpt-5.5", model_provider="openai")`. Provider classes also exist (`ChatOpenAI`, `ChatAnthropic`, `ChatGoogleGenerativeAI`, `ChatBedrock`, `ChatHuggingFace`, `ChatOpenRouter`). Azure needs `azure_deployment`; Bedrock uses `model_provider="bedrock_converse"`.

| Parameter | Meaning |
| --- | --- |
| `model` | Required, optionally prefixed by provider |
| `temperature` | Higher is more varied, lower is more deterministic |
| `max_tokens` | Caps reply length |
| `timeout` | Seconds before a request is cancelled |
| `max_retries` | **Default 6**, exponential backoff with jitter. Network errors, 429 and 5xx are retried; 401 and 404 are not. The docs suggest 10 to 15 for long agents on flaky networks |

**Invocation methods**

- `invoke()` returns one `AIMessage`. If you get a plain string, you are probably using a legacy LLM class, not a `Chat*` model.
- `stream()` yields `AIMessageChunk`s you can add together (`full = full + chunk`). `astream_events()` emits `on_chat_model_start`, `on_chat_model_stream` and `on_chat_model_end`.
- `batch()` runs independent requests in parallel on the client; `batch_as_completed()` yields results as they finish, out of order, with their input index. Limit parallelism with `config={"max_concurrency": 5}`. This is separate from a provider's own batch API.
- Inside a LangGraph agent, `invoke()` quietly **streams under the hood** when the whole app is streamed, so token callbacks still fire.

**Tool calling details.** `bind_tools` only advertises tools; calls appear in `response.tool_calls` (`name`, `args`, `id`) and your code or the agent loop runs them and returns `ToolMessage`s with the matching `tool_call_id`. `tool_choice="any"` forces some tool call and a tool name forces that tool. `parallel_tool_calls=False` turns off parallel calls on providers such as OpenAI and Anthropic. **Server-side tools** (for example `{"type": "web_search"}`) run on the provider; results arrive as `server_tool_call` and `server_tool_result` blocks and need no `ToolMessage`.

**Structured output on a bare model.** `with_structured_output(schema, method=...)` with a Pydantic model, `TypedDict` or JSON Schema. Methods: `json_schema` (native), `function_calling` (a forced tool call) and `json_mode` (valid JSON, schema described in the prompt). `include_raw=True` returns `{"raw", "parsed", "parsing_error"}`, handy for token counts.

**Model profiles** (`langchain>=1.1`, beta). `model.profile` lists capabilities such as `max_input_tokens`, `image_inputs`, `reasoning_output` and `tool_calling`; agents and middleware use them to choose behaviour. Override with `init_chat_model(..., profile={...})`.

**Reasoning.** Read reasoning blocks from `content_blocks`. `reasoning_effort` is a standard parameter (set at construction or per call, for example `invoke(..., reasoning_effort="high")`) on several providers. Valid values are in `model.profile["reasoning_effort_levels"]`.

**Prompt caching.** Some providers cache implicitly (OpenAI, Gemini). Explicit controls include `prompt_cache_key` (OpenAI), `cache_control` blocks (Anthropic) and `cachePoint` (Bedrock), plus `AnthropicPromptCachingMiddleware` and `BedrockPromptCachingMiddleware`. Caches often need a minimum token count, and hits show in usage metadata.

**Exceptions** (`langchain_core.exceptions`). Each inherits both the LangChain base and the provider SDK's exception and has `is_retryable`. **Not retryable:** `ModelAuthenticationError`, `ModelPermissionDeniedError`, `ModelInvalidRequestError`, `ModelNotFoundError`, `ContextOverflowError`. **Retryable:** `ModelRateLimitError`, `ModelAPIError`, `ModelConnectionError`, `ModelTimeoutError`.

**Rate limiting.** `InMemoryRateLimiter(requests_per_second=..., check_every_n_seconds=..., max_bucket_size=...)` passed as `rate_limiter=`. It is thread-safe in one process and limits request **count**, not request **size**.

**Other settings.** `base_url` (with `model_provider="openai"`) targets OpenAI-compatible servers such as vLLM; for OpenRouter or LiteLLM use their own classes, because the generic path can drop provider-specific fields. `.bind(logprobs=True)` then read `response_metadata["logprobs"]`. Ollama is the suggested way to run models locally.

**Token usage.** `response.usage_metadata` has input, output and total tokens plus detail fields such as `cache_read` and `reasoning`. `UsageMetadataCallbackHandler` (in `config={"callbacks": [...]}`) or the `get_usage_metadata_callback()` context manager aggregates per model.

**Run config** (`RunnableConfig`): `run_name`, `tags`, `metadata`, `callbacks`, `max_concurrency`, `recursion_limit`. Tags and metadata propagate to sub-calls; `run_name` does not.

**Configurable models.** `init_chat_model(temperature=0)` with no model makes `model` and `model_provider` configurable per call; `configurable_fields=(...)` and `config_prefix="first"` expose more. Pass values under `config={"configurable": {...}}`.

:::trap Dynamic model choice and structured output
When picking a model per call with `wrap_model_call`, pass **unbound** models. A model already passed through `bind_tools` does not work with structured output in that pattern.
:::

## From the docs: messages in depth

*Added from the LangChain Messages page (read 30 Oct 2026).*

- **Three input forms**: a plain string, a list of message objects, or OpenAI-style dicts with `role` and `content`.
- **`HumanMessage`** can carry text, images, audio, files or video, with optional `name` and `id`. **`AIMessage`** has `text`, `content`, `content_blocks`, `tool_calls`, `id`, `usage_metadata` and `response_metadata`.
- **`ToolMessage`** needs `content`, a matching `tool_call_id` and `name`. Its optional **`artifact`** holds data **for your application only** (for example document ids and page numbers), not sent to the model.
- **`content`** can be a string, provider-native blocks, or standard blocks. **`content_blocks`** lazily converts it to a typed standard form; provider reasoning (Anthropic thinking, OpenAI reasoning items) maps to a standard `reasoning` block. To store standard blocks in `content`, set `LC_OUTPUT_VERSION=v1` or `output_version="v1"` on the model.
- **Block types**: `text` (with `annotations`), `reasoning`, `image`, `audio`, `video`, `file`, `text-plain`, `tool_call`, `tool_call_chunk`, `invalid_tool_call` (malformed calls such as JSON parse failures), `server_tool_call`, `server_tool_call_chunk`, `server_tool_result` (with `status` of success or error) and `non_standard` (an escape hatch for provider-specific data).
- **Multimodal sources** are `url`, `base64` (with a **required** `mime_type`) or `file_id`. File types and size limits depend on the provider.
- **Serialisation**: `dumpd(message)` to a dict and `load(data)` back.

:::trap Never `load()` untrusted data
`load()` rebuilds objects and can trigger side effects. The docs warn against using it on untrusted or unauthenticated data. This links to the LangChain serialization vulnerability (CVE-2025-68664) noted in Chapter 1.
:::
<!-- /docs-add -->

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Expecting `bind_tools` to run the tool | Empty `content`, nothing happens | Run the tool yourself or use `create_agent` |
| Sending the tool result as a plain string | Model cannot link it to its request | Use `ToolMessage` with the same `tool_call_id` |
| Reply exceeds the limit (OpenRouter) | Error on long output | Raise `max_tokens` |
| Believing batching reduces tokens | Wrong cost estimates | It saves time and money via provider batch APIs, not tokens |
| Batching dependent requests | Wrong answers | Batch only independent requests |
| Piling instructions into the system message | Inconsistent results | Add few-shot example messages |
| Waiting for the full reply in a UI | Screen feels frozen | Use `.stream()` |
| Faking `AIMessage` history to bias the model | Misleading later reasoning | Insert only genuine history |

## Hands-on lab

1. Set `temperature`, `max_tokens`, `timeout` and `max_retries` explicitly and watch the differences.
2. Build a few-shot message list and compare it with a plain system-message version.
3. Stream a long answer and print chunks as they arrive, then add them with `+`.
4. Batch three questions, then try `batch_as_completed` and compare the experience.
5. `bind_tools` a function, call `invoke`, inspect `tool_calls`, and notice nothing ran.
6. Resolve the call by hand with a `ToolMessage`.
7. Use `with_structured_output` on a Pydantic class and print the type.

## Interview corner

:::pitch
A model call returns an `AIMessage` with the text, any tool calls, exact token usage and metadata. I can stream it for responsiveness, batch independent requests for throughput, bind tools so the model can request them (though my code or the agent runs them), and use structured output to get a validated object. Underneath it is always one API request and response.
:::

### Basics

:::qa What does `bind_tools` do?
It tells the model which tools exist and describes them. It does **not** execute anything. After `.invoke()`, the response has empty `content` and a `tool_calls` list with the name, arguments and id. You (or `create_agent`) must run the function and return a `ToolMessage`.
:::

:::qa What is in the `AIMessage` besides the text?
`.content` and `.content_blocks`, `.tool_calls`, `.id`, `.usage_metadata` (exact token counts) and `.response_metadata` (provider details such as the model and stop reason).
:::

:::qa Invoke, stream or batch?
Invoke for one answer. Stream when a person is watching, so output appears progressively. Batch for many independent requests. `batch_as_completed` returns each result as it finishes.
:::

:::qa What is few-shot prompting?
Showing the model a few example input and output pairs, here as prior Human and AI messages, before the real question. It often beats a longer system message.
:::

### Intermediate

:::qa Does batching save tokens?
No. Each request still carries its own system message and context. It saves cost and time: provider batch APIs (about half price for asynchronous jobs, for example OpenAI's) and fewer round trips and connections at scale.
:::

:::qa What happens between the model asking for a tool and the final answer?
The model replies with empty content and a `tool_call` (name, arguments, id). Your code runs the function, wraps the result in a `ToolMessage` with the same `tool_call_id`, and sends the history back. The model then answers using the result.
:::

:::qa What are `artifact` and `status` on a `ToolMessage`?
`artifact` carries extra data for your application that is never sent to the model, such as a document id for a citation. `status` records success or failure, useful for tracing.
:::

:::qa How do you get cost per user without a token-counting library?
Sum `usage_metadata` across the conversation. It holds the exact tokens the provider billed.
:::

### Tricky

:::qa How would you route a user to one of five specialised agents?
Treat the agents like tools. Give the router a short name and description per agent, not their full knowledge. Use a plain `if` when domains are distinct, a small classifier LLM when they overlap, and retrieval over agent descriptions if those descriptions are large.
:::

:::qa How do you carry context across a multi-day project without huge token cost?
Maintain a summary file the AI updates after each session and load only that. State the trade-off: summaries can drop detail, so keep a human in the loop for complex work.
:::

:::qa Is it fine to insert an `AIMessage` you wrote yourself?
Yes, for restoring genuine saved history or setting up a test, because the model treats it as its own prior turn. It is not fine for fabricating agreement to steer the model dishonestly, because that misleads its later reasoning.
:::

:::qa Are LangChain calls different from raw API calls underneath?
No. Every route (raw Python, LangChain, OpenRouter, Claude) is a standard API request with parameters and a body, and a standard response. LangChain adds a consistent interface, not a different mechanism.
:::

<!-- assign-add -->
### Course assignment questions

*From `Assignment_LangChain_Fundamentals_Landscape_to_Tools.ipynb` and its answer-key notebook (Weekend 05, the GreenPlate restaurant scenario). Answers are condensed from the instructor's key.*


:::qa Name four things an `AIMessage` carries besides `.content`.
`.tool_calls` (tool requests), `.usage_metadata` (real token counts), `.id` (unique identifier), `.response_metadata` (provider extras such as the exact model that replied). `.content_blocks` is also acceptable.
:::

:::qa Why does streaming produce `AIMessageChunk` objects, not plain strings?
A stream is a partial response that must later combine into a whole. Chunks can be added with `+` into a complete message and can carry structure (tool-call fragments, metadata) that a string fragment cannot.
:::

:::qa `.batch()` versus `.batch_as_completed()`?
`.batch()` waits for all results and returns them in input order. `.batch_as_completed()` yields each result as soon as it finishes, possibly out of order, tagged with its input index. Use the second when you want to start on whichever result arrives first instead of waiting for the slowest.
:::

:::qa `ToolMessage` has `.content` and `.artifact`. What is the difference?
`.content` is what the **model** reads; `.artifact` is extra data for the **application** that is never sent to the model. A retrieval tool uses it to attach a document id or citation link for the UI without bloating the model's input.
:::

:::qa Your prompt template contains a literal JSON example such as `{"status": "ok"}`. What breaks?
LangChain reads the braces as more template variables and fails (`INVALID_PROMPT_INPUT`). Escape them by doubling: `{{` and `}}`.
:::

:::qa What does `MessagesPlaceholder` do that a string variable cannot?
It injects a whole **list** of prior messages as one template variable. A string variable holds a single string and cannot represent a structured message history.
:::
<!-- /assign-add -->

## Quick revision

- [ ] I know the six model parameters and which one is required
- [ ] I can explain few-shot prompting with the story
- [ ] I can list the fields on an `AIMessage` and where exact token usage lives
- [ ] I know invoke, stream, batch and `batch_as_completed`
- [ ] I can say precisely what batching does and does not save
- [ ] I can resolve a tool call by hand with a `ToolMessage`
- [ ] I can get a typed object with `with_structured_output`

## Sources and further reading

- [Class 08 full notes]({{src:classes_transcription_summary/08 - 19 Jul - LangChain - Inside the Model.md}})
- [Class 08 short summary]({{src:classes_summary/08 - 19 Jul - Inside the Model.md}})
- [Environment, models and messages notebook]({{src:Weekend 04 - 18-19 Jul/07-08 - 18-19 Jul - LangChain Family & the Model Layer/Notebook For Reference/02_03_environment_models_messages_student_notes.ipynb}})
- [Revision notebook, parts 1 to 4]({{src:Weekend 04 - 18-19 Jul/07-08 - 18-19 Jul - LangChain Family & the Model Layer/Notebook For Reference/Revision_Parts_1-4.ipynb}})
- [LangChain practical project]({{tree:Weekend 04 - 18-19 Jul/07-08 - 18-19 Jul - LangChain Family & the Model Layer/Langchain Practical/langchain-course}})
- [Weekend 04 code folder]({{tree:Weekend 04 - 18-19 Jul/07-08 - 18-19 Jul - LangChain Family & the Model Layer}})
