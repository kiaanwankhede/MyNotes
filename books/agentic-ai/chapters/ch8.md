# Guardrails, todo lists and resilient tools
> lead: The rest of the built-in middleware catalogue: tool call limits, deeper PII handling, todo lists, smart tool selection, graceful tool errors, retries with backoff and tool emulation for testing.
meta: Class 13 | 9 August | 40 min read | No code folder shared for this class

:::repo No code was shared for this class
The repo has a written summary but no code folder for Class 13. The snippets below come from that summary. LangChain moves fast, so check the exact class and parameter names against your installed version and its middleware reference.
:::

## Why it matters

Agents fail in boring ways: a tool throws, a service times out, a limit is hit, personal data slips through. This chapter is the "production hardening" toolbox. It also maps directly to industries: fraud-detection hooks in fintech, PII redaction as a real HIPAA requirement in healthcare, refund approval gates in customer support, audit logging in internal developer tools.

## Core ideas

### 1. Tool call limit: run limit vs thread limit

:::analogy Meals and days
A **run** is one meal and a **thread** is a whole day. A run limit of 4 caps how many chapatis you eat in one sitting. A thread limit of 10 caps the day's total, however you split it across meals. In Claude: the searches inside one reply are the run, and the total across the chat is the thread.
:::

```python
from langchain.agents.middleware import ToolCallLimitMiddleware
from langgraph.checkpoint.memory import InMemorySaver

tool_limited_agent = create_agent(
    model="openai:gpt-5.5",
    tools=cinebot_tools,
    checkpointer=InMemorySaver(),
    middleware=[
        ToolCallLimitMiddleware(run_limit=8),                    # all tools, this turn
        ToolCallLimitMiddleware(tool_name="cancel_booking",      # one tool, whole conversation
                                thread_limit=2, run_limit=1),
    ],
)

config = {"configurable": {"thread_id": "tool-limit-demo"}}
for i in range(3):
    tool_limited_agent.invoke(
        {"messages": [("user", f"Please cancel my Booking with ID B{100+i}?")]}, config=config)
```

Run three times in one thread: the first two cancellations succeed and the third is blocked. A **tool message with an error status** comes back, phrased so the model can relay it to the user.

:::key A limit is a tool message, not an interrupt
An interrupt exists to ask a human for a decision. A limit rejection needs none, so it is simply refused and reported back as information. The right number comes from understanding the business use case; LangChain does not decide it for you.
:::

### 2. Guardrails: the highway analogy

A barrier on a mountain road keeps a car from going over the edge. An agent's output is unpredictable by default, so something must bound what it can say or do. The working definition: **a guardrail is a way to control the agent's behaviour, nothing more.**

- ChatGPT refuses to explain how to jump off a moving plane or to hand over its raw system message: built-in guardrails. The tighter the guardrail, the harder it is to get around.
- A guardrail is the **goal**. Middleware is one **mechanism** for it, alongside careful system prompts or third-party libraries. Even a tool call limit counts as a guardrail.
- **Compliance is defined outside the framework**: by company policy, regulation or certification (HIPAA, GDPR, SOC 2).

### 3. PII, in more depth

```python
from langchain.agents.middleware import PIIMiddleware

pii_agent = create_agent(
    model="openai:gpt-5.5",
    tools=cinebot_tools,
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)
```

In the demo the reply even **warned the user not to share full card numbers in chat**, a better experience than a blunt refusal, and the history showed the email redacted before it reached the model.

:::key Why not just tell the model to behave?
Even with a system prompt forbidding misuse, **sending personal data to a third-party provider is itself a compliance question**. A customer can ask why their data ever left your application's boundary. Increasingly this is asked in real audits.
:::

**Why the card was not masked at first:** the detector validates numbers with the **Luhn algorithm**, the checksum real card numbers satisfy. An arbitrary digit string fails it and is not treated as a card.

| Strategy | Behaviour |
| --- | --- |
| `block` | Raises an exception when PII is detected, halting the flow |
| `redact` | Replaces it with a type placeholder. The original is gone |
| `mask` | Partly obscures it (for example only the last digits) |
| `hash` | Replaces it with a **deterministic hash**: the same input always gives the same hash, preserving identity for analytics or debugging without exposing the value |

For hash, a card referenced internally as `AMZ1234ABC` tells an outsider nothing, but your system can look it up consistently. When a tool genuinely needs the real value, that lookup happens **separately, outside the model's view**.

**Custom detectors** can be a regex or a full function:

```python
import re

def detect_booking_code(content: str) -> list[dict]:
    """CineBot's own booking code: BK followed by 4 digits."""
    return [{"text": m.group(0), "start": m.start(), "end": m.end()}
            for m in re.finditer(r"BK\d{4}", content)]

custom_pii_agent = create_agent(
    model="openai:gpt-5.5",
    tools=cinebot_tools,
    middleware=[PIIMiddleware("booking_code", detector=detect_booking_code, strategy="hash")],
)
```

:::tip Payments belong in a headless tool
Should card numbers ever pass through the AI to complete a purchase? The better pattern is a **headless tool**: a secure payment page the user uses directly, entirely outside the model's view.
:::

### 4. Todo list middleware

For multi-step work, an agent should plan upfront and track progress, like the visible checklists in Claude Code.

```python
from langchain.agents.middleware import TodoListMiddleware

todo_agent = create_agent(
    model="openai:gpt-5.5",
    tools=cinebot_tools,
    middleware=[TodoListMiddleware()],
)
todo_agent.invoke({"messages": [("user",
    "Plan a movie night: check what's showing, pick something good, and book 2 seats.")]})
```

Before any real tool call, the first AI message had empty content and a tool call that **populated a list**: gather preferences, get showtimes, recommend, confirm, book. Each item carries a status, and the list updates in place as the agent works.

:::key Why not ask for a plan in the system prompt?
A prompt does not reliably produce a **maintained, structured object** that the model keeps updating turn after turn. This middleware provides that object. It is part of why tools like Claude Code feel stronger at multi-step tasks: not different reasoning, a better-scaffolded harness. Because the list persists across turns, it needs a **checkpointer**.
:::

### 5. LLM tool selector: choose tools by query, not by state

Dynamic loading (Chapter 6) filters by **state** (who is asking: VIP, authenticated). A different axis remains: if an agent has 15 tools, does every **query** need all 15 sent? Claude does not load every connector's tools for every request; it loads what is relevant.

```python
from langchain.agents.middleware import LLMToolSelectorMiddleware

selector_agent = create_agent(
    model="openai:gpt-5.5",
    tools=cinebot_tools,
    middleware=[
        LLMToolSelectorMiddleware(
            model="openai:gpt-5-mini",           # can be cheaper than the main model
            max_tools=2,
            always_include=["check_showtimes"],  # always kept, does not count toward max_tools
        ),
    ],
)
```

It uses **structured output**: a possibly cheaper model chooses which tools are relevant to the current query, and only that subset goes to the main model. The selector still needs the full list of names and descriptions to judge from, so the saving is in what the expensive main model receives.

**The first custom middleware of the course**, written to prove it works:

```python
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def show_tools(request, handler):
    print("TOOLS SENT TO MODEL:", [tool.name for tool in request.tools])
    return handler(request)
```

A refund-policy question sent only `check_showtimes` and `get_refund_policy`. A cancellation sent `cancel_booking` and related tools. Never the whole set of six. Each model call resends the tool list filtered for that turn.

:::trap Do not let an LLM decide what you already know
If a non-logged-in user must **never** see `book_seats`, that decision belongs in your own code. Models are fuzzy and can err; properly written code does not. Use the selector for genuine query-dependent relevance and plain logic wherever the answer is known in advance.
:::

### 6. Tool error middleware: fail gracefully, without retrying

Without handling, a tool's exception **halts the whole run**, because underneath it is still Python.

```python
from langchain.agents.middleware import ToolErrorMiddleware

@tool
def lookup_seat_map(movie_title: str, seat_number: str) -> str:
    """Look up a specific seat. Fails if the seat number format is wrong."""
    if not seat_number or not seat_number[0].isalpha():
        raise ValueError(f"Malformed seat number '{seat_number}'. Expected a letter plus number like 'A12'.")
    return f"Seat {seat_number} for {movie_title}: available."

def on_seat_error(exc: Exception, request) -> str | None:
    if isinstance(exc, ValueError):
        return (f"`{request.tool_call['name']}` failed with {type(exc).__name__}. "
                "Please provide a valid seat number like 'A12'.")
    return None        # anything else propagates and halts the run

error_handled_agent = create_agent(
    model="openai:gpt-5.5",
    tools=cinebot_tools,
    middleware=[ToolErrorMiddleware(on_error=on_seat_error)],
)
```

The exception becomes a normal tool message the model can read and react to, like Claude visibly self-correcting after an error.

- `on_error` takes **one function**, which has the exception, the request and the tool name.
- Returning a **string** makes it the tool message. Returning **`None`** lets the exception propagate and halt the run, so you can separate recoverable from fatal errors.
- Returning the **exception type**, not the raw message, avoids leaking internals to the model or user.
- It does **not** retry. That is the next middleware.

### 7. Tool retry middleware: exponential backoff

```python
from langchain.agents.middleware import ToolRetryMiddleware

resilient_tool_agent = create_agent(
    model="openai:gpt-5.5",
    tools=[flaky_showtime_check],
    middleware=[ToolRetryMiddleware(max_retries=3, backoff_factor=2.0,
                                    initial_delay=1.0, on_failure="continue")],
)
```

`max_retries` counts retries **after** the first call, so `max_retries=3` allows up to **4** calls. Defaults when unspecified: `max_retries=2`, `backoff_factor=2.0`, `initial_delay=1.0`, `max_delay=60.0`, `jitter=True`, `on_failure="continue"`.

```latex
delay = initial_delay × backoff_factor ^ retry_number
```

| Retry | Wait (initial 1s, factor 2) |
| --- | --- |
| 0 | 1 second |
| 1 | 2 seconds |
| 2 | 4 seconds |

If a service is briefly down, instant retries do not help. Waiting longer gives it time to recover, the same instinct as not hammering refresh on a dead site. `max_delay` caps any single wait and `jitter` adds small randomness so many clients do not retry in lockstep.

:::trap The surprise: 8 calls, not 4
With `max_retries=3` the flaky tool ran **8** times. After four failed attempts, `on_failure="continue"` returned a tool message, and the **model** read it and independently asked to try again, triggering a second cycle of four. The middleware only controls its own retries per invocation; it cannot stop the model deciding to retry. Prevent it with an explicit system-prompt instruction not to retry after a reported failure. It shows the model's fuzzy, non-deterministic behaviour, not a bug.
:::

| | Tool error | Tool retry |
| --- | --- | --- |
| Action | Converts one failure into a readable message | Actively retries the call |
| Retries | No | Yes, with backoff |
| Use when | Failures are permanent or need explaining | Failures are transient (network) |

You often wrap errors in middleware because tools are frequently third-party or shared, so you cannot change their internals.

### 8. LLM tool emulator: fake tool calls for testing

```python
from langchain.agents.middleware import LLMToolEmulator

emulated_agent = create_agent(
    model="openai:gpt-5.5",
    tools=cinebot_tools,
    middleware=[LLMToolEmulator(tools=["book_seats", "cancel_booking"], model="openai:gpt-5-mini")],
)
```

A model **invents** a plausible tool response; the tool is never executed. In the demo, `get_weather` was emulated and the rest of the flow (drafting a leave email) ran as if the call was real. Use it to validate an agent's logic without cost, risk or side effects. Without a `tools` list, **every** tool is emulated.

### 9. Preview: deep agent tools

Two more built-ins were previewed: a shell tool giving the agent a persistent shell, and filesystem search tools. A live demo ran a real `mkdir`. They belong to Deep Agents, a later module. Chapter 9 covers shell tools.

<!-- docs-add -->
## From the docs: the guardrails page

*Added from the LangChain Guardrails page (read 30 Oct 2026).*

- **Two approaches.** **Deterministic** guardrails use rules (regex, keywords, explicit checks): fast, cheap and predictable but they miss nuance. **Model-based** guardrails use an LLM or classifier to judge meaning: they catch subtler issues but cost latency and money on every response.
- **`PIIMiddleware` strategies**: `redact` (typed placeholder), `mask` (partial, for example last four digits), `hash` (deterministic hash) and `block` (raise an exception). Built-in types are `email`, `credit_card` (Luhn-validated), `ip`, `mac_address` and `url`; custom types use a regex `detector`, for example `PIIMiddleware("employee_id", detector=r"EMP-\d{6}", strategy="block")`.
- **Where it applies**: `apply_to_input` (default on), `apply_to_output` (default off; with `langchain>=1.3.2` it also redacts streamed output, Chapter 10A) and `apply_to_tool_results` (default off).
- **Custom guardrail hooks.** `before_agent` runs once at the start (input checks, authentication, rate limits). `after_agent` runs once on the final reply (model-based safety, quality, compliance). To stop early, declare `can_jump_to=["end"]` on the hook and return a message with `jump_to: "end"`.
- **Stacking order** matters because middleware runs in list order. The page's typical stack: a deterministic input filter, then PII handling, then human approval for sensitive tools, then a model-based output check last.
- **Judge model**: the safety example uses a smaller, cheaper model that answers `SAFE` or `UNSAFE`; if unsafe, the hook replaces the reply with a refusal.
<!-- /docs-add -->

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Confusing run and thread limits | Limit hits too early or never | Run is one invoke; thread is the whole conversation (needs a checkpointer) |
| Expecting a limit to raise an interrupt | Waiting for a human | It returns a tool message with an error status |
| Test card numbers not masked | PII reaches the model | Use a Luhn-valid number, or a custom detector |
| Letting an LLM gate access | Tool exposed by mistake | Decide known cases in code |
| Tool error returning the raw exception | Internals leak | Return the exception type or a clean message |
| Returning `None` by mistake | Run halts | Return a string for recoverable errors |
| Using retry for permanent failures | Wasted calls | Use error handling; retry only transient failures |
| Not telling the model to stop retrying | Surprise extra cycles | Add an instruction in the system prompt |
| Todo list without a checkpointer | List not maintained | Add a checkpointer |

## Hands-on lab

1. Build the limit demo with a global `run_limit` and a tool-specific `thread_limit`, and trace when each resets.
2. Try all four PII strategies (`block`, `redact`, `mask`, `hash`) on the same input.
3. Add `TodoListMiddleware` to a multi-tool agent and give it a multi-step request.
4. Write `show_tools` with `@wrap_model_call` and verify the selector on three queries.
5. Raise a `ValueError` in a tool, wrap it with error handling and confirm the agent no longer crashes.
6. Make a tool that always fails, add retries and check the backoff timing by hand.
7. Emulate a tool you do not want to call yet and compare its output with the real one.

## Interview corner

:::pitch
For production hardening I layer middleware: call limits to cap cost, PII handling so sensitive data never reaches the provider, a todo list for multi-step planning, a tool selector to send only relevant tools, error handling so one failing tool does not halt the run, retries with exponential backoff for transient failures, and an emulator for safe testing. A guardrail is the goal; these are the mechanisms.
:::

### Basics

:::qa Run limit vs thread limit?
Run limit caps calls within one `invoke`. Thread limit caps calls across the whole conversation and needs a checkpointer. A meal versus a day.
:::

:::qa What are the four PII strategies?
`block` (raise an exception), `redact` (replace with a placeholder), `mask` (partly hide) and `hash` (deterministic hash that keeps identity without the value).
:::

:::qa What does the todo list middleware add?
A structured, maintained plan object the agent updates as it works. A prompt alone does not reliably create and track one.
:::

:::qa Tool error vs tool retry?
Error handling converts one failure into a readable tool message without retrying. Retry actively re-runs the call with backoff. Use error handling for permanent failures and retry for transient ones.
:::

### Intermediate

:::qa Why does a tool call limit produce a tool message rather than an interrupt?
An interrupt asks a human for a decision. A limit rejection needs none, so it is returned to the model as information.
:::

:::qa How does the LLM tool selector differ from dynamic tool loading?
Dynamic loading filters by known **state** (who the user is). The selector filters by the **content of the current query**, using a possibly cheaper model with structured output to choose relevant tools.
:::

:::qa When should you not use the LLM tool selector?
When the answer is already known with certainty, such as a non-logged-in user who must never see a booking tool. Put that in code. Models are fuzzy; code is not.
:::

:::qa What is the backoff formula and why use it?
`delay = initial_delay × backoff_factor ^ retry_number`. Waiting longer between attempts gives a briefly failing service time to recover, `max_delay` caps the wait and jitter avoids synchronised retries.
:::

:::qa How does `max_retries` count?
Retries **after** the first call. `max_retries=3` allows up to four calls in total.
:::

### Tricky

:::qa Your flaky tool ran 8 times with `max_retries=3`. Why?
The middleware made 4 calls, returned a failure tool message, and the model decided on its own to call the tool again, starting another cycle of 4. The middleware controls only its own retries. Add a system-prompt instruction telling the model not to retry after a reported failure.
:::

:::qa Why was the credit card not masked in the demo?
The card detector checks numbers with the Luhn checksum. An arbitrary digit string fails it, so it was not recognised as a card.
:::

:::qa Even with a "do not misuse personal data" prompt, why use PII middleware?
Because sending the data to a third-party provider is itself a compliance issue. Middleware prevents it leaving your boundary at all. Compliance rules come from outside the framework: policy, regulation, certification.
:::

:::qa If a tool needs the real value behind a hash, what happens?
A separate lookup outside the model's view resolves the hash when a tool genuinely needs it. The model never sees the real value.
:::

:::qa What is the LLM tool emulator for?
Testing. A model fabricates a plausible tool result without running the tool, so you can validate agent logic without cost, risk or side effects. It is not for production.
:::

:::qa How should card payments be handled in an agent?
Not through the model. Use a headless tool: a secure payment page the user interacts with directly, outside the model's view.
:::

:::qa A production agent appears to hang. How do you debug it?
Check tracing first (LangSmith or equivalent) and look at the last completed step. The usual causes are a tool blocked on a slow external call with **no timeout**, or an agent that never reaches a stopping condition because **no call cap** was set. The hardened fix is a tool and model call ceiling in middleware plus real timeouts on external calls, set up before an incident rather than discovered during one.
:::

## Quick revision

- [ ] I can explain run vs thread limits and why a limit is a tool message
- [ ] I can define a guardrail and separate it from middleware and compliance
- [ ] I can list four PII strategies and explain Luhn and custom detectors
- [ ] I can explain why a todo list middleware beats a prompt
- [ ] I can separate tool selection from dynamic loading, and say when not to use it
- [ ] I can write `show_tools` with `wrap_model_call`
- [ ] I can compare tool error and tool retry and do the backoff math
- [ ] I can explain the 8 calls surprise and the fix
- [ ] I can say what the emulator is for

## Sources and further reading

- [Class 13 full notes]({{src:classes_transcription_summary/13 - 09 Aug - LangChain - Middlware & Tools.md}})
- [Class 13 short summary]({{src:classes_summary/13 - 09 Aug - Guardrails, Todo Lists & Tool Resilience.md}})
- [Weekend 07 overview]({{src:Weekend 07 - 8-9 Aug/README.md}})
- [Weekend 07 middleware notebook]({{src:Weekend 07 - 8-9 Aug/MIddleware.ipynb}})
- [Researched LangChain interview questions (PDF)]({{src:Weekend 05 - 25-26 Jul/09-10 - 25-26 Jul - Structured Output & Tools (CineBot)/Assignment & Questions/LangChain_Interview_Questions_Researched.md.pdf}})
