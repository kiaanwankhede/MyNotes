# Chapter 6: Agents and memory

*Every `create_agent` argument in one place, the loop it runs, and how it remembers.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the full anatomy of `create_agent`, agent state, `thread_id` vs `context`, the six harness capability areas, and saver vs store vs cache vs database
> - **You will build:** the TripMate travel agent with tools, memory, a store and streaming
> - **Level:** intermediate · **Time:** about 45 minutes
> - **Builds on:** [Chapter 1](01-introduction-to-langchain.md) (first agent, checkpointer basics) and [Chapter 5](05-tools.md) (tools, `ToolRuntime`, `InMemoryStore`). Middleware is in [Chapter 7](07-middleware.md).

**After this chapter you can:**

- Explain why models, messages, structured output and tools were already "agents"
- Describe the agentic loop and where tokens are spent
- Name the six areas a harness covers, and which chapter teaches each
- Tell memory saver, memory store, cache and database apart, and pick one
- Give an agent short-term memory (`thread_id`) and long-term memory (`store`), and say how `thread_id` differs from `context`
- Store, get and search long-term memories by namespace and key, and keep one user's memories away from another's
- Assemble a full agent with tools, middleware, memory, context, custom state and a name
- Explain headless tools
- Harden a tool that calls a real API: timeouts, outage vs not found, strict parsing
- Explain why an agent with `ToolStrategy` can loop, and stop it in code

## 6.1 Everything so far was already an agent

> An agent is a model calling tools in a loop until a given task is complete. A harness is everything around that loop.

- **Agent = model + harness.** Around the model you add tools, context, sub-agents, memory, skills, middleware: anything that helps you get the most from the model
- **The harness has one job:** get the model **the right context at the right time** for the task. Every harness feature serves that job
- Models, messages, structured output and tools were never separate topics. They are the **components** an agent is built from
- What changed in the last few years? Essentially one thing: we got an artificial brain (the LLM). The rest of software engineering is the same
- So the real question is always: **how do I best harness this model?**

![Agent = model + harness (LangChain docs): the model sits inside a harness of system prompt, tools, context, memory, skills and subagents](images/agent_model_harness.svg)

### The harness, by capability

`create_agent` starts small. **Middleware** is how it grows: each piece handles one concern, hooks into the loop at the right moment, and combines freely with the others. Take what the use case needs and skip the rest.

![Harness capabilities (LangChain docs): execution environment, context management, delegation and steering, with the middleware in each](images/agent_harness_capabilities.svg)

| Area | What it solves | Typical middleware | Where in this book |
|---|---|---|---|
| **Execution environment** | Agent acts, not just talks: tools, a filesystem across turns, code execution, sandboxes | `FilesystemMiddleware`, shell tools | [Ch 10](10-shell-tools-and-custom-middleware.md) |
| **Context management** | The context window fills up: compress history, load lasting memory, surface skills on demand, cache prompts | `SummarizationMiddleware`, memory, skills | [Ch 7](07-middleware.md), [Ch 14](14-handoffs-skills-router-and-custom-workflows.md) |
| **Planning and delegation** | One context window is not enough: plan with a to-do list, hand pieces to subagents with clean contexts | `TodoListMiddleware`, subagents | [Ch 9](09-guardrails-to-do-lists-and-tool-resilience.md), [Ch 13](13-multi-agent-systems-and-subagents.md) |
| **Fault tolerance** | Rate limits, timeouts, flaky APIs, without try/except in every tool | `ModelRetryMiddleware`, `ToolRetryMiddleware`, fallbacks, call limits | [Ch 8](08-prebuilt-middleware-limits-fallback-and-pii.md), [Ch 9](09-guardrails-to-do-lists-and-tool-resilience.md) |
| **Guardrails** | Rules that must hold whatever the model does (applied in code, not in the prompt) | `PIIMiddleware`, content filters | [Ch 8](08-prebuilt-middleware-limits-fallback-and-pii.md), [Ch 9](09-guardrails-to-do-lists-and-tool-resilience.md) |
| **Steering** | A human decides at risky points: destructive writes, expensive calls, judgment calls | `HumanInTheLoopMiddleware` | [Ch 7](07-middleware.md), [Ch 11](11-runtime-and-human-in-the-loop.md) |

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelRetryMiddleware, ToolRetryMiddleware, PIIMiddleware, HumanInTheLoopMiddleware,
)

agent = create_agent(
    model="openai:gpt-6.1-sol",
    tools=[search, write_file],
    middleware=[
        ModelRetryMiddleware(max_retries=3),                         # fault tolerance
        ToolRetryMiddleware(max_retries=2),
        PIIMiddleware("email"),                                      # guardrail
        HumanInTheLoopMiddleware(interrupt_on={"write_file": True}), # steering
    ],
)
```

✅ *Verified: this stack builds on `langchain` 1.5.0 (details at the end).*

**Borrowing Deep Agents pieces.** The `deepagents` package (`uv add deepagents`) ships middleware you can drop into a plain `create_agent`: a virtual filesystem, memory loaded from an `AGENTS.md` file, skills from a folder, and subagents.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware, MemoryMiddleware, SkillsMiddleware
from deepagents.middleware.subagents import SubAgentMiddleware

backend = StateBackend()                       # files live in the agent's state
agent = create_agent(
    model="openai:gpt-6.1-sol",
    tools=[search],
    middleware=[
        FilesystemMiddleware(backend=backend),                    # ls, read_file, write_file, edit_file, glob, grep...
        MemoryMiddleware(backend=backend, sources=["./AGENTS.md"]),  # lasting instructions at startup
        SkillsMiddleware(backend=backend, sources=["./skills/"]),    # domain know-how, loaded on demand
        TodoListMiddleware(),                                     # planning
        SubAgentMiddleware(backend=backend, subagents=[{
            "name": "researcher",
            "description": "Searches and returns a structured summary.",
            "system_prompt": "Use the search tool to research the question and summarize key points.",
            "tools": [search],
        }]),
    ],
)
```

- Each subagent runs in its **own context**, so the main agent's window stays clean and work can run in parallel
- `create_deep_agent(...)` pre-assembles this whole stack (plus summarization and prompt caching). Build it by hand with `create_agent` only when you want a **smaller** harness ([Ch 2](02-langchain-family-and-harness-engineering.md), 2.1)

> [!WARNING]
> **Two classes called `SummarizationMiddleware`.** `deepagents.middleware.SummarizationMiddleware` needs a `backend` and offloads old history into it. `langchain.agents.middleware.SummarizationMiddleware` ([Ch 7](07-middleware.md), 7.5) does not. Check the import line before copying an example.

## 6.2 The agentic loop, restated

![The core agent loop (LangChain docs): request → model → action → tools → observation → model → result](images/core_agent_loop.svg)

1. A message arrives
2. The model decides: does it need a tool?
3. **Yes:** run the tool, append the result to the messages, go back to step 2
4. **No:** return the final answer

- This used to be called the **ReAct pattern**. "Agentic loop" is the more accurate name today
- A tool's result **always goes back to the model**, never straight to the user. The user only sees the model's final reply
- **The model is used at least twice per tool use:** once to choose the tool and its arguments, once to turn the tool result into an answer
- **Only model calls cost tokens.** A tool running by itself, with no model call, does not
- Exception: `return_direct` ([Chapter 5](05-tools.md), 5.10) skips the final model pass on purpose

## 6.3 Real tools: the TripMate project

- CineBot stays in the course **only to explain concepts** (mock tools)
- **TripMate** is a fuller project: a travel-planning agent with **real** tools
- Real tools in TripMate:
  - **Weather:** Open-Meteo, a free, open-source API that needs no key
  - **Web search:** Tavily. It is a third-party service. LangChain only gives you an easy way to plug it in, so you do not rewrite the integration each time
  - **Save and get trips:** a SQLite table (`trips`) keyed by user id
  - **Save and recall preferences:** long-term memory through `ToolRuntime.store` ([Chapter 5](05-tools.md), 5.10)
  - **Premium concierge:** gated, premium members only ([Chapter 7](07-middleware.md))
- **Why SQLite?** It is just a local mock-up of "a database". Any store works: Postgres, MongoDB, ChromaDB
- **Why a database at all?** If the application restarts, data stored **outside** the process is still there

Example written for these notes (not the class code), showing the save and get pattern with the standard library:

```python
import sqlite3
from langchain_core.tools import tool

conn = sqlite3.connect("trips.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS trips (user_id TEXT, destination TEXT, dates TEXT)")

@tool
def save_trip(user_id: str, destination: str, dates: str) -> str:
    """Save a confirmed trip for a user to the database."""
    conn.execute("INSERT INTO trips VALUES (?, ?, ?)", (user_id, destination, dates))
    conn.commit()
    return f"Saved trip to {destination} ({dates}) for {user_id}."

@tool
def get_saved_trips(user_id: str) -> str:
    """List the trips saved for a user."""
    rows = conn.execute("SELECT destination, dates FROM trips WHERE user_id = ?", (user_id,)).fetchall()
    return "; ".join(f"{d} ({dt})" for d, dt in rows) or "No saved trips."
```

- The class version (Weekend 05 notebook, cells 95–97) adds a `trip_id INTEGER PRIMARY KEY AUTOINCREMENT` and a `status` column, and returns `Trip #<id> saved`. Keep the id: the modify and cancel schemas in 6.6 need a `trip_id`, so the model must be able to see it

### The real weather tool, and what it needs before production

The class tool (Weekend 05 notebook, cell 87, walked through again in class 11) makes two calls: find the city's coordinates, then read the current weather there. Open-Meteo needs no key.

```python
import requests
from langchain.tools import tool

@tool
def get_real_weather(city: str) -> str:
    """Get the REAL current weather for a city, using a live weather API."""
    geo_data = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                            params={"name": city, "count": 1}).json()
    if not geo_data.get("results"):
        return f"Could not find a location matching '{city}'."
    location = geo_data["results"][0]
    weather_data = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": location["latitude"], "longitude": location["longitude"], "current_weather": "true"}).json()
    current = weather_data.get("current_weather", {})
    return (f"Real current weather in {location['name']}, {location.get('country', '')}: "
            f"{current.get('temperature')}°C, wind {current.get('windspeed')} km/h.")
```

- In class, `get_real_weather.invoke({"city": "Bengaluru"})` printed `Real current weather in Bengaluru, India: 24.9°C, wind 21.0 km/h.`
- It works on a good day. What it does on a bad day (tested against a local stand-in for the two Open-Meteo endpoints):

| The weather service… | The class tool returns | Why that hurts |
|---|---|---|
| answers with HTTP 500 (an outage) | `Could not find a location matching '…'.` | An outage is reported as a spelling mistake |
| drops `current_weather` from its reply | `… None°C, wind None km/h.` | Wrong data, which the model repeats as fact |
| never answers | nothing: still waiting after 5 s | `requests` has **no default timeout**, so the whole agent run hangs |

Hardened version (*added by Claude*):

```python
import requests
from langchain.tools import tool

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT = (3, 10)          # seconds: (connect, read). requests has NO default timeout

@tool
def get_real_weather(city: str) -> str:
    """Get the current temperature and wind for a city from Open-Meteo (live data)."""
    try:
        geo = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=TIMEOUT)
        geo.raise_for_status()                         # a 500 is an outage, not "city not found"
        results = geo.json().get("results")
        if not results:
            return f"No place called '{city}' was found. Ask the user to check the spelling."
        place = results[0]
        wx = requests.get(FORECAST_URL, timeout=TIMEOUT, params={
            "latitude": place["latitude"], "longitude": place["longitude"], "current_weather": "true"})
        wx.raise_for_status()
        current = wx.json()["current_weather"]         # KeyError if the reply shape changed
        return (f"{place['name']}, {place.get('country', '')}: "
                f"{current['temperature']}°C, wind {current['windspeed']} km/h")
    except requests.RequestException as e:             # timeouts, connection errors, HTTP errors
        return f"Weather service unavailable ({type(e).__name__}). Do not guess the weather; tell the user."
    except (KeyError, ValueError) as e:                # missing fields, invalid JSON
        return f"Weather service sent an unexpected reply ({type(e).__name__}). Do not guess the weather."
```

✅ *Verified against the same stand-in: Bengaluru gave `Bengaluru, India: 24.9°C, wind 21.0 km/h`; the 500 gave `Weather service unavailable (HTTPError)…`; the missing field gave `…unexpected reply (KeyError)…`; the silent server gave `…(ReadTimeout)…` after 1.0 s (read timeout set to 1 s for the test).*

- **Every outside call gets a timeout.** One slow API otherwise blocks the whole run, and the user waits for nothing
- **Tell an outage apart from a real "not found".** The model acts on the text you return: "check the spelling" and "the service is down, don't guess" lead to different replies
- **Fail on a changed reply instead of reading `None`** (`["current_weather"]`, not `.get(...)`): a wrong number stated as fact is worse than an error
- **Return text or raise?** Returning text, as here, keeps the tool self-contained. To retry instead, let the exception escape and add `ToolRetryMiddleware` and `ToolErrorMiddleware` ([Chapter 9](09-guardrails-to-do-lists-and-tool-resilience.md), 9.4–9.6)
- Weather stays valid for minutes: cache it per city with the helper in [Chapter 1](01-introduction-to-langchain.md), 1.8

> [!NOTE]
> **Two ways to ask Open-Meteo for the current weather.**
> - The class code sends `current_weather=true` and reads `current_weather.temperature`. It worked in class
> - Open-Meteo's current docs show `current=temperature_2m,wind_speed_10m`, which returns a `current` object instead
> - I found no deprecation notice. Check [open-meteo.com/en/docs](https://open-meteo.com/en/docs) before building on either
> - *Web-checked 2026-11-15. open-meteo.com was blocked from this environment, so neither form was called live*

## 6.4 The forgetting problem and the fix

- Tell the agent "my name is Mayank". In the next call ask "who am I?". It does not know
- By default **an agent does not remember you**
- Fix: a **checkpointer** plus a **`thread_id`**

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
agent_with_memory = create_agent(model=model, tools=[...], checkpointer=checkpointer)

config = {"configurable": {"thread_id": "mayank-session-1"}}
agent_with_memory.invoke({"messages": [("user", "My name is Mayank")]}, config=config)
agent_with_memory.invoke({"messages": [("user", "Who am I?")]}, config=config)
```

- This is the official pattern from the docs. Nothing custom
- **`thread_id`** is just a unique id so the checkpointer can find the right chat
  - Not a reserved keyword. It is the key the checkpointer looks for in the config
  - **Your application** creates and controls it, not the user. New session, new `thread_id`
  - The docs generate it with `uuid7()`: unique, hard to guess, and time-ordered, so threads sort by creation

```python
from langchain_core.utils.uuid import uuid7

config = {"configurable": {"thread_id": str(uuid7())}}   # one new id per conversation
```

- **Forget the `thread_id` and the call fails.** Once an agent has a checkpointer, every call needs one (class 11 made the same point). Tested on 1.5.0: `ValueError: Checkpointer requires one or more of the following 'configurable' keys: thread_id, checkpoint_ns, checkpoint_id`
- **`InMemorySaver` lives in RAM.** No time limit, but it ends when the Python process ends
- A persistent saver (for example Postgres) follows the same pattern
- **Deployed on LangSmith?** A checkpointer is provided for you. Locally you must pass one, or `thread_id` does nothing
- **A thread is like an email thread:** many interactions, one conversation. Short-term memory is scoped to one thread
- **When memory is written and read** (docs): the agent's state is saved when the agent is invoked and each time a step (a model call, a tool call) completes. It is read at the start of each step
- Short-term memory **is** the agent's state, mainly `messages`. Custom fields are saved with it too (`state_schema`, 6.6)

### `thread_id` vs `context`: two different jobs

| | `thread_id` (in `config`) | `context` (with `context_schema`) |
|---|---|---|
| Scopes | The **conversation**: message history, checkpoints | One **run**: data tools and middleware read at call time |
| Typical contents | A conversation id | User id, plan or tier, API keys, feature flags |
| Lives | As long as the checkpointer keeps it | Only for that `invoke` |
| Read by | The checkpointer | `runtime.context` in tools and middleware ([Ch 11](11-runtime-and-human-in-the-loop.md)) |
| Who sets it | Your app | Your app, from auth, never from the model |

```python
from dataclasses import dataclass

@dataclass
class Context:
    user_id: str

agent = create_agent(model=model, tools=[...], context_schema=Context, checkpointer=InMemorySaver())
agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in San Francisco?"}]},
    config={"configurable": {"thread_id": str(uuid7())}},   # which conversation
    context=Context(user_id="user-123"),                    # who is asking, this run
)
```

- They are usually passed **together**: the thread says which chat, the context says who and with what rights

✅ *Verified: `uuid7`, and `thread_id` with `context` in one call (details at the end).*
- Before and after, as drawn on the whiteboard:
  - **Without a saver:** `invoke`, result, `invoke2`: "Empty and nothing remembered"
  - **With a saver:** `invoke2` has all the previous messages

Look at what is saved for a thread:

```python
state = agent_with_memory.get_state(config)
print(state.values["messages"])    # the saved conversation
print(state.next)                  # () when the run finished, otherwise the step it is paused at
```

- Full mechanics (state as checkpoints) belong to LangGraph and are covered there in depth

### Deleting messages with `RemoveMessage`

- *Source: LangChain docs, `short-term-memory.mdx` (Delete messages).*
- The state key must use the `add_messages` reducer; the default `AgentState` does.
- Remove some: return `{"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}` from a hook.
- Remove all: `RemoveMessage(id=REMOVE_ALL_MESSAGES)` from `langgraph.graph.message`.
- ✅ *Verified (details in "How this chapter was checked").*
- Deleting is **permanent**: the checkpointer saves the shorter history. Trimming for one model call only is in [Chapter 7](07-middleware.md), 7.5

```python
from langchain.messages import RemoveMessage
from langchain.agents import AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime

@after_model
def delete_old_messages(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove old messages to keep the conversation manageable."""
    messages = state["messages"]
    if len(messages) > 2:
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}   # the earliest two
    return None

agent = create_agent(model, tools=[], middleware=[delete_old_messages], checkpointer=InMemorySaver())
```

- What the thread holds after each turn (checked, scripted model):
  - `hi! I'm bob` → `[human "hi! I'm bob", ai "Hi Bob!"]`
  - `write a short poem about cats` → `[human "write a short poem…", ai "cat poem"]`. The first turn is gone
  - `what's my name?` → the model never sees "bob" again. Deleting is forgetting

> [!WARNING]
> **The remaining history must still be valid for the provider.**
> - Some providers expect the history to **start with a user message**
> - Most require an AI message with tool calls to be **followed by its tool results**
> - Deleting "the first N" messages can cut between a tool call and its result. Check what is left, not just how many. *Source: LangChain docs, Short-term memory.*


## 6.5 Saver, store, cache or database?

```mermaid
flowchart LR
    subgraph Thread["Short-term: one conversation"]
        CP[(Checkpointer<br/>thread_id)]
    end
    subgraph LongTerm["Long-term: across conversations"]
        ST[(Store<br/>namespace + key)]
    end
    A[Agent run] -->|saves every step| CP
    A -->|reads/writes facts| ST
    CP -->|same thread_id| A
```

There is no single right answer. It depends on the use case.

- **Memory saver (checkpointer)**
  - Saves **one conversation's** history so the agent can resume it, tied to a `thread_id`
  - Lifetime: as long as that thread needs, from minutes to persistent, depending on the backend
- **Memory store**
  - Saves information **about a user** (preferences, facts) for use across many conversations
  - Persistent by design. This is **long-term memory**
- **Cache**
  - Avoids repeating expensive calls for near-identical requests
  - Short and tunable: an hour, a day, whatever fits
- **Database**
  - General persistent storage for anything the app must keep
  - Persistent, defined by the application

Rules of thumb:

- Short-lived conversation context → **saver**
- Preferences across sessions → **store**
- Same expensive call repeated → **cache**
- Everything else that must last → **database**
- Example: a user says "I like Python as a language". A saver would only help that one chat. A **store** makes it usable in every later chat
- Example: "weather in Delhi" asked a million times an hour. Cache the result instead of calling the API each time
- Example: a customer chatbot that closes after 10 minutes of silence. Keeping that chat in memory forever helps nobody

The whiteboard compares the two in-memory classes:

- **`InMemoryStore`**
  - Module `langgraph.store.memory`
  - Stores long-term application data: arbitrary key-value data (user memory, preferences, documents, profiles)
  - You call it: `put()`, `get()`, `search()`, `delete()`. Used by tools, nodes, custom code
  - **Supports namespaces:** yes. Semantic search: depends on the configured index
  - Lives only while the Python process runs
- **`InMemorySaver`**
  - Module `langgraph.checkpoint.memory`
  - Saves graph checkpoints: the entire graph state after each step
  - Used **automatically** by the graph runtime. Typical use: resume interrupted conversations, keep chat history
  - Namespaces: no. Semantic search: no
  - Lives only while the Python process runs

> [!IMPORTANT]
> **🏭 In production**
> - `InMemorySaver` is for development only; use a database saver (for example Postgres) so threads survive restarts and scale across workers
> - Namespace long-term memory by user or tenant, and never let one user's memory into another's prompt
> - Set retention: old threads cost storage and may hold personal data you must delete on request
> - *Added by Claude.*

### Long-term memory with a store

- Long-term memory = what the agent stores and recalls **across conversations and sessions**
  - Short-term memory is scoped to one thread (6.4). Long-term memory persists across threads and can be recalled at any time
- It is built on **LangGraph stores**: each memory is a **JSON document** filed under a `namespace` and a `key`
  - `namespace` ≈ a folder: a tuple such as `("my-user", "chitchat")`. It often holds user or org ids
  - `key` ≈ a file name inside that folder
- Create a store and pass it to `create_agent`. Tools then reach it as `runtime.store`

```python
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()   # an in-memory dictionary: development only, use a DB-backed store in production
agent = create_agent("claude-sonnet-4-6", tools=[], store=store)
```

```mermaid
flowchart TD
    S[(Store)] --> N1["namespace<br/>('my-user', 'chitchat')"]
    S --> N2["namespace<br/>('my-user', 'travel')"]
    S --> N3["namespace<br/>('other-user', 'chitchat')"]
    N1 --> K1["key 'a-memory'<br/>rules, my-key"]
    N2 --> K2["key 'prefs'<br/>seat: aisle"]
    N3 --> K3["key 'a-memory'<br/>another user's rules"]
```

- The tuple makes a hierarchy: `search(("my-user",))` sees both `my-user` namespaces, never `other-user`'s
- For memory types (semantic, episodic, procedural) and strategies for writing them, the docs point to the [Memory conceptual guide](https://docs.langchain.com/oss/python/concepts/memory#long-term-memory) (not read for these notes)

### Storing, getting and searching memories

```python
from collections.abc import Sequence

from langgraph.store.base import IndexConfig
from langgraph.store.memory import InMemoryStore


def embed(texts: Sequence[str]) -> list[list[float]]:
    # Replace with an actual embedding function or LangChain embeddings object
    return [[1.0, 2.0] for _ in texts]


store = InMemoryStore(index=IndexConfig(embed=embed, dims=2))
user_id = "my-user"
application_context = "chitchat"
namespace = (user_id, application_context)
store.put(
    namespace,
    "a-memory",
    {
        "rules": [
            "User likes short, direct language",
            "User only speaks English & python",
        ],
        "my-key": "my-value",
    },
)
# get the "memory" by ID
item = store.get(namespace, "a-memory")
# search for "memories" within this namespace, filtering on content equivalence, sorted by vector similarity
items = store.search(
    namespace, filter={"my-key": "my-value"}, query="language preferences"
)
```

- `put(namespace, key, value)`: `value` is a dict, stored as one JSON document
- `get(namespace, key)`: one item, or `None` if the key is missing
- `search(namespace_prefix, filter=..., query=..., limit=10)`:
  - `filter`: exact match on fields of the value
  - `query`: natural-language text, ranked by **vector similarity**. That needs an `index`: an embedding function (or a LangChain embeddings object) and its `dims`
  - The namespace is a **prefix**, so one search can cover many namespaces ("cross-namespace searching", in the docs' words)
- Also on every store: `delete(namespace, key)` and `list_namespaces()`
- **Docs vs package** (tested on `langgraph` 1.2.22):
  - The docs' comments call the result of `get` a "StoreValue object". The package returns `langgraph.store.base.Item`, with `.value`, `.key`, `.namespace`, `.created_at` and `.updated_at`
  - `search` returns `SearchItem`s, which add a `.score`
- **Watch out** (tested):
  - The docs' `embed` gives every text the same vector, so every score ties. It only shows the shape of the call
  - A `query` on a store with **no** index does not fail. It returns the items unranked, with `score=None`
  - `search` returns at most 10 items unless you pass `limit`

### Read and write memory from tools

The docs' two examples, a read tool and a write tool, combined here into one agent:

```python
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import ToolRuntime, tool
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict


@dataclass
class Context:
    user_id: str


class UserInfo(TypedDict):           # the structure of user information, for the LLM
    name: str


store = InMemoryStore()
store.put(("users",), "user_123", {"name": "John Smith", "language": "English"})


@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """Look up user info."""
    assert runtime.store is not None             # the store given to create_agent
    user_info = runtime.store.get(("users",), runtime.context.user_id)
    return str(user_info.value) if user_info else "Unknown user"


@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Save user info."""
    assert runtime.store is not None
    runtime.store.put(("users",), runtime.context.user_id, dict(user_info))
    return "Successfully saved user info."


agent = create_agent("claude-sonnet-4-6", tools=[get_user_info, save_user_info],
                     store=store, context_schema=Context)
agent.invoke({"messages": [{"role": "user", "content": "My name is John Smith"}]},
             context=Context(user_id="user_123"))   # whose information is updated
item = store.get(("users",), "user_123")            # read the store directly, outside the agent
```

- `user_id` comes from `context`, which your app sets. The model never chooses whose memory it touches
- `runtime.store` is `None` when the agent was built without a store; the `assert` makes that a loud error
- The `UserInfo` TypedDict becomes the tool's argument schema, so the model must send `{"name": ...}`

> [!WARNING]
> **`put` replaces the whole document.** In the run above, `save_user_info` overwrote `{"name": "John Smith", "language": "English"}` with `{"name": "John Smith"}`, and `language` was gone. To update one field, `get` the old value, merge, then `put`. *(Found in testing; the docs do not mention it.)*

### Long-term memory from a tool, scoped per user (*added by Claude*)

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore

@dataclass
class Ctx:
    user_id: str                      # from your auth layer, never from the model

@tool
def save_preference(pref: str, runtime: ToolRuntime[Ctx]) -> str:
    """Save a lasting user preference (language, tone, favourite tools)."""
    runtime.store.put(("users", runtime.context.user_id), "prefs", {"text": pref})
    return "saved"

agent = create_agent(model="openai:gpt-4o-mini", tools=[save_preference],
                     store=InMemoryStore(), context_schema=Ctx)
agent.invoke({"messages": [{"role": "user", "content": "I like Python"}]},
             context=Ctx(user_id="u42"))
```

- The **namespace** `("users", user_id)` is the isolation boundary; the `user_id` comes from `context`, so the model can't read or spoof it
- Read it back in another conversation with `runtime.store.get(("users", user_id), "prefs")`, or `search(...)` when the store has an embedding index

> [!CAUTION]
> **🔒 Security: put the user in the namespace, not only in the key**
> - The docs' tools file every user under one namespace, `("users",)`, with the user id as the key
> - That is safe for `get`, but `search(("users",))` returns **every user's** record (tested: `u1` and `u2` both came back)
> - A memory-search tool built on that layout can leak one user's facts into another user's prompt
> - With `("users", user_id)` as the namespace, every search is limited to that user's prefix
> - *Added by Claude.*

✅ *Verified offline with a scripted model: after the run, `store.get(("users", "u42"), "prefs").value` was `{'text': 'likes Python'}`.*

### Swapping in durable backends

```python
# uv add langgraph-checkpoint-postgres "psycopg[binary]"
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

with PostgresSaver.from_conn_string(DB_URI) as saver, PostgresStore.from_conn_string(DB_URI) as store:
    saver.setup(); store.setup()               # create tables once
    agent = create_agent(model=..., tools=..., checkpointer=saver, store=store)
```

- Same agent code; only the objects change. `langgraph-checkpoint-sqlite` (`SqliteSaver`) is the lighter option for a single machine
- The combined block is Added by Claude. Each half is in the docs:
  - **Saver** (Short-term memory page) and **store** (Long-term memory page) share one install: `pip install -U langgraph-checkpoint-postgres "psycopg[binary]"`. The package installs `psycopg` 3 **without** extras; `[binary]` is the recommended add-on
  - `PostgresSaver.from_conn_string(DB_URI)` / `PostgresStore.from_conn_string(DB_URI)` as a context manager, then `.setup()` once to create the tables
  - Semantic search on Postgres: `PostgresStore.from_conn_string(DB_URI, index=IndexConfig(embed=embed, dims=2))`
  - The docs' URI: `"postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable"`. *Added by Claude:* never put real credentials in code
  - Other checkpointer libraries: SQLite, Postgres, Azure Cosmos DB. Other stores, including Redis and MongoDB: the docs' [store integrations](https://docs.langchain.com/oss/python/integrations/long-term-memory) list
- *Checked:* `SqliteSaver` for real. A thread saved through one saver was read back by a **new** saver and a **new** agent on the same file (a stand-in for a restart): the second agent saw `Hi! My name is Bob.`
- *Not run:* Postgres (no server in the sandbox; `PostgresSaver` and `PostgresStore` were only imported or taken from the docs)

## 6.6 Putting it together: the full TripMate agent

### Every `create_agent` argument, in one place

| Argument | Accepts | Use it for | Taught in |
|---|---|---|---|
| `model` | `"provider:model"` string **or** a model object (`init_chat_model(...)`, `ChatOpenAI(...)`) | The brain. Use an object when you need parameters (temperature, timeout, Azure deployment) | [Ch 2](02-langchain-family-and-harness-engineering.md) 2.6, [Ch 3](03-models-messages-and-parameters.md) |
| `tools` | Plain Python functions, `@tool` tools, or **tool dicts** (JSON-schema style) | Actions the model may request | [Ch 5](05-tools.md) |
| `system_prompt` | A string **or** a `SystemMessage` | Role and rules. For a prompt that changes per run, use middleware | [Ch 3](03-models-messages-and-parameters.md), [Ch 10](10-shell-tools-and-custom-middleware.md) |
| `response_format` | A Pydantic model, dataclass, JSON schema or strategy | A validated answer in `result["structured_response"]` | [Ch 4](04-structured-output.md) |
| `middleware` | A list of middleware | Growing the harness (6.1) | [Ch 7](07-middleware.md)–[10](10-shell-tools-and-custom-middleware.md) |
| `state_schema` | A subclass of `AgentState` | Extra fields carried through the run | below |
| `context_schema` | A dataclass or TypedDict | Per-run data for tools and middleware | 6.4, [Ch 11](11-runtime-and-human-in-the-loop.md) |
| `checkpointer` | `InMemorySaver()`, a Postgres saver... | Short-term memory per `thread_id` | 6.4 |
| `store` | `InMemoryStore()`, a Postgres store... | Long-term memory across threads | 6.5 |
| `name` | A string | The agent's id when it is a subgraph inside a multi-agent system | below, [Ch 13](13-multi-agent-systems-and-subagents.md) |

- `create_agent` also takes `interrupt_before`, `interrupt_after`, `debug` and `cache`. You will rarely need them: human approval is done with middleware ([Ch 11](11-runtime-and-human-in-the-loop.md))
- `create_agent` returns a compiled LangGraph graph. That is why `invoke`, `stream`, `get_state` and checkpointers all work on it

```python
from pydantic import BaseModel

class Answer(BaseModel):
    summary: str
    confidence: float

agent = create_agent(model="openai:gpt-6.1-sol", tools=tools, response_format=Answer)
result = agent.invoke({"messages": [{"role": "user", "content": "Summarize AI trends"}]})
result["structured_response"]      # Answer(summary=..., confidence=...)
```

### Agent state: what the run carries

- Every agent keeps its working data in **`AgentState`**, a typed dictionary
- Built-in field: **`messages`**, the full conversation for the current thread. It is **append-only**: new messages are added, old ones are not replaced (deleting needs `RemoveMessage`, 6.4)
- `structured_response` appears in the result when you set `response_format`
- `AgentState` is also what every node-style hook receives (`before_model`, `after_model`...). A hook returns a dict of updates that is merged back in ([Ch 7](07-middleware.md))
- To carry your own fields, subclass it and pass `state_schema=`:

```python
from langchain.agents import AgentState, create_agent

class MyState(AgentState):
    user_id: str
    call_count: int

agent = create_agent(model="openai:gpt-6.1-sol", tools=[], state_schema=MyState)
```

| Put it in… | When the value… | Example |
|---|---|---|
| **State** (`state_schema`) | Changes during the run, and should be saved with the thread | A call counter, a flag set by a tool |
| **Context** (`context_schema`) | Is fixed for the run, and comes from your app | User id, account tier |
| **Store** | Must last across conversations | Preferences |

### Name your agent

- `name="research_assistant"` gives the agent an id
- It matters most when this agent becomes a **subgraph** inside a multi-agent system: traces, streamed chunks and handoffs show which agent did what ([Ch 13](13-multi-agent-systems-and-subagents.md))
- The name is copied onto the agent's replies (`AIMessage.name`). Use short `snake_case` names, because some providers restrict the characters allowed in that field

### The full TripMate agent

```python
from dataclasses import dataclass

@dataclass
class TravelerContext:          # the class's fields (notebook cell 138), as a plain dataclass
    user_id: str
    home_currency: str
    membership_tier: str
    is_premium_member: bool

full_tripmate = create_agent(
    model="openai:gpt-5-mini",
    tools=[
        tavily_search,              # TavilySearch(max_results=5, topic="general"): needs a Tavily key
        get_real_weather,
        save_trip,
        get_saved_trips,
        save_travel_style,
        recall_travel_style,
        book_premium_concierge,
    ],
    system_prompt=(
        "You are TripMate, a real travel planning assistant. Check real weather before "
        "recommending destinations. Save trips when confirmed. Remember travel style preferences."
    ),
    middleware=[gate_premium_tools],
    checkpointer=InMemorySaver(),
    store=travel_store,
    context_schema=TravelerContext,
    name="tripmate_agent",
)
```

What each argument is for:

- **`tools`:** weather and search are real APIs, trips go to SQLite, travel style goes to the store, the concierge tool is gated
- **`middleware=[gate_premium_tools]`:** removes the premium tool unless the user is allowed it. "Only passed when required". Read the flag from context: the class version read state, where the flag never arrived (see "Why the full TripMate never finished" below)
- **`checkpointer=InMemorySaver()`:** saves the chat, the previous messages
- **`store=travel_store`:** an `InMemoryStore` for preferences, key-value pairs
- **`context_schema=TravelerContext`:** declares the data you pass in per run, to reach **middleware and tools** (`runtime.context`)
- **`name="tripmate_agent"`:** names the agent

Three kinds of memory in one agent:

- **`InMemorySaver`:** previous messages
- **SQL database:** the user's saved trips
- **`InMemoryStore`:** the user's preferences

Run it, passing the per-run context:

```python
result = full_tripmate.invoke(
    {"messages": [("user", "I'm rohan_01. What's the weather like in Bali? I prefer budget travel, please remember that.")]},
    {"configurable": {"thread_id": "rohan-planning-session"}},
    context=TravelerContext(user_id="rohan_01", home_currency="INR", membership_tier="standard", is_premium_member=False),
)
```

### Why the full TripMate never finished (the class 11 homework)

The trip schemas from the class (notebook cell 122), and the two things the class version added to the agent above:

```python
from typing import Union
from pydantic import BaseModel, Field
from langchain.agents.structured_output import ToolStrategy

class NewTripRequest(BaseModel):
    """A request to plan a new trip."""
    user_id: str
    destination: str
    start_date: str = Field(description="Format: YYYY-MM-DD")
    end_date: str = Field(description="Format: YYYY-MM-DD")

class ModifyTripRequest(BaseModel):
    """A request to change an existing trip."""
    user_id: str
    trip_id: int
    change_description: str

class CancelTripRequest(BaseModel):
    """A request to cancel an existing trip."""
    user_id: str
    trip_id: int

# added in the class version (notebook cell 139)
response_format = ToolStrategy(Union[NewTripRequest, ModifyTripRequest, CancelTripRequest])
system_prompt = ("... Remember travel style preferences"
                 "Please make sure that you give the answer after running for 10  times and don't keep on running, be quick")
```

What happened in class:

- An earlier, smaller agent with the same `Union` worked: "I am rohan_01, plan a trip to Bali from 2026-09-01 to 2026-09-10" gave `NewTripRequest(...)` after one model call (cells 123–127)
- The full agent, asked the weather-and-preference question above, ran on and on. Every call re-sent a longer history, and it had cost about $0.50 when the mentor stopped it
- A student asked: "How does the model know that the loop is completed?"
- The mentor suspected the Pydantic warnings printed at the start, and set the fix as homework

What I found (tested on `langchain` 1.5.0 with stand-in models, no live model):

```mermaid
flowchart TD
    M["Model call<br/>tool_choice = required"] --> W{Which tool?}
    W -->|weather, search, save| T[Run the tool] --> M
    W -->|NewTrip, ModifyTrip or CancelTrip| E([structured_response: the run ends])
    W -.->|plain-text answer| N[Not allowed]
```

1. **`ToolStrategy` forces a tool call on every model call.** Every request carried `tool_choice: "required"`. The model can never just answer, so the run ends only when it calls one of the schema tools ([Chapter 4](04-structured-output.md), 4.4)
2. **The question fits none of the schemas.** "What's the weather like in Bali? I prefer budget travel" is not a new trip (no dates), a change or a cancellation. So there is no honest way to finish: the model keeps calling tools, or invents dates to fill `NewTripRequest` ([Chapter 4](04-structured-output.md), 4.11)
3. **Nothing in code stops it.** `create_agent` sets a step limit of 9,999, about 5,000 model calls. The prompt's "stop after 10 times" is a request, not a limit. With a model that never picks a schema tool and the step limit lowered to 25, the run raised `GraphRecursionError` after 13 model calls
4. **The warning is not the cause.** It comes from LangChain serialising the `runtime` argument of tools such as `save_travel_style` (`PydanticSerializationUnexpectedValue … field_name='context'`). Tested: 2 warnings with a plain dataclass, 2 with a `BaseModel`, none for a tool without `runtime`. Each run finished and the store was written. A warning never retries anything
5. **The premium gate never let anyone in.** `gate_premium_tools` reads `request.state`, and `is_premium_member` in the invoke input is dropped because the state schema has no such field. Tested: a premium user's model call never got `book_premium_concierge` ([Chapter 5](05-tools.md), 5.10)

> [!WARNING]
> **`@dataclass` on a `BaseModel` does not build.**
> - The saved notebook declares `@dataclass class TravelerContext(BaseModel)`
> - Creating one raises `AttributeError: 'TravelerContext' object has no attribute '__pydantic_fields_set__'` (tested on Pydantic 2.10 to 2.14, Python 3.12 and 3.13)
> - The class run printed warnings, not this error, so it must have used a plain `@dataclass`. The `(BaseModel)` looks like a later edit ("ideally, we could make it base model"), saved without re-running. *My reading of the notebook*
> - Use a dataclass or a `BaseModel`, never both

The homework, solved:

```python
from langchain.agents.middleware import ModelCallLimitMiddleware, wrap_model_call

class GeneralReply(BaseModel):
    """Any other answer: weather, advice, questions, small talk."""
    message: str

@wrap_model_call
def gate_premium_from_context(request, handler):
    """Only premium members see the concierge. The flag comes from your app (auth), via context."""
    if not request.runtime.context.is_premium_member:
        request = request.override(tools=[t for t in request.tools if t.name != "book_premium_concierge"])
    return handler(request)

full_tripmate = create_agent(
    model="openai:gpt-5-mini",
    tools=[tavily_search, get_real_weather, save_trip, get_saved_trips,
           save_travel_style, recall_travel_style, book_premium_concierge],
    system_prompt=(
        "You are TripMate, a real travel planning assistant. Check real weather before "
        "recommending destinations. Save trips when confirmed. Remember travel style preferences."
    ),
    response_format=ToolStrategy(
        Union[NewTripRequest, ModifyTripRequest, CancelTripRequest, GeneralReply]),   # 1. a way out
    middleware=[
        gate_premium_from_context,                                    # 2. premium flag from context
        ModelCallLimitMiddleware(run_limit=10, exit_behavior="end"),  # 3. "10 times", enforced in code
    ],
    checkpointer=InMemorySaver(),
    store=travel_store,
    context_schema=TravelerContext,                                   # 4. the plain dataclass above
    name="tripmate_agent",
)
result = full_tripmate.invoke(
    {"messages": [("user", "I'm rohan_01. What's the weather like in Bali?")]},
    {"configurable": {"thread_id": "rohan-planning-session"}},
    context=TravelerContext(user_id="rohan_01", home_currency="INR", membership_tier="standard", is_premium_member=False),
)
reply = result.get("structured_response")    # GeneralReply(...), or None when the call limit ended the run
```

✅ *Verified with stand-in models: with `GeneralReply` in the `Union`, a model that took the exit finished in 2 calls with `GeneralReply(message='Bali: 24.9°C, …')`. A model that never picks a schema tool stopped at 10 calls, with the last message `Model call limits exceeded: run limit (10/10)` and `structured_response` `None`. The context gate sent `book_premium_concierge` to a premium user.*

- **Better still, ask whether a chat agent needs `response_format` at all.** It suits agents whose every turn ends in that shape: an extractor, a classifier, a router. TripMate's turns don't. Keep it conversational, and extract a `NewTripRequest` with `with_structured_output` ([Chapter 4](04-structured-output.md), 4.2) once the user confirms a trip *(added by Claude)*
- **Find the loop in the trace, not by guessing.** A LangSmith trace ([Chapter 15](15-testing-agents-and-tracing.md)) lists every model call and the tool it picked. Ten identical tool calls in a row tell the story at a glance
- **Cap the whole conversation too:** `thread_limit` on the same middleware ([Chapter 8](08-prebuilt-middleware-limits-fallback-and-pii.md), 8.1)

## 6.7 Headless tools

Where does a tool run?

- **Server-side (provider) tools:** run on the AI provider's servers (web search, code interpreter). You neither write nor run them
- **Regular tools:** your own functions, running wherever your agent runs
- **Headless tools:** run on the **user's device**: clipboard, location, payments

Why headless tools exist:

- Payment, clipboard, geolocation, browser storage: the server has **no way** to do these. Only the user's machine can
- Example: Amazon needs your location. It runs in **your browser**, gets the location and sends it back. The server in another country cannot read it
- The idea is not AI-specific. An agent now needs to trigger these client-side abilities when appropriate

How it works:

- The tool **definition** (name, description, argument schema) is registered **on the server** with your agent
- The **implementation** is registered only on the **client**
- It runs after a short **interrupt and resume** handshake

## 6.8 Streaming an agent

- *Source: LangChain docs, `streaming.mdx` and `event-streaming.mdx`.*
- **Two APIs.** `agent.stream()` with stream modes is the lower layer. For new apps the docs now recommend event streaming (`stream_events(..., version="v3")`, below), which the package still marks experimental
- `agent.stream(input, stream_mode=...)` modes:
  - `updates`: one chunk per step, keyed by node (`model`, `tools`).
    - If several nodes run in the same step, each one's update arrives as its own chunk
  - `values`: the full state after each step.
  - `messages`: `(token_chunk, metadata)` tuples for LLM tokens.
    - `metadata["langgraph_node"]` says which node produced it; `metadata["lc_agent_name"]` is the agent's `name=`
    - Read the chunk through `token.content_blocks`: text, `tool_call_chunk` pieces, reasoning
  - `custom`: anything a tool writes with `get_stream_writer()`.
  - Pass a list to get several modes at once.
- **`version="v2"`** (LangGraph 1.1+): every chunk is a dict with `type`, `ns`, `data`; no `(mode, data)` tuple unpacking.
  - `invoke(..., version="v2")` returns `GraphOutput` with `.value` (state) and `.interrupts` (empty tuple if none).
  - **Without `version`** (v1, still the default): a list of modes yields `(mode, data)` tuples; a single mode yields the data alone (checked)
```python
from langgraph.config import get_stream_writer
@tool
def get_weather(city: str) -> str:
    """Weather."""
    get_stream_writer()(f"Looking up {city}")   # custom update
    return "sunny"
for c in agent.stream(inp, stream_mode="custom", version="v2"):
    print(c["type"], c["data"])   # custom Looking up SF
```
- A tool that calls `get_stream_writer()` cannot be run outside a LangGraph run.
- **Event streaming (v3, experimental)**: `stream = agent.stream_events(input, version="v3")`.
  - Returns a run object with typed **projections**: read each one on its own instead of unpacking `(mode, data)` tuples. Full detail below
  - Async code can read several projections together with `asyncio.gather`.
- **Why stream at all:** `invoke` returns only at the end. With several tool calls, users need progress before that. A simple progress feed from full-state snapshots:

```python
from langchain.messages import AIMessage, HumanMessage

stream = agent.stream_events(
    {"messages": [{"role": "user", "content": "Search for AI news and summarize the findings"}]},
    version="v3",
)
for snapshot in stream.values:                 # full state after each step
    latest = snapshot["messages"][-1]
    if latest.content:
        if isinstance(latest, HumanMessage):
            print(f"User: {latest.content}")
        elif isinstance(latest, AIMessage):
            print(f"Agent: {latest.content}")
    elif latest.tool_calls:
        print(f"Calling tools: {[tc['name'] for tc in latest.tool_calls]}")
```

- ✅ *Verified (details in "How this chapter was checked").*

### Event streaming (v3): projections and rules

- **Docs vs package:**
  - The docs recommend v3 "for most application and frontend use cases"
  - The package marks it experimental: every call raised `LangChainBetaWarning: The v3 streaming protocol on Pregel is experimental.` (tested on `langgraph` 1.2.22)

```mermaid
flowchart LR
    R["stream_events(input, version='v3')"] --> M["each model call → stream.messages<br/>.text · .reasoning · .tool_calls · .output"]
    R --> T["each tool run → stream.tool_calls<br/>input · output_deltas · output · error"]
    R --> V["each step → stream.values"]
    R --> O["end of run → stream.output"]
    R --> N["nested runs → stream.subagents · stream.subgraphs"]
    R --> X["your transformers → stream.extensions"]
```

| Projection | What you get |
|---|---|
| `stream.messages` | one stream per model call; `.text` deltas, `.reasoning`, `.tool_calls.get()`, `.output` (final `AIMessage`), `.node` |
| `message.reasoning` | reasoning deltas, only if the model emits reasoning blocks ([Ch 3](03-models-messages-and-parameters.md)) |
| `message.tool_calls` | tool-call **argument chunks** while the model writes the call; `.get()` gives the parsed calls |
| `stream.tool_calls` | tool run lifecycle (`tool_name`, `input`, `output_deltas`, `output`, `error`) |
| `stream.values` / `stream.output` | a state snapshot after each step / the final state |
| `stream.subagents` / `stream.subgraphs` | named inner agents / every nested graph ([Ch 13](13-multi-agent-systems-and-subagents.md), 13.6) |
| `stream.extensions` | projections from your own transformers ([Ch 10](10-shell-tools-and-custom-middleware.md), 10.11) |
| `for event in stream` | raw protocol events: every channel, full envelope |

**Reading a projection (sync):** iterate it for live deltas; read it once more for the final value.

```python
stream = agent.stream_events(input, version="v3")
for message in stream.messages:
    print(f"[{message.node}] ", end="")
    for delta in message.text:                 # live: 'It ', 'is ', 'sunny ' ...
        print(delta, end="", flush=True)
    final_text = str(message.text)             # the whole text
    calls = message.tool_calls.get()           # parsed tool calls, [] if none
    usage = message.output.usage_metadata      # tokens live on the final AIMessage
```

- **Tool calls have two views:** `message.tool_calls` streams the **arguments** as the model writes them; `stream.tool_calls` follows the **execution** after the tool starts
- Each argument chunk holds the call's `id`, `name` and **only the new part** of `args` (needs `langchain-core>=1.6.13`; older versions repeat all args so far)
  - *Checked on 1.8.0:* `'{"ci'`, `'ty":'`, `' "Bo'`, `'ston'`, `'"}'`, then `.get()` → `{'city': 'Boston'}`

> [!WARNING]
> **In sync code, read projections together, not one after another.**
> - *Checked on 1.5.0:* a full loop over `stream.messages` left a later `stream.tool_calls` loop **empty**, and the reverse order did the same
> - The docs' own "Tool calls" example uses two loops in a row, so its lifecycle loop printed nothing
> - Use `stream.interleave("messages", "tool_calls", "values")` (sync) or `asyncio.gather` over `astream_events` (async). Both returned every item

```python
for name, item in stream.interleave("messages", "tool_calls", "values"):
    if name == "messages":
        print(str(item.text))
    elif name == "tool_calls":
        print(item.tool_name, item.input)
    elif name == "values":
        print(len(item["messages"]))
```

> [!WARNING]
> **The final message's `.content` is a list in v3.** *Checked:* `stream.output["messages"][-1].content` was `[{'type': 'text', 'text': 'done', 'index': 0}]`, while `invoke()` gave `'done'`. Read `.text`, which works for both.

**Raw events** for channels without a projection, or for debugging:

```python
for event in stream:
    print(event["method"], event["params"]["namespace"], event["params"]["data"])
# methods seen: messages, values, tools ("tool-started", "tool-finished")
```

✅ *Verified on `langchain` 1.5.0 with a scripted model that streams text word by word and tool arguments in 4-character pieces (details at the end).*

### `stream()` patterns: tool calls, reasoning, completed messages

| You want | Stream mode(s) |
|---|---|
| progress after each step (model, then tools) | `"updates"` |
| tokens as they are written, including tool-call pieces | `"messages"` |
| your own progress lines from tools or middleware | `"custom"` |
| live pieces **and** the finished, parsed messages | `["messages", "updates"]` |
| the whole state after every step | `"values"` |

**Tool calls: live pieces plus completed calls.** `messages` gives the partial JSON; `updates` gives the parsed call and the tool's result once they exist.

```python
from langchain.messages import AIMessage, AIMessageChunk, ToolMessage

for chunk in agent.stream({"messages": [input_message]},
                          stream_mode=["messages", "updates"], version="v2"):
    if chunk["type"] == "messages":                         # live pieces
        token, metadata = chunk["data"]
        if isinstance(token, AIMessageChunk):
            if token.text:
                print(token.text, end="|")
            if token.tool_call_chunks:
                print(token.tool_call_chunks)               # name and id first, then args bit by bit
    elif chunk["type"] == "updates":                        # completed messages
        for source, update in chunk["data"].items():
            if source in ("model", "tools"):
                message = update["messages"][-1]
                if isinstance(message, AIMessage) and message.tool_calls:
                    print(f"Tool calls: {message.tool_calls}")
                if isinstance(message, ToolMessage):
                    print(f"Tool response: {message.content_blocks}")
```

- **Messages not in state** (a model called inside middleware, say) never reach `updates`. Two ways out:
- **Way 1, add the chunks up yourself:** every model call ends with an empty chunk whose `chunk_position` is `"last"`

```python
full_message = None
for chunk in agent.stream({"messages": [input_message]}, stream_mode="messages", version="v2"):
    token, metadata = chunk["data"]
    if isinstance(token, AIMessageChunk):
        full_message = token if full_message is None else full_message + token
        if token.chunk_position == "last":                  # this model call is complete
            if full_message.tool_calls:
                print(f"Tool calls: {full_message.tool_calls}")
            full_message = None
```

- **Way 2, send it on the `custom` channel** from where it is made, for example a guardrail middleware:

```python
from langchain.agents.middleware import after_agent, AgentState
from langgraph.config import get_stream_writer

@after_agent(can_jump_to=["end"])
def safety_guardrail(state: AgentState, runtime) -> dict | None:
    result = safety_model.invoke(...)          # a model call that is not saved in state
    get_stream_writer()(result)                # arrives as chunk["type"] == "custom"
    return None
```

**Reasoning tokens** (the model must have reasoning switched on, [Chapter 3](03-models-messages-and-parameters.md)):

```python
for chunk in agent.stream({"messages": [input_message]}, stream_mode="messages", version="v2"):
    token, metadata = chunk["data"]
    for block in token.content_blocks:
        if block["type"] == "reasoning":
            print(f"[thinking] {block['reasoning']}", end="")
        elif block["type"] == "text":
            print(block["text"], end="")
```

- Providers' formats (Anthropic `thinking` blocks, OpenAI reasoning summaries) are normalised to `"reasoning"` blocks (docs)
  - *Checked:* an Anthropic-style `{'type': 'thinking', ...}` block became `{'type': 'reasoning', 'reasoning': ...}` when the message carried `model_provider="anthropic"` metadata (real providers set it). Without that metadata it stayed `non_standard`
- With v3 the same thing is `message.reasoning` (table above)

**Elsewhere:**

- Pausing for approval mid-stream: [Chapter 11](11-runtime-and-human-in-the-loop.md), 11.13
- Tokens from subagents (`subgraphs=True`): [Chapter 13](13-multi-agent-systems-and-subagents.md), 13.6
- Turning streaming off for one model: [Chapter 3](03-models-messages-and-parameters.md), 3.9

✅ *Verified on `langchain` 1.5.0 with the scripted streaming model (details at the end). A real model's reasoning stream was not run.*


## 6.9 Questions from the class

- **Is `thread_id` a reserved keyword?** No. It is just the identifier the checkpointer looks for in the config. The app decides how ids are made
- **Can I see what is stored for a thread?** Yes, through the checkpointer's API (6.4). Full mechanics are in LangGraph
- **Does `InMemorySaver` have a time limit?** No. It lasts as long as the Python process. A persistent store such as Postgres removes that limit
- **Does running a tool cost money like a model call?** No. Only model calls use tokens
- **Will the course cover training a model?** No. It is about using and harnessing existing models
- **Is the older (Classic) course content still relevant?** The concepts carry over. The code reflects LangChain Classic, and this course stays on the latest version
- **How do I choose between store, saver, cache and database?** See 6.5
- **Does the store save configuration?** The class's first answer was "the store saves configuration, the saver saves chats". The class then corrected it with the 6.5 table: the store keeps long-term data (preferences, profiles). Per-run configuration (user id, keys, feature flags) goes in `context` (6.4)
- **Is there a size limit per thread?** Not by default. `InMemorySaver` is limited by your RAM. But every turn re-sends the whole thread, so each turn costs more than the last (6.11; summarization in [Chapter 7](07-middleware.md), 7.5)
- **Thread id or session id?** The same idea here: one id per conversation. One user can have many threads
- **Is Redis used for this?** The class: "Redis is a different thing" (a cache, as in [Chapter 1](01-introduction-to-langchain.md), 1.8). Also true: the `langgraph-checkpoint-redis` package provides a Redis checkpointer (`RedisSaver`) and store (`RedisStore`), so Redis can hold both kinds of memory. *Web-checked; the import paths were read from the 0.6.0 package, not run against a Redis server*
- **How does the model know the loop is complete?** It does not "know". The loop ends when a reply has no tool calls. With `ToolStrategy` it ends when the model calls a schema tool. If neither happens, only a limit stops it (6.6)
- **Why did the full TripMate never finish?** See "Why the full TripMate never finished" in 6.6

## 6.10 Interview corner

**What interviewers listen for:** you separate **short-term** (thread) from **long-term** (store) memory, you know what a checkpointer saves, and you think about privacy and retention.

### 🟢 Basic

<details class="qa"><summary>1. Why does an agent forget between runs, and how do you fix it?</summary>

- Each `invoke` sees only what you pass in
- Add a checkpointer and pass the same `thread_id`
- *Stronger answer:* `InMemorySaver` is per process. Production needs a database-backed saver

</details>

<details class="qa"><summary>2. Saver vs store?</summary>

- Saver = one conversation's state, tied to a `thread_id`, used automatically
- Store = long-term data about a user, shared across threads, you call `put` and `get`
- *Stronger answer:* the store uses namespaces such as `(user_id, "preferences")`, a saver does not

</details>

### 🟡 Intermediate

<details class="qa"><summary>3. Where does a tool's result go?</summary>

- Back to the model, never straight to the user
- *Stronger answer:* that is why a tool call costs at least two model calls, and why `return_direct` exists

</details>

<details class="qa"><summary>4. What are headless tools?</summary>

- Tools whose definition lives on the server but whose code runs on the user's device (clipboard, location, payments), via interrupt and resume

</details>

<details class="qa"><summary>5. <code>thread_id</code> vs <code>context</code>?</summary>

- `thread_id` (in `config`) picks the conversation the checkpointer loads and saves
- `context` is per-run data (user id, tier, flags) that tools and middleware read via `runtime.context`
- *Stronger answer:* both come from your app, never the model; you usually pass both, and `thread_id` does nothing without a checkpointer

</details>

<details class="qa"><summary>6. What does a harness actually do, and what areas does it cover?</summary>

- Gets the model the right context at the right time
- Six areas: execution environment, context management, planning and delegation, fault tolerance, guardrails, steering
- *Stronger answer:* name one middleware per area and say which ones you would add first for a given risk (retries and a call limit before anything clever)

</details>

### 🔴 Senior

<details class="qa"><summary>7. What is <code>context_schema</code> for?</summary>

- Declares the per-run data you pass to tools and middleware (`runtime.context`)
- *Stronger answer:* context is per invocation and immutable. It is the right place for user id and plan, not message history

</details>

<details class="qa"><summary>8. When would you add a cache?</summary>

- When the same expensive call repeats and the answer stays valid for a while (weather, currency rates)

</details>

<details class="qa"><summary>9. Design memory for an assistant used by 10,000 users.</summary>

- A database checkpointer keyed by `thread_id`, one thread per conversation; a store namespaced per user for durable facts
- *Stronger answer:* trim or summarise long threads, encrypt and expire personal data, and add a "forget me" path

</details>

<details class="qa"><summary>10. A value must reach a tool. Do you put it in state, context or the store?</summary>

- **Context:** fixed for the run and set by your app (user id, tier)
- **State:** changes during the run and should be saved with the thread (a counter, a flag a tool sets)
- **Store:** must outlive the conversation (preferences)
- *Stronger answer:* anything security-relevant goes in context, because the model can influence state through tool calls but cannot touch context

</details>

<details class="qa"><summary>11. <code>create_deep_agent</code> or <code>create_agent</code> plus Deep Agents middleware?</summary>

- `create_deep_agent`: the full stack pre-assembled (filesystem, summarization, subagents, prompt caching)
- Hand-built: pick only the pieces you need, for a smaller prompt and fewer tools
- *Stronger answer:* start hand-built for focused agents, since every extra tool and prompt section costs tokens and confuses tool choice; reach for the full stack for long, open-ended research or coding work

</details>

<details class="qa"><summary>12. Your chat UI streams the model's tokens, but tool progress never shows. Why?</summary>

- With v3 in sync code, the UI probably loops over `stream.messages` and then over `stream.tool_calls`
- The first loop consumes the run; the second finds nothing (checked on 1.5.0)
- Fix: `stream.interleave("messages", "tool_calls")`, or async `astream_events` with `asyncio.gather`
- *Stronger answer:* also show argument chunks from `message.tool_calls` so the user sees the call forming, and read text with `.text`, because v3's final `.content` is a list of blocks

</details>

<details class="qa"><summary>13. With <code>stream()</code>, how do you show a tool call forming and then the parsed call and its result?</summary>

- `stream_mode=["messages", "updates"]` with `version="v2"`
- `messages` chunks carry `tool_call_chunks` (name and id first, then the args in pieces)
- `updates` carries the finished `AIMessage` with parsed `tool_calls`, then the `ToolMessage`
- *Stronger answer:* for model calls that never reach state (inside middleware), add chunks until `chunk_position == "last"` or push the finished message through `get_stream_writer()`. With several agents, filter by `metadata["lc_agent_name"]`

</details>

<details class="qa"><summary>14. Store each user's memory under <code>("users",)</code> with the user id as key, or under <code>("users", user_id)</code>?</summary>

- Both work for `get`: one record per user either way
- `search` takes a namespace **prefix**, so under `("users",)` one search returns every user's records
- Choose `("users", user_id)` (add the app context, such as `"chitchat"`, as a third part when needed)
- *Stronger answer:* take `user_id` from `context`, never from a tool argument, and remember `put` replaces the whole document, so merge before writing one field

</details>

<details class="qa"><summary>15. Your agent has a <code>response_format</code>, keeps calling tools, and the bill climbs. Why, and what do you change?</summary>

- With `ToolStrategy`, every model call is sent with `tool_choice` "required", so the model can never just answer
- The run ends only when it calls a schema tool. A question that fits no schema has no exit, and `create_agent`'s step limit is 9,999
- Fixes: add a general reply schema to the `Union`, or drop `response_format` from a chat agent and extract only when needed; cap calls with `ModelCallLimitMiddleware`
- *Stronger answer:* find it in the trace first (the same tool again and again), put `run_limit` and `thread_limit` on every agent, and alert on cost per thread. A prompt line like "stop after 10 times" is not a limit

</details>

<details class="qa"><summary>16. What does a tool that calls a public API need before you give it to an agent?</summary>

- A timeout on every request (`requests` has none by default), so one slow service cannot hang the run
- A clear difference between "not found" and "service down", because the model acts on the text you return
- Strict parsing: fail on a changed reply instead of reading `None`, which the model would state as fact
- *Stronger answer:* decide per tool whether to return an error message or raise and let `ToolRetryMiddleware` and `ToolErrorMiddleware` handle it; cache results that stay valid (weather for minutes); keep keys server-side; log latency and error rate per tool

</details>

> [!TIP]
> **🧩 Design question to practise:** *"A travel assistant must remember a user's preferences across trips but not leak them to other users."* Cover thread vs store, namespaces, what gets saved, and deletion.

## 6.11 Added by Claude, not from the sources

Not in the course material. Established practice, but check current docs.

- **Do not use guessable `thread_id`s.** If ids are sequential, one user can read another's chat. Derive the id from the authenticated user and session, and check ownership on the server
- **Scope the store per user.** Use a namespace like `(user_id, "preferences")`, as in the per-user tool in 6.5, so users never read each other's data. The docs' examples key by user id inside one shared namespace instead; see the 🔒 box in 6.5
- **Long-term memory is personal data.** Decide what you keep, tell users, and make deletion possible (privacy laws such as GDPR and India's DPDP Act apply)
- **Use parameterised SQL** (`?` placeholders, as in 6.3) in tools. The model controls the arguments, so never build SQL with string formatting
- **Threads grow every turn.** The checkpointer keeps the whole message list, and you pay for those tokens on every call. [Chapter 7](07-middleware.md) covers summarization
- **Production savers:** LangGraph ships database-backed checkpointers (for example a Postgres one in a separate package). Check the current package name in the docs

## Cheat sheet

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_core.utils.uuid import uuid7
agent = create_agent(model, tools, system_prompt="...",          # str or SystemMessage
                     middleware=[...], response_format=Answer,     # harness, typed answer
                     state_schema=MyState, context_schema=Ctx,     # run data / per-run data
                     checkpointer=InMemorySaver(), store=InMemoryStore(), name="trip_agent")
cfg = {"configurable": {"thread_id": str(uuid7())}}               # which conversation
store = InMemoryStore(index={"embed": embeddings, "dims": 1536})   # index = semantic search
store.put(("u1", "prefs"), "seat", {"value": "aisle"})          # namespace (folder), key (file), JSON doc
store.search(("u1",), filter={"value": "aisle"}, query="seat")   # prefix + exact filter + similarity
agent.invoke({"messages": [("user", "I prefer aisle seats")]}, cfg, context=Ctx(user_id="u1"))
for c in agent.stream(inp, cfg, stream_mode="updates"): print(c)
# state = changes in the run · context = fixed per run · store = across conversations
response_format=ToolStrategy(Union[NewTrip, CancelTrip, GeneralReply])   # ToolStrategy forces a tool call: give it an exit
ModelCallLimitMiddleware(run_limit=10, exit_behavior="end")              # limits live in code, not in the prompt
requests.get(url, params=params, timeout=(3, 10)); r.raise_for_status()  # every outside call: timeout + status check
```

## Recap

- Agent = model + harness. Models, messages, structured output and tools are its parts
- The harness's job: the right context at the right time. It grows through middleware across six areas: execution environment, context management, planning and delegation, fault tolerance, guardrails, steering
- The loop: message, model decides, tool runs, result goes **back to the model**, repeat, then final answer
- Tool use costs at least two model calls. Tools themselves cost no tokens
- Default = no memory. Add `checkpointer` + `thread_id`
- Saver = one chat. Store = about a user, across chats. Cache = repeat calls. Database = everything else
- Store = JSON documents by namespace (folder) and key (file). `search` scans a namespace prefix, filters exactly and, with an index, ranks by similarity. Put the user id in the namespace
- `put` replaces the whole document. Merge before updating one field
- `store`, `context_schema`, `middleware`, `name` go into `create_agent` alongside tools and the checkpointer
- `thread_id` = which conversation. `context` = who is asking, this run. State = what changes during the run (`state_schema`)
- `name` matters when the agent becomes a subgraph in a multi-agent system
- Headless tools: defined on the server, run on the user's device
- A checkpointer without a `thread_id` in the config raises a `ValueError`
- A real-API tool needs a timeout, a clear "service down" vs "not found", and strict parsing (6.3)
- `ToolStrategy` forces a tool call on every model call. A message that fits no schema has no exit: add a general reply schema or keep `response_format` off chat agents, and cap calls in code (6.6)

## Practice

1. Reproduce the whiteboard before and after: two `invoke()` calls without a checkpointer, then the same two with `InMemorySaver()` and a fixed `thread_id`. Then change the `thread_id` and confirm it forgets
2. Build one **real** tool from a free public API that needs no key, instead of a hard-coded placeholder
3. Add `save_trip` and `get_saved_trips` with SQLite and show the data survives a restart
4. Walk through the TripMate build: real weather, real search, real SQLite persistence
5. Revise saver vs store vs cache vs database until the differences are automatic
6. Print `get_state(config).values["messages"]` for a thread and read it
7. Add a `state_schema` with a `call_count` field and a `before_model` hook that increments it; print it from `get_state`
8. Give an agent `ModelRetryMiddleware`, `PIIMiddleware("email")` and `HumanInTheLoopMiddleware`, then say which harness area each covers
9. Assignment 2 (NovaBank banking assistant), the parts this chapter prepares you for. The assignment has no answer key:
   - A1 Q1 to Q3: describe the loop; what else `thread_id` needs; `thread_id` vs `context` (6.4)
   - A1 Q4 on `stream_mode` (6.8) and Q5 on `name=` (6.6)
   - B1.1: two tools plus a checkpointer, proving memory across two `.invoke()` calls
   - B1.2: a `context_schema` with `account_tier` that a tool reads through `runtime.context`
10. Add the `delete_old_messages` hook, chat three turns, and print the thread after each. Then explain why the agent forgot your name
11. Swap `InMemorySaver` for `SqliteSaver` on a file, restart Python, and continue the same `thread_id`
12. Give an `InMemoryStore` an index with real embeddings, save three preferences, and search them with a query. Then store two users under `("users",)` keyed by id, search `("users",)`, and see what leaks
13. Point the class `get_real_weather` at a small local server that answers 500, drops `current_weather`, or never answers. Then run the hardened version against the same three cases
14. The class 11 homework: give a fake model that never picks a schema tool to an agent with the three trip schemas. Watch it run to the step limit, stop it with `ModelCallLimitMiddleware`, then add `GeneralReply` and let a model take the exit

## How this chapter was checked

- Run offline with a stand-in model on `langchain` 1.4.7: the full agent assembly (tools, middleware, checkpointer, store, context schema, name), per-run context reaching tools and middleware, `InMemoryStore` put, get and search with a tuple namespace, `get_state`, and the SQLite save and get tools
- **Not run against a live model or real APIs:** Open-Meteo, Tavily, a Postgres saver, headless tools. Those are class statements
- The TripMate real-tool code is in the Weekend 05 notebook (`Langchain_Till_Agents.ipynb`, cells 84–144), which class 11 ran. Sections 6.3 and 6.6 now use it. *(This line used to say the code was not in the sources; it was, in that notebook.)* The SQLite example in 6.3 is still my own, shorter version of the class's `save_trip` and `get_saved_trips`
- **Details by section** (moved here from the ✅ markers):
  - *Deleting messages with `RemoveMessage`:* Checked: an `after_model` hook with a checkpointer dropped the first two messages, so after two turns the thread held `['b', '2']`; the remove-all hook left `[]`.
  - *6.8 Streaming an agent:* Checked (scripted model, langchain 1.4.7): the v2 chunk keys; `updates` gave `model, tools, model`; `values` gave 4 snapshots; `messages` gave tuples; `GraphOutput.interrupts` was `()`; `custom` printed both writer lines; v3 `stream.messages` gave text `It is sunny` and tool call `get_weather {'city': 'SF'}`. **Observed:** in sync code, reading `stream.messages` first left `stream.tool_calls` empty. Use `stream.interleave("messages", "tool_calls")` to get both in order (tested in Ch16), plus `stream.interrupted` and `stream.interrupts` for a paused run.
  - *Update from the Agents docs page (2026-11-15), run on `langchain` 1.5.0 and `deepagents` 0.7.38 with a scripted fake chat model (no keys, no network):*
    - 6.1 middleware stack (`ModelRetryMiddleware`, `ToolRetryMiddleware`, `PIIMiddleware`, `HumanInTheLoopMiddleware`) compiled
    - 6.1 Deep Agents pieces inside `create_agent` built and ran; `FilesystemMiddleware` added `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`; `SubAgentMiddleware` added `task`
    - 6.4 `uuid7()` gave a time-ordered id; one call with `thread_id` and `context` let a tool read `user-123` and saved 4 messages to the thread
    - 6.6 `response_format=Answer` returned `Answer(summary='AI grows', confidence=0.8)`; `state_schema` + a `before_model` hook counted 2 model calls; `name="research_assistant"` appeared on the graph and on `AIMessage.name`
    - 6.8 the `stream.values` loop printed User → Calling tools `['search']` → Agent
    - `create_agent` parameter list in 6.6 taken from its signature in `langchain` 1.5.0
    - **Not run:** live models, a LangSmith deployment (the automatic checkpointer is a docs statement), `MemoryMiddleware` and `SkillsMiddleware` with real `AGENTS.md` and `skills/` files
  - *Update from the Short-term memory docs page (2026-11-15), same versions and fake model:*
    - 6.4 `delete_old_messages` (`after_model`) with `InMemorySaver`: after three turns the thread held only the last turn; turn 3's model input had no "bob"
    - 6.5 `SqliteSaver.from_conn_string(file)`: turn 1 through one saver and agent, turn 2 through a new saver and a new agent; the result held all four messages. Packages: `langgraph-checkpoint-sqlite` 3.1.3, `langgraph-checkpoint-postgres` 3.2.1, `psycopg` 3.3.9
    - `PostgresSaver` imported and has `from_conn_string` and `setup`; not connected (no server)
  - *Update from the Streaming docs page (2026-11-15), same versions and scripted streaming model:*
    - `messages` mode with `name="weather_bot"`: every chunk had `langgraph_node` (`model` or `tools`) and `lc_agent_name='weather_bot'`; `content_blocks` showed `tool_call_chunk` pieces; each model call ended with an empty chunk with `chunk_position='last'`
    - The `["messages", "updates"]` loop printed the chunks, `Tool calls: [... 'Boston' ...]` and `Tool response: [...]`. The `chunk_position` aggregation rebuilt `[{'name': 'get_weather', 'args': {'city': 'Boston'}, ...}]`
    - v1: `stream_mode=["updates", "custom"]` yielded tuples; `stream_mode="updates"` yielded dicts
    - `@after_agent(can_jump_to=["end"])` with `get_stream_writer()` sent `{'evaluation': 'safe'}` on `custom`
    - Reasoning: `content_blocks` of chunks holding `{'type': 'reasoning', ...}`, and of `{'type': 'thinking', ...}` with and without `model_provider="anthropic"`. The reasoning snippet, run as written on an agent whose model streamed two Anthropic-style `thinking` chunks then text, printed `[thinking] User wants weather. [thinking] No tool needed.It is sunny`. Not run: a real provider's reasoning stream
    - Every new 6.8 block was extracted from this file and run as written (model swapped for the scripted one)
    - Docs slips: "Agent progress" describes `stream_mode="updates"` but its code uses v3 `interleave`; the guardrail streaming example uses `ToolMessage` without importing it
  - *Update from the Event streaming docs page (2026-11-15), `langchain` 1.5.0, `langchain-core` 1.8.0, `langgraph` 1.2.22, with a scripted chat model whose `_stream` yields text word by word and tool-call args in 4-character `tool_call_chunks`:*
    - `stream.messages`: deltas `['It ', 'is ', 'sunny ', 'in ', 'SF']`, `str(message.text)` `'It is sunny in SF'`, `.tool_calls.get()` on the tool-call message, `message.output.usage_metadata` `{'input_tokens': 12, 'output_tokens': 5, 'total_tokens': 17}`, `.node` `model`
    - `message.tool_calls` chunks: `'{"ci'`, `'ty":'`, `' "Bo'`, `'ston'`, `'"}'`; `.get()` → `{'city': 'Boston'}`
    - `stream.tool_calls` read alone: `get_weather {'city': 'Boston'}`, `output_deltas` empty (the tool returns at once), `output` the result, `error` `None`. After a full `stream.messages` loop it was empty; `stream.messages` after a full `stream.tool_calls` loop was empty too
    - `interleave("messages", "tool_calls", "values")` gave values, messages, values, tool_calls, values, messages, values. `astream_events` + `asyncio.gather` gave both messages and the tool call
    - v3 final `.content` was a list of blocks; `invoke()` gave a string. `LangChainBetaWarning` on every v3 call
    - Raw events: methods `messages`, `values`, `tools` (`tool-started`, `tool-finished`), namespace `[]` at the root
  - *Update from the Long-term memory docs page (2026-11-15), `langchain` 1.5.0, `langgraph` 1.2.22, with a scripted fake chat model (no keys, no network):*
    - Every new 6.5 block was extracted from this file and run as written (model swapped for the scripted one)
    - Store basics: `create_agent(..., store=store)` built. The docs' storage snippet ran; `get` returned an `Item` (not a "StoreValue"), `search` a list of `SearchItem` with `.score`
    - Docs `embed` gave every item the same score. With `DeterministicFakeEmbedding` and `fields=["t"]`, the matching text scored 1.0 and the other lower. A `query` on a store with no index returned items with `score=None`
    - Read and write tools in one agent: `get_user_info` returned `{'name': 'John Smith', 'language': 'English'}`; `save_user_info` then left `{'name': 'John Smith'}` (the `put` overwrite in the ⚠️ box). With no store, the `assert` raised
    - Isolation: under `("users",)` keyed by id, `search(("users",))` returned both users; under `("users", user_id)`, a search on one user's prefix returned only theirs
    - Cheat sheet store lines ran with a fake embedding (1536 dims)
    - `PostgresStore` imported; `from_conn_string` takes `index`, and it has `setup`. Not connected (no server)
  - *Update from the class 11 recording (1 Aug) and the Weekend 05 notebook (2026-11-15), `langchain` 1.5.0, `langchain-openai` 1.8.0, `langgraph` 1.2.22, `pydantic` 2.12.5, `requests` 2.34.2, Python 3.13. No live model or API: a local stand-in for the two Open-Meteo endpoints (reply shapes copied from the notebook) and a local stand-in for the OpenAI API that logged every request body:*
    - 6.3 class `get_real_weather` (code as in cell 87): Bengaluru as in class; a 500 gave "Could not find a location…"; a reply without `current_weather` gave `None°C, wind None km/h`; a server that never answered left the call waiting after 5 s (no timeout)
    - 6.3 hardened version, run as written: the four results in the ✅ line (read timeout lowered to 1 s for the test)
    - 6.4 an agent with `InMemorySaver` invoked without a config raised `ValueError: Checkpointer requires one or more of the following 'configurable' keys: thread_id, checkpoint_ns, checkpoint_id`
    - 6.6 forced tool choice: every request from a `ToolStrategy(Union[...])` agent carried `"tool_choice": "required"`, and the tools sent were `get_real_weather` plus the three schema tools. `ProviderStrategy(NewTripRequest)` and an agent without `response_format` sent no `tool_choice`
    - 6.6 loop: `create_agent` set `recursion_limit` 9999. A stand-in model that always called `get_real_weather` hit `GraphRecursionError` after 13 model calls with the limit set to 25, and stopped at 10 calls with `ModelCallLimitMiddleware(run_limit=10, exit_behavior="end")` (`structured_response` `None`). With `GeneralReply` added, a stand-in that took the exit finished in 2 calls
    - 6.6 warning: a tool with `runtime: ToolRuntime` produced 2 `PydanticSerializationUnexpectedValue` warnings (`field_name='context'`) with a dataclass context and 2 with a `BaseModel` context; a tool without `runtime` produced none. The warning is raised in `langchain_core/tools/base.py` (`_parse_input`, `model_dump()`). Each run finished and wrote the store
    - 6.6 `@dataclass` on a `BaseModel`: construction raised `AttributeError … '__pydantic_fields_set__'` on Pydantic 2.10.6, 2.11.10, 2.12.5, 2.13.4 and 2.14.3 (Python 3.13) and on 2.11.10 and 2.12.5 (Python 3.12.3). Notebook execution counts: cell 138 ran as number 108, the invoke as number 117
    - 6.6 premium gate: with `is_premium_member: True` in the input and in context, the class gate (reads `request.state`) sent only `save_travel_style`; the context gate also sent `book_premium_concierge`
    - 6.9 Redis: `langgraph-checkpoint-redis` 0.6.0 downloaded and its files read: `langgraph.checkpoint.redis` exports `RedisSaver` (and `ShallowRedisSaver`, async versions), `langgraph.store.redis` exports `RedisStore`. Not run (no Redis server)
    - **Not run:** gpt-5-mini itself, so what the real model did in the class loop is inferred from the forced tool choice and the class output, not reproduced; live Open-Meteo and Tavily
- The 2026 review added the diagrams, 🏭 In production boxes, graded interview layout, extra senior and design questions and the cheat sheet. These are Added by Claude: standard engineering practice. Cheat-sheet APIs were checked against the installed `langchain` 1.4.7 signatures, and the updated cheat sheet against 1.5.0
- **Cheat sheet:** ran the checkpointer, store, thread id and `stream_mode="updates"`; the thread state held the messages. Ran on `langchain` 1.4.7 with a scripted fake chat model (no API keys, no network), so no real model call was made.

## Sources and further reading

- Live-Class-2026, `classes_summary/11 - 01 Aug - Agents, Middleware & Memory.md`
- Live-Class-2026, `classes_transcription_summary/11 - 01 Aug - LangChain - Agents, Memory, Middleware.md`
- Live-Class-2026, whiteboards `Langchain-2-Updated.pdf` and `Agent-Middleware-Architecture.pdf` in `Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/`
- Live-Class-2026, `MIddleware.ipynb` (cells 0 to 56) in the same folder
- Live-Class-2026, `Weekend 05 - 25-26 Jul/09-10 - 25-26 Jul - Structured Output & Tools (CineBot)/Langchain_Till_Agents.ipynb`, cells 84–144 (real weather, Tavily, SQLite trips, the trip schemas, the store tools, the premium gate and the full TripMate run), run in class 11
- Class 11 recording transcript (1 Aug 2026), teaching part only (00:00–03:11; the doubt session after it was left out): the TripMate run and its cost, the store vs saver answer, the questions in 6.9
- Open-Meteo docs: [open-meteo.com/en/docs](https://open-meteo.com/en/docs) (the `current=` parameter; web-checked 2026-11-15, the site itself was blocked here)
- PyPI: [langgraph-checkpoint-redis](https://pypi.org/project/langgraph-checkpoint-redis/) (Redis checkpointer and store, 0.6.0)
- LangChain docs: [Agents](https://docs.langchain.com/oss/python/langchain/agents) (read in full 2026-11-15): agent anatomy, `AgentState`, invocation with `thread_id` and `context`, streaming, the harness capability areas. The three diagrams in `images/` are copied from this page
- LangChain docs: `short-term-memory.mdx`, `streaming.mdx`, `event-streaming.mdx` (earlier batches)
- LangChain docs: [Streaming](https://docs.langchain.com/oss/python/langchain/streaming), read in full 2026-11-15 from its source (`langchain-ai/docs` commit `04d4d4a`, `src/oss/langchain/streaming.mdx` and two snippet files; docs.langchain.com was blocked from this environment). Used for the stream-mode bullets and "`stream()` patterns" in 6.8
- LangChain docs: [Event streaming](https://docs.langchain.com/oss/python/langchain/event-streaming), read in full 2026-11-15 from its source (`langchain-ai/docs` commit `04d4d4a`, `src/oss/langchain/event-streaming.mdx`; docs.langchain.com was blocked from this environment). Used for "Event streaming (v3): projections and rules" in 6.8. The two ⚠️ boxes are from testing
- LangChain docs: [Short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory), read in full 2026-11-15 from its source (`langchain-ai/docs` commit `04d4d4a`, `src/oss/langchain/short-term-memory.mdx`; docs.langchain.com was blocked from this environment). Used for 6.4 (threads, when memory is saved, deleting and the valid-history warning) and 6.5 (the Postgres saver install and setup)
- LangChain docs: [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory), read in full 2026-11-15 from its source (`langchain-ai/docs` commit `04d4d4a`, `src/oss/langchain/long-term-memory.mdx` and eight Python snippet files; docs.langchain.com was blocked from this environment). Used for the store sections of 6.5: namespace and key, put / get / search, the index, the read and write tools, and the Postgres store
- Section 6.11, the SQLite example and the hardened weather tool in 6.3, the state / context / store table in 6.6, the "homework, solved" code and the bullets after it in 6.6, the per-user tool and 🔒 box in 6.5, and senior questions 10–11 and 14–16 are added by Claude and are not from these sources

Previous: [Chapter 5, Tools](05-tools.md) · Next: [Chapter 7, Middleware](07-middleware.md)
