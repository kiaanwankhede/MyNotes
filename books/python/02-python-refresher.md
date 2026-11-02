# Chapter 2: Python refresher

**After this chapter you can:**

- Use lists, tuples, dicts and a list of dicts, and write a list comprehension
- Build a class with state and a guard clause, and a dataclass without boilerplate
- Write and stack decorators with `functools.wraps`
- Handle errors with `try/except/finally`
- Say why Python needs Pydantic

**Builds on:** [Chapter 1](01-setup-and-api-basics.md). **Leads to:** [Chapter 3](03-anatomy-of-an-agent.md) and the [Pydantic book](../pydantic/01-why-pydantic-and-basemodel.md).

Each topic is here because agents lean on it later.

## 2.1 Types, f-strings, control flow and data structures

Files `_0` to `_4` are plain Python with no AI. The class presents them as skills worth having on their own.

### Types, f-strings and decisions

```python
temperature = 22.5

if temperature > 30:
    print("Pack light clothes.")
elif temperature > 15:
    print("A light jacket should be enough.")
else:
    print("Pack a warm coat.")

print(5 == 5, 5 != 3, 10 > 20)       # True True False
has_ticket = True
has_id = True
if has_ticket and has_id:
    print("Ready to board.")
```

- *Checked* (`_0_basics_refresher.py`): prints "A light jacket should be enough.", `True True False`, "Ready to board."

### Lists

- An ordered, changeable collection. Indexing works from both ends

| Index | 0 | 1 | 2 |
|---|---|---|---|
| Value | Tokyo | Delhi | London |
| Negative index | -3 | -2 | -1 |

```python
cities = ["Tokyo", "Delhi", "London"]
print(cities[0])          # first item
print(cities[-1])         # last item
print(cities[0:2])        # slice -> ['Tokyo', 'Delhi']
cities.append("Paris")    # add to the end
```

- A list can mix types. `Python_run.ipynb` uses `["Tokyo", "Delhi", "London", 1]` and it accepts the number. *Checked*
- The notebook has a note to compare arrays and lists, but nothing under it, so this book does not make that comparison

*Source: `classes_summary/02`, `classes_transcription_summary/02`, `_1_data_structures.py`, `Python_run.ipynb`.*

### Tuples

- Like a list that cannot change after creation. *Checked:* assigning to an item raised `TypeError`
- **Unpacking** splits it into variables:

```python
coordinates = (35.68, 139.69)         # latitude, longitude
latitude, longitude = coordinates
```

### Dictionaries

```python
weather_reading = {"city": "Tokyo", "temperature_c": 22.5, "condition": "partly cloudy"}
print(weather_reading["city"])          # by key
print(weather_reading.get("humidity"))  # None instead of a crash if missing
weather_reading["humidity"] = 60        # add a key
for key, value in weather_reading.items():
    print(f"{key}: {value}")
```

### A list of dictionaries, and a list comprehension

The shape that matters most later: tool results and chat messages look like this.

```python
readings = [
    {"city": "Tokyo", "temperature_c": 22.5},
    {"city": "Delhi", "temperature_c": 34.0},
    {"city": "London", "temperature_c": 15.0},
]
warm_cities = [r["city"] for r in readings if r["temperature_c"] > 20]   # ['Tokyo', 'Delhi']
```

- *Checked* (`_1_data_structures.py`): `None` for the missing key, the dict with `humidity` added, and `['Tokyo', 'Delhi']`

*Source: `_1_data_structures.py`.*

## 2.2 Object-oriented Python: a bank account

- A class is a blueprint. Each object gets its own data (its **state**)
- The class was drawn on a whiteboard first, then coded:

```python
class BankAccount:
    """A blueprint for a bank account -- nothing to do with AI."""

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self.balance = balance    # the account's STATE
        self.history = []

    def deposit(self, amount: float) -> None:
        self.balance += amount
        self.history.append(f"Deposited {amount}")

    def withdraw(self, amount: float) -> None:
        if amount > self.balance:
            print(f"Insufficient funds: tried to withdraw {amount}, balance is {self.balance}")
            return
        self.balance -= amount
        self.history.append(f"Withdrew {amount}")

account_1 = BankAccount(owner="Mayank", balance=1000)
account_2 = BankAccount(owner="Krish", balance=500)
account_1.deposit(200); account_1.withdraw(50); account_2.withdraw(1000)
```

- *Checked* (`_2_oop_classes.py`): "Insufficient funds: tried to withdraw 1000, balance is 500"; Mayank ends at 1150 with two history lines; Krish stays at 500 with none. The objects do not share state
- `self` is "this particular object"
- `__init__` runs when the object is created and sets starting values
- `if amount > self.balance` is a **guard clause**: reject a bad request before it corrupts state. Agents need the same habit

### The OOP outline from class 01

- `OOPS.py` holds only comments: classes, objects, inheritance, polymorphism, abstraction, encapsulation
- The summaries explain classes and objects only. This book does not explain the other four

*Source: `classes_summary/02`, `classes_transcription_summary/02`, `_2_oop_classes.py`, `OOPS.py`.*

## 2.3 Dataclasses: no boilerplate

- `@dataclass` writes `__init__` from type-hinted fields. Java developers: compare Lombok

```python
from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    author: str
    pages_read: int = 0
    tags: list = field(default_factory=list)   # mutable defaults need default_factory

    def read(self, pages: int) -> None:
        self.pages_read += pages
    def add_tag(self, tag: str) -> None:
        self.tags.append(tag)

print(Book(title="Atomic Habits", author="James Clear"))
# Book(title='Atomic Habits', author='James Clear', pages_read=0, tags=[])
```

- A dataclass prints itself readably with no extra code
- **Pitfall 1: mutable defaults.** A list, dict or set default needs `field(default_factory=...)`. *Checked:* `tags: list = []` raises `ValueError: mutable default <class 'list'> for field tags is not allowed`
- **Pitfall 2: no validation.** *Checked:* `Book(title="x", pages_read="banana")` succeeds and stores the string. Pydantic fixes this ([Pydantic Ch 1](../pydantic/01-why-pydantic-and-basemodel.md))

*Source: `classes_summary/02`, `classes_transcription_summary/02`.*

## 2.4 Decorators: wrap a function without changing it

- A decorator is gift wrap. The contents stay the same; behaviour is added around them
- It works because functions are objects: you can pass one in and return one
- `@decorator` above a function is shorthand for `func = decorator(func)`

```python
import functools, time

def announce(func):
    @functools.wraps(func)   # keeps func.__name__
    def wrapper(*args, **kwargs):
        print(f"Starting {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}.")
        return result
    return wrapper

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {(time.perf_counter() - start) * 1000:.2f} ms")
        return result
    return wrapper

@announce
@timed
def slow_greeting(name):
    time.sleep(0.02)
    return f"Hello there, {name}!"
```

- `functools.wraps` keeps the original name. *Checked:* without it the name was `w`, the wrapper's
- Forget `return result` and the wrapped function gives back `None`. *Checked*
- `*args` collects positional arguments; `**kwargs` collects keywords as a dict. *Checked:* `f(1, 2, x=3)` gave `((1, 2), {'x': 3})`
- **Stacking:** the one nearest the function wraps first. *Checked:* the call order was `announce start`, `timed start`, body, `timed end`, `announce end`
- **Why it matters:** the `@tool` decorator ([Chapter 1](01-setup-and-api-basics.md), 1.4) uses this exact pattern

*Source: `classes_summary/02`, `classes_transcription_summary/02`, `_4_decorators.py`.*

## 2.5 Error handling: catch a problem on purpose

- Without handling, one problem stops the program. `10 / 0` raises `ZeroDivisionError`
- `try/except` catches it so you decide what happens

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    result = 0

try:
    age = int("not a number")
except ValueError:
    age = 0
```

Several `except` blocks for several problems:

```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return 0
    except TypeError:
        return 0

print(safe_divide(10, 2), safe_divide(10, 0), safe_divide(10, "x"))   # 5.0 0 0
```

`finally` runs no matter what:

```python
def read_setting(value):
    try:
        return int(value)
    except ValueError:
        print(f"{value!r} isn't a number, defaulting to 0.")
        return 0
    finally:
        print("(Done attempting to read this setting.)")
```

A missing dictionary key raises `KeyError`:

```python
try:
    print(weather_reading["humidity"])
except KeyError:
    print("No humidity data available -- that's fine, we'll skip it.")
```

- *Checked* (`_3_error_handling.py`): the output matches the comments. `5.0 0 0`; `finally` printed after both the good and the bad value
- The summaries list this file only as `try`/`except`/`finally` with a missing key; the examples are from the file

*Source: `_3_error_handling.py`.*

## 2.6 Calling a real API from a function

[Chapter 1](01-setup-and-api-basics.md) made one request. `_5_calling_a_real_api.py` makes the simplest request, prints the status and the parsed dict, then wraps the call in a reusable function:

```python
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | str:
    """Convert `amount` between currencies using real, live ECB rates."""
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": from_currency.upper(), "symbols": to_currency.upper()},
            timeout=10,
        )
        response.raise_for_status()
        rate = response.json()["rates"][to_currency.upper()]
        return round(amount * rate, 2)
    except requests.exceptions.RequestException as exc:
        return f"Couldn't reach the currency service: {exc}"
    except KeyError:
        return f"No rate available for {from_currency} -> {to_currency}"
```

- Two `except` blocks: the network or server fails (`RequestException`), or there is no rate for the pair (`KeyError`)
- The file calls it with `(100, "USD", "INR")`, `(5000, "INR", "JPY")` and a bad pair `(50, "USD", "ZZZ")`
- It ends by noting this function still knows nothing about AI
- **Two URL forms in the course:** Chapter 1's `currency.py` uses `api.frankfurter.app` (`from`, `to`, `amount`). This file uses `api.frankfurter.dev/v1` (`base`, `symbols`) and multiplies by the rate itself. Which is current was not checked, and neither could be run here

*Source: `_5_calling_a_real_api.py`.*

## 2.7 The problem: Python does not enforce types

```python
def create_user(name, age): ...

create_user("Mayank", 25)   # fine
create_user(25, "Mayank")   # allowed, no error
```

- The bad value breaks things later, in a database, spreadsheet or API
- Hand-written `isinstance()` checks work for one function, not ten (`create_user`, `update_user`, `delete_user`...)
- Pydantic solves it: [Why Pydantic, and BaseModel](../pydantic/01-why-pydantic-and-basemodel.md)

*Source: `classes_summary/02`, `classes_transcription_summary/02`.*

## 2.8 The class 02-03 code folder

15 numbered files, from basics to an agent with memory. Run in this order:

| File | Covers | In these notes |
|---|---|---|
| `_0_basics_refresher.py` | Class 01 recap | 2.1 |
| `_1_data_structures.py` | Lists, dicts, tuples, list of dicts | 2.1 |
| `_2_oop_classes.py` | `BankAccount` and `Book` | 2.2, 2.3 |
| `_3_error_handling.py` | `try/except` | 2.5 |
| `_4_decorators.py` | The wrapper pattern, stacked | 2.4 |
| `_5_calling_a_real_api.py` | `requests`, real conversion | 2.6 |
| `_6_fake_ai_call.py` | The OpenAI-style shape with no dependencies | [Chapter 3](03-anatomy-of-an-agent.md), 3.4 |
| `_7_ai_call_free_and_paid.py` | Groq, OpenRouter (free), OpenAI (paid) | Chapter 3, 3.4 |
| `_8_pydantic_with_ai.py` | BaseModel, Field, validators, nested, LLM output | [Pydantic book](../pydantic/05-validating-llm-output.md) |
| `_9_api_call_with_structure.py` | The `_5` call, validated | [Pydantic Ch 5](../pydantic/05-validating-llm-output.md), 5.2 |
| `_10_tool_with_ai_call.py` | A validated tool beside an AI call | Pydantic Ch 5, 5.3 |
| `_11` to `_14` | Agent with brain only, one tool, three tools, memory | Chapter 3, 3.7 |

```bash
uv add requests pydantic python-dotenv
uv add openai        # optional, for real AI calls; every file falls back without it
cp .env.example .env     # paste a free Groq and/or OpenRouter key
uv run _0_basics_refresher.py
```

Notes from the folder's README:

- Filenames start with an underscore (`_0_`) because Python cannot `import` a file that starts with a bare digit. The underscore sorts the same and stays importable
- Every file is self-contained. Later files re-declare earlier patterns instead of importing across the chain (one exception: `_6_fake_ai_call` is imported)
- The folder's rule: if you cannot point to which earlier file taught a pattern, it does not belong yet
- `_5`, `_7`, `_9`, `_10`, `_12`, `_13` and `_14` make real network calls. The README says its author tested request building, parsing and validation with mocked responses (the build environment blocked those domains), and advises running each once for real

*Source: the folder's `README.md`.*

## 2.9 Interview corner

**Q1. List or tuple? Dict or list?**
- List: changeable, ordered. Tuple: fixed. Dict: values by key. A list of dicts is the shape of chat messages and tool results

**Q2. Why does a dataclass reject `tags: list = []`?**
- A mutable default would be shared by all instances. Use `field(default_factory=list)`

**Q3. Dataclass or Pydantic model?**
- A dataclass has no run-time checks. Pydantic validates. Use it at the edges: APIs, LLM output

**Q4. What does `functools.wraps` do?**
- Copies the original function's name and docstring onto the wrapper, which frameworks read

**Q5. What are `*args` and `**kwargs`?**
- Collect positional and keyword arguments so a wrapper can pass any call through

**Q6. In what order do stacked decorators run?**
- Applied bottom up; called outside in. The top decorator's "before" runs first, its "after" last

**Q7. `try/except/else/finally`: what does `finally` guarantee?**
- It runs whether or not an error happened, even with a `return` in the `try`

**Q8. What is a guard clause?**
- An early check that rejects bad input before it changes state

**Q9. Why does Python need Pydantic?**
- Hints are not enforced, so bad values flow on silently

## 2.10 Added by Claude, not from the sources

- **Mutable default arguments bite in functions too.** *Checked:* `def bad(x, acc=[])` gave `[1, 2]` for both calls, because the list is shared. Use `None` and create a new list inside
- **Catch the exception you expect.** A bare `except:` hides bugs. The files catch named errors
- **`dict.get` for optional keys; `[]` for required ones.** The first returns `None`, the second raises `KeyError`, which is what you want for a key that must be there
- **A dict key lookup that fails in a tool** is better returned as a message than raised, so the model can read it ([LLM Ch 2](../llm/02-the-agentic-loop-in-pure-python.md))
- **Test files from the code folder in order,** and compare each output with the comments. All of `_0` to `_4` matched

## Recap

- Lists, tuples, dicts and lists of dicts carry all the data in an agent
- A class holds state; a guard clause protects it
- Dataclass removes boilerplate but not bad data
- A decorator wraps behaviour; use `functools.wraps` and return the result
- `try/except/finally` handles expected failures
- Python does not enforce types: that is Pydantic's job

## Practice

1. Rebuild `BankAccount` from scratch without copying
2. Write a `@dataclass` and trigger the mutable-default error on purpose
3. Write a decorator with `functools.wraps`, then stack two on one function
4. Catch `KeyError` and `ValueError` separately and use `finally` once
5. Run `_0` to `_4` in order and match each output to this chapter
6. Fix `def bad(x, acc=[])`

## How this chapter was checked

- **Run:** `_0`, `_1`, `_2`, `_3`, `_4` (outputs match); the dataclass mutable default and `banana`; decorator order, missing `wraps`, missing `return`; `*args`/`**kwargs`; tuple immutability; slicing and a mixed list; the shared default list
- **Not run:** `_5`, `_9`, `_10`, `_12` to `_14` against the live API (no network); the notebook `Python_run.ipynb`
- **Rewritten** from the earlier chapter; the class summaries were not re-opened in this pass

## Sources and further reading

- Live-Class-2026, `classes_summary/02 - 28 Jun - Python Refresher.md`
- Live-Class-2026, `classes_transcription_summary/02 - 28 June - Python Refresher.md`
- Live-Class-2026, code folder `Weekend 01 - 27-28 Jun/02-03 - 28 Jun & 4 Jul - Python Refresher & Pydantic Deep Dive/`: `_0` to `_5`, `Python_run.ipynb` and the folder `README.md`

Previous: [Chapter 1](01-setup-and-api-basics.md) · Next: [Chapter 3, Anatomy of an agent](03-anatomy-of-an-agent.md)
