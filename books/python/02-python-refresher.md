# Chapter 2: Python refresher

Variables and lists, classes, dataclasses, and decorators. Each is shown because agents lean on it later, and the chapter ends with the problem that Chapter 3 solves.

## 2.1 Quick refresher: types, f-strings, control flow and data structures

The first five code files (`_0` to `_4`) are plain Python with no AI in them. The class presents them as skills worth having on their own.

### Types, f-strings and decisions

Variables hold `str`, `float` and `bool` values, and f-strings embed them in text. `if` can chain with `elif`, and comparisons and `and` build conditions:

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

I ran `_0_basics_refresher.py`: with 22.5 it prints "A light jacket should be enough.", then `True True False`, then "Ready to board."

*Source: code file `_0_basics_refresher.py`.*

### Lists

A list is an ordered, changeable collection. Indexing works from both ends. For `["Tokyo", "Delhi", "London"]`:

| Index | 0 | 1 | 2 |
|---|---|---|---|
| Value | Tokyo | Delhi | London |
| Negative index | -3 | -2 | -1 |

```python
cities = ["Tokyo", "Delhi", "London"]
print(cities[0])          # indexing: first item
print(cities[-1])         # negative indexing: last item
print(cities[0:2])        # slicing: a sub-list  ->  ['Tokyo', 'Delhi']
cities.append("Paris")    # add to the end

for city in cities:
    print(f"Visiting {city}")
```

A list can mix types. The class notebook `Python_run.ipynb` uses `["Tokyo", "Delhi", "London", 1]` and the list accepts the number without complaint. The notebook also has a note to compare arrays and lists in a table, but that is only a comment with nothing written under it, so this book does not make the comparison.

*Source: `classes_summary/02`, `classes_transcription_summary/02`, code files `_1_data_structures.py` and `Python_run.ipynb`.*

### Tuples

A tuple is like a list that cannot be changed after it is created. **Unpacking** splits it into separate variables:

```python
coordinates = (35.68, 139.69)         # latitude, longitude: a fixed pair
latitude, longitude = coordinates     # unpacking
print(f"Lat: {latitude}, Lon: {longitude}")
```

### Dictionaries

A dictionary holds labelled data and is read by key instead of position.

```python
weather_reading = {
    "city": "Tokyo",
    "temperature_c": 22.5,
    "condition": "partly cloudy",
}
print(weather_reading["city"])          # access by key
print(weather_reading.get("humidity"))  # .get() returns None instead of crashing if the key is missing
weather_reading["humidity"] = 60        # add a new key

for key, value in weather_reading.items():   # loop over keys and values together
    print(f"{key}: {value}")
```

### A list of dictionaries, and a list comprehension

This is the combination that matters most later, because tool results and chat messages take this shape.

```python
readings = [
    {"city": "Tokyo", "temperature_c": 22.5},
    {"city": "Delhi", "temperature_c": 34.0},
    {"city": "London", "temperature_c": 15.0},
]
for reading in readings:
    print(f"{reading['city']}: {reading['temperature_c']}°C")

warm_cities = [r["city"] for r in readings if r["temperature_c"] > 20]   # a list comprehension
print(f"Warm cities: {warm_cities}")     # ['Tokyo', 'Delhi']
```

I ran `_1_data_structures.py` and got the outputs shown in the comments (`None` for the missing key, then the dictionary with `humidity` added, then the warm cities `['Tokyo', 'Delhi']`).

*Source: code file `_1_data_structures.py`.*

## 2.2 Object-oriented Python: a bank account

A class is a blueprint. Each object built from it gets its own data (its **state**). The class was drawn on a whiteboard first, then coded:

```python
class BankAccount:
    """A blueprint for a bank account -- nothing to do with AI."""

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner       # every instance gets its OWN owner
        self.balance = balance   # and its OWN balance -- the account's STATE
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

    def show_history(self) -> None:
        for entry in self.history:
            print(f"  - {entry}")

# Two separate accounts from the same blueprint: each has its own state.
account_1 = BankAccount(owner="Mayank", balance=1000)
account_2 = BankAccount(owner="Krish", balance=500)

account_1.deposit(200)
account_1.withdraw(50)
account_2.withdraw(1000)   # too much on purpose: the guard clause rejects it

print(f"{account_1.owner}'s balance: {account_1.balance}")
account_1.show_history()
```

I ran `_2_oop_classes.py`. The rejected withdrawal prints "Insufficient funds: tried to withdraw 1000, balance is 500". Mayank ends at 1150 with a history of "Deposited 200" and "Withdrew 50". Krish stays at 500 with no history, which shows the two objects do not share state.

- `self` means "this particular object".
- `__init__` runs when the object is created and sets starting values (here `balance=0` unless given).
- The `if amount > self.balance` check is a **guard clause**: reject a bad request instead of letting it corrupt state. Agents need the same habit.

*Source: `classes_summary/02`, `classes_transcription_summary/02`, code file `_2_oop_classes.py`.*

### The OOP outline from class 01

The first class's `OOPS.py` holds only an outline, as comments: classes, objects, inheritance, polymorphism, abstraction, encapsulation. The class summaries explain classes and objects (the `BankAccount` above); they do not explain the other four, so this book does not either yet.

*Source: code file `OOPS.py` (class 01 folder).*

## 2.3 Dataclasses: no boilerplate

`@dataclass` writes `__init__` for you from type-hinted fields. The idea is the same blueprint, written shorter. Java developers can compare it to Lombok.

```python
from dataclasses import dataclass, field

@dataclass
class Book:
    title: str
    author: str
    pages_read: int = 0
    # tags = []                                # the file keeps this wrong version as a comment
    tags: list = field(default_factory=list)   # mutable defaults need default_factory

    def read(self, pages: int) -> None:
        self.pages_read += pages

    def add_tag(self, tag: str) -> None:
        self.tags.append(tag)

my_book = Book(title="Atomic Habits", author="James Clear")
my_book.read(40)
my_book.add_tag("self-help")
print(my_book)   # Book(title='Atomic Habits', author='James Clear', pages_read=40, tags=['self-help'])
```

A dataclass also prints itself in that readable form with no extra code.

**Pitfall 1: mutable defaults.** A list, dict or set default must use `field(default_factory=...)`. A plain `tags: list = []` is rejected by dataclasses, and this is a very common beginner trap.

**Pitfall 2: no validation.** A dataclass does not check types at run time. I confirmed this by building `Book(title="x", pages_read="banana")`: it succeeds and stores the string. The Pydantic book fixes this.

*Source: `classes_summary/02`, `classes_transcription_summary/02`.*

## 2.4 Decorators: wrap a function without changing it

A decorator is gift wrap. The contents (your function) stay the same, but extra behaviour is added around them. It works because functions in Python are first-class objects: you can pass one in and return one out. Writing `@decorator` above a function is shorthand for `func = decorator(func)`.

```python
import functools, time

def announce(func):
    """Announces when a function starts and finishes."""
    @functools.wraps(func)   # keeps func.__name__ for introspection
    def wrapper(*args, **kwargs):
        print(f"Starting {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}.")
        return result
    return wrapper

def timed(func):
    """Prints how long a function took to run."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"{func.__name__} took {elapsed_ms:.2f} ms")
        return result
    return wrapper

@announce
@timed
def slow_greeting(name):
    time.sleep(0.02)
    return f"Hello there, {name}!"
```

Things to remember:

- `functools.wraps` keeps the original name. Without it, tools that inspect the function see `wrapper`.
- Forget the `return result` and the wrapped function gives back `None`.
- `*args` collects positional arguments and `**kwargs` collects keyword arguments as a dictionary. The class listed these as a topic to study further on your own.
- Stacked decorators apply from the bottom up: `@timed` wraps first, then `@announce` wraps that.
- **Why it matters:** the `@tool` decorator for agent tools (Chapter 1.4) uses exactly this pattern.

*Source: `classes_summary/02`, `classes_transcription_summary/02`, code file `_4_decorators.py`.*

## 2.5 Error handling: catch a problem on purpose

Without error handling, one unexpected problem stops the whole program. For example `10 / 0` raises a `ZeroDivisionError`. `try/except` lets you catch the problem and decide what happens instead.

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Can't divide by zero -- using 0 instead.")
    result = 0

try:
    age = int("not a number")
except ValueError:
    print("That wasn't a valid number -- using 0 instead.")
    age = 0
```

Different failure, same shape: name the exception you expect and say what to do.

**More than one possible problem.** Stack several `except` blocks:

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

**`finally` runs no matter what happened:**

```python
def read_setting(value):
    try:
        return int(value)
    except ValueError:
        print(f"{value!r} isn't a number, defaulting to 0.")
        return 0
    finally:
        print("(Done attempting to read this setting.)")

read_setting("42")     # prints only the "Done" line
read_setting("oops")   # prints the "isn't a number" line, then the "Done" line
```

**A missing dictionary key** raises `KeyError`, tying back to the dictionaries above:

```python
weather_reading = {"city": "Tokyo", "temperature_c": 22.5}
try:
    print(weather_reading["humidity"])   # this key doesn't exist
except KeyError:
    print("No humidity data available -- that's fine, we'll skip it.")
```

I ran `_3_error_handling.py` and its output matches the comments above.

*Source: code file `_3_error_handling.py`. The class summaries list this file only as `try`/`except`/`finally` tied to a missing dict key; the examples are from the file.*

## 2.6 Calling a real API from a function

Chapter 1 made one request. The code file `_5_calling_a_real_api.py` makes the simplest request first, prints the status code and the parsed dictionary, and then wraps the call in a reusable function with the error handling from the section above:

```python
import requests

response = requests.get(
    "https://api.frankfurter.dev/v1/latest",
    params={"base": "USD", "symbols": "INR"},
    timeout=10,   # never call a real API with no timeout
)
print("Status code:", response.status_code)
print("Parsed as a dict:", response.json())

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

The two `except` blocks handle two different failures: the network or server failing (`RequestException`) and the service having no rate for the currency pair (`KeyError`). The file calls it with `convert_currency(100, "USD", "INR")`, `convert_currency(5000, "INR", "JPY")` and a deliberately bad pair, `convert_currency(50, "USD", "ZZZ")`. It ends by noting that this function still knows nothing about AI.

**Two URL forms in the course.** Chapter 1's `currency.py` uses `api.frankfurter.app` with `from`, `to` and `amount`. This file uses `api.frankfurter.dev/v1` with `base` and `symbols` and multiplies by the rate itself. Both appear in the repo and I have not checked which is current. I could not run either, because the sandbox has no network.

*Source: code file `_5_calling_a_real_api.py`.*

## 2.7 The problem: Python does not enforce types

Python is dynamically typed. It never enforces that `name` is a string or `age` an integer, even if you write type hints:

```python
def create_user(name, age): ...

create_user("Mayank", 25)   # fine
create_user(25, "Mayank")   # Python allows this with no error
```

The bad value then breaks things further along, in a database, a spreadsheet or an API. Adding `isinstance()` checks by hand works for one function but not for ten (`create_user`, `update_user`, `delete_user` and so on). Pydantic solves this, and it has its own book: start at [Why Pydantic, and BaseModel](../pydantic/01-why-pydantic-and-basemodel.md).

*Source: `classes_summary/02`, `classes_transcription_summary/02`.*

## 2.8 The class 02-03 code folder

The folder `02-03 - 28 Jun & 4 Jul - Python Refresher & Pydantic Deep Dive/` holds 15 numbered files, from basics to an agent that holds memory. Run them in this order:

| File | Covers | Where in these notes |
|---|---|---|
| `_0_basics_refresher.py` | Quick class 01 recap | This chapter, 2.1 |
| `_1_data_structures.py` | Lists, dicts, tuples, list of dicts | This chapter, 2.1 |
| `_2_oop_classes.py` | `BankAccount` and `Book`, no agent | This chapter, 2.2 and 2.3 |
| `_3_error_handling.py` | `try/except` patterns | This chapter, 2.5 |
| `_4_decorators.py` | The wrapper pattern, then stacked | This chapter, 2.4 |
| `_5_calling_a_real_api.py` | `requests`, real currency conversion | This chapter, 2.6 |
| `_6_fake_ai_call.py` | The OpenAI-style shape with no dependencies | Chapter 3, 3.4 |
| `_7_ai_call_free_and_paid.py` | Groq, OpenRouter (free), OpenAI (paid) | Chapter 3, 3.4 |
| `_8_pydantic_with_ai.py` | BaseModel, Field, validators, nested models, LLM output | Pydantic book |
| `_9_api_call_with_structure.py` | The `_5` API call, now validated | Not written up yet |
| `_10_tool_with_ai_call.py` | A validated tool beside an AI call | Not written up yet |
| `_11` to `_14` (agent files) | Agent with brain only, one tool, three tools, memory | Not written up yet |

Setup, using UV from Chapter 1:

```bash
uv add requests pydantic python-dotenv
# optional, for real AI calls (every file falls back automatically without it)
uv add openai
cp .env.example .env     # paste a free Groq and/or OpenRouter key in
uv run _0_basics_refresher.py
```

Notes from the folder's README:

- Filenames start with an underscore (`_0_`, `_1_`) because Python cannot `import` a file that starts with a bare digit. The underscore sorts the same way and stays importable.
- Every file is self-contained and runs on its own. Later files re-declare earlier patterns instead of importing across the whole chain.
- The folder's rule: if you cannot point to which earlier file taught a pattern, it does not belong yet.
- Testing: files `_5`, `_7`, `_9`, `_10`, `_12`, `_13` and `_14` make real network calls. The README says its author tested all request building, response parsing and validation with mocked responses, because the build environment blocked those domains, and advises running each once for real before class.

*Source: the folder's `README.md`.*

## Practice

1. Rebuild `BankAccount` from scratch without copying.
2. Write a `@dataclass` and trigger the mutable-default error on purpose.
3. Write a decorator with `functools.wraps`, then stack two on one function.
4. Read about `*args` and `**kwargs`.
5. Write a function that catches `KeyError` and `ValueError` separately, and use `finally` once.
6. Run `_0` to `_4` in order and match each output to this chapter.

## Sources and further reading

- Live-Class-2026, `classes_summary/02 - 28 Jun - Python Refresher.md`
- Live-Class-2026, `classes_transcription_summary/02 - 28 June - Python Refresher.md`
- Live-Class-2026, code folder `Weekend 01 - 27-28 Jun/02-03 - 28 Jun & 4 Jul - Python Refresher & Pydantic Deep Dive/`: `_0` to `_5`, `Python_run.ipynb` and the folder `README.md`

Previous: [Chapter 1](01-setup-and-api-basics.md) · Next: [Chapter 3, Anatomy of an agent](03-anatomy-of-an-agent.md) (Pydantic has its own book: [Why Pydantic](../pydantic/01-why-pydantic-and-basemodel.md))
