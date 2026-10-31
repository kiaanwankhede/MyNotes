# Chapter 1: Why Pydantic, and `BaseModel`

Pydantic checks data at run time. It sits between "something produced some data" (a user, an API, an LLM) and "my code is allowed to trust it". Read Python Chapter 2 first for dataclasses and the typing problem.

## 1.1 Why Pydantic exists

In languages such as Java and C++, a declared type reserves memory and is enforced. Python variables are names pointing at values, so a name can be re-pointed from an `int` to a `str` to a `list` with no complaint. That is friendly for learning and dangerous in production, where real users, bad input and downstream systems meet. A wrong type silently flows on until something breaks far away.

Pydantic is one of the most downloaded packages on PyPI and is used by major SDKs, including the OpenAI and Anthropic ones. The mentor's argument for learning it even though AI can write the code: if you do not understand it, you cannot debug or trust what the AI hands you.

*Source: `classes_transcription_summary/03` (this section); `classes_summary/03` (the failure shown first in code).*

### Three ways to define a blueprint

| Approach | Type checking |
|---|---|
| Plain class with your own `__init__` | None |
| `@dataclass` | None (it only removes boilerplate) |
| Pydantic `BaseModel` | Full, on every field, automatically |

In the live demo the plain class and the dataclass both accepted `age="banana"`. Only `BaseModel` raised an error immediately.

| Dataclass | Pydantic `BaseModel` |
|---|---|
| Removes boilerplate only | Removes boilerplate and validates |
| Nothing enforced at run time | Raises `ValidationError` on bad input |
| Fine for simple internal structures | Essential for API inputs and outputs and for agent tool schemas |

### The problem in plain Python

Python does not check types. The notebook `Pydantic_From_Scratch.ipynb` shows this step by step. First a function with nothing telling Python what its parameters should be:

```python
def register_user(name, email, age):
    """Registers a user and calculates the year they were born."""
    birth_year = 2026 - age  # this line silently assumes `age` is an int
    print(f"Registered {name} ({email}), born approx. {birth_year}")

register_user("Aditi", "aditi@example.com", 28)      # Registered Aditi ..., born approx. 1998
register_user("Rohan", "rohan@example.com", 10000)   # Registered Rohan ..., born approx. -7974
```

Nothing stops the caller passing garbage. The second call is a valid integer but not a sensible age, which is the difference between **type validation** and **data validation** (Chapter 2). I ran both calls and got the outputs in the comments.

**Type hints are not enforced.** The notebook also annotates variables:

```python
name: str = "Aditi"
age: int = 28
tags: list[str] = ["python", "pydantic", "fastapi"]
quantities: list[int] = [1, 5, 3, 2]
word_counts: dict[str, int] = {"error": 12, "warning": 5}
settings: dict[str, str] = {"theme": "dark", "language": "en"}

age: int = "twenty-eight"   # Python accepts this; `age` is now the string
```

The file `1. Why Pydantic.py` shows the same typed lists and dictionaries (`list[str]`, `list[int]`, `dict[str, int]`, `dict[str, str]`) and ends with `from pydantic import BaseModel, EmailStr`. The hints describe what you intend. Only a Pydantic model checks them.

The notebook then shows a plain class (`FormData`) accepting a number as a name, and a dataclass accepting `"gadfa"` as an email and `4214` as an age, before the Pydantic version that rejects bad data.

*Source: `Pydantic_From_Scratch.ipynb` (cells on `register_user`, annotations and plain class vs dataclass) and `1. Why Pydantic.py`.*

## 1.2 `BaseModel`: the shape you are willing to trust

The class opened with the actual failure that Pydantic catches, a messy LLM reply such as `{"amount": "five hundred", "currency": "us dollars"}`. "Five hundred" cannot be used in maths and "us dollars" is not a currency code.

```python
from pydantic import BaseModel, Field, field_validator, ValidationError

class CurrencyAmount(BaseModel):
    amount: float
    currency: str

good = CurrencyAmount(amount=100, currency="USD")            # fine

try:
    CurrencyAmount(amount="five hundred", currency="USD")    # ValidationError, instantly
except ValidationError as exc:
    print(exc)

coerced = CurrencyAmount(amount="100", currency="USD")       # "100" (str) becomes 100.0 (float)
```

### Optional fields and defaults

A field with a default becomes optional. Every other field is required. If you do not know the right default, use `None` (Python has no `null`).

```python
class SignupForm(BaseModel):
    name: str
    age: int
    is_interested: bool = False       # default makes it optional
    nationality: str | None = None    # unknown default: use None
```

### Type coercion

Pydantic forgives a reasonable mismatch but refuses ambiguous or lossy ones. I ran these checks on an `age: int` field:

| Input | Result |
|---|---|
| `"28"` | Converted to `28` |
| `"28eight"` | `ValidationError` |
| `28.5` | `ValidationError` (a float with a fraction is too lossy to guess) |

### Required fields, `bool` coercion and `model_dump`

More behaviour from the notebook, which I ran:

```python
class SignupForm(BaseModel):
    username: str
    email: str
    age: int
    newsletter_opt_in: bool = False     # has a default, so it is optional

SignupForm(username="aditi28", email="aditi@example.com", age=28, newsletter_opt_in="True")
# newsletter_opt_in=True       the string "True" is coerced to a real bool

SignupForm(username="Mayank")
# ValidationError: `email` and `age` are required (error type: missing)

user = SignupForm(username="a", email="a@example.com", age="28")
user.model_dump()
# {'username': 'a', 'email': 'a@example.com', 'age': 28, 'newsletter_opt_in': False}
```

- A missing required field is an error, not a default.
- `model_dump()` turns the model back into a plain dictionary, already cleaned (`"28"` is now `28`).
- With no `Field()` limits, a huge value such as `age=100000` is accepted. The notebook shows this, which leads into Chapter 2.

*Source: `Pydantic_From_Scratch.ipynb` (optional vs mandatory, coercion and `model_dump` cells).*

### The mini-project folder

The standalone folder `8_Pydantic/` is a `uv` project:

| File | What it is |
|---|---|
| `1. Why Pydantic.py` | The motivating problem: typed lists and dicts |
| `Pydantic_From_Scratch.ipynb` | The step-by-step build used in this book |
| `main.py` | A "Hello from 8-pydantic!" scaffold with no Pydantic in it |
| `test.ipynb` | Two empty cells |

```bash
uv sync
uv run main.py
```

*Source: the folder's `README.md`, `main.py` and `test.ipynb`.*

## Practice

1. Explain, with the plain-class, dataclass and `BaseModel` demo, why only `BaseModel` rejects `age="banana"`.
2. Predict what happens for `age` set to `"28"`, `"28eight"` and `28.5`.
3. Write `register_user` with a `BaseModel` so that `age=10000` is rejected (you will need Chapter 2).

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, code folder `.../02-03 - 28 Jun & 4 Jul - .../8_Pydantic/` (all five files)

Previous: [Python book, Chapter 2](../python/02-python-refresher.md) · Next: [Chapter 2](02-field-and-special-types.md)
