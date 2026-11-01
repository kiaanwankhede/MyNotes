# Chapter 3: Models, messages and parameters

**After this chapter you can:**

- Call any model through one interface
- Set the parameters that matter
- Build message lists (and few-shot prompts)
- Read everything inside a model reply
- Choose between `invoke`, `stream` and `batch`
- Write prompt templates without the brace bug

**Before this:** [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md) (the loop by hand), [Chapter 1](01-introduction-to-langchain.md) and [Chapter 2](02-langchain-family-and-harness-engineering.md).

## 3.1 The first model call

`init_chat_model` is LangChain's universal entry point. Change the provider string, the rest of the code stays the same.

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-5")
response = model.invoke("Tell me what LangChain is")
print(response.content)
```

- Without LangChain you write different code for OpenAI, Claude, Groq, OpenRouter. LangChain puts them behind one interface
- The "give me any LLM" pattern appears in other frameworks too (CrewAI's docs use it), so it transfers
- **Models differ in capabilities:** tool calling, structured output, multimodality (text + images), reasoning. Look up the model's capability sheet before you plan around a feature ([Chapter 4](04-structured-output.md), section 4.7, shows `model.profile`)

**Messages steer behaviour.** A system message and a human message go in as a list:

```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="You are a pirate. Answer everything in pirate language."),
    HumanMessage(content="What is the capital of France?"),
]
print(model.invoke(messages).content)     # pirate-flavoured: the system message steers the model
```

- Roles match [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md)
- The chat model does **not** manage history. You pass the history in

### Why LangChain's one interface matters: the same question through three SDKs

The class notebook asked "What is the capital of France" through each provider's **own** Python SDK. The three shapes differ:

| Provider SDK | Call | Where the text is |
|---|---|---|
| Anthropic | `client.messages.create(model=..., max_tokens=..., messages=...)` | `response.content[0].text` |
| Google (Gemini) | `client.models.generate_content(model=..., contents=...)` | `response.text` |
| OpenAI | `client.chat.completions.create(model=..., messages=...)` | `response.choices[0].message.content` |

- Each also needs its own package, its own key variable and its own error handling
- `init_chat_model("provider:model").invoke(...)` is **one call, one reply type**, whatever the provider
- *Not run here: it needs three provider keys. The shapes are from the class notebook*

## 3.2 Where your API key lives

- If `.env` is not in `.gitignore`, the first push sends your real key to GitHub with the code
- Scanners find leaked keys, often within minutes

```python
import os
from dotenv import load_dotenv
load_dotenv()
assert os.environ.get("OPENAI_API_KEY"), "Missing OPENAI_API_KEY -- check your .env file"
```

- Error? Either `.env` is not in the folder you run from, or you created it after the session started
- Second case: **restart the kernel** so `load_dotenv()` picks it up

## 3.3 Model parameters

`init_chat_model` takes the model name plus keyword arguments.

- **`model`:** the only required one, for example `"openai:gpt-5-mini"`
- **`api_key`:** optional. LangChain reads the standard variable (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, ...)
- **`temperature`:** randomness and creativity. Low = steady, high = varied
- **`max_tokens`:** caps the length of the reply
- **`timeout`:** how long to wait for the model before giving up
- **`max_retries`:** how many times to retry (default 6)

```python
deterministic = init_chat_model("openai:gpt-5-mini", temperature=0.0, max_tokens=200, timeout=30)
creative      = init_chat_model("openai:gpt-5-mini", temperature=1.0, max_tokens=200, timeout=30)

prompt = "Describe a sunset in one creative sentence."
print(deterministic.invoke(prompt).content)   # nearly identical on every run
print(creative.invoke(prompt).content)        # varies run to run
```

- Car-dashboard picture: temperature = creative liberty, `max_tokens` = fuel ceiling on the reply, `timeout` = how long you wait at a red light, `max_retries` = how many times you retry starting the car
- Common OpenRouter error: reply longer than the allowed limit. Raise `max_tokens`
- OpenRouter's free router: `init_chat_model("openrouter/free")` once `OPENROUTER_API_KEY` is set

**Paid, free and local**

- **Paid** (OpenAI, Anthropic, Gemini): billed per token
- **Free tiers** (OpenRouter, Groq, NVIDIA): rate limited. In class OpenRouter's free tier hit 20 requests a minute and 50 a day (class numbers, may have changed)
- **Groq:** hosts mostly open-source models. That is the trade for free or cheap access
- **Local (Ollama):** no API cost, but needs real RAM (ideally a GPU). Quality trails a frontier paid model
- Same interface, different intelligence

```python
paid_model = init_chat_model("openai:gpt-5-mini")
# local_model = init_chat_model("ollama:llama3.2")   # runs on your machine, no API key
```

## 3.4 Messages

**Why a message list?** One long string mixes instructions with the user's words, so the model cannot tell them apart. A message list labels each piece with **who said it**.

Four message types:

- **System:** behaviour, tone, rules (the "director's note", not part of the scene)
- **Human:** the user's input
- **AI:** the model's earlier reply
- **Tool:** a tool's result, sent back to the model ([Chapter 5](05-tools.md))

Good to know:

- A single "hi" to Claude sends thousands of tokens once the hidden system message counts
- In a finished product (Claude's web app) the provider fixes the system message. In your own agent **you** control it
- The system message can change whichever model sits behind it
- A system message is **not** a "skill"

**Message shapes**

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 1. objects (readable, preferred)
[SystemMessage("be brief"), HumanMessage("hi")]
# 2. dictionaries (common when history comes from a database or JSON API)
[{"role": "system", "content": "be brief"}, {"role": "user", "content": "hi"}]
# 3. tuple and bare string (a bare string becomes a human message)
[("human", "hi")]
```

- No functional difference between objects and dicts. Use objects for readability
- Plain text: one standalone request, no history
- Message objects: multi-turn, multimodal, system instructions
- A dict with no `content`, or an unknown `role`, raises an error (`MESSAGE_COERCION_FAILURE`)

`HumanMessage` has two optional fields:

```python
HumanMessage(content="Hi, how are you?", name="mayank", id="user_1234")
# name: label who is speaking in a multi-user chat. id: stable message identifier
```

### Few-shot prompting

- Story from class: a co-pilot style chatbot did poorly even with a good system message
- Fix: put a few example exchanges into the conversation **before** the real question
- The model copies the pattern it is shown. This is **few-shot prompting**

```python
messages = [
    SystemMessage(content="You are a helpful support assistant."),
    HumanMessage(content="Example question..."),
    AIMessage(content="Example ideal answer..."),     # an example, not a real earlier reply
    HumanMessage(content="Actual user question here"),
]
response = model.invoke(messages)
```

**Caution on inserting history by hand**

- Fine for restoring **real** conversation history
- Not a trick to make the model "believe" it agreed to something. A made-up `AIMessage` is treated as real context either way

## 3.5 What comes back: the full `AIMessage`

A call returns far more than text.

- **`.text`:** the plain reply, always a string
- **`.content` / `.content_blocks`:** raw content, or the standard structure for rich content (text, reasoning, citations, images)
- **`.tool_calls`:** tool calls requested, empty list if none
- **`.id`:** unique message id
- **`.usage_metadata`:** real token counts (`input_tokens`, `output_tokens`, `total_tokens`)
- **`.response_metadata`:** provider extras, such as the exact model and why it stopped

```python
response = model.invoke("Explain agentic AI in one sentence.")
print("text:      ", response.text)
print("tool_calls:", response.tool_calls)      # empty: no tools bound yet
print(response.usage_metadata)
```

- `.content` is usually the same as `.text` but can be a list of blocks for richer replies
- `pprint(response)` shows everything on the object
- No separate token-counting library needed. The billed numbers are on the response
- `usage_metadata` can hold finer detail (`input_token_details`, `output_token_details`, for example cached and reasoning tokens)
- **Reasoning models spend hidden tokens.** In the class run, a one-line pirate answer to "capital of France" reported `input_tokens: 27` and `output_tokens: 151`, and `output_token_details.reasoning` was **128** of those. The visible reply was a few words. Read the field, do not guess the cost from the length of the text
- **Cost per user or session:** add up `usage_metadata` across the conversation. It is the exact billed number, not an estimate
- Streaming, structured output and tool calling all build on reading these fields correctly

## 3.6 Streaming: it feels fast

- About 2,000 words took roughly 5 to 7 seconds to generate in ChatGPT, but the text appears piece by piece
- Streaming does not make the answer arrive sooner. The wait **feels** shorter
- Nobody wants a frozen screen for seven seconds in a product

```python
for chunk in model.stream("Why do parrots have colorful feathers?"):
    print(chunk.text, end="", flush=True)
```

- Built into the model call. Swap `.invoke()` for `.stream()`, install nothing
- Each chunk is an `AIMessageChunk`. Chunks add together with `+`:

```python
full = None
for chunk in model.stream("Write one short sentence about the ocean."):
    full = chunk if full is None else full + chunk
print("Reconstructed:", full.content)
```

- `.invoke()` was never called, yet the summed message has the same shape as one from `.invoke()`

## 3.7 Batching

Asking one question, waiting, asking the next is slow. `.batch()` sends several together.

```python
questions = ["Why do parrots have colorful feathers?", "How do airplanes fly?", "What is quantum computing?"]

responses = model.batch(questions)                          # waits for ALL, same order as input
for q, r in zip(questions, responses):
    print(f"Q: {q}\nA: {r.content[:80]}...")

for idx, response in model.batch_as_completed(questions):   # each result as it finishes, order not guaranteed
    print(f"[input #{idx}] {response.content[:50]}...")
```

- Restaurant picture: `.batch()` brings every dish out together when the last is done. `.batch_as_completed()` brings each dish out the moment it is ready
- `batch_as_completed` returns the **input index** with each answer so you can match them up
- Requests must be **independent**, which is what lets them run in parallel
- Batching and streaming combine through `batch_as_completed`
- Example use: a Q&A portal collects questions over a short window (every 15 seconds) and batches them

**Does batching save tokens? No.**

- Every request still carries its own system message and context
- What it saves is **cost and time**, from two places:
  - Provider batch APIs (OpenAI's batch endpoint runs jobs asynchronously at roughly 50% lower cost, class figure, a pricing decision by the provider)
  - Fewer round trips and connections when a million calls are grouped

**Three ways to call a model**

- `.invoke()`: one call, the whole answer
- `.stream()`: progressive output
- `.batch()`: parallel, independent requests

## 3.8 Prompt templates

An f-string works for one case. For the same structure with different tones or variables you rewrite it each time, with no warning on a silent typo. `ChatPromptTemplate` separates structure from what changes.

```python
from langchain_core.prompts import ChatPromptTemplate

fun_fact_prompt = ChatPromptTemplate.from_messages([
    ("system", "You generate a single surprising fun fact. Tone: {tone}."),
    ("human", "Topic: {topic}"),
])

chain = fun_fact_prompt | model        # the | pipe feeds the template's output into the model

for tone, topic in [("playful and silly", "octopuses"), ("deadpan and serious", "octopuses")]:
    result = chain.invoke({"tone": tone, "topic": topic})
    print(f"[{tone} / {topic}] -> {result.content}")
```

- One prompt, two blanks, filled many ways. Same structure on every call
- The two octopus answers differ because of `tone` alone
- f-string = a napkin you scribble on. Template = a form with labelled blanks

**Most common real bug: unescaped curly braces**

- Literal braces in the fixed text (often a pasted example JSON) are read as extra variables
- Result: `KeyError` for a missing variable
- Fix: double the braces

```python
# WRONG: {"name": ...} is read as a variable, raises KeyError
ChatPromptTemplate.from_messages([
    ("system", 'Respond in this format: {"name": "John", "age": 21}'),
    ("human", "{question}"),
])

# RIGHT: escape literal braces by doubling them
ChatPromptTemplate.from_messages([
    ("system", 'Respond in this format: {{"name": "John", "age": 21}}'),
    ("human", "{question}"),
])
```

**`MessagesPlaceholder`** slots a whole list of earlier messages in as one variable:

```python
from langchain_core.prompts import MessagesPlaceholder

history_aware_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("history"),
    ("human", "{new_question}"),
])
result = history_aware_prompt.invoke({
    "history": [HumanMessage("My name is Rina."), AIMessage("Nice to meet you, Rina!")],
    "new_question": "What's my name?",
})
response = model.invoke(result.to_messages())
```

## 3.9 Questions from the class

- **Does `create_agent` call a tool in a single `invoke`?** Normally yes, it resolves within one invoke
- **Can the system message change if a different LLM is used?** Yes, whichever model sits behind it
- **System message = "skill"?** No, different concepts
- **Advantage of message dicts over classes?** No functional advantage
- **Does batching increase latency?** Only if you wait for the whole batch. `batch_as_completed` avoids that
- **Is every AI call a standard API request and response?** Yes. LangChain, OpenRouter, Claude and the raw `chat.completions` calls from the LLM book are all the same kind of request and response. No framework adds magic
- **Routing a query to one of several specialised agents** (each with a big Markdown knowledge file)
  - Treat each agent like a tool and give the router only a short name and description
  - Routing can be an `if` statement or a small classification call
  - Belongs with the multi-agent chapter
- **A `memory.md` pattern for multi-day builds**
  - Keep a running summary file the AI updates after each session and read only that next time
  - Summarising can lose detail
  - Belongs with agents and memory

## 3.10 Interview corner

**1. Why `init_chat_model` instead of the provider's own SDK?**

- One interface across providers. Change the string, keep the code
- *Stronger answer:* it lowers switching cost, but capabilities still differ per model, so check them

**2. What does temperature do, and when would you set it to 0?**

- Controls randomness. 0 for extraction, classification, anything that should be repeatable
- *Stronger answer:* 0 is steadier, not guaranteed identical

**3. What is in a model reply besides the text?**

- `.tool_calls`, `.usage_metadata` (token counts), `.response_metadata` (model and stop reason), `.id`, `.content_blocks`
- *Stronger answer:* `usage_metadata` is how you track cost per user

**4. `invoke` vs `stream` vs `batch`?**

- One whole answer / progressive output / many independent requests in parallel
- *Stronger answer:* streaming improves **perceived** speed, not total time. `batch_as_completed` combines both ideas

**5. Does batching save tokens?**

- No. Each request carries its own context. It saves cost (provider batch pricing) and time (fewer round trips)

**6. What is few-shot prompting?**

- Put example question and answer pairs before the real question so the model copies the pattern
- *Stronger answer:* often beats adding more instructions

**7. A template that contains example JSON throws `KeyError`. Why?**

- The braces are read as variables. Double them: `{{ }}`

## 3.11 Added by Claude, not from the sources

Not in the course material. Established practice, but check current docs.

- **Temperature 0 is not a guarantee.** Providers can still return slightly different text. Do not build logic that needs byte-identical output
- **Check why the reply stopped.** If `max_tokens` is too small the reply is cut off and nothing crashes. Look at the stop reason in `response_metadata` (the key name differs by provider)
- **Always set a `timeout`** in production, and decide how many retries you can afford. Retries multiply cost and latency
- **History grows every turn and you pay for it every turn.** Long chats need trimming or summarising before they hit the context limit or the budget
- **Do not put secrets in the system prompt.** Users can often coax a model into repeating its instructions

## Recap

- `init_chat_model("provider:model")` = one entry point for all providers
- Parameters: `temperature`, `max_tokens`, `timeout`, `max_retries`
- Messages: system, human, AI, tool. Objects or dicts, same result
- Few-shot = example exchanges before the real question
- A reply has text, tool calls, token usage and metadata
- `.stream()` = feels fast. `.batch()` = parallel and cheaper, **not** fewer tokens
- Templates separate structure from variables. Double literal braces

## Practice

1. Set `temperature`, `max_tokens`, `timeout` and `max_retries` explicitly and see what changes
2. Rebuild the few-shot pattern and compare with a system-message-only version
3. Run `.stream()` on a long prompt, then `.batch()` on three questions, then `batch_as_completed()`
4. Print `.usage_metadata` on a real call and compare with your provider's dashboard
5. If you have the RAM, run the same prompt through a local Ollama model and compare quality

## How this chapter was checked

- The reasoning-token figures (3.5) and the three-SDK comparison (3.1) come from the class notebook output and code. Neither was run here (they need provider keys)
- Run offline with a stand-in model on `langchain` 1.4.7: message dicts, tuples, bad `role` and missing `content` errors, `name` and `id`, `.batch()`, `.batch_as_completed()`, prompt template filling, the unescaped-brace `KeyError`, the doubled-brace fix, `MessagesPlaceholder`
- **Not run against a live model:** temperature behaviour, token counts, OpenRouter limits, provider batch pricing. Those are class figures

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/07 - 18 Jul - LangChain Family & Harness Engineering.md` (section 3.1)
- Live-Class-2026, `classes_summary/08 - 19 Jul - Inside the Model.md`
- Live-Class-2026, `classes_transcription_summary/08 - 19 Jul - LangChain - Inside the Model.md`
- Live-Class-2026, notebooks `02_03_environment_models_messages_student_notes.ipynb`, `04_05_prompt_templates_structured_output_student_notes.ipynb` and `Revision_Parts_1-4.ipynb` in `Weekend 04 - 18-19 Jul/07-08 - .../Notebook For Reference/`
- Section 3.11 is added by Claude and is not from these sources
- Live-Class-2026, `Weekend 04 - 18-19 Jul/.../Learning/Part 2 - Models/Langchain (1).ipynb` and `Langchain - Colab.ipynb` (reasoning-token output, three-SDK comparison). Both notebooks hold **API keys in their source**. They were not copied. Revoke any that are yours
- Live-Class-2026, `Weekend 04 - 18-19 Jul/07-08 .../Langchain.pdf` and the Weekend 4 README (whiteboard summary of classes 7 and 8: family, harness, messages, structured output)

Previous: [Chapter 2](02-langchain-family-and-harness-engineering.md) · Next: [Chapter 4, Structured output](04-structured-output.md)
