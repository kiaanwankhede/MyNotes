# Chapter 1: Why Pydantic, and `BaseModel`

**After this chapter you can:**

- Say why Python type hints do not protect you, and what Pydantic adds
- Tell a plain class, a dataclass and a `BaseModel` apart by what each checks
- Predict how Pydantic converts or rejects `"28"`, `"28eight"`, `28.5` and `"True"`
- Read a `ValidationError` and use `model_dump()`

**Builds on:** [Python Ch 2](../python/02-python-refresher.md) (dataclasses and the typing problem).

Pydantic checks data at run time. It sits between "something produced data" (a user, an API, an LLM) and "my code may trust it".

## 1.1 Why Pydantic exists

- In Java or C++, a declared type is enforced. In Python a name can be re-pointed from `int` to `str` to `list` without complaint
- Friendly for learning. Dangerous in production, where bad input meets downstream systems
- A wrong type flows on silently until something breaks far away
- Pydantic is one of the most downloaded packages on PyPI. The OpenAI and Anthropic SDKs use it
- Mentor's argument for learning it even though AI can write the code: if you do not understand it, you cannot debug or trust what the AI hands you

*Source: Live-Class-2026, `classes_transcription_summary/03`; `classes_summary/03`.*

### Three ways to define a blueprint

| Approach | Type checking |
|---|---|
| Plain class with your own `__init__` | None |
| `@dataclass` | None (it only removes boilerplate) |
| Pydantic `BaseModel` | Full, on every field, automatically |

- *Checked:* the plain class and the dataclass both accepted `age="banana"`. Only `BaseModel` raised
- The class slide uses a paper customs-declaration form: fields (`Name: str`, `PassportNumber: str`) are the blueprint. The three approaches differ in whether anyone checks the boxes
- The slide marks `BaseModel` as the one to master. Loose typing in Python and JavaScript becomes a big problem in production
- The slide also maps validators to fields: `email` needs a validator or `EmailStr`; years of experience needs a validator or a `Field()` limit
- Editors show the type when you hover a variable, for example `settings: dict[str, str]`

*Source: `Class-3-4.pdf` (class 03 whiteboard).*

| Dataclass | Pydantic `BaseModel` |
|---|---|
| Removes boilerplate only | Removes boilerplate and validates |
| Nothing enforced at run time | Raises `ValidationError` on bad input |
| Fine for simple internal structures | Essential for API inputs and outputs and agent tool schemas |

### The problem in plain Python

From `Pydantic_From_Scratch.ipynb`:

```python
def register_user(name, email, age):
    birth_year = 2026 - age        # silently assumes `age` is an int
    print(f"Registered {name} ({email}), born approx. {birth_year}")

register_user("Aditi", "aditi@example.com", 28)      # born approx. 1998
register_user("Rohan", "rohan@example.com", 10000)   # born approx. -7974
```

- Nothing stops garbage. The second call is a valid `int` but not a sensible age
- That is the difference between **type validation** and **data validation** ([Chapter 2](02-field-and-special-types.md))
- I ran both calls and got the outputs in the comments

**Type hints are not enforced:**

```python
age: int = 28
tags: list[str] = ["python", "pydantic", "fastapi"]
word_counts: dict[str, int] = {"error": 12, "warning": 5}
age: int = "twenty-eight"   # Python accepts this; `age` is now a string
```

- `1. Why Pydantic.py` shows the same typed lists and dicts, and ends with `from pydantic import BaseModel, EmailStr`
- Hints describe intent. Only a Pydantic model checks them

*Source: `Pydantic_From_Scratch.ipynb` and `1. Why Pydantic.py`.*

## 1.2 `BaseModel`: the shape you are willing to trust

The class opened with the failure Pydantic catches: a messy LLM reply such as `{"amount": "five hundred", "currency": "us dollars"}`.

```python
from pydantic import BaseModel, ValidationError

class CurrencyAmount(BaseModel):
    amount: float
    currency: str

good = CurrencyAmount(amount=100, currency="USD")            # fine
CurrencyAmount(amount="five hundred", currency="USD")        # ValidationError, instantly
CurrencyAmount(amount="100", currency="USD")                 # "100" becomes 100.0
```

### Optional fields and defaults

- A field with a default is optional. Every other field is required
- No known default? Use `None` (Python has no `null`)

```python
class SignupForm(BaseModel):
    name: str
    age: int
    is_interested: bool = False       # default makes it optional
    nationality: str | None = None    # unknown default: use None
```

### Type coercion

Pydantic forgives a reasonable mismatch and refuses a lossy or ambiguous one. *Checked* on an `age: int` field (Pydantic 2.12.5):

| Input | Result |
|---|---|
| `"28"` | `28` |
| `"28.0"` or `28.0` | `28` |
| `"28eight"` | `ValidationError` |
| `28.5` | `ValidationError` (a fraction is too lossy to guess) |
| `True` | `1` (see 1.5) |

### Required fields, `bool` coercion and `model_dump`

```python
class SignupForm(BaseModel):
    username: str
    email: str
    age: int
    newsletter_opt_in: bool = False

SignupForm(username="aditi28", email="a@e.com", age=28, newsletter_opt_in="True")
# newsletter_opt_in=True       the string "True" becomes a real bool

SignupForm(username="Mayank")
# ValidationError: email and age are missing (error type: missing)

SignupForm(username="a", email="a@e.com", age="28").model_dump()
# {'username': 'a', 'email': 'a@e.com', 'age': 28, 'newsletter_opt_in': False}
```

- A missing required field is an error, not a default
- `model_dump()` gives a plain dict, already cleaned (`"28"` is now `28`)
- With no `Field()` limits, `age=100000` is accepted (leads into Chapter 2)

*Source: `Pydantic_From_Scratch.ipynb` (optional vs mandatory, coercion, `model_dump`).*

### The mini-project folder

`8_Pydantic/` is a `uv` project:

| File | What it is |
|---|---|
| `1. Why Pydantic.py` | The motivating problem: typed lists and dicts |
| `Pydantic_From_Scratch.ipynb` | The step-by-step build used in this book |
| `main.py` | A "Hello from 8-pydantic!" scaffold with no Pydantic |
| `test.ipynb` | Two empty cells |

```bash
uv sync
uv run main.py
```

*Source: the folder's `README.md`, `main.py`, `test.ipynb`.*

## 1.3 Interview corner

**Q1. Why does Python need Pydantic if it has type hints?**
- Hints are not enforced at run time. Pydantic checks them when the object is created

**Q2. Dataclass or `BaseModel`?**
- A dataclass only removes boilerplate. `BaseModel` also validates and raises `ValidationError`. Use it at the edges: APIs, LLM output, tool arguments

**Q3. What is the difference between type validation and data validation?**
- Type: is it an `int`? Data: does the value make sense (age 10000)? `Field()` and validators do the second

**Q4. What does Pydantic do with `"28"` for an `int` field?**
- Converts it. It rejects `"28eight"` and `28.5`

**Q5. Required or optional?**
- A field with a default (or `None`) is optional. All others are required

**Q6. How do you turn a model back into a dict or JSON?**
- `model_dump()` for a dict, `model_dump_json()` for a JSON string

**Q7. How do you validate a dict or a JSON string?**
- `Model(**data)` or `Model.model_validate(data)`; `Model.model_validate_json(text)` for raw JSON

**Q8. Why do agent frameworks lean on Pydantic?**
- Tool arguments and structured replies come from a model. They must be checked before use ([Chapter 5](05-validating-llm-output.md))

## 1.4 Added by Claude, not from the sources

All *checked* with Pydantic 2.12.5.

- **Unknown keys are ignored by default.** `Form(..., color="red")` worked and dropped `color`. Use `ConfigDict(extra="forbid")` to reject it
- **Assignment is not validated by default.** After `m.age = "banana"`, `m.age` was `'banana'`. Set `validate_assignment=True` to check assignments
- **Strict mode stops coercion.** With `ConfigDict(strict=True)`, `age="28"` was rejected
- **JSON schema comes free.** `BM.model_json_schema()` returned `properties` and `required`. This is how tools and structured output get their schemas
- **Surprising coercions:** `"yes"` became `True` for a `bool` field; `"maybe"` was rejected. `True` became `1` for an `int` field. Use strict mode if that matters
- **`model_dump_json()`** gives a JSON string directly, with cleaned values

## 1.5 Recap

- Python hints are not enforced. `BaseModel` checks every field when you create the object
- Plain class and dataclass: no checks. `BaseModel`: full checks
- Coercion: `"28"` yes, `"28eight"` no, `28.5` no
- Defaults make a field optional. `model_dump()` returns a clean dict
- Extras are ignored and assignment is unchecked unless you configure it

## Practice

1. Show with the plain-class, dataclass and `BaseModel` demo why only `BaseModel` rejects `age="banana"`
2. Predict the result for `age` set to `"28"`, `"28eight"` and `28.5`, then run it
3. Make a model reject unknown keys, then one that validates assignments
4. Write `register_user` with a `BaseModel` so `age=10000` is rejected (you need Chapter 2)

## How this chapter was checked

- **Run** (Pydantic 2.12.5): the plain class, dataclass and model with `"banana"`; six `age` inputs; `bool` coercion; missing fields; `model_dump`; a huge age; unknown keys; strict mode; `extra="forbid"`; assignment with and without `validate_assignment`; the JSON schema; `model_dump_json`
- **Rewritten** from the earlier chapter, built from the class summaries, the whiteboard and the notebook. I did not re-open those in this pass
- **Not run:** `uv sync` and `main.py` in the mini-project folder

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, code folder `.../02-03 - 28 Jun & 4 Jul - .../8_Pydantic/` and the whiteboard `Class-3-4.pdf`

Previous: [Python Ch 2](../python/02-python-refresher.md) · Next: [Chapter 2](02-field-and-special-types.md)
