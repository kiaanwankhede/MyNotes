# Chapter 1: Setup and API basics

By the end of this chapter you can set up a Python project with UV, write the basic Python an agent is built from, call a web API, and explain what a "tool" is in plain Python.

## 1.1 The development environment

Pick your terminal first. Mac and Linux already have a good one. On Windows, use **Git Bash** or **Windows Terminal**, not plain CMD or PowerShell. Many Linux-style commands fail on CMD, and almost every cloud machine you will log into runs Linux, so working in a Linux-style shell from day one keeps you platform-independent.

Then install, in this order: Python 3.10 or newer, **UV**, and **VS Code**.

*Source: Live-Class-2026, `classes_summary/01` and `classes_transcription_summary/01`.*

### Why UV

UV is one fast tool that replaces the usual mix of `pip`, `venv` and `conda`/`poetry`. It also mirrors how modern teams manage projects: a single file records the exact Python version and the libraries a project needs, so a teammate can rebuild the same setup. This is the same job `package.json` does in Node. Think of it as a recipe that lists exact ingredients and quantities rather than "some salt".

### Virtual environments: the "room" idea

A virtual environment is a room.

- `uv venv` builds the room.
- Activating it (`source .venv/bin/activate` on Mac/Linux) means you have walked in.
- Whatever you install inside stays inside. The outside world and its packages cannot see in.
- `deactivate` walks you out.

Outside the room is your base Python with its global packages. Inside, a new environment starts empty until you install something. Each project can have its own Python version and its own packages, so projects never conflict.

```bash
uv venv                      # build the room
source .venv/bin/activate    # walk in (the activation command differs by OS; ask an AI to translate it for yours)
uv add requests              # install inside the room (or: uv pip install requests)
deactivate                   # walk out
```

### Project mode: `uv init`

`uv init my-first-project` creates a project folder with:

| File | Purpose |
|---|---|
| `pyproject.toml` | Python version and dependency list. The file a teammate's machine reads to rebuild your setup |
| `uv.lock` | Also created by `uv init` (lock file) |
| `.python-version` | Also created by `uv init` |
| `main.py` | A starter script |

The starter `main.py` only proves the wiring works:

```python
def main():
    print("Hello from my-first-project!")

if __name__ == "__main__":
    main()
```

The class asked you to look up `if __name__ == "__main__":` yourself and promised a proper explanation in a later class. (Standard Python behaviour, not taught in these summaries: the block runs only when the file is run directly, not when it is imported.)

Common questions from the class:

| Question | Answer |
|---|---|
| `requirements.txt` or `pyproject.toml`? | UV reads only `pyproject.toml`. Pick one workflow per project and do not mix `pip install` with `uv add`, which can cause version conflicts |
| Do I have to activate the environment? | Not strictly. `uv run` in project mode also works. Both are valid |
| Change the Python version? | `uv python upgrade` |
| Already use conda? | Keep it if you like, but do not mix conda and UV commands in the same project |

### Why VS Code and not Jupyter notebooks

This course is about agents, not data science. The work is `.py` scripts, a real terminal (you will log into cloud machines often) and proper debugging. VS Code gives you all three. Notebooks are still used for some demos later.

## 1.2 Python fundamentals, with the agent meaning attached

The class file `Python_foundamentals.py` captions every basic line with the role it plays in an agent later:

```python
city = "Tokyo"                    # str   -- a tool ARGUMENT looks like this
temperature = 22.5                # float -- a tool RESULT often looks like this
is_raining = False                # bool  -- a DECISION inside an agent looks like this
forecast = [22.5, 23.1, 21.8]     # list  -- a sequence of readings, in order

print(f"The temperature in {city} is {temperature} degrees.")
print(f"That's {temperature * 9 / 5 + 32:.1f}°F.")   # math works inside f-string { }

if is_raining:
    print("Bring an umbrella.")
else:
    print("No umbrella needed.")

for day_temp in forecast:
    if day_temp > 23:
        print(f"{day_temp}°C — warm day")
```

Points to take from it:

- **No type declarations.** You write `x = 5`, not `int x = 5`.
- **f-strings** put variables (and even small calculations) straight into text.
- **Functions need docstrings.** Agent tooling later reads the docstring to tell the model what a function does.

*Source: `classes_summary/01`, code file `Python_foundamentals.py`.*

## 1.3 APIs, before any framework

An API call is your code asking another service for data and getting a response. The class analogy: you have a keypad phone with no internet and want a flight price from India to Dubai. You phone a travel agent, tell them what you need, and they call back with the price. Your code is you, the API is the agent, and the data source is wherever the agent looks it up.

The demo, `currency.py`, calls a free currency API that needs no key:

```python
import requests

BASE = "https://api.frankfurter.app"
url = f"{BASE}/latest"
params = {"from": "USD", "to": "INR", "amount": 100}

try:
    response = requests.get(url, params=params, timeout=10)  # hang up after 10 s of silence
    response.raise_for_status()
    data = response.json()
    converted_amount = data["rates"]["INR"]
    print(f"100 USD = {converted_amount:.2f} INR")
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
```

What each part does:

- `timeout=10` stops your program waiting forever, like hanging up when nobody answers.
- `raise_for_status()` turns an HTTP error (404, 500) into an exception.
- The `try/except` handles the case where the call fails.

Every LLM call later (OpenAI, Anthropic, Groq) has this same shape: send a request, get structured data back, and handle failure. In class the live rate was checked against a web search to prove the call was real.

*Source: `classes_summary/01`, `classes_transcription_summary/01`, code file `currency.py`. The snippet is copied from the class code; I did not run it here because the sandbox could not reach the API.*

## 1.4 The first idea of a "tool"

A tool is just a function with a docstring and a return value. Two examples from `functions or tools.py`:

```python
import time

def get_current_time() -> str:
    """Return the current time as a human-readable string."""
    return time.strftime("%Y-%m-%d %H:%M:%S")

fake_weather_data = {
    "tokyo": "22°C, partly cloudy",
    "delhi": "34°C, clear skies",
    "london": "15°C, light rain",
}

def get_weather(city: str) -> str:
    """Return the current weather for `city`. (Mock data for teaching.)"""
    return fake_weather_data.get(city.lower(), f"No weather data for {city!r}")
```

`tools.py` goes one step further. It builds a `@tool` decorator that times every call and registers the function in a `TOOL_REGISTRY` dictionary. This is the shape that tool calling takes in every framework (decorators are explained in Chapter 2):

```python
import functools, time
from typing import Callable

TOOL_REGISTRY: dict[str, Callable] = {}

def tool(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[tool call] {func.__name__}({args}, {kwargs}) -> {result!r}  ({elapsed_ms:.2f} ms)")
        return result
    TOOL_REGISTRY[func.__name__] = wrapper
    return wrapper

@tool
def calculator(expression: str) -> float:
    """Safely evaluate a simple arithmetic expression, e.g. '12 * (4 + 1)'."""
    allowed_characters = set("0123456789+-*/(). ")
    if not set(expression) <= allowed_characters:
        raise ValueError(f"Expression contains characters that aren't allowed: {expression!r}")
    return eval(expression)  # safe here ONLY because of the character check above
```

**Pitfall.** `eval` is dangerous on arbitrary text. It is acceptable here only because the character check runs first. The class deliberately feeds the tool a SQL-injection-shaped string, `"12 + ; DROP TABLE users;"`, to show the guard rejects it. This habit matters more once a model, not a person, chooses the string.

I ran the decorator and the calculator guard: `calculator("12 * (4 + 1)")` returns `60`, and the injection string raises `ValueError`.

*Source: `classes_summary/01`, code files `functions or tools.py` and `tools.py`.*

## 1.5 Why frameworks come last

The mentor's rule for the whole course: an agent is a concept, so learn it in plain Python first and only then use LangChain. This book, together with the Pydantic book, is that plain-Python phase.

## Practice

1. Install Python 3.10+, UV and VS Code, then run `uv venv`, activate, `uv add requests`, `deactivate`.
2. Re-run `currency.py` and check the rate against a web search.
3. Run `tools.py`, then break `calculator("2 + ; DROP TABLE")` on purpose and watch it get caught.
4. Look up `if __name__ == "__main__":`.

## Sources and further reading

- Live-Class-2026, `classes_summary/01 - 27 Jun - Python Setup & API Basics.md`
- Live-Class-2026, `classes_transcription_summary/01 - 27 June - Python Setup & API Basics.md`
- Live-Class-2026, code folder `Weekend 01 - 27-28 Jun/01 - 27 Jun - Python Setup & API Basics/`

Next: [Chapter 2, Python refresher](02-python-refresher.md)
