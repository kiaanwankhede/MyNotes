# Chapter 9: Guardrails, to-do lists and tool resilience

**After this chapter you can:**

- Place each built-in middleware on a guardrail map
- Give an agent a maintained plan with `TodoListMiddleware`
- Send only the relevant tools to the main model with `LLMToolSelectorMiddleware`
- Turn a tool failure into a readable message with `ToolErrorMiddleware`
- Retry flaky tools with backoff using `ToolRetryMiddleware`, and combine it with error handling in the right order
- Test an agent without real side effects using `LLMToolEmulator`

**Builds on:** [Chapter 7](07-middleware.md) (hooks, tool filtering), [Chapter 8](08-prebuilt-middleware-limits-fallback-and-pii.md) (limits, fallback, PII, guardrail vs middleware). Custom middleware is in [Chapter 10](10-shell-tools-and-custom-middleware.md).

## 9.1 A guardrail map

*A summary of Chapters 7 to 9, not from one source.* A guardrail is the goal. Each middleware guards something different:

- **What goes into the model:** `PIIMiddleware` (redact, mask, hash, block)
- **What it costs:** `ModelCallLimitMiddleware`, `ToolCallLimitMiddleware`, `SummarizationMiddleware`
- **What it can do:** tool filtering ([Chapter 7](07-middleware.md), 7.4), `HumanInTheLoopMiddleware` for irreversible tools, `LLMToolSelectorMiddleware`
- **What happens when it breaks:** `ModelFallbackMiddleware`, `ToolErrorMiddleware`, `ToolRetryMiddleware`
- **How it plans:** `TodoListMiddleware`
- **How you test it safely:** `LLMToolEmulator`

The class opened with real industry mapping: fraud-detection hooks in fintech, PII redaction as a legal requirement in healthcare, refund approval gates in customer support, audit logging in internal tools.

## 9.2 `TodoListMiddleware`

For a complex, multi-step task, an agent does better when it **plans first and tracks progress** against the plan. This is the visible checklist you see in tools like Claude Code.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langgraph.checkpoint.memory import InMemorySaver

todo_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    middleware=[TodoListMiddleware()],
    checkpointer=InMemorySaver(),     # keeps the list across separate invokes
)

result = todo_agent.invoke(
    {"messages": [("user", "I want to plan a movie night: check what's showing, pick something good, and book 2 seats.")]},
    config={"configurable": {"thread_id": "movie-night"}},
)
print(result["todos"])
```

What happened in class:

- Before any real tool call, the first AI message came back with **empty content and a tool call that fills a list**: gather preferences, retrieve showtimes, recommend a movie, confirm, book. Each item carried a **status**
- As the agent worked through the plan, the list **updated in place**

How it works (checked):

- The middleware adds a **`write_todos` tool** to the agent
- The plan lives in the agent state under **`todos`**, a list of `{"content": ..., "status": ...}` items
- With a checkpointer the list persists on the next turn of the same thread

**Why not just ask for a plan in the system prompt?**

- Plain instructions do **not** reliably produce a *maintained*, structured object that the model keeps updating turn after turn
- The middleware gives the agent that planning object
- This is part of why tools like Claude Code feel more capable on multi-step work. Not different reasoning, just a better-built harness

Two more points:

- The class said it **requires a checkpointer** because the list must persist and update across turns
- The built-in prompt tells the model to use the list for **complex, many-step** work and to skip it for simple requests. Planning costs tokens
- The class notebook cell for this has an empty `system_prompt=` (a syntax error). Leave the argument out, or give it a string

## 9.3 `LLMToolSelectorMiddleware`

**Which problem?** Dynamic tool loading ([Chapter 7](07-middleware.md), 7.2) filters tools by known **state**: is this user a VIP, is this user logged in. A different problem remains even for one fully authorised user: with 15 tools, does every query need all 15 sent to the model?

- Dynamic loading is about **who** is asking. The selector is about **what** is being asked
- Live picture: with many connectors active, a chat product loads only the tools relevant to the query, not every available tool

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware

selector_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    middleware=[
        LLMToolSelectorMiddleware(
            model="openai:gpt-5-mini",             # can be a CHEAPER model than the main agent
            max_tools=2,
            always_include=["check_showtimes"],    # always kept, does not count against max_tools
        ),
    ],
)
```

How it works:

- It uses **structured output**: it asks a (possibly cheaper) model which tools are relevant, then forwards only that subset to the **main** model call
- The selecting model still needs the **full list of tool names and descriptions** to judge from. The saving is in what the **main**, usually more expensive, model receives
- It sees only the **last user message** plus the tool list (checked)
- It runs again on **every** model call, so the tool set can change between the first call and the call after a tool result
- The selection is capped at `max_tools`, and `always_include` tools are added on top
- A name the selector invents raises a `ValueError`. So does an `always_include` name that is not in the tool list

**Prove it with a small custom middleware** (the first hands-on custom middleware of the course):

```python
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def show_tools(request, handler):
    print("\nTOOLS SENT TO MODEL:")
    print([tool.name for tool in request.tools])
    return handler(request)

selector_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    middleware=[
        LLMToolSelectorMiddleware(model="openai:gpt-5-mini", max_tools=2, always_include=["check_showtimes"]),
        show_tools,
    ],
)
```

- Class results: a refund-policy question sent only `check_showtimes` and `get_refund_policy`. A cancellation sent `cancel_booking` and related tools. Never the full six
- **Order matters.** In the list, `show_tools` must come **after** the selector to see the filtered list. Put it first and it prints all six tools (checked, see 9.6)
- **Version note.** In the class notebook (`langchain` 1.3.14) a cancellation first sent **four** tools: `cancel_booking`, `check_order_status`, `get_refund_policy` and the always-included `check_showtimes`, with `max_tools=2`. In 1.4.7 the selection is capped at `max_tools`, so the most you get is three. The second model call in the class run sent two: `cancel_booking` and `check_showtimes`

**Use the right tool for the job.**

- If you **know** a tool must never reach a user (a logged-out user must never see `book_seats`), do that in your own code
- Models are fuzzy and can be wrong. Properly written code is not
- Use the selector only for genuinely **query-dependent** relevance

## 9.4 `ToolErrorMiddleware`

Tools fail: a malformed argument, a missing record, a permission problem.

- **Without any handling,** a tool's exception halts the **whole run**. This is still just Python. In class, `lookup_seat_map` with seat `12` stopped the agent with a `ValueError`
- `ToolErrorMiddleware` catches the exception and turns it into a normal **tool message** the model can read and react to. You see this in products that self-correct after an error instead of crashing

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolErrorMiddleware

def on_seat_error(exc: Exception, request) -> str | None:
    if isinstance(exc, ValueError):
        # Return the exception TYPE, not str(exc): internal detail never reaches the model
        return f"`{request.tool_call['name']}` failed with {type(exc).__name__}. Please provide a valid seat number like 'A12'."
    return None      # anything else propagates and halts the run

error_handled_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    middleware=[ToolErrorMiddleware(on_error=on_seat_error)],
)
```

Details:

- **`on_error` is one function.** Everything you need is inside it: the exception, the tool call request and the tool's name. No multiple handlers
- **Return a string:** it becomes the tool message sent back to the model. In class: `` `lookup_seat_map` failed with ValueError. Please provide a valid seat number like 'A12'. `` with status `error`
- **Return `None`:** the original exception **propagates** and halts the run. Use this to tell recoverable errors from ones that should stop everything (checked: a `KeyError` propagated)
- **Return the exception type, not its message,** so internal details do not leak to the model or the user
- **It does not retry.** Retrying is the next middleware
- **Why handle it here instead of fixing the tool?** Tools are often third-party or shared, so you cannot always change them. Handling failure at the middleware level is the more general solution

## 9.5 `ToolRetryMiddleware`

```python
import random
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware

@tool
def flaky_showtime_check(movie_title: str) -> str:
    """Check showtimes via an external service that can transiently fail."""
    if not random.random() > 1:       # always true here: a deliberately persistent failure
        raise ConnectionError("Simulated network failure")
    return f"{movie_title}: showing at 8:00 PM."

resilient_tool_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=[flaky_showtime_check],
    middleware=[
        ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0, on_failure="continue"),
    ],
)
```

**Settings and defaults** (from the docs, checked): `max_retries=2`, `backoff_factor=2.0`, `initial_delay=1.0`, `max_delay=60.0`, `jitter=True`, `on_failure="continue"`.

- **`max_retries` counts retries after the first call.** `max_retries=3` means up to **4 calls** in total
- **`max_delay`** caps how long any single wait can grow
- **`jitter`** adds small randomness so many clients do not retry in lockstep
- **`on_failure="continue"`:** after the last failure the error comes back as a **tool message**. **`"error"`** re-raises the exception instead

**The backoff formula**

```python
delay = initial_delay * backoff_factor ** retry_number
# retry 0: 1 * 2**0 = 1s
# retry 1: 1 * 2**1 = 2s
# retry 2: 1 * 2**2 = 4s
```

- Why: if a service is briefly down, instant retries do not help. Waiting longer gives it time to recover (like not refreshing a page that is down)
- The whiteboard shows it as "Initial_Delay" and "4 (1 default and 3 retries)": one first try plus three retries
- Class notebook, with a timing tool: gaps of **0.91, 1.90 and 3.42 seconds**. The formula says 1, 2, 4. The difference is **jitter**
- With `jitter=False` the gaps are exactly 1, 2 and 4 seconds (checked)

**A surprising live result: 8 calls, not 4**

- After the first 4 attempts failed, `on_failure="continue"` returned the failure as a tool message instead of crashing
- The **model read that message and independently asked to try the tool again**. That started a second full cycle of 4 attempts. Then it gave up and answered in plain text
- `ToolRetryMiddleware` only controls its **own** retries. It cannot stop the model from deciding to retry on its own
- That is the model's fuzzy, non-deterministic behaviour, not a bug
- To prevent it, **tell the model in the system prompt** not to retry a tool call itself after a failure is reported
- Reproduced offline with a scripted model: 4 + 4 = 8 tool calls

## 9.6 Error and retry together: the order matters

*From testing. Class 13 says only that error handling does not retry.* Both middlewares wrap the tool call, and the **first in the list is the outermost**. An exception travels outwards, so the middleware that should see the raw exception must be **inside**.

```python
middleware=[
    ToolErrorMiddleware(on_error=safe_message),                  # outer: turns the final failure into a safe message
    ToolRetryMiddleware(max_retries=2, on_failure="error"),      # inner: retries, then re-raises
]
```

Checked with a tool that always raises `ValueError`:

- **`[ToolErrorMiddleware, ToolRetryMiddleware]`:** the tool ran **3 times** (1 + 2 retries), then the model got the safe message
- **`[ToolRetryMiddleware, ToolErrorMiddleware]`:** the tool ran **once**. The error middleware turned the exception into a message first, so the retry middleware never saw a failure and never retried
- The same rule explains 9.3: `show_tools` only sees the filtered tools when it is listed **after** the selector

## 9.7 `LLMToolEmulator`

Some tools are expensive, risky, or simply not ready to hit for real during development. The emulator lets a **model simulate** a plausible tool response **without running the tool**.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator

emulated_agent = create_agent(
    model="openai:gpt-5-mini",
    tools=cinebot_tools,
    middleware=[LLMToolEmulator(tools=["book_seats", "cancel_booking"], model="openai:gpt-5-mini")],
)
```

- **Class demo:** the user asked for a leave email citing bad weather, with `get_weather` emulated. The model made up a plausible weather result, and the email was drafted as if the call were real
- **The tool was never called.** The model **manufactured** the response
- **Purpose:** testing and development. Validate an agent's logic without the cost, risk or side effects of a real action (a real email, a real payment)
- **No `tools=` list means every tool is emulated** (checked)
- `model=` is passed **explicitly** in the examples, on purpose. Set it yourself rather than relying on a default
- Checked: with `tools=["book_seats2"]` the real function ran **0 times** and the emulator's text became the tool message

## 9.8 A preview: shell and filesystem tools

- Two more built-in tools were previewed: a **shell tool** (a persistent shell to run real commands) and **filesystem search tools**
- Both belong properly to **Deep Agents**, a later module
- A short demo had an agent run a real `mkdir` on request: a glimpse of how far "an agent's hands" can go
- Full depth comes in [Chapter 10](10-shell-tools-and-custom-middleware.md) and with Deep Agents

## 9.9 Questions from the class

- **Tool Error vs Tool Retry?** Error handles a failure gracefully **once**, as a readable tool message, with no retry. Retry actively retries the call, with backoff
- **Why does a tool call limit give a tool message, not an interrupt?** An interrupt asks a human for a decision. A limit needs none ([Chapter 8](08-prebuilt-middleware-limits-fallback-and-pii.md), 8.2)
- **Do `always_include` tools count against `max_tools`?** No. They are always sent and are not counted
- **If PII is hashed, can the agent still complete a real booking?** Not from the hash. A separate lookup, outside the model's view, resolves it only when a tool truly needs the real value (8.4)
- **Can `on_error` take more than one handler?** No. One function, with full access to the exception, tool name and request
- **Is tool selection the same as dynamic tool loading?** No. Loading filters by **known state** (user type). Selection filters by **what the query says**
- **Why 8 calls, not 4, with `max_retries=3`?** The middleware's cycle is 4. The model then asked for the tool again, which started another cycle (9.5)
- **Why wrap tool errors as a message instead of fixing the tool?** Tools are often third-party or shared, so the general fix is at the middleware level

## 9.10 Interview corner

**1. Why use `TodoListMiddleware` instead of a prompt that says "make a plan"?**

- A prompt does not reliably create a **maintained, structured** list that the model updates every turn. The middleware adds a `write_todos` tool and a `todos` state
- *Stronger answer:* it costs tokens, so it suits complex multi-step work, not simple requests

**2. Tool selector vs dynamic tool loading?**

- Loading filters by known state (who is asking). The selector filters by the content of the query using a cheaper model
- *Stronger answer:* if you already know a tool must not reach a user, use plain code, not an LLM

**3. Tool error middleware vs tool retry middleware?**

- Error: turn a failure into a readable tool message once. Retry: re-run the call with backoff
- *Stronger answer:* they combine, with error listed first (outermost) and retry second (inner)

**4. Your retry middleware has `max_retries=3` but the tool ran 8 times. Why?**

- After the failure message, the **model** asked to retry, starting another cycle
- *Stronger answer:* tell the model in the system prompt not to retry on its own, and use a tool-call limit as a backstop

**5. What is the backoff formula and why jitter?**

- `delay = initial_delay * backoff_factor ** retry_number`: 1s, 2s, 4s. Waiting longer gives a service time to recover
- Jitter adds randomness so many clients do not retry at the same moment

**6. Why return the exception **type** instead of the message from `on_error`?**

- So internal details (paths, queries, secrets) never reach the model or the user

**7. When would you use `LLMToolEmulator`?**

- In development and tests, to check agent logic without real side effects
- *Stronger answer:* the output is invented by a model, so it never belongs in production or in results you rely on

## 9.11 Added by Claude, not from the sources

Not in the course material. Established practice, but check current docs. Items marked *checked* were tested on `langchain` 1.4.7.

**Retry**

- **Retry only what can be retried.** A deterministic failure (a `ValueError` for bad input) never succeeds on a second try. *Checked:* by default the retry middleware **retried a `ValueError` tool 3 times**. Limit it with `retry_on`:

```python
ToolRetryMiddleware(max_retries=3, retry_on=(ConnectionError, TimeoutError))
```

- *Checked:* with `retry_on=(ConnectionError, TimeoutError)` a `ValueError` tool ran **once**, and the `ValueError` was raised as it was. A `ConnectionError` tool was retried
- **Make retried tools safe to repeat.** A retried `book_seats` could book twice. Retry reads freely. For writes, add an idempotency key or do not retry
- **The default failure message includes the exception text** (for example `Tool 'x' failed after 3 attempts with ValueError: bad`). That can leak internal detail. Put `ToolErrorMiddleware` outside it to control the final wording (9.6)

**Cost and testing**

- **The tool selector adds a model call to every model call.** It pays off when you have many tools or large schemas (the class said "15 tools" as the scale). With 3 or 4 tools, skip it. Measure before you adopt it
- **Emulated results are invented.** Label any test that used the emulator, and do not mix its output into evaluation of real behaviour
- **A to-do list is extra tokens and extra tool calls.** Use it only where a plan helps

## Recap

- **Guardrail map:** PII (input), limits and summarization (cost), HITL and selector (what it can do), fallback, error and retry (when things break), to-do list (planning), emulator (testing)
- **To-do list:** adds a `write_todos` tool and a `todos` state. Use a checkpointer to keep it across turns. A prompt alone does not give a maintained list
- **Tool selector:** a cheaper model picks relevant tools from the last user message. `max_tools` caps it, `always_include` is added on top. Query-based, unlike state-based loading
- **Tool error:** one `on_error` function. Return a string to continue, `None` to propagate. Return the exception **type**
- **Tool retry:** `max_retries=3` = 4 calls. `delay = initial_delay * backoff_factor ** retry_number`, with jitter. The **model** may still retry on its own
- **Order:** error outermost, retry inside. First in the list is outermost
- **Emulator:** a model fakes the tool result. For tests only

## Practice

1. Add `TodoListMiddleware` and a checkpointer to a multi-tool agent, give it a genuinely multi-step request and watch the plan fill and update. Print `result["todos"]`
2. Build the `show_tools` middleware yourself and verify `LLMToolSelectorMiddleware` on at least three different queries. Then swap their order and see what changes
3. Write a tool that raises `ValueError`, wrap it with `ToolErrorMiddleware` and confirm the agent no longer crashes. Then return `None` for another exception type and see it propagate
4. Set up `ToolRetryMiddleware` on a tool that always fails. Verify the gaps with `jitter=False` (1, 2, 4 seconds), then with jitter on
5. Make the **model** retry on its own (the 8-call case), then stop it with a system prompt line
6. Combine error and retry in both orders and count the tool calls
7. Try `LLMToolEmulator` on a tool you do not want to call for real yet, and compare its invented answer with the real one
8. Assignment 2 (NovaBank), the parts this chapter prepares you for. The assignment has no answer key:
   - A3 Q11: the correct order of `ToolErrorMiddleware` and `ToolRetryMiddleware`, and what goes wrong if reversed (9.6)
   - B2.3: a tool that raises `ConnectionError` about half the time, with `ToolRetryMiddleware`, printing each attempt
   - B3.2: six or more tools with `LLMToolSelectorMiddleware(max_tools=3, always_include=...)`, confirming the subset sent
   - B3.3: a tool that always raises `ValueError`, with retry (`on_failure="error"`) and error middleware in the right order, proving the final message does not leak the raw exception text
   - (Q6, Q8, Q9, Q12 to Q15 and the capstone need later material: the hook ordering rule, the three retry mechanisms, the three PII `apply_to` flags, the `LLMToolEmulator` model note and `ProviderToolSearchMiddleware`)

## How this chapter was checked

- Run offline with a stand-in model on `langchain` 1.4.7:
  - to-do list: the `write_todos` tool, the `todos` state key, persistence on a second turn with a checkpointer
  - tool selector: a selector returning three names with `max_tools=2` (capped to two, plus the always-included tool), the refund query, an invalid name, a missing `always_include` name, and the order with `show_tools`
  - tool error: the unhandled `ValueError`, the handled message with status `error`, and `None` propagating a `KeyError`
  - tool retry: defaults, 4 calls for `max_retries=3`, the delays with and without jitter, `on_failure="error"`, the 8-call case with a scripted model, and `retry_on`
  - error and retry in both orders
  - tool emulator: the real function never ran, and default emulation of all tools
- **Not run against a live model:** real selector quality, real emulated answers, real service timing. Class output was read from the notebook (cells 98 to 145)
- Not covered here: custom middleware (class 14), the three retry mechanisms and `ProviderToolSearchMiddleware` (assignment questions only)

## Sources and further reading

- Live-Class-2026, `classes_summary/13 - 09 Aug - Guardrails, Todo Lists & Tool Resilience.md` and `classes_summary/12 - 08 Aug - Mastering Middleware.md` (to-do list, selector, error, retry, emulator)
- Live-Class-2026, `classes_transcription_summary/13 - 09 Aug - LangChain - Middlware & Tools.md`
- Live-Class-2026, `MIddleware.ipynb` (cells 98 to 145), the whiteboard `Agent-Middleware-Architecture.pdf` and the folder README in `Weekend 06 - 1 Aug/11-12 - 1-8 Aug - Agents, Memory & Middleware/`
- `Assignment_2_Agents_and_Prebuilt_Middleware.ipynb` (questions only)
- The guardrail map (9.1), the order rule (9.6) and section 9.11 are from testing, not from the class sources

Previous: [Chapter 8, Prebuilt middleware](08-prebuilt-middleware-limits-fallback-and-pii.md) · Next: [Chapter 10, Shell tools and custom middleware](10-shell-tools-and-custom-middleware.md) (not written yet)
