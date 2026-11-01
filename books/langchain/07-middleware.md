# Chapter 7: Middleware

**After this chapter you can:**

- Explain why not every tool belongs to every user, and how dynamic tool loading solves it
- Name the six middleware hooks and where each sits in the agent loop
- Filter tools by state or by context
- Compress long conversations with `SummarizationMiddleware`
- Guard irreversible tools with `HumanInTheLoopMiddleware` and resume a paused run
- Cap cost with model and tool call limits, survive outages with model fallback
- Keep personal data away from the model with `PIIMiddleware`, including custom detectors
- Explain the difference between a guardrail and middleware

**Builds on:** [Chapter 5](05-tools.md) (tools, gating) and [Chapter 6](06-agents-and-memory.md) (agents, checkpointer, context). The middlewares for to-do lists, tool selection, tool errors, tool retry and tool emulation are in [Chapter 8](08-guardrails-to-do-lists-and-tool-resilience.md). [Chapter 10](10-runtime-and-human-in-the-loop.md) goes deeper on runtime and human-in-the-loop.

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

More on the options:

- **`trigger`** can be an absolute token count, a message count, or a **fraction of the model's context length** (for example once the context is 80% full)
- **`keep`** can also be a fraction, a token count or a message count. Class example: keep the last 10 messages, summarise everything before
- You have already seen this in chat products: the "conversation has been compacted" behaviour is this mechanism. Claude Code's `/compact` command is a visible example, with a context-usage breakdown (system prompt, tools, custom instructions, messages)
- **The trade-off is real:** squeezing a long history into a short summary can lose information. That is part of why models seem to forget or hallucinate in very long chats
- **No way to guarantee zero loss.** If something must be kept, save it separately into long-term memory ([Chapter 6](06-agents-and-memory.md)), do not rely on the summary alone
- Summarization is a model call, so it adds some latency. It runs on its own separate text, not on the agent's main running context

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

Why it applies only to **tool calls**:

- Everything before a tool call is just the model reasoning. A tool call is the "hands" changing something in the real world
- That is the moment worth pausing on, not the model's internal reasoning
- Motivating case: if an agent decided on its own to spend a large sum, should it be allowed to do that without checking? The user is the human in the loop

**HITL is not a transfer.** A support bot escalating to a human agent hands off the **whole conversation** and steps out. That is a transfer. Human-in-the-loop keeps the agent in the loop, **paused for a decision**, for example proposing a refund and asking a representative to approve or adjust the amount.

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
- **No UI comes with it.** You resolve the interrupt in code with `Command(resume=...)`, or wire it to your own interface (a pop-up, an approve and reject button)
- **Two levels of sign-off** (for example manager then director) are not available out of the box. That needs custom middleware

## 7.7 `ModelCallLimitMiddleware`

**Why:** cost. An agent that makes 100 model calls in one run costs real money, and there was no built-in cap.

- Same idea as the `max_turns` safeguard from the raw Python loop ([LLM book, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md)), formalised with better checks
- **Where to set the number** comes from domain knowledge, not a framework default. A web-search agent rarely needs more than 5 to 15 searches
- **Why not tell the model "do not call more than twice"?** A model can ignore it, and it breaks when you swap the model. A limit in code is specific and dependable

**Run limit vs thread limit** (whiteboard analogy: breakfast, lunch, dinner):

- **Run limit:** a cap on **one `.invoke()`**. "Chappatis allowed per meal"
- **Thread limit:** a cap **across all runs** of one conversation. "Chappatis allowed in total, across all meals"

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

call_limited_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    checkpointer=InMemorySaver(),        # needed for thread_limit to persist across calls
    middleware=[
        ModelCallLimitMiddleware(        # low values, just for the example
            thread_limit=5,              # across the WHOLE conversation
            run_limit=2,                 # per single .invoke() call
            exit_behavior="end",         # graceful stop, not an exception
        ),
    ],
)
```

- **`exit_behavior="end"`:** the run stops and the last message is an `AIMessage` such as `Model call limits exceeded: run limit (2/2)` or `... thread limit (5/5)`. The class notebook showed the thread version
- **`exit_behavior="error"`:** raises `ModelCallLimitExceededError` instead
- The run limit **resets on every `invoke`**. The thread limit does not
- **Without a checkpointer** the thread limit has nothing to remember between calls. In my test a thread limit of 1 never fired across two separate `invoke`s

## 7.8 `ToolCallLimitMiddleware`

**Why:** tool calls add to context size and cost. An agent asked to "find the important emails" could keep digging through years of mail unless capped.

- Works **globally** or for **one named tool**. Use two instances together:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

tool_limited_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    checkpointer=InMemorySaver(),
    middleware=[
        ToolCallLimitMiddleware(run_limit=8),                                              # global, this run
        ToolCallLimitMiddleware(tool_name="cancel_booking", thread_limit=2, run_limit=1),  # one tool, tighter
    ],
)
```

- Whiteboard numbers: **8** for the global run limit. For `cancel_booking`, **`run_limit=1`** and **`thread_limit=2`** (the conversation limit)
- The board traces bookings B100, B101, B102: the first two cancels go through (one per run, two in the whole thread). The third is blocked, because the thread limit is used up. A new run refreshes only the **run** counter
- Class demo: three separate `invoke`s asking to cancel B100, B101, B102. The third tool call was refused with the tool message `Tool call limit exceeded. Do not call 'cancel_booking' again.`
- **Default behaviour (`exit_behavior="continue"`):** the blocked call becomes an **error tool message**, and the model carries on and can explain. Other options: `"end"` and `"error"`
- A strict limit on one irreversible tool plus a looser overall limit is a common pairing (assignment question A2 Q10)

## 7.9 `ModelFallbackMiddleware`

**Why:** if the primary model provider has an outage, the app should not simply stop working.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

resilient_agent = create_agent(
    model="openai:gpt-5",                  # primary
    tools=cinebot_tools,
    middleware=[
        ModelFallbackMiddleware(
            "openai:gpt-5-mini",           # first fallback
            # "ollama:llama3.2",           # a further, fully local last resort
        ),
    ],
)
```

- Models are passed **positionally**, first fallback first, then more in order
- **What counts as a failure:** a hard error such as a 404 or an expired key
- **What it is not:** routing by speed or cost, or a smart dispatcher choosing the best model for a task. It only activates when the primary model genuinely fails
- The **full conversation history** goes to whichever model ends up answering. Nothing else changes
- Class demo: the primary name was one that does not exist, so without the middleware the call failed with a 404 `model_not_found` error. With the middleware it fell through to `gpt-5-mini`
- The whiteboard draws the symptom it prevents: **"AI -> I am unable to connect."**

> **Correction.** The class transcript wrote `ModelFallbackMiddleware(model="...")`. That raises `TypeError: unexpected keyword argument 'model'`. The notebook's positional form is the one that works

## 7.10 `PIIMiddleware`

**PII** (personally identifiable information): date of birth, phone number, email, government ID numbers, passwords. It generally should **not reach the model** at all.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

pii_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)
```

Strategies (checked on `langchain` 1.4.7):

- **`redact`:** removes the value. `priya@example.com` becomes `[REDACTED_EMAIL]`
- **`mask`:** keeps a hint so the model can tell something was there. `priya@example.com` becomes `priya@****.com`
- **`hash`:** replaces it with a hash, for example `<email_hash:6bdb7e96>`
- **`block`:** stops the run with a `PIIDetectionError`

Built-in types in this version: `email`, `credit_card`, `ip`, `mac_address`, `url`. Anything else is a **custom** type.

> **What really happened with the class card number.** The class text says the card `4111-1111-1111-1234` was masked. The notebook output shows it was **not**: only the email was redacted, and the model even warned the user about the card. The built-in card detector checks that the number is **valid** (a checksum, the Luhn check), and this made-up number fails it. A valid test number such as `4111-1111-1111-1111` is masked to `****-****-****-1111`. Class 13 covers the detail. For now: **test with valid-looking numbers, and remember a detector can skip lookalikes**

**Custom PII types.** Aadhaar and PAN (India-specific IDs) are named on the whiteboard as formats no framework can ship for every country. Supply your own detector, either as a **function** or as a **regex string**:

```python
import re
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

def detect_booking_code(content: str) -> list[dict]:
    """Detect CineBot's own booking code format: BK followed by 4 digits."""
    return [
        {"text": m.group(0), "start": m.start(), "end": m.end()}
        for m in re.finditer(r"BK\d{4}", content)
    ]

custom_pii_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    middleware=[
        PIIMiddleware("booking_code", detector=detect_booking_code, strategy="mask"),
        PIIMiddleware("aadhaar", detector=r"\b\d{12}\b", strategy="mask"),     # regex as a STRING
    ],
)
# "my booking BK1044"    -> "my booking ****1044"
# "aadhaar 123456789012" -> "aadhaar ****9012"
```

> **Correction.** The class transcript passed a compiled pattern, `detector=re.compile(r"\b\d{12}\b")`. That raises `TypeError: 're.Pattern' object is not callable`. Pass the pattern as a **string**, or write a function that returns a list of matches

The function detector returns a list of dicts with `text`, `start` and `end`.

Three more switches (from the library signature, not explained in class 12):

- `apply_to_input` (default `True`): clean user messages before the model
- `apply_to_output` (default `False`): clean what the model replies
- `apply_to_tool_results` (default `False`): clean what tools return

## 7.11 Guardrail vs middleware

> **A guardrail is the concept: protecting the agent from doing something undesirable. Middleware is the mechanism you use to implement it.**

- The whiteboard: "Guardrails is a way to control the AI agent behaviour." PII detection is one concrete guardrail, implemented with `PIIMiddleware`
- They are **not two competing systems**. Guardrails are applied **as** middleware
- Examples the board gives: the user talks rudely or gives personal info, and the agent flags it
- This came up repeatedly in class and is a **common interview question**

Where these patterns show up in real work (from the notebook):

- **Fintech fraud detection:** a `wrap_tool_call` hook around every transaction tool, flagging or blocking by velocity, amount or pattern
- **Healthcare assistants:** PII redaction is often a legal requirement (HIPAA in the US), not optional polish
- **Customer support:** approval gates before refunds or account changes (human in the loop)
- **Internal tools:** audit logging via `wrap_tool_call`, anywhere "who did what, when" needs an answer

## 7.12 Several middlewares, and LangChain vs LangGraph

**Several middlewares on one agent**

- Pass them as a **list**. No need for a separate agent per concern
- Order is **not random**. Either a defined priority applies, or they run in **declaration order**. They are designed not to collide
- My test: two `before_model` hooks ran in the order they were listed
- **Latency:** a middleware that calls a model (summarization) adds some. Pure code (a call-limit check) adds almost none

**When to stay in LangChain and when to drop to LangGraph**

- Middleware exists in LangGraph too. It is not unique to LangChain
- LangChain sits on top of LangGraph and gives a more convenient, somewhat abstracted interface to the same machinery
- **Stay in LangChain + middleware** for most agents, including a simple RAG chatbot (which may not even need middleware)
- **Go to LangGraph** when you need precise, deterministic control of state, checkpointer internals, stores or interrupts
- Other tools use other names for the same idea: Google's Agent Development Kit says "callbacks", Claude Code and Cursor say "hooks"
- Agents built only from MCP connections and instructions (no framework) are usually local developer tools, not deployable services

**Observability:** there is no universal best choice. LangFuse integrates easily with the LangChain family. For RAG, test dedicated evaluation tools. Early results are often deceptively easy, so real quality needs more testing than the basics.

## 7.13 Questions from the class

- **What if a tool fails or times out?** Recoverable failures are typically retried by the harness. A fatal error (for example no internet) makes the agent fail outright. Retry and error middleware come in [Chapter 8](08-guardrails-to-do-lists-and-tool-resilience.md)
- **Can an agent discover brand-new tools at run time?** Yes. This is where MCP and middleware meet
- **Why not a plain `if/else` for the tool list?** It cannot read the agent's live state or store (7.2)
- **Why not just prompt "do not call the tool more than twice"?** A prompt is not reliable. A limit in code is (7.7)
- **Does middleware add latency?** Only if it calls a model, or does heavy work (7.12)
- **Two levels of human approval?** Needs custom middleware (7.6)
- **Does summarization share the agent's main context?** No. It works on its own separate text
- **Is PII a guardrail or middleware?** The guardrail is the goal, middleware is how you implement it (7.11)
- **Can I attach several middlewares?** Yes, as a list (7.12)
- **LangChain + middleware or LangGraph?** See 7.12
- **Does a support bot handing a chat to a human count as HITL?** No, that is a transfer (7.6)

## 7.14 Interview corner

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

**6. Is a support bot passing a chat to a human "human in the loop"?**

- No. That is a **transfer**: the agent leaves. In HITL the agent stays, paused for a decision

**7. What does `SummarizationMiddleware` do, and what is lost?**

- Replaces old messages with a generated summary when a trigger is hit
- *Stronger answer:* detail is lost, media is not compressed, the summary call costs tokens, and must-keep facts belong in long-term memory

**8. Run limit vs thread limit?**

- Run limit: one `invoke`. Thread limit: the whole conversation, which needs a checkpointer
- *Stronger answer:* you can limit one tool tightly and the whole run loosely. Set the numbers from domain knowledge

**9. What does model fallback do, and what does it not do?**

- It switches to another model when the primary hard-fails (404, bad key, outage)
- It does **not** route by cost, speed or task. The full history goes to the fallback

**10. Redact vs mask vs hash vs block for PII?**

- Redact removes it, mask hides part, hash replaces it with a hash, block stops the run
- *Stronger answer:* masking an id your tool needs breaks the tool call. Pick the strategy per field

**11. Guardrail vs middleware?**

- A guardrail is the goal of keeping the agent from undesirable behaviour. Middleware is the mechanism that implements it
- *Stronger answer:* give an example, such as PII protection implemented with `PIIMiddleware`

## 7.15 Added by Claude, not from the sources

Not in the course material. Established practice, but check current docs.

**Human in the loop**

- **Show the reviewer the exact arguments**, not a paraphrase. The `action_requests` in the interrupt hold them. Log who approved what and when
- **Paused runs wait forever.** Decide how long an approval may stay open and what happens when it expires. Only let the **same authorised user** resume a thread

**Summarization and cost**

- **Summaries drop exact facts** (ids, amounts, dates). Keep must-not-lose facts in the system prompt, the state or the store
- **The summarising model sees the whole history**, so it also sees any personal data in it
- **Fewer tools per call means fewer input tokens per call.** Filtering tools is a cost control as well as a safety control
- **Gate twice.** Hide the tool with middleware, and check permission again inside the tool ([Chapter 5](05-tools.md), 5.12)

**Limits and fallback**

- **Limits stop runaway cost, not bad behaviour.** Keep the run limit comfortably above what a normal task needs, and add a time limit too
- **A thread limit needs a persistent checkpointer** to survive restarts
- **Log when a fallback fires.** It can hide an outage, and the fallback model may follow your prompt and tools differently. Re-test your prompts on it, and do not fall back to a weaker model silently for safety-critical work

**PII**

- **Masking an identifier your tools need breaks the tool call.** After `BK1044` becomes `****1044`, the model cannot pass the real code to a tool. Mask what the **model** must not see, and fetch the real value in code
- **Regex detectors guess.** A 12-digit pattern matches any 12-digit number, and misses numbers written with spaces. A PAN pattern is more specific (five letters, four digits, one letter):

```python
PIIMiddleware("pan", detector=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", strategy="mask")
```

- **PII middleware is one layer.** Logs, traces and your own database may still hold the raw text. Check what each of them records

## Recap

- Not every tool belongs to every user. **Change the tool list at run time**, do not ask the model to behave
- **Dynamic tool loading:** filter pre-registered tools, or register tools dynamically (MCP)
- Six hooks: `before_agent`, `before_model`, `wrap_model_call`, `after_model`, `wrap_tool_call`, `after_agent`
- Filter with `request.override(tools=...)`. Per-user flags need a **state schema** or **context**
- `SummarizationMiddleware`: `model`, `trigger=("tokens", n)`, `keep=("messages", n)`. Text only, and lossy
- `HumanInTheLoopMiddleware`: needs a **checkpointer**. Resume with `Command(resume={"decisions": [...]})`. Four decisions: approve, edit, reject, respond. It is **not** a transfer
- **Model call limit:** `run_limit` (one invoke) and `thread_limit` (whole conversation, needs a checkpointer). **Tool call limit:** global or per tool
- **Model fallback:** models passed positionally, only on hard failure, full history passed on
- **PII:** redact, mask, hash or block. Custom detector = function or regex **string**. The card checksum can skip fake numbers
- **Guardrail = goal, middleware = mechanism**
- Several middlewares go in one list and run in declaration order

## Practice

1. Recreate the VIP middleware. **Deliberately trigger the "state field not tracked" bug**, then fix it with a custom state schema
2. Write middleware from scratch that filters tools by `request.state`
3. Recreate `SummarizationMiddleware` with your own `trigger` and `keep`, and watch a long conversation compress
4. Build the `cancel_booking` HITL demo, run `run_interactive_hitl_demo()` yourself and try **all four** decisions
5. Open the whiteboard `Agent-Middleware-Architecture.excalidraw` in excalidraw.com and trace the full loop diagram by hand
6. Set both a `run_limit` and a `thread_limit` on one agent and trigger each one independently
7. Add a model call limit and a tool call limit to an existing agent and deliberately trigger both
8. Configure `ModelFallbackMiddleware` and force the primary model to fail (an intentionally wrong model name or key) to confirm the fallback fires
9. Write your own custom `PIIMiddleware` detector (with `re`) for an ID format from your own country or use case
10. Explain the difference between a guardrail and middleware in your own words, out loud
11. Assignment 2 (NovaBank), the parts this chapter prepares you for. The assignment has no answer key:
    - A2 Q7: a realistic NovaBank `transfer_funds` situation for each of the four HITL decisions
    - A2 Q10: a strict `ToolCallLimitMiddleware` on one tool with a looser `ModelCallLimitMiddleware` overall
    - B2.1: guard `transfer_funds` with all four decisions, resume with an `edit` that changes the amount, and confirm the edited amount was used (remember the `edited_action` shape)
    - B2.2: a custom detector for `NB-` plus 8 digits, attached with `strategy="mask"`
    - B3.1 (partly): `SummarizationMiddleware`, `ToolCallLimitMiddleware` and `ModelCallLimitMiddleware` together on one agent
    - (Q6, Q9, Q11 to Q15, B2.3, B3.2, B3.3 and the capstone need the middlewares in Chapter 8)

## How this chapter was checked

- Run offline with a stand-in model on `langchain` 1.4.7:
  - tool filtering with state schema and with context, and the deprecated `request.tools` assignment
  - summarization: the summary message and its `lc_source`, the invalid `"token"` and the valid `"tokens"`
  - HITL: interrupt, `get_state`, approve, edit (both shapes), reject, respond, a disallowed decision, resume without a checkpointer
  - model call limit: run limit, thread limit, `"end"` and `"error"`, and no thread limit without a checkpointer
  - tool call limit: global plus per tool, the blocked third cancel
  - model fallback: a failing primary, the fallback seeing the same message, and the keyword `model=` `TypeError`
  - PII: redact, mask, hash and block, the card checksum, the function detector, the regex string, the compiled-regex `TypeError`, and declaration order of two hooks
- **Not run against a live model:** the quality of a real summary, real tool-call choices, a real provider outage. Class output was read from the notebook (cells 57 to 101)
- The middlewares for to-do lists, tool selection, tool errors, tool retry and tool emulation are **not** in this chapter. They belong to [Chapter 8](08-guardrails-to-do-lists-and-tool-resilience.md)

## Sources and further reading

- Live-Class-2026, `classes_summary/11 - 01 Aug - Agents, Middleware & Memory.md` and `classes_summary/12 - 08 Aug - Mastering Middleware.md`
- Live-Class-2026, `classes_transcription_summary/11 - 01 Aug - LangChain - Agents, Memory, Middleware.md` and `classes_transcription_summary/12 - 08 Aug - LangChain - Mastering Middleware.md`
- Live-Class-2026, `MIddleware.ipynb` (cells 0 to 101), `Middleware-Architecture-Sketch.ipynb`, the whiteboards `Agent-Middleware-Architecture.pdf` and `Langchain-2-Updated.pdf`, and the folder README, all in `Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/`
- Live-Class-2026, `Weekend 07 - 8-9 Aug/README.md` (the other files in that folder are copies of Weekend 06 files)
- Live-Class-2026, `Assignment_2_Agents_and_Prebuilt_Middleware.ipynb` (questions only; the answers belong to later classes)
- Section 7.15 and the corrections in 7.4 to 7.10 are from testing, not from the class sources

Previous: [Chapter 6, Agents and memory](06-agents-and-memory.md) · Next: [Chapter 8, Guardrails, to-do lists and tool resilience](08-guardrails-to-do-lists-and-tool-resilience.md) (not written yet)
