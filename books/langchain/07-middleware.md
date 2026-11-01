# Chapter 7: Middleware

**After this chapter you can:**

- Explain why not every tool belongs to every user, and how dynamic tool loading solves it
- Name the six middleware hooks and where each sits in the agent loop
- Filter tools by state or by context
- Compress long conversations with `SummarizationMiddleware`
- Guard irreversible tools with `HumanInTheLoopMiddleware` and resume a paused run

**Builds on:** [Chapter 5](05-tools.md) (tools, gating) and [Chapter 6](06-agents-and-memory.md) (agents, checkpointer, context). The other built-in middlewares (limits, fallback, PII, retry, todo list, tool selector) come next, from class 12 onward. [Chapter 10](10-runtime-and-human-in-the-loop.md) goes deeper on runtime and human-in-the-loop.

## 7.1 The problem: not every tool belongs to every user

- CineBot has a standard booking tool, a VIP lounge tool and an admin tool
- A regular, non-paying user asks for a VIP seat. What should happen?
- **Tempting fix 1: ask the user "are you a VIP?"** Useless. Everyone says yes
- **Tempting fix 2: remove the VIP tool.** Then a real VIP can no longer use it
- **The right fix:** change **which tools the agent can see**, per user, at run time
- **Menu analogy:** the menu reprints itself before you sit down. A VIP sees the full menu, a regular guest a shorter one. Not because they were told "please do not order that", but because the item is **not printed**
- **Real-world proof:** each connector in a chat product is just a collection of tools (a Gmail connector has write and delete tools, a Slack one has about 11)
  - A free-tier user will never be allowed to use them. Loading all of them anyway means sending unwanted tool tokens to the model **on every call**
  - Companies lose money on that every day

## 7.2 Dynamic tool loading

> With dynamic tool loading, the set of tools available to the agent is modified **at run time**, not defined all up front.

- All possible tools are defined once. A runtime check (state, permissions, feature flags) decides which ones the model sees
- **Two approaches**
  - **Filter pre-registered tools:** you know every tool at creation time. Register all, then filter what is exposed by state, permissions and context
  - **Register tools dynamically:** the full set is not known up front, for example tools arriving through MCP
- **Why not a plain Python `if/else` that picks one of two tool lists?**
  - Code outside the agent **cannot read the agent's live state or store**. For example, it cannot see the message count change mid-run
  - That visibility exists only **inside** the agent run, which is exactly what middleware gives you
- **Design warning:** if you have 1,000 tools "in public" and load all of them for an authenticated user, the design is wrong. Do not build 1,000 tools in the first place
- Not the same as dynamic tool **calling** (the model picking among the tools it sees). See [Chapter 5](05-tools.md), 5.10

## 7.3 Middleware: cutting into the loop

> Middleware provides a way to more tightly control what happens inside the agent.

- The loop is: request, model call, tool call, result. Middleware lets you **cut into the middle**: before the model, after the model, around a tool call
- It is a universal idea across frameworks, not a LangChain quirk
- The six hooks, in order, as drawn on the whiteboard:

```
Request
  → before_agent
  → before_model
  → wrap_model_call → [ Model Call ]
  → after_model
  → wrap_tool_call → [ Tool Executes ]
  → after_agent
  → Response
```

What middleware is used for (four groups):

- **Track behaviour:** logging, analytics, debugging
- **Transform:** prompts, tool selection, output formatting
- **Add resilience:** retries, fallbacks, early termination
- **Protect:** rate limits, guardrails, PII detection

Where the whiteboard places the main ideas:

- **Human in the loop**
- **Guardrails**
- **Summarization**
- **Dynamic tool loading**

Two kinds of middleware:

- **Prebuilt:** ready-made classes (summarization, HITL, PII, retries, limits...). Covered one by one from here on
- **Custom:** you write the hook yourself (class 12 onward)

## 7.4 Filtering tools in code

**By state.** Hide tools until the user is authenticated:

```python
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import wrap_model_call

class AuthState(AgentState):
    authenticated: bool                 # the agent must be told to track this field

@wrap_model_call
def only_public_tools_if_unauthenticated(request, handler):
    if not request.state.get("authenticated"):
        request = request.override(
            tools=[t for t in request.tools if t.name.startswith("public_")]
        )
    return handler(request)

agent = create_agent(
    model="openai:gpt-5-mini",
    tools=[public_search, account_details],
    middleware=[only_public_tools_if_unauthenticated],
    state_schema=AuthState,
)
agent.invoke({"messages": [("user", "Show my account")], "authenticated": False})
```

- Reads from `request.state`. If not authenticated, give only tools whose name starts with `public_`
- **Corrections to the class code:**
  - The class wrote `request.tools = [...]` and returned `request`. In current LangChain, assigning to `request.tools` still works but is **deprecated**. Use `request.override(tools=...)` and `return handler(request)`
  - The class snippets were simplified (a bare function). The real hook is decorated with `@wrap_model_call` and takes `(request, handler)`

**By context or store.** Use `request.runtime.context` (a user id, feature flags, a plan) instead of state. The VIP example is in [Chapter 5](05-tools.md), 5.10.

**The live bug in class.** The VIP middleware read `is_vip_member` from state, but passing `is_vip_member=True` into `invoke()` was ignored. It always read `False`.

- Why: the agent only tracks fields **it was told about**
- Fix: a **custom state schema** that adds `is_vip_member` next to the built-in fields (such as the message list), passed as `state_schema=`
- Once added, the same middleware read the flag and exposed the VIP tool. This is why "agents allow you to create a state"
- Remember the claim to prove: **at run time**, not at start-up, you can change which tools the agent has

## 7.5 `SummarizationMiddleware`

Long conversations keep growing the context. Summarization condenses the old part.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="openai:gpt-5-mini",
    tools=[save_trip_demo],
    middleware=[
        SummarizationMiddleware(
            model="gpt-5.4-mini",          # a separate, often cheaper model just for condensing
            trigger=("tokens", 4000),      # when to summarise
            keep=("messages", 10),         # how much recent history stays word for word
        )
    ],
)
```

- **`model`:** a separate (often cheaper) model that writes the summary
- **`trigger`:** when to start. Accepts `("tokens", n)`, `("messages", n)` or `("fraction", f)`
- **`keep`:** how many recent messages (or tokens) stay untouched
- **Whiteboard numbers:** a trigger at 4k tokens squeezes a large conversation, for example **100k down to about 10k**
- **Class demo:** `trigger=("tokens", 300)`, `keep=("messages", 1)`. After a multi-part request, the old messages were replaced by one message that began "Here is a summary of the conversation to date:"

What the summary looks like:

- It is a message in the history, marked in `additional_kwargs["lc_source"]` as `"summarization"`
- The default summary prompt asks for four sections:
  - **SESSION INTENT**
  - **SUMMARY**
  - **ARTIFACTS**
  - **NEXT STEPS**
- Recent messages kept by `keep` stay as they were. Older ones live only in the summary

**Text only.** Summarization compresses text. It does not shrink images, audio or video:

- Recent messages that `keep` retains still carry their original media
- Older media messages that get summarised survive only as text
- For image-heavy apps, store media in a file system or object store and pass **URLs or file references** through the history

> **Pitfall in the class notebook.** An early cell used `trigger=("token", 4000)`. That raises `ValueError: Unsupported context size type token`. The word is **`"tokens"`** (plural)

## 7.6 `HumanInTheLoopMiddleware`

When an agent can do something **irreversible**, a human should sign off first.

- CineBot's `book_seats` and `cancel_booking` carry the word "Irreversible" in their docstrings. That property is what makes them worth gating
- Whiteboard analogy: **Request → Brain → Tool**, with a human standing at the last arrow, captioned "Intern". An intern with a great brain still needs sign-off before doing something irreversible

The flow:

```
User: "Send an email asking for leave"
  → LLM decides to call your_send_email_tool
  → requires approval → INTERRUPT
        approve → send the email
        edit    → change the arguments, then send
        reject  → do not send
```

**Set it up**

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

guarded_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "cancel_booking": {"allowed_decisions": ["approve", "edit", "reject", "respond"]},
                "check_showtimes": False,            # never interrupt this one
            }
        ),
    ],
    checkpointer=InMemorySaver(),    # REQUIRED: the run must pause and resume later
)
config = {"configurable": {"thread_id": "hitl-demo-live"}}
```

- **A checkpointer is required.** Without one you can still start the run, but `Command(resume=...)` raises `RuntimeError: Cannot use Command(resume=...) without checkpointer`
- `interrupt_on` maps a **tool name** to its allowed decisions. `False` means "never interrupt"

**Trigger the pause and look at it**

```python
result = guarded_agent.invoke({"messages": [("user", "Please cancel booking BK1042")]}, config=config)

request = result["__interrupt__"][0].value
print(request["action_requests"])      # tool name and arguments the model wants to run
print(request["review_configs"])       # which decisions are allowed

state = guarded_agent.get_state(config)
print(state.next)                      # ('HumanInTheLoopMiddleware.after_model',)
print(state.tasks[0])                  # the paused task
```

- The result holds an `__interrupt__` entry listing the proposed action and the allowed decisions
- `state.next` shows where the run is paused: here, the `after_model` hook of the middleware

**Resume with a decision**

```python
from langgraph.types import Command

resumed = guarded_agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config,
)
```

- `decisions` has **one entry per interrupted tool call** (usually one)
- Each decision is a dict with a `"type"` and, for some types, extra data

| Decision | Shape | What happens |
|---|---|---|
| approve | `{"type": "approve"}` | Runs as proposed |
| edit | `{"type": "edit", "edited_action": {"name": "cancel_booking", "args": {"booking_id": "BK9999"}}}` | Runs with your changed arguments. The model is told a reviewer replaced its call |
| reject | `{"type": "reject", "message": "Reason"}` | Blocked. The reason goes back to the model as an **error** tool message |
| respond | `{"type": "respond", "message": "Which booking?"}` | Nothing runs. Your text becomes the tool result |

**Corrections to the class code (checked on `langchain` 1.4.7)**

- **Edit shape:** the class used `{"type": "edit", "args": {...}}`. That raises `KeyError: 'edited_action'`. The arguments go inside `edited_action`, together with the tool `name`. (In class the demo choice was reject, so the edit path never ran)
- **Disallowed decision:** sending a type that is not in `allowed_decisions` raises `ValueError`
- **A typo in notebook cell 39:** `print(guarded_agent.invoke(...), config=config)` passes `config` to `print`, not `invoke`. It raises `TypeError`

**An interactive demo** (class idea, with the edit fixed):

```python
def run_interactive_hitl_demo(agent, config):
    state = agent.get_state(config)
    if not state.next:
        print("Nothing is currently paused for approval.")
        return

    print("1) approve  2) edit  3) reject  4) respond")
    choice = input("Type 1, 2, 3, or 4: ").strip()

    if choice == "1":
        decision = {"type": "approve"}
    elif choice == "2":
        new_id = input("New booking_id to use instead: ").strip()
        decision = {"type": "edit",
                    "edited_action": {"name": "cancel_booking", "args": {"booking_id": new_id}}}
    elif choice == "3":
        decision = {"type": "reject", "message": input("Reason for rejecting: ").strip()}
    elif choice == "4":
        decision = {"type": "respond", "message": input("Your response to the agent: ").strip()}
    else:
        print("Not a valid choice.")
        return

    resumed = agent.invoke(Command(resume={"decisions": [decision]}), config=config)
    print("Agent's final response:", resumed["messages"][-1].content)
```

- In class, rejecting with "Don't want to cancel" made the agent report that the cancel was not accepted and offer next options (check status, show policy, retry, contact support)

## 7.7 Questions from the class

- **What if a tool fails or times out?**
  - Recoverable failures are typically retried by the harness
  - A fatal error (for example no internet) makes the agent fail outright
  - That is why defining a harness matters. Retries and error handling come in later middleware
- **Can an agent discover brand-new tools at run time, not just from a fixed list?** Yes. This is where MCP and middleware meet. Tools arriving dynamically can still be registered and made available mid-run
- **Why can't a plain `if/else` decide the tool list?** It cannot read the agent's live state or store (7.2)

## 7.8 Interview corner

**1. What is middleware in an agent?**

- Hooks that let you run code before or after the model call, and around tool calls
- *Stronger answer:* name the six hooks and give one use for each group (logging, transforming, resilience, protection)

**2. Why filter tools instead of telling the model "do not use the VIP tool"?**

- A prompt only asks. A tool that is not on the list **cannot** be called
- *Stronger answer:* it also saves tokens, because tool schemas are sent on every model call

**3. Why not choose tools with a normal `if/else`?**

- Code outside the agent cannot read the agent's live state or store

**4. Your middleware reads `is_vip_member` from state but always sees `False`. Why?**

- The agent only tracks fields it knows about. Add a custom `state_schema`
- *Stronger answer:* or pass the flag as run `context`, which is the cleaner place for per-user data

**5. How do you make an irreversible tool safe?**

- Human in the loop: interrupt, then approve, edit, reject or respond
- *Stronger answer:* it needs a checkpointer, because the run must pause and resume

**6. What does `SummarizationMiddleware` do, and what is lost?**

- Replaces old messages with a generated summary when a trigger is hit
- *Stronger answer:* detail is lost, media is not compressed, and the summary call costs tokens

## 7.9 Added by Claude, not from the sources

Not in the course material. Established practice, but check current docs.

- **Show the reviewer the exact arguments**, not a paraphrase. The `action_requests` in the interrupt hold them. Log who approved what and when
- **Paused runs wait forever.** Decide how long an approval may stay open and what happens when it expires. Only let the **same authorised user** resume a thread
- **Summaries drop exact facts** (ids, amounts, dates). Keep must-not-lose facts in the system prompt, the state or the store, not only in chat history
- **The summarising model sees the whole history**, so it also sees any personal data in it. Treat it like any other model call
- **Fewer tools per call means fewer input tokens per call.** Filtering tools is a cost control as well as a safety control
- **Gate twice.** Hide the tool with middleware, and check permission again inside the tool ([Chapter 5](05-tools.md), 5.12)

## Recap

- Not every tool belongs to every user. **Change the tool list at run time**, do not ask the model to behave
- **Dynamic tool loading:** filter pre-registered tools, or register tools dynamically (MCP)
- Six hooks: `before_agent`, `before_model`, `wrap_model_call`, `after_model`, `wrap_tool_call`, `after_agent`
- Filter with `request.override(tools=...)`. Per-user flags need a **state schema** or **context**
- `SummarizationMiddleware`: `model`, `trigger=("tokens", n)`, `keep=("messages", n)`. Text only
- `HumanInTheLoopMiddleware`: needs a **checkpointer**. Resume with `Command(resume={"decisions": [...]})`. Four decisions: approve, edit, reject, respond

## Practice

1. Recreate the VIP middleware. **Deliberately trigger the "state field not tracked" bug**, then fix it with a custom state schema
2. Write middleware from scratch that filters tools by `request.state`
3. Recreate `SummarizationMiddleware` with your own `trigger` and `keep`, and watch a long conversation compress
4. Build the `cancel_booking` HITL demo, run `run_interactive_hitl_demo()` yourself and try **all four** decisions
5. Open the whiteboard `Agent-Middleware-Architecture.excalidraw` in excalidraw.com and trace the full loop diagram by hand
6. Assignment 2 (NovaBank), the parts this chapter prepares you for. The assignment has no answer key:
   - A2 Q7: a realistic NovaBank `transfer_funds` situation for each of the four HITL decisions
   - B2.1: guard `transfer_funds` with all four decisions, resume with an `edit` that changes the amount, and confirm the edited amount was used (remember the `edited_action` shape)
   - (Q6, Q8 to Q15 and B2.2 to B3.3 need the middlewares from class 12 onward)

## How this chapter was checked

- Run offline with a stand-in model on `langchain` 1.4.7: tool filtering with state schema and with context, the deprecated `request.tools` assignment (works, with a deprecation warning), summarization (the summary message and its `lc_source`, the invalid `"token"` and valid `"tokens"`), HITL interrupt, `get_state`, approve, edit (both shapes), reject, respond, a disallowed decision, and resume without a checkpointer
- **Not run against a live model:** the quality of a real summary, and real model tool-call choices. Class output was read from the notebook
- Class 12 material (the nine built-in middlewares, limits, PII, retries) is **not** in this chapter yet

## Sources and further reading

- Live-Class-2026, `classes_summary/11 - 01 Aug - Agents, Middleware & Memory.md`
- Live-Class-2026, `classes_transcription_summary/11 - 01 Aug - LangChain - Agents, Memory, Middleware.md`
- Live-Class-2026, `MIddleware.ipynb` (cells 0 to 56), `Middleware-Architecture-Sketch.ipynb`, the whiteboards `Agent-Middleware-Architecture.pdf` and `Langchain-2-Updated.pdf`, and the folder README, all in `Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/`
- Live-Class-2026, `Assignment_2_Agents_and_Prebuilt_Middleware.ipynb` (questions only; the answers belong to later classes)
- Section 7.9 and the corrections in 7.4 to 7.6 are from testing, not from the class sources

Previous: [Chapter 6, Agents and memory](06-agents-and-memory.md) · Next: [Chapter 8, Guardrails, to-do lists and tool resilience](08-guardrails-to-do-lists-and-tool-resilience.md) (not written yet)
