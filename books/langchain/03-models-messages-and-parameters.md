# Chapter 3: Models, messages and parameters

Everyone can "use a model" after a five-minute tutorial. This chapter is about the knobs LangChain puts around a model: the parameters you set, the messages you send, what comes back, and the three ways to call it. The mentor's point in class 08 was that real work needs all of these, and that most quickstarts stop at `create_agent()`.

Read [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md) first. It builds by hand the loop that LangChain later wraps. This chapter assumes the LangChain family and `create_agent` from [Chapter 1](01-introduction-to-langchain.md) and [Chapter 2](02-langchain-family-and-harness-engineering.md).

*Status: written from classes 07 and 08.*

## 3.1 The first model call

`init_chat_model` is LangChain's universal entry point to a model. Change the provider string and the rest of the code stays the same:

```python
from langchain.chat_models import init_chat_model

model = init_chat_model("openai:gpt-5")
response = model.invoke("Tell me what LangChain is")
print(response.content)
```

Without LangChain you would write different code to reach OpenAI, Claude, Groq and OpenRouter. LangChain puts them behind one interface. The class showed that CrewAI's documentation uses the same "give me any LLM" pattern, which is why learning it deeply here pays off across later frameworks.

**Models differ in capabilities.** Tool calling, structured output, multimodality (text and images) and reasoning vary from model to model. In class the mentor had ChatGPT summarise one model's capability sheet (tool calling yes, structured output yes, multimodal yes, reasoning present but weaker than the flagships). Look up the sheet for the model you plan to use.

**Messages steer behaviour.** A system message and a human message go in as a list:

```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="You are a pirate. Answer everything in pirate language."),
    HumanMessage(content="What is the capital of France?"),
]
response = model.invoke(messages)
print(response.content)
```

Running it gave a pirate-flavoured answer, a concrete proof that the system message steers the model. This matches the roles in [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md). Note that the chat model does nothing to manage chat history for you. That is still your job.

Class 07 stopped here and said the next class would cover temperature, `max_tokens` and the API timeout, which are section 3.3 below.

*Source: Live-Class-2026, `classes_transcription_summary/07`. Not run: LangChain is not installed in my sandbox.*

## 3.2 Where your API key lives

The class notebook is blunt about this. If `.env` is not listed in `.gitignore`, the first time you commit and push, your real API key goes to GitHub with the code. Automated scanners that look for leaked keys can find and use it, often within minutes.

```python
import os
from dotenv import load_dotenv
load_dotenv()
assert os.environ.get("OPENAI_API_KEY"), "Missing OPENAI_API_KEY -- check your .env file"
```

If this raises an error, either `.env` is not in the folder you are running from, or you created it after starting the notebook session. In the second case, restart the kernel so `load_dotenv()` picks up the file.

*Source: Live-Class-2026, `classes_summary/08`.*

## 3.3 Model parameters

`init_chat_model` takes the model name and a few parameters:

| Parameter | What it does |
|---|---|
| `model` | The only required one: which LLM to use, for example `"openai:gpt-5-mini"` |
| `api_key` | Optional, because LangChain looks for the standard environment variable (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY` and so on) |
| `temperature` | A dial for randomness and creativity |
| `max_tokens` | Caps the output length |
| `timeout` and `max_retries` | How long and how persistently LangChain waits for the model before giving up. The default for retries is 6 |

They are passed as keyword arguments, `key=value` beside the model name. The revision notebook's analogy is the dials on a car dashboard: `temperature` is how much creative liberty you allow, `max_tokens` is a hard fuel ceiling on the reply, `timeout` is how long you wait at a red light before giving up, and `max_retries` is how many times you try restarting a car that will not start.

```python
deterministic_model = init_chat_model("openai:gpt-5-mini", temperature=0.0, max_tokens=200, timeout=30)
creative_model      = init_chat_model("openai:gpt-5-mini", temperature=1.0, max_tokens=200, timeout=30)

prompt = "Describe a sunset in one creative sentence."
print(deterministic_model.invoke(prompt).content)
print(creative_model.invoke(prompt).content)
```

The notebook's note: run the `temperature=0.0` model twice and it comes back nearly identical, while `temperature=1.0` varies from run to run. A common OpenRouter error is a reply longer than the allowed limit, and raising `max_tokens` fixes it. OpenRouter's free router can be used with `init_chat_model("openrouter/free")` once `OPENROUTER_API_KEY` is set.

```python
paid_model = init_chat_model("openai:gpt-5-mini")

# free_model = init_chat_model("ollama:llama3.2")   # runs on your own machine, no API key
```

**Paid, free and local.** Paid providers (OpenAI, Anthropic, Gemini) bill per token. Free tiers (OpenRouter, Groq, NVIDIA) are rate limited. In class the mentor hit OpenRouter's free-tier limit live, quoting 20 requests a minute and 50 a day. Those numbers are from the class and may have changed. Groq hosts mostly open-source models and pays for the hosting, which is the trade for free or cheap access. Free models generally trail the flagship paid models in quality.

A local model through Ollama has no API cost, but it needs real RAM (ideally a GPU) to run at usable speed, and its quality also trails a frontier paid model. The interface is the same and the intelligence is different.

*Source: `classes_summary/08`, `classes_transcription_summary/08`. Not run: LangChain is not installed in my sandbox and the calls need keys.*

## 3.4 Messages

You could send one long string that mixes the instructions and the user's question, but the model then has no reliable way to tell which part is an instruction and which is what the user said (the revision notebook's picture is a note slid under a door). A **message list** labels each piece with who said it. The notebooks list four types:

- **System message:** behaviour, tone and rules.
- **Human message:** the user's input.
- **AI message:** the model's own earlier reply.
- **Tool message:** the result of a tool call, sent back so the model can carry on (see [Chapter 5](05-tools.md)).

The notebook calls the system message the director's note: not something spoken in the scene. In the pirate example the "be a pirate" instruction never gets mixed into the actual question.

The class showed again that a single "hi" to Claude sends thousands of tokens once the hidden system message is counted. In a finished product such as Claude's web app, the provider fixes the system message and you cannot change it. When you build your own agent you control it, which is the point of building your own harness. The system message can be changed whichever model sits behind it. A system message is not the same thing as a "skill".

Messages can be the classes below or plain dictionaries with a `role` key (`"system"`, `"user"`, `"assistant"`). There is no functional difference. The mentor prefers the classes for readability. Dictionaries are common when the history comes from a database or a JSON API.

**Which shape when:**

| Shape | Use when |
|---|---|
| Plain text | A single standalone request with no history |
| Message objects | Multi-turn conversations, multimodal content, system instructions |
| Dictionaries | The same as objects, when the data arrives from a database or JSON API |

LangChain also accepts a `("human", "text")` tuple and a bare string (turned into a human message), and converts all four shapes consistently. A dictionary that has no `content`, or has an unknown `role`, raises `MESSAGE_COERCION_FAILURE`.

A `HumanMessage` can carry two optional fields, `name` (useful to label who is speaking in a multi-user chat) and `id` (a stable identifier for the message):

```python
human_msg = HumanMessage(content="Hi, how are you?", name="mayank", id="user_1234")
```

### Few-shot prompting

The mentor told a story from earlier in his career. A co-pilot style chatbot performed poorly even with a good system message. Instead of piling more instructions into it, he put a few example exchanges into the conversation as separate earlier messages (a sample user message, then a sample AI reply), before the real question. The output improved. This is called **few-shot prompting**: the model mimics the pattern it is shown.

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="You are a helpful support assistant."),
    HumanMessage(content="Example question..."),
    AIMessage(content="Example ideal answer..."),     # an example, not a real earlier reply
    HumanMessage(content="Actual user question here"),
]
response = model.invoke(messages)
```

**Inserting history by hand.** The notebook adds a caution. Putting an `AIMessage` into the list yourself is fine for restoring real conversation history. It is not a way to make the model "believe" it agreed to something so as to bias it dishonestly, because the model treats a made-up `AIMessage` as real context either way.

*Source: `classes_summary/08`, `classes_transcription_summary/08`.*

## 3.5 What comes back: the full `AIMessage`

The notebook says most tutorials skip this. A model call returns far more than the text:

| Field | What it holds |
|---|---|
| `.text` | The plain reply, always a string |
| `.content` and `.content_blocks` | The raw content, or LangChain's standard structure for rich content (text, reasoning, citations, images) |
| `.tool_calls` | Any tool calls requested, an empty list if none |
| `.id` | A unique identifier for the message |
| `.usage_metadata` | Real token counts: `input_tokens`, `output_tokens`, `total_tokens` |
| `.response_metadata` | Provider extras, such as which exact model answered and why it stopped |

```python
response = openai_model.invoke("Explain agentic AI in one sentence.")
print("text:          ", response.text)
print("tool_calls:    ", response.tool_calls)     # empty: no tools bound yet
print(response.usage_metadata)
```

`.text` is always a string. `.content` is usually the same, but can be a list of content blocks for richer replies. `pprint(response)` shows everything on the object at once. You do not need a separate token-counting library, because the billed numbers are on the response. `usage_metadata` can also hold finer breakdowns (`input_token_details` and `output_token_details`, for example cached tokens and reasoning tokens). If you need to track spend per user or per session, add `usage_metadata` up across the conversation: it is the exact billed number, not an estimate. Streaming, structured output and tool calling all build on reading these fields correctly.

*Source: `classes_summary/08`.*

## 3.6 Streaming: it feels fast

In class, a request for about 2,000 words took roughly 5 to 7 seconds to generate in ChatGPT, but the text appeared piece by piece. That progressive appearance is streaming. It does not make the answer arrive sooner, but the wait feels shorter. For a product (the examples were Amazon or Swiggy) nobody wants a screen frozen for seven seconds.

```python
for chunk in model.stream("Why do parrots have colorful feathers?"):
    print(chunk.text, end="", flush=True)
```

Streaming is built into the model call. You swap `.invoke()` for `.stream()` and install nothing. Each chunk is an `AIMessageChunk`, and chunks add together with `+`:

```python
full_message = None
for chunk in openai_model.stream("Write one short sentence about the ocean."):
    full_message = chunk if full_message is None else full_message + chunk
print("Reconstructed full message:", full_message.content)
```

The notebook's point: `.invoke()` was never called, yet the message built by summing the chunks has the same shape as one from `.invoke()`.

*Source: `classes_summary/08`, `classes_transcription_summary/08`.*

## 3.7 Batching

Imagine a company that receives a constant stream of questions. Asking one, waiting, asking the next is slow. `.batch()` sends several questions together:

```python
responses = model.batch([Q1, Q2, Q3])
for response in responses:
    print(response)
```

```python
questions = ["Why do parrots have colorful feathers?", "How do airplanes fly?", "What is quantum computing?"]

responses = model.batch(questions)                         # waits for ALL, same order as the input
for q, r in zip(questions, responses):
    print(f"Q: {q}\nA: {r.content[:80]}...")

for idx, response in model.batch_as_completed(questions):  # each result as it finishes, order not guaranteed
    print(f"[input #{idx}] {response.content[:50]}...")
```

The revision notebook's picture is a restaurant kitchen: `.batch()` sends every order at once and brings them **all** out together when the last one is done, while `.batch_as_completed()` brings each dish out the moment it is ready, possibly out of order. `batch_as_completed` hands back the input's index with each answer so you can match them up.

- The requests must be **independent**, which is what lets them run in parallel.
- By default `.batch()` waits and returns everything at once. `batch_as_completed()` returns each answer as soon as that one finishes, so it avoids waiting for the slowest. That is also how batching and streaming combine.
- A company Q&A portal could collect questions over a short window (every 15 seconds, say) and batch them.

**Does batching save tokens?** A learner pushed on this in class. The mentor's answer: no. Every request inside a batch still carries its own system message and context. What is saved is cost and time, from two separate places: provider batch APIs (the example given was OpenAI's batch endpoint, which runs jobs asynchronously at roughly 50% lower cost, a pricing decision by the provider) and infrastructure savings from fewer round trips and connections when a million calls are grouped into far fewer. The 50% figure is the class's, so check the current price.

**Three ways to call a model:**

| Call | Use |
|---|---|
| `.invoke()` | One call, the whole answer |
| `.stream()` | Progressive output |
| `.batch()` | Parallel, independent requests |

*Source: `classes_summary/08`, `classes_transcription_summary/08`.*

## 3.8 Prompt templates

An f-string prompt works for one case. When you need the same structure with different tones or several variables, you rewrite it by hand each time, with no warning on a silent typo. `ChatPromptTemplate` separates the fixed structure from what changes:

```python
from langchain_core.prompts import ChatPromptTemplate

fun_fact_prompt = ChatPromptTemplate.from_messages([
    ("system", "You generate a single surprising fun fact. Tone: {tone}."),
    ("human", "Topic: {topic}"),
])

chain = fun_fact_prompt | openai_model   # the | pipe feeds the template's output into the model

for tone, topic in [("playful and silly", "octopuses"), ("deadpan and serious", "octopuses")]:
    result = chain.invoke({"tone": tone, "topic": topic})
    print(f"[{tone} / {topic}] -> {result.content}")
```

The class ran it a third time with `("excited like a sports commentator", "the Roman Empire")`. The structure is the same on every call and only the two variables change. The two "octopuses" answers sound completely different because of `tone` alone.

You are writing one prompt with two blanks and filling them three ways, not three prompts. The revision notebook's picture: an f-string is a napkin you scribble on each time, and a `ChatPromptTemplate` is a resume template with labelled blank fields.

**The most common real bug: unescaped curly braces.** If the fixed text of a template contains literal braces (often from pasting in an example JSON object), LangChain reads them as more variables and fails. Double them to escape:

```python
# WRONG: the JSON example's braces are read as extra variables, so this raises KeyError
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

**`MessagesPlaceholder`** slots a whole list of earlier messages into a template as one variable:

```python
from langchain_core.prompts import MessagesPlaceholder

history_aware_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("history"),
    ("human", "{new_question}"),
])
result = history_aware_prompt.invoke({"history": [HumanMessage("My name is Rina."), AIMessage("Nice to meet you, Rina!")],
                                      "new_question": "What's my name?"})
response = model.invoke(result.to_messages())
```

*Source: `classes_summary/08`, notebooks `04_05_prompt_templates_structured_output_student_notes.ipynb` and `Revision_Parts_1-4.ipynb`. Not run.*

## 3.9 Questions from the class

| Question | Answer |
|---|---|
| Does `create_agent` call a tool in a single `invoke`? | Normally yes, it resolves within one invoke call |
| Can the system message change if a different LLM is used? | Yes, regardless of which model sits behind it |
| Is a system message the same as a "skill"? | No, they are different concepts |
| Any advantage to message dictionaries over message classes? | No functional advantage; the mentor prefers the classes |
| Does batching increase latency? | Only if you wait for the whole batch. `batch_as_completed` avoids that |
| Can streaming and batching be combined? | Yes, `batch_as_completed` streams results as each item finishes |
| Is every AI call underneath a standard API request and response? | Yes: LangChain, OpenRouter, Claude and the raw `chat.completions` calls from LLM Chapter 2 are all the same kind of request and response. No framework adds magic |

Two more answers from the end-of-class session belong with later chapters, so they are only noted here:

- **Routing a query to one of several specialised agents** (each with a large Markdown knowledge file): treat each agent like a tool and give the routing step only a short name and description. The routing can be an `if` statement or a small classification call. This belongs in the multi-agent chapter.
- **A `memory.md` pattern for multi-day builds:** keep a running summary file that the AI updates after each session and read only that next time, accepting that summarising can lose detail. This belongs with agents and memory.

*Source: `classes_transcription_summary/08`. I left out an off-topic freelancing answer.*

## Practice

1. Set `temperature`, `max_tokens`, `timeout` and `max_retries` explicitly and see what changes.
2. Rebuild the few-shot pattern and compare its output with a system-message-only version.
3. Run `.stream()` on a long prompt, then `.batch()` on three questions, then `batch_as_completed()`.
4. Print `.usage_metadata` on a real call and compare it with your provider's dashboard.
5. If you have the RAM, run the same prompt through a local Ollama model and compare quality.

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/07 - 18 Jul - LangChain Family & Harness Engineering.md` (section 3.1)
- Live-Class-2026, `classes_summary/08 - 19 Jul - Inside the Model.md`
- Live-Class-2026, `classes_transcription_summary/08 - 19 Jul - LangChain - Inside the Model.md`
- Live-Class-2026, notebooks `02_03_environment_models_messages_student_notes.ipynb`, `04_05_prompt_templates_structured_output_student_notes.ipynb` and `Revision_Parts_1-4.ipynb` in `Weekend 04 - 18-19 Jul/07-08 - .../Notebook For Reference/`

Previous: [Chapter 2](02-langchain-family-and-harness-engineering.md) · Next: [Chapter 4, Structured output](04-structured-output.md)
