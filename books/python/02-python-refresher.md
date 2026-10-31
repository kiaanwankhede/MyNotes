# Chapter 2: Python refresher

Variables and lists, classes, dataclasses, and decorators. Each is shown because agents lean on it later, and the chapter ends with the problem that Chapter 3 solves.

## 2.1 Quick refresher: types, f-strings, control flow and lists

Variables hold `str`, `float` and `bool` values, f-strings embed them in text, and `if/else` makes decisions. Lists add append and slicing.

Indexing works from both ends. For `["Tokyo", "Delhi", "London"]`:

| Index | 0 | 1 | 2 |
|---|---|---|---|
| Value | Tokyo | Delhi | London |
| Negative index | -3 | -2 | -1 |

The code file `_1_data_structures.py` also covers tuple unpacking and dictionaries. The pattern that matters most later is a **list of dicts**, because tool results and chat messages take that shape.

*Source: `classes_summary/02`, `classes_transcription_summary/02`, code files `_0_basics_refresher.py` and `_1_data_structures.py`. The code files were not opened in this batch, so only what the summaries say about them is recorded.*

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

account_1 = BankAccount(owner="Mayank", balance=1000)
account_2 = BankAccount(owner="Krish", balance=500)
account_1.deposit(200)
account_2.withdraw(1000)   # too much on purpose: the guard clause rejects it
```

- `self` means "this particular object".
- `__init__` runs when the object is created and sets starting values (here `balance=0` unless given).
- The `if amount > self.balance` check is a **guard clause**: reject a bad request instead of letting it corrupt state. Agents need the same habit.

*Source: `classes_summary/02`, `classes_transcription_summary/02`, code file `_2_oop_classes.py`.*

## 2.3 Dataclasses: no boilerplate

`@dataclass` writes `__init__` for you from type-hinted fields. The idea is the same blueprint, written shorter. Java developers can compare it to Lombok.

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

my_book = Book(title="Atomic Habits", author="James Clear")
my_book.read(40)
```

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

## 2.5 The problem: Python does not enforce types

Python is dynamically typed. It never enforces that `name` is a string or `age` an integer, even if you write type hints:

```python
def create_user(name, age): ...

create_user("Mayank", 25)   # fine
create_user(25, "Mayank")   # Python allows this with no error
```

The bad value then breaks things further along, in a database, a spreadsheet or an API. Adding `isinstance()` checks by hand works for one function but not for ten (`create_user`, `update_user`, `delete_user` and so on). Pydantic solves this, and it has its own book: start at [Why Pydantic, and BaseModel](../pydantic/01-why-pydantic-and-basemodel.md).

*Source: `classes_summary/02`, `classes_transcription_summary/02`.*

## Practice

1. Rebuild `BankAccount` from scratch without copying.
2. Write a `@dataclass` and trigger the mutable-default error on purpose.
3. Write a decorator with `functools.wraps`, then stack two on one function.
4. Read about `*args` and `**kwargs`.

## Sources and further reading

- Live-Class-2026, `classes_summary/02 - 28 Jun - Python Refresher.md`
- Live-Class-2026, `classes_transcription_summary/02 - 28 June - Python Refresher.md`
- Live-Class-2026, code folder `Weekend 01 - 27-28 Jun/02-03 - 28 Jun & 4 Jul - Python Refresher & Pydantic Deep Dive/`

Previous: [Chapter 1](01-setup-and-api-basics.md) · Next: [Chapter 3, Anatomy of an agent](03-anatomy-of-an-agent.md) (Pydantic has its own book: [Why Pydantic](../pydantic/01-why-pydantic-and-basemodel.md))
