# Agents, memory and middleware
> lead: Everything so far was already an agent. This chapter restates the loop, shows why tools must be loaded per user with middleware, introduces headless tools and builds TripMate with real tools and real memory.
meta: Class 11 | 1 August | 40 min read | Code: Weekend 06

## Why it matters

A real agent has to answer three questions the earlier chapters left open. Which tools should *this* user even see? How does it remember a conversation? Where should different kinds of memory live? Interviews love these because the wrong answers (asking the user, or telling the model "please don't") sound plausible.

:::key Models, messages, structured output and tools were always the agent
They were never separate topics. They are the parts an agent is built from. As the instructor put it: apart from the LLM, little else has changed in four or five years. The whole game is how best to **harness** the model.
:::

## Core ideas

### 1. The agentic loop, restated

```mermaid
flowchart TD
    A["Message received"] --> B["Model decides: tool needed?"]
    B -->|Yes| C["Execute tool"]
    C --> D["Append result to messages"]
    D --> B
    B -->|No| E["Final answer returned"]
```

This was once called the **ReAct pattern**. "Agentic loop" is the more accurate term today. A tool's result **always goes back to the model, never straight to the user**. The user sees only the model's final reply after it has processed the result. (The exception, `return_direct` from Chapter 5, deliberately skips that step.)

### 2. The problem: not every tool belongs to every user

CineBot has a standard booking tool, a VIP lounge tool and an admin tool. A regular user asks for a VIP seat. Two tempting fixes fail:

- **Ask the user if they are a VIP.** They will always say yes.
- **Remove the VIP tool.** Then real VIPs cannot use it.

:::analogy A menu that reprints itself
A VIP sees the full menu, a regular guest sees a shorter one. Not because they were told "please do not order the VIP item", but because those items are **not printed on their menu at all**. The tool is not an option, rather than being discouraged.
:::

**Why it costs money.** In class, ChatGPT's connector settings showed that each connector is just a collection of tools (Gmail has write and delete tools, Slack has 11). On a free account, ChatGPT still prepares for around 500 tools it will never let you use, loading them into context and sending unwanted tokens to the model on every call. Companies lose money on this daily. A small related example: asking "who won the FIFA World Cup" triggered an unneeded web search that returned the wrong year, a tool firing when it should not.

### 3. Dynamic tool loading

:::key Say this line precisely
With dynamic tool loading, the set of tools available to the agent is **modified at runtime**, not defined all upfront.
:::

```mermaid
flowchart LR
    A["All possible tools<br/>defined once"] --> B{"Runtime check:<br/>state, permissions, feature flags"}
    B --> C["Only relevant tools<br/>exposed to the model"]
```

Two approaches, depending on whether the tools are known ahead of time:

- **Filter pre-registered tools:** register every tool at creation, then filter what is exposed using state, permissions and context.
- **Register tools dynamically:** for when the full toolset is not known upfront, for example tools arriving through MCP.

**Why not a plain Python `if/else`?** Your code outside the agent cannot read what the agent has access to: its state or its store. For example, when the message count grows, plain code does not see it. That is only possible when running **inside** the agent.

### 4. Middleware: cutting into the loop

> "What if you cut a few things in the middle here?" Before the model call, after it, before a tool, after a tool, after observing.

```mermaid
flowchart LR
    A["Request"] --> M1["before model"]
    M1 --> B["Model call"]
    B --> M2["after model"]
    M2 --> C["Tool call"]
    C --> M3["after tool"]
    M3 --> D["Final result"]
```

Middleware is a universal idea (the instructor compared it to Java's Spring ecosystem), not a LangChain quirk. Chapter 7 covers the built-in ones in depth.

**State-based filtering**, as shown in class:

```python
def only_public_tools_if_unauthenticated(request):
    if not request.state.get("authenticated"):
        request.tools = [t for t in request.tools if t.name.startswith("public_")]
    return request
```

A second example read `request.runtime.context` (a user id and feature flags) to decide which tools to load. The instructor's design warning: if you have 1,000 tools, your design is wrong in the first place.

:::beyond Real syntax is slightly different
The snippets above are simplified for teaching. In current LangChain, such a function is written with the `wrap_model_call` hook, which is how the interview PDF in the repo describes filtering the tool list. Chapters 8 and 9 show the real hooks.
:::

### 5. The VIP demo and its live bug

```python
def vip_gate_middleware(request):
    is_vip = request.state.get("is_vip_member", False)
    if not is_vip:
        request.tools = [t for t in request.tools if t.name != "vip_lounge_booking"]
    return request
```

With a regular user the agent genuinely had no idea a VIP tool existed. But passing `is_vip_member=True` into `invoke()` **did not work**: the middleware always read `False`.

:::trap Agent state has to be declared
The fix was a **custom state schema** that tells the agent to track `is_vip_member` alongside its built-in fields (like the message list). Without it, the field was silently dropped. Once declared, the same middleware read the flag correctly and exposed the VIP tool. The take-away: based on the user, **at runtime**, you can change which tools the agent has.
:::

### 6. Headless tools

Where does a tool run? Payment, clipboard, location: on the server or on the user's machine?

```mermaid
flowchart TD
    A["Agent"] --> B["Server-side tools<br/>web search, code interpreter:<br/>run on the AI provider's servers"]
    A --> C["Regular tools<br/>your functions: run wherever your agent runs"]
    A --> D["Headless tools<br/>clipboard, location, payment:<br/>run on the USER's device"]
```

A **headless tool** has its definition (name, description, argument schema) registered on the server with the agent, but its **implementation** registered only on the client, executed after a short interrupt-and-resume handshake. The idea is not AI-specific (geolocation, clipboard and IndexedDB are normal browser APIs). Amazon needs your location, so it runs in your browser and sends the result back, because its US server has no way to get it.

### 7. TripMate: real tools instead of mocks

Alongside CineBot (kept for concepts), class introduced **TripMate**, a travel-planning agent, with four real tools:

| Tool | What it uses | Note |
| --- | --- | --- |
| Weather | **Open-Meteo**, a free, keyless, open-source weather API | Read its docs |
| Web search | **Tavily** | A third-party service; LangChain just makes integration easier |
| Save trip | SQLite `trips` table | Stores by user id |
| Get saved trip | SQLite | Retrieves by user id |

SQLite is only for local mocking. Any store works: ChromaDB, Postgres, MongoDB. Because the data lives **outside** the process, a restart does not lose it.

### 8. The forgetting problem, and the fix

Tell the agent "my name is Mayank", then ask "who am I?" It does not know. An agent should remember, **but by default it does not**.

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

agent_with_memory = create_agent(
    model=model,
    tools=[...],
    checkpointer=checkpointer,
)

config = {"configurable": {"thread_id": "mayank-session-1"}}
agent_with_memory.invoke({"messages": [...]}, config=config)
```

This is the official approach from the documentation. The **`thread_id`** is simply a unique id so the checkpointer can locate the chat. The **application controls it**, not the user: "Session 1" for the first chat, a different id for a new session. It is not a reserved keyword; it is the key the checkpointer looks for in the config. Swap the id and the agent forgets again. `InMemorySaver` lasts as long as the Python process; a persistent backend such as Postgres follows the same pattern.

### 9. Memory saver, memory store, caching, database

There is no single right answer. Think of Swiggy or Amazon's chatbot: if you do not reply in 10 minutes the chat closes. Keeping that chat in memory forever would not help.

| Concept | What it is for | Typical lifetime |
| --- | --- | --- |
| **Memory saver** (checkpointer) | One conversation's history, tied to a `thread_id`, so the agent can resume | As long as that thread needs: minutes to persistent |
| **Memory store** | Facts **about a user** (preferences) usable across many conversations | Persistent by design |
| **Caching** | Avoid repeating expensive near-identical calls | Short and tunable: an hour, a day |
| **Database** | General persistent storage for the app | Persistent, application-defined |

"I like Python as a language" belongs in the **store**, not the saver, because it should be usable in other chats too. That is long-term memory. For caching: if "weather in Delhi" is asked a million times in an hour, cache it. API calls at scale are not cheap.

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Asking the user if they are a VIP | Everyone says yes | Decide from trusted state or context |
| Telling the model "do not offer VIP tools" | Model may still offer them | Remove the tool from the list with middleware |
| Passing a custom field to `invoke` without declaring it | Middleware always sees the default | Add a custom state schema |
| Loading hundreds of tools for everyone | Wasted tokens and cost | Dynamic loading |
| No checkpointer or no `thread_id` | Agent forgets between calls | Add `InMemorySaver` and reuse the id |
| Using `InMemorySaver` in production | Memory lost on restart | Use a persistent backend |
| Storing user preferences only in the saver | Lost in other chats | Use the store |
| Caching everything | Stale answers | Choose a TTL per data type |

## Hands-on lab

1. Rebuild the VIP middleware and trigger the "state not tracked" bug on purpose, then fix it with a custom state schema.
2. Write middleware that filters tools using `request.state`.
3. Build one real tool from a free public API, such as Open-Meteo.
4. Add `InMemorySaver` and a `thread_id`. Confirm it remembers your name, then change the id and confirm it forgets.
5. Walk through TripMate: real weather, real search, SQLite save and fetch.
6. For five facts (a chat history, a language preference, a repeated weather lookup, an order record, a feature flag) say which of the four stores each belongs in.

## Interview corner

:::pitch
An agent is a model plus a harness, running the agentic loop: model decides, tool executes, result goes back to the model. To control it, I use middleware, which hooks into the loop before and after the model and tools. For per-user tool access I filter the tool list at runtime so unauthorised tools are not even visible, and for memory I use a checkpointer with a thread id for conversations and a store for long-term facts.
:::

### Basics

:::qa Does a tool result go to the user?
No. It goes back to the model, which produces the final reply. The user sees only that. (`return_direct` is the deliberate exception.)
:::

:::qa What is the agentic loop?
Receive a message, the model decides whether a tool is needed, run it, append the result, and repeat until the model answers in plain text. It was called the ReAct pattern.
:::

:::qa How does an agent remember a conversation?
A checkpointer (for example `InMemorySaver`) passed to `create_agent`, plus a `thread_id` in the config. The same id restores the history; a new id starts fresh.
:::

:::qa Is `thread_id` a reserved keyword?
No. It is just the identifier the checkpointer looks for in the config. The application decides how ids are generated and assigned.
:::

### Intermediate

:::qa How would you give VIP users an extra tool?
Use middleware that reads trusted state or context and filters the tool list before the model call, so non-VIPs never see the tool. Do not ask the user, and do not rely on a system-prompt instruction.
:::

:::qa Why not use an `if/else` outside the agent to choose a tool list?
Code outside the agent cannot read the agent's live state or store (for example a growing message count). Only code running inside the agent, such as middleware, can.
:::

:::qa What is dynamic tool loading, and what are its two approaches?
Modifying the available tools at runtime instead of defining them all upfront. Either filter a pre-registered set based on state, permissions and flags, or register tools dynamically when they are not known ahead (for example from MCP).
:::

:::qa Memory saver vs memory store vs cache vs database?
Saver: one conversation's history by thread id. Store: facts about a user across conversations. Cache: short-lived results of repeated expensive calls. Database: general persistent application data. Choose by use case and lifetime.
:::

### Tricky

:::qa The middleware kept reading `is_vip_member` as False even when you passed True. Why?
The agent only tracks fields in its state schema. A custom field passed to `invoke` is dropped unless a **custom state schema** declares it. Declare it and the middleware sees it.
:::

:::qa What is a headless tool?
A tool whose definition lives on the server with the agent, but whose implementation runs on the **client** (clipboard, location, payment), executed through an interrupt-and-resume handshake. The agent decides to use it; the user's device does the work.
:::

:::qa Why is loading hundreds of tools bad even if the user cannot use them?
Their definitions are loaded into context and sent to the model on every call, costing tokens and possibly causing wrong tool choices. Load only what is relevant.
:::

:::qa Where would you store "I prefer Python"?
In the **store** (long-term memory), so every future conversation can use it. A checkpointer is tied to one thread and would not carry it across chats.
:::

:::qa Does a tool call cost money like a model call?
No. Only model calls consume tokens. A tool running on its own, with no model call, does not (though the tool's own API may have fees).
:::

## Quick revision

- [ ] I can restate the loop and say where the tool result goes
- [ ] I can explain the menu analogy and why asking the user or using the prompt fails
- [ ] I can define dynamic tool loading in one sentence and give two approaches
- [ ] I can draw the middleware hook points
- [ ] I can explain the VIP bug and the custom state fix
- [ ] I can define a headless tool and give three examples
- [ ] I can set up a checkpointer with a thread id
- [ ] I can sort memory saver, store, cache and database by purpose

## Sources and further reading

- [Class 11 full notes]({{src:classes_transcription_summary/11 - 01 Aug - LangChain - Agents, Memory, Middleware.md}})
- [Class 11 short summary]({{src:classes_summary/11 - 01 Aug - Agents, Middleware & Memory.md}})
- [Middleware notebook]({{src:Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/MIddleware.ipynb}})
- [Middleware architecture sketch notebook]({{src:Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/Middleware-Architecture-Sketch.ipynb}})
- [Assignment 2: agents and prebuilt middleware]({{src:Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/Assignment & Questions/Assignment_2_Agents_and_Prebuilt_Middleware.ipynb}})
- [Architecture diagram (PDF)]({{src:Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/Agent-Middleware-Architecture.pdf}})
- [Weekend 06 code folder]({{tree:Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware}})
