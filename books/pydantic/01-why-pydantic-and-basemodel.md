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

*Source: `classes_summary/03`, `classes_transcription_summary/03`, code file `_8_pydantic_with_ai.py`.*

## Practice

1. Explain, with the plain-class, dataclass and `BaseModel` demo, why only `BaseModel` rejects `age="banana"`.
2. Predict what happens for `age` set to `"28"`, `"28eight"` and `28.5`.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`

Previous: [Python book, Chapter 2](../python/02-python-refresher.md) · Next: [Chapter 2](02-field-and-special-types.md)
