# Chapter 6: Agents and memory

**After this chapter you can:**

- Explain why models, messages, structured output and tools were already "agents"
- Describe the agentic loop and where tokens are spent
- Tell memory saver, memory store, cache and database apart, and pick one
- Give an agent short-term memory (`thread_id`) and long-term memory (`store`)
- Assemble a full agent with tools, middleware, memory, context and a name
- Explain headless tools

**Builds on:** [Chapter 1](01-introduction-to-langchain.md) (first agent, checkpointer basics) and [Chapter 5](05-tools.md) (tools, `ToolRuntime`, `InMemoryStore`). Middleware is in [Chapter 7](07-middleware.md).

## 6.1 Everything so far was already an agent

- **Agent = model + harness.** Around the model you add tools, context, sub-agents, memory, skills, middleware: anything that helps you get the most from the model
- Models, messages, structured output and tools were never separate topics. They are the **components** an agent is built from
- What changed in the last few years? Essentially one thing: we got an artificial brain (the LLM). The rest of software engineering is the same
- So the real question is always: **how do I best harness this model?**

## 6.2 The agentic loop, restated

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
- **`InMemorySaver` lives in RAM.** No time limit, but it ends when the Python process ends
- A persistent saver (for example Postgres) follows the same pattern
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

### Deleting messages with `RemoveMessage` (LangChain docs)

- *Source: LangChain docs, `short-term-memory.mdx` (Delete messages).*
- The state key must use the `add_messages` reducer; the default `AgentState` does.
- Remove some: return `{"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}` from a hook.
- Remove all: `RemoveMessage(id=REMOVE_ALL_MESSAGES)` from `langgraph.graph.message`.
- *Checked:* an `after_model` hook with a checkpointer dropped the first two messages, so after two turns the thread held `['b', '2']`; the remove-all hook left `[]`.
- Postgres saver install note: `langgraph-checkpoint-postgres "psycopg[binary]"`.


## 6.5 Saver, store, cache or database?

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

## 6.6 Putting it together: the full TripMate agent

```python
full_tripmate = create_agent(
    model="openai:gpt-5-mini",
    tools=[
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
- **`middleware=[gate_premium_tools]`:** removes the premium tool unless the user is allowed it. "Only passed when required"
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
from dataclasses import dataclass

@dataclass
class TravelerContext:          # illustrative fields, the slide does not show them
    user_id: str
    is_premium: bool = False

full_tripmate.invoke(
    {"messages": [("user", "Plan a trip for me")]},
    {"configurable": {"thread_id": "trip-1"}},
    context=TravelerContext(user_id="u1", is_premium=False),
)
```

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

## Streaming an agent (LangChain docs)

- *Source: LangChain docs, `streaming.mdx` and `event-streaming.mdx`.*
- `agent.stream(input, stream_mode=...)` modes:
  - `updates`: one chunk per step, keyed by node (`model`, `tools`).
  - `values`: the full state after each step.
  - `messages`: `(token_chunk, metadata)` tuples for LLM tokens.
  - `custom`: anything a tool writes with `get_stream_writer()`.
  - Pass a list to get several modes at once.
- **`version="v2"`** (LangGraph 1.1+): every chunk is a dict with `type`, `ns`, `data`; no `(mode, data)` tuple unpacking.
  - `invoke(..., version="v2")` returns `GraphOutput` with `.value` (state) and `.interrupts` (empty tuple if none).
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
  - `stream.messages`: one stream per model call; `.text` deltas, `.reasoning`, `.tool_calls.get()`, `.output` (final `AIMessage`), `.node`.
  - `stream.tool_calls`: tool run lifecycle (`tool_name`, `input`, `output_deltas`, `output`, `error`).
  - `stream.values`, `stream.output` (final state), `stream.subgraphs`, `stream.extensions`.
  - Async code can read several projections together with `asyncio.gather`.
- *Checked (scripted model, langchain 1.4.7):* the v2 chunk keys; `updates` gave `model, tools, model`; `values` gave 4 snapshots; `messages` gave tuples; `GraphOutput.interrupts` was `()`; `custom` printed both writer lines; v3 `stream.messages` gave text `It is sunny` and tool call `get_weather {'city': 'SF'}`. **Observed:** in sync code, reading `stream.messages` first left `stream.tool_calls` empty; reading it alone worked, so consume one projection at a time or use async.


## 6.8 Questions from the class

- **Is `thread_id` a reserved keyword?** No. It is just the identifier the checkpointer looks for in the config. The app decides how ids are made
- **Can I see what is stored for a thread?** Yes, through the checkpointer's API (6.4). Full mechanics are in LangGraph
- **Does `InMemorySaver` have a time limit?** No. It lasts as long as the Python process. A persistent store such as Postgres removes that limit
- **Does running a tool cost money like a model call?** No. Only model calls use tokens
- **Will the course cover training a model?** No. It is about using and harnessing existing models
- **Is the older (Classic) course content still relevant?** The concepts carry over. The code reflects LangChain Classic, and this course stays on the latest version
- **How do I choose between store, saver, cache and database?** See 6.5

## 6.9 Interview corner

**1. Why does an agent forget between runs, and how do you fix it?**

- Each `invoke` sees only what you pass in
- Add a checkpointer and pass the same `thread_id`
- *Stronger answer:* `InMemorySaver` is per process. Production needs a database-backed saver

**2. Saver vs store?**

- Saver = one conversation's state, tied to a `thread_id`, used automatically
- Store = long-term data about a user, shared across threads, you call `put` and `get`
- *Stronger answer:* the store uses namespaces such as `(user_id, "preferences")`, a saver does not

**3. Where does a tool's result go?**

- Back to the model, never straight to the user
- *Stronger answer:* that is why a tool call costs at least two model calls, and why `return_direct` exists

**4. What are headless tools?**

- Tools whose definition lives on the server but whose code runs on the user's device (clipboard, location, payments), via interrupt and resume

**5. What is `context_schema` for?**

- Declares the per-run data you pass to tools and middleware (`runtime.context`)
- *Stronger answer:* context is per invocation and immutable. It is the right place for user id and plan, not message history

**6. When would you add a cache?**

- When the same expensive call repeats and the answer stays valid for a while (weather, currency rates)

## 6.10 Added by Claude, not from the sources

Not in the course material. Established practice, but check current docs.

- **Do not use guessable `thread_id`s.** If ids are sequential, one user can read another's chat. Derive the id from the authenticated user and session, and check ownership on the server
- **Scope the store per user.** Use a namespace like `(user_id, "preferences")`, as in the examples, so users never read each other's data
- **Long-term memory is personal data.** Decide what you keep, tell users, and make deletion possible (privacy laws such as GDPR and India's DPDP Act apply)
- **Use parameterised SQL** (`?` placeholders, as in 6.3) in tools. The model controls the arguments, so never build SQL with string formatting
- **Threads grow every turn.** The checkpointer keeps the whole message list, and you pay for those tokens on every call. [Chapter 7](07-middleware.md) covers summarization
- **Production savers:** LangGraph ships database-backed checkpointers (for example a Postgres one in a separate package). Check the current package name in the docs

## Recap

- Agent = model + harness. Models, messages, structured output and tools are its parts
- The loop: message, model decides, tool runs, result goes **back to the model**, repeat, then final answer
- Tool use costs at least two model calls. Tools themselves cost no tokens
- Default = no memory. Add `checkpointer` + `thread_id`
- Saver = one chat. Store = about a user, across chats. Cache = repeat calls. Database = everything else
- `store`, `context_schema`, `middleware`, `name` go into `create_agent` alongside tools and the checkpointer
- Headless tools: defined on the server, run on the user's device

## Practice

1. Reproduce the whiteboard before and after: two `invoke()` calls without a checkpointer, then the same two with `InMemorySaver()` and a fixed `thread_id`. Then change the `thread_id` and confirm it forgets
2. Build one **real** tool from a free public API that needs no key, instead of a hard-coded placeholder
3. Add `save_trip` and `get_saved_trips` with SQLite and show the data survives a restart
4. Walk through the TripMate build: real weather, real search, real SQLite persistence
5. Revise saver vs store vs cache vs database until the differences are automatic
6. Print `get_state(config).values["messages"]` for a thread and read it
7. Assignment 2 (NovaBank banking assistant), the parts this chapter prepares you for. The assignment has no answer key:
   - A1 Q1 to Q3: describe the loop; what else `thread_id` needs; `thread_id` vs `context`
   - B1.1: two tools plus a checkpointer, proving memory across two `.invoke()` calls
   - B1.2: a `context_schema` with `account_tier` that a tool reads through `runtime.context`
   - (A1 Q4 on `stream_mode` and Q5 on `name=` are not taught in the sources read so far)

## How this chapter was checked

- Run offline with a stand-in model on `langchain` 1.4.7: the full agent assembly (tools, middleware, checkpointer, store, context schema, name), per-run context reaching tools and middleware, `InMemoryStore` put, get and search with a tuple namespace, `get_state`, and the SQLite save and get tools
- **Not run against a live model or real APIs:** Open-Meteo, Tavily, a persistent saver, headless tools. Those are class statements
- The TripMate real-tool code is not in the sources read for this chapter, so section 6.3 shows only my own SQLite example

## Sources and further reading

- Live-Class-2026, `classes_summary/11 - 01 Aug - Agents, Middleware & Memory.md`
- Live-Class-2026, `classes_transcription_summary/11 - 01 Aug - LangChain - Agents, Memory, Middleware.md`
- Live-Class-2026, whiteboards `Langchain-2-Updated.pdf` and `Agent-Middleware-Architecture.pdf` in `Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/`
- Live-Class-2026, `MIddleware.ipynb` (cells 0 to 56) in the same folder
- Section 6.10 and the SQLite example in 6.3 are added by Claude and are not from these sources

Previous: [Chapter 5, Tools](05-tools.md) · Next: [Chapter 7, Middleware](07-middleware.md)
