# Chapter 1: Introduction to LangChain

**After this chapter you can:**

- Explain what an agent is
- Build one with `create_agent()`
- Read what it returns
- Give it memory
- Answer the common interview questions

**Before this:** the agent loop from [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md). Here the same loop is run by a framework.

## 1.1 Why a framework

- **Agent** = a model that decides the next step, calls tools, and loops until it has an answer.
- The raw loop is easy to write **once**. Repeating it per project is the pain:
  - different providers
  - tool schemas
  - memory
  - retries
  - approvals
  - tracing
- **LangChain** supplies that plumbing. You choose the model, tools and instructions. It runs the loop.
- **Quick test:** if an AI tells you to search the web and paste results back, it is not acting as an agent. An agent calls the tool **itself**.

## 1.2 Agent = model + harness

- **Model:** text in, text out. No memory, no tools.
- **Harness:** everything around the model:
  - system prompt (role and rules)
  - tools (actions the model can request)
  - the loop (call model → run tools → feed results back → repeat)
  - memory (stored conversation)
  - middleware (hooks on the loop, from [Chapter 7](07-middleware.md))
- `create_agent()` is LangChain's harness: minimal, but highly configurable.

## 1.3 The LangChain family (short version)

Full detail in [Chapter 2](02-langchain-family-and-harness-engineering.md). They are layers, not rivals.

- **Deep Agents:** top layer. Planning, a virtual file system and sub-agents are ready-made. Little control inside.
- **LangChain:** middle layer. A harness you configure. **This book starts here.**
- **LangGraph:** bottom layer. You define every step and branch. Most control, steepest learning curve.
- **LangSmith:** not for building. It records and evaluates what your agent did.
- **Version note:** everything before LangChain v1 is called **LangChain Classic**. Many old tutorials teach Classic, so mismatched code usually means a version difference.

## 1.4 Set up a project

```bash
uv init
uv add langchain langchain-openai langchain-anthropic
uv sync
```

Create three files:

- `.env`: your provider keys
- `.gitignore`: must list `.env` and `.venv`
- `.env.example`: key names with empty values. This one **is** committed

```
# .env.example
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

Good to know:

- Three installs pull in about 45 dependencies. That is normal.
- `pyproject.toml` already does the job of `requirements.txt`.
- You need **your own key** for each provider. LangChain is only the harness.
- **Pitfall:** a key pushed to a public repo is found by bots within minutes. Deleting the commit is not enough. **Revoke the key** and create a new one. See [Chapter 3](03-models-messages-and-parameters.md), section 3.2.

## 1.5 Your first agent

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="openai:gpt-4o-mini",      # "provider:model-name"
    tools=[get_weather],
    system_prompt="You are a helpful weather assistant.",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Weather in San Francisco?"}]}
)
print(result["messages"][-1].content)
```

What each argument does:

- **`model`**
  - String in the form `provider:model-name`
  - Switch provider by changing the prefix (OpenAI, Anthropic, Gemini, Groq, Ollama, Azure, Bedrock and more)
  - Model names change often, so check the provider's current list
- **`tools`**
  - A list of **plain Python functions**
  - No hand-written JSON schema. LangChain builds it from the **name, type hints and docstring**
- **`system_prompt`**: the role and rules
- **`agent.invoke(...)`**: runs the whole loop and returns when the model stops asking for tools

**The model never sees your code.** It only sees the tool's name, parameters and docstring. A vague docstring is the top reason for wrong tool choices.

`@tool` makes the tool explicit ([Chapter 5](05-tools.md)):

```python
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city. Use for any weather question."""
    return f"It's always sunny in {city}!"
```

### What comes back

```python
for m in result["messages"]:
    m.pretty_print()
```

`result["messages"]` is the full conversation:

1. **`HumanMessage`:** the question
2. **`AIMessage`:** empty text plus a **tool call** (`get_weather`, `{"city": "San Francisco"}`, an id)
3. **`ToolMessage`:** the function's return value, with the **same id** as step 2
4. **`AIMessage`:** the final answer

Notes:

- The model was called **twice**: once to ask for the tool, once to answer.
- The matching id tells the model which result belongs to which request. It matters when several tools are requested at once.
- AI messages carry token counts (`prompt_tokens`, `completion_tokens`, `total_tokens`). Use them to work out cost.

## 1.6 Memory

- Each `invoke` sees **only the messages you pass in**.
- So "Hi, I am Mayank" in one call and "Who am I?" in the next: the agent does not know.
- Fix: a **checkpointer** (stores state) plus a **thread_id** (picks the conversation).

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather],
    system_prompt="You are a helpful assistant.",
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "chat-1"}}
agent.invoke({"messages": [{"role": "user", "content": "Hi, I am Mayank"}]}, config)
reply = agent.invoke({"messages": [{"role": "user", "content": "Who am I?"}]}, config)
```

- Same `thread_id` → remembers. New `thread_id` → fresh start.
- **Pitfall:** `InMemorySaver` lives in the running process. Script ends → memory gone. Production needs a database-backed saver ([Chapter 6](06-agents-and-memory.md)).
- **Pitfall:** `checkpointer=checkpointer` raises `NameError` if you never created it. Create it first.

## 1.7 Make the model check, not guess

- Models sound sure even when wrong. Counting, lookups and maths should come from a **tool**, not from the model.
- Pattern: give a fetch tool, then tell the model not to guess.

```python
import urllib.request, urllib.error
from langchain.tools import tool
from langchain.chat_models import init_chat_model

@tool
def fetch_text_from_url(url: str) -> str:
    """Fetch the text of a document from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "notes-demo/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"

SYSTEM_PROMPT = """You are a literary data assistant.

## Capabilities
- `fetch_text_from_url`: loads document text from a URL.

Do not guess line counts or positions. Ground them in tool results.
If an exact answer cannot be verified, return null and explain why."""

model = init_chat_model("openai:gpt-4o-mini", temperature=0.5, timeout=300, max_tokens=25000)
```

Three habits to copy:

- **Name each tool's purpose** in the system prompt, not only its docstring.
- **Allow "I cannot verify this."** Otherwise the model invents a number.
- **Return errors as text** (`"Fetch failed: ..."`) so the model can react instead of the run crashing.

`init_chat_model(...)` is the alternative to the model string. Use it to set `temperature`, `timeout` or `max_tokens` ([Chapter 3](03-models-messages-and-parameters.md)).

## 1.8 Caching tool results

- Cache time depends on **how fast the data changes**:
  - Stock prices: do not cache
  - Currency rates: minutes
  - Weather: hours
  - Static reference data: long
- Idea: a **TTL** (time-to-live), meaning how long a stored result may be reused.
- A cached wrong answer is worse than a slow right one.

```python
import time

_cache = {}

def cached(key, ttl_seconds, fetch):
    hit = _cache.get(key)
    if hit and time.time() - hit[0] < ttl_seconds:
        return hit[1]
    value = fetch()
    _cache[key] = (time.time(), value)
    return value

# inside a tool:
# return cached(("fx", "USD", "INR"), 600, lambda: call_rates_api("USD", "INR"))
```

## 1.9 Trade-offs

- **You gain**
  - A working agent in a few lines
  - Provider swap by changing a string
  - Memory, structured output, middleware and tracing on tap
- **You give up**
  - Some visibility: the tool schema is inferred
  - Some speed: extra work per call (ids, message objects, bookkeeping)
  - Fine control, unless you step down to LangGraph
- **Career angle:** depth in the fundamentals (the raw loop) lasts longer than a list of framework names. Clients care about control and speed, not how many frameworks you know.

## 1.10 Interview corner

**1. What is an agent in LangChain?**

- A model plus a harness (instructions, tools, loop, memory, middleware)
- `create_agent()` is the minimal configurable harness
- *Stronger answer:* the model alone is stateless and cannot act, so almost everything useful comes from the harness

**2. Why a framework instead of writing the loop?**

- The loop is easy. The plumbing is not: providers, tool schemas, structured output, memory, retries, approvals, tracing
- *Stronger answer:* name the costs (less visibility, overhead, one more dependency) and say you can still write the loop by hand

**3. LangChain vs LangGraph vs Deep Agents vs LangSmith?**

- Deep Agents: batteries-included top layer
- LangChain: configurable harness
- LangGraph: low-level orchestration
- LangSmith: observability, not a builder
- *Stronger answer:* they are layers, not rivals. LangChain agents run on LangGraph underneath

**4. When does the loop stop?**

- When the model replies **without** requesting a tool
- *Stronger answer:* you still need a safety limit (`recursion_limit`) in case it keeps calling tools

**5. Why does an agent forget between runs?**

- Each `invoke` sees only what you pass in
- Fix: checkpointer + `thread_id`
- *Stronger answer:* the in-memory saver dies with the process, so production uses a database-backed one

**6. How does LangChain describe your function to the model?**

- From its name, type hints and docstring. `@tool` gives explicit control
- *Stronger answer:* the docstring is effectively part of the prompt

**7. A tool fetches any URL. What can go wrong?**

- Huge pages, hangs, failures
- *Stronger answer:* prompt injection and SSRF (see 1.11)

## 1.11 Added by Claude, not from the sources

Not in the course material. Well-established practice, but check current docs before relying on it.

- **Prompt injection**
  - A fetched web page can contain text written to look like instructions
  - Treat tool output as **data**, never as instructions
  - Do not give an agent that reads the open web tools that can also send, delete or spend, without a human approval step ([Chapter 11](11-runtime-and-human-in-the-loop.md))
- **SSRF (server-side request forgery)**
  - If the model controls the URL, it can be steered to internal addresses
  - In real systems, allow-list domains and block private IP ranges
- **Set your own step limit**
  - In the LangGraph version I checked (while preparing this chapter), the default `recursion_limit` was very high (10007)
  - A looping agent can run, and cost money, for a long time
  - Set a lower value:

```python
agent.invoke(
    {"messages": [{"role": "user", "content": "..."}]},
    config={"recursion_limit": 25},
)
```

- **Tools with side effects can run more than once**
  - Loops, retries or a model asking twice can repeat a call
  - Make write, send and charge tools **idempotent** (safe to repeat), or guard them with approval
- **`create_agent` is the current way to build agents in LangChain v1.** Older tutorials use other helpers

## Recap

- Agent = **model + harness**. `create_agent()` is the harness
- You give `model`, `tools`, `system_prompt`. `invoke` runs the loop
- Result = human → AI (tool call) → tool result (same id) → final AI
- Tool descriptions come from name, type hints, **docstring**
- Memory = **checkpointer + thread_id**. In-memory is lost when the process ends
- Make the model **verify with tools** and allow "cannot verify"
- Cache by how fast the data changes
- Frameworks trade some visibility and speed for a lot of plumbing

## Practice

1. New project with `uv add langchain langchain-openai langchain-anthropic`, plus `.env`, `.gitignore`, `.env.example`
2. Build the weather agent. Print the messages and match each to a step of the hand-built loop
3. Add `InMemorySaver` and `thread_id`. Show it remembers within a thread and forgets across threads
4. Write a tool with a clear docstring, then make it vague and watch tool choice get worse
5. Run the line-counting agent from 1.7 on a real text and check its numbers yourself

## How this chapter was checked

- Run offline with a stand-in model on `langchain` 1.4.7: message order, matching tool-call id, `pretty_print`, checkpointer memory per `thread_id`, `recursion_limit` in config, and the `cached` helper
- **Not** run against a live model (needs a provider key). Check model names and prompts before running

## Sources and further reading

- Live-Class-2026, `classes_summary/06 - 12 Jul - Introduction to LangChain.md`
- Live-Class-2026, `classes_transcription_summary/06 - 12 Jul - Introduction to LangChain.md`
- Live-Class-2026, code folder `Weekend 03 - 11-12 Jul/06 - 12 Jul - Introduction to LangChain/`
- Section 1.11 is added by Claude and is not from these sources

Previous: [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md) · Next: [Chapter 2, LangChain family and harness engineering](02-langchain-family-and-harness-engineering.md)
