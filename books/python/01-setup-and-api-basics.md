# Chapter 1: Setup and API basics

By the end of this chapter you can set up a Python project with UV, write the basic Python an agent is built from, call a web API, and explain what a "tool" is in plain Python.

## 1.1 The development environment

Pick your terminal first. Mac and Linux already have a good one. On Windows, use **Git Bash** or **Windows Terminal**, not plain CMD or PowerShell. Many Linux-style commands fail on CMD, and almost every cloud machine you will log into runs Linux, so working in a Linux-style shell from day one keeps you platform-independent.

Then install, in this order: Python 3.10 or newer, **UV**, and **VS Code**.

*Source: Live-Class-2026, `classes_summary/01` and `classes_transcription_summary/01`.*

### Why UV

UV is one fast tool that replaces the usual mix of `pip`, `venv` and `conda`/`poetry`. It also mirrors how modern teams manage projects: a single file records the exact Python version and the libraries a project needs, so a teammate can rebuild the same setup. This is the same job `package.json` does in Node. Think of it as a recipe that lists exact ingredients and quantities rather than "some salt".

UV is both a **package manager** (it helps you install packages) and a **project manager** (it keeps the Python version and the package list together). The class slide says UV is "10-100x faster than pip etc.". That is the slide's claim and I have not measured it. The slide also lists `pip`, `venv` and `conda` as the older options and crosses out Anaconda (Anaconda, Miniconda and Conda). The class 01 transcript is gentler: keep conda if you already use it, but do not mix conda and UV commands in one project.

### What you need installed

Before the first coding class: Python, UV, VS Code and a terminal. The slide's advice is to develop in a terminal. Windows has no real terminal by default (it has `cmd` and PowerShell), which is why Git Bash or Windows Terminal is recommended. The class also advised against using an office laptop.

### Check your Python version

Run both `python3 --version` and `python --version`. The slide's example shows two different answers on one machine (3.13.2 and 3.12.9) and says both should be 3.10 or newer. Python versions are like Windows or Office versions: several exist side by side, and you need to be on a recent enough one.

*Source: `Class-1-Python-and-AI.pdf` (class 01 whiteboard), `classes_transcription_summary/01`.*

### Virtual environments: the "room" idea

A virtual environment is a room.

- `uv venv` builds the room.
- Activating it (`source .venv/bin/activate` on Mac/Linux) means you have walked in.
- Whatever you install inside stays inside. The outside world and its packages cannot see in.
- `deactivate` walks you out.

Outside the room is your base Python with its global packages. Inside, a new environment starts empty until you install something. Each project can have its own Python version and its own packages, so projects never conflict. The slide draws this as one machine with several rooms: one `venv` on Python 3.12 with no packages, another on 3.13 with a few, and a terminal-level Python (3.12.9) beside a venv Python (3.13.2) that holds `requests`. The slide labels the two things you choose for a project: the libraries you want and the Python version.

```bash
uv venv                      # build the room
source .venv/bin/activate    # walk in (Windows: .venv\Scripts\activate)
uv add requests              # install inside the room (or: uv pip install requests)
deactivate                   # walk out
```

### Project mode: `uv init`

`uv init my-first-project` creates a project folder. The slide's table says what each item is, whether `uv init` creates it, and whether you edit it:

| File or folder | Created by `uv init`? | Purpose | Edit it? |
|---|---|---|---|
| `.venv/` | No. Created by `uv venv` or `uv sync` | The virtual environment: the Python interpreter, installed packages, activation scripts. Keeps the project's dependencies separate from the system Python | No |
| `.python-version` | Yes | Stores the Python version the project should use (for example `3.12`). Tools such as `uv` or `pyenv` select it when you enter the directory | Rarely |
| `main.py` | Yes | A simple starter file, an entry point where you begin writing the application | Yes |
| `pyproject.toml` | Yes | The heart of a modern Python project: name, version and description, dependencies, build configuration, scripts, and tool settings (for example Ruff, Black, Pytest) | Yes |
| `README.md` | Yes | Documentation: what the project does, how to install and run it. GitHub shows it automatically | Yes |
| `uv.lock` | Yes, but only after you add dependencies or run `uv sync` | Records the exact version of every installed dependency, including the ones those depend on, so everyone gets the same environment | No (generated automatically) |

*Source: the table on the class 01 whiteboard, `Class-1-Python-and-AI.pdf`. An earlier version of this chapter said `uv.lock` comes from `uv init` itself; the slide says otherwise, so that line was corrected.*

The class's `my-first-project` folder is exactly this scaffold. To run it on a fresh machine:

```bash
uv sync          # install what pyproject.toml lists
uv run main.py   # run the script
```

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

A variable is a labelled box, and the data type says what kind of thing may go inside it (you would not store soup in a box labelled "books"). The class file `Python_foundamentals.py` captions every basic line with the role it plays in an agent later:

```python
city = "Tokyo"                    # str   -- a tool ARGUMENT looks like this
temperature = 22.5                # float -- a tool RESULT often looks like this
is_raining = False                # bool  -- a DECISION inside an agent looks like this
forecast = [22.5, 23.1, 21.8]     # list  -- a sequence of readings, in order

print(type(city), type(temperature), type(is_raining), type(forecast))   # shows the data types

print(f"The temperature in {city} is {temperature} degrees.")
print(f"That's {temperature * 9 / 5 + 32:.1f}°F.")   # math works inside { }; :.1f rounds to 1 decimal

if is_raining:
    print("Bring an umbrella.")
else:
    print("No umbrella needed.")

for day_temp in forecast:
    if day_temp > 23:
        print(f"{day_temp}°C — warm day")
    else:
        print(f"{day_temp}°C — mild day")
```

I ran the file. It prints the four types (`str`, `float`, `bool`, `list`), `That's 72.5°F.`, `No umbrella needed.`, then `22.5°C — mild day`, `23.1°C — warm day`, `21.8°C — mild day`. The file ends with the line "Every one of these types and decisions reappears, unchanged, inside the agent you build later.", printed only when the file is run directly.

The companion `notebook.ipynb` repeats the same variables (with `city = "Delhi"`) and the f-string demo, so you can run it cell by cell.

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

**Why the registry exists.** The decorator stores each function in `TOOL_REGISTRY` under its name. When a model later answers "call `get_weather`", your code has to find the real function by that name, and the registry is the lookup. The file registers three tools: `get_current_time`, `calculator` and `get_weather` (with its mock data inside the function). The calculator allows only digits, brackets, spaces and `+ - * / .`.

The bottom of `tools.py` runs a demo:

```python
if __name__ == "__main__":
    get_current_time()
    calculator("12 * (4 + 1)")
    get_weather("Tokyo")
    print("\nRegistered tools:", list(TOOL_REGISTRY.keys()))

    try:
        calculator("12 + ; DROP TABLE users;")
    except ValueError as exc:
        print(f"Caught cleanly, nothing crashed: {exc}")
```

The reason for the `try/except`: a tool that crashes the whole program on bad input cannot be trusted when an AI calls it automatically, so the error is caught and the program carries on.

I ran `tools.py`. It prints one `[tool call]` line for each of the three tools (the calculator returns `60`, the weather tool returns `22°C, partly cloudy`), then `Registered tools: ['get_current_time', 'calculator', 'get_weather']`, then the "Caught cleanly, nothing crashed" line with the rejected string.

*Source: `classes_summary/01`, code files `functions or tools.py` and `tools.py`. A comment in `tools.py` names the agent loop as "Class 4"; the course index puts it in Class 05, so I have not repeated the number.*

## 1.5 Why frameworks come last

The mentor's rule for the whole course: an agent is a concept, so learn it in plain Python first and only then use LangChain. This book, together with the Pydantic book, is that plain-Python phase.

## Run the class code

From the class 01 folder:

```bash
uv venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv add requests
uv run currency.py
```

| File | What it is |
|---|---|
| `Python_foundamentals.py` | Variables, types, f-strings, control flow, functions and docstrings |
| `OOPS.py` | First object-oriented Python outline (see Chapter 2) |
| `currency.py` | Live currency API call with `requests` |
| `functions or tools.py`, `tools.py` | Plain functions that preview agent tools, then the `@tool` registry |
| `notebook.ipynb` | Companion exploration notebook |
| `my-first-project/` | A real `uv init` project |

*Source: the folder's `README.md`.*

## Practice

1. Install Python 3.10+, UV and VS Code, then run `uv venv`, activate, `uv add requests`, `deactivate`.
2. Re-run `currency.py` and check the rate against a web search.
3. Run `tools.py`, then break `calculator("2 + ; DROP TABLE")` on purpose and watch it get caught.
4. Look up `if __name__ == "__main__":`.

## Sources and further reading

- Live-Class-2026, `classes_summary/01 - 27 Jun - Python Setup & API Basics.md`
- Live-Class-2026, `classes_transcription_summary/01 - 27 June - Python Setup & API Basics.md`
- Live-Class-2026, code folder `Weekend 01 - 27-28 Jun/01 - 27 Jun - Python Setup & API Basics/` (all files in it, including its `README.md`, the `my-first-project` folder and the whiteboard `Class-1-Python-and-AI.pdf`)

Next: [Chapter 2, Python refresher](02-python-refresher.md)
