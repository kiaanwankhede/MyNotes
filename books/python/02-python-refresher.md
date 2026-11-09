# Chapter 2: Python you need for agent code

*Only the Python that agent frameworks are built on: data shapes, classes, decorators, errors, typing, streaming, async and logging.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** the patterns you will read in every SDK, LangChain and MCP codebase
> - **Level:** beginner · **Time:** about 20 minutes
> - **Builds on:** [Chapter 1](01-setup-and-api-basics.md) · **Leads to:** [Chapter 3](03-anatomy-of-an-agent.md), [Pydantic book](../pydantic/01-why-pydantic-and-basemodel.md)

---

## 2.1 The data shape that matters most: a list of dicts

```python
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Weather in Tokyo?"},
]
users = [m for m in messages if m["role"] == "user"]     # comprehension
reading.get("humidity")       # None if missing (optional key)
reading["city"]               # KeyError if missing (required key)
lat, lon = (35.68, 139.69)    # tuple unpacking
```

- Chat history, tool results and JSON payloads are all lists of dicts

## 2.2 Classes and dataclasses

```python
@dataclass
class Agent:
    name: str
    system_prompt: str
    tools: dict = field(default_factory=dict)       # mutable default → default_factory
    messages: list = field(default_factory=list)    # the memory

    def remember(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
```

- An object holds **state**; methods change it. Use **guard clauses** to reject bad requests before they corrupt state
- `@dataclass` writes `__init__`/`__repr__` but **validates nothing** → Pydantic at boundaries
- **Abstraction / duck typing:** every tool exposes the same call shape, so an agent can loop over them

```python
class Tool(ABC):
    @abstractmethod
    def run(self, text: str) -> str: ...
```

## 2.3 Decorators

```python
def timed(func):
    @functools.wraps(func)                     # keeps __name__ and docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            log.info("%s took %.1f ms", func.__name__, (time.perf_counter() - start) * 1000)
    return wrapper
```

- `@d` is `func = d(func)`; stacked decorators wrap outside-in
- **Why it matters:** `@tool` in LangChain/MCP is exactly this pattern, and `functools.wraps` keeps the docstring the model reads

## 2.4 Errors

```python
def convert(amount, src, dst) -> float | str:
    try:
        r = requests.get(URL, params={"base": src, "symbols": dst}, timeout=10)
        r.raise_for_status()
        return round(amount * r.json()["rates"][dst], 2)
    except requests.exceptions.RequestException as e:
        return f"Currency service unavailable: {e}"
    except KeyError:
        return f"No rate for {src}->{dst}"
```

- Catch **named** exceptions, never bare `except:`
- In tools, **return** errors as text so the model can react; `finally` for clean-up

## 2.5 Type hints and `TypedDict`

```python
class Message(TypedDict):
    role: Literal["system", "user", "assistant", "tool"]
    content: str

def get_weather(city: str, unit: Literal["c", "f"] = "c") -> dict:
    """Return current weather for `city`."""
```

- Frameworks turn hints + docstring into the **tool schema**; nothing checks them at run time (Pydantic does)

## 2.6 Generators (streaming) and context managers

```python
def stream_words(text):
    for w in text.split():
        yield w + " "                 # one piece at a time, like streamed tokens

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        log.info("%s: %.0f ms", label, (time.perf_counter() - start) * 1000)
```

- `for chunk in client.stream(...)` is a generator; `with` / `async with` guarantee clean-up of clients and connections

## 2.7 `async` for parallel tool calls

```python
async def main():
    return await asyncio.gather(call_tool("weather"), call_tool("currency"), call_tool("news"))
asyncio.run(main())                  # ~0.2 s total instead of 0.6 s
```

- Helps when waiting on I/O (network, disk), not CPU work
- LangChain `ainvoke`, MCP clients and FastAPI are async-first

## 2.8 Logging, not `print`

```python
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("agent")
log.info("tool=%s duration_ms=%.1f", "get_weather", 12.3)
```

> [!IMPORTANT]
> **🏭 In production:** log tool name, duration and outcome, never keys or personal data; type-hint every tool; use async when one agent calls several tools or serves several users.

## Interview corner

<details class="qa"><summary>1. Why <code>functools.wraps</code> in a tool decorator?</summary>

- Keeps the original name and docstring, which frameworks use to build the tool schema

</details>

<details class="qa"><summary>2. When does <code>async</code> help an agent?</summary>

- When it waits on several network calls (tools, model APIs); `gather` runs them concurrently. Not for CPU-heavy work

</details>

<details class="qa"><summary>3. Dataclass vs Pydantic model?</summary>

- Dataclass: internal structures, no validation; Pydantic: anything from outside (API, config, LLM output)

</details>

---

*Source: Live-Class-2026 class 02 files `_0`–`_5` (basics, OOP, dataclasses, decorators, errors, API call); typing, generators, async and logging added by Claude.*

Previous: [Chapter 1](01-setup-and-api-basics.md) · Next: [Chapter 3, Anatomy of an agent](03-anatomy-of-an-agent.md)
