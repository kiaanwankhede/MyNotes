# Chapter 3: Pydantic deep dive

Pydantic checks data at run time. It sits between "something produced some data" (a user, an API, an LLM) and "my code is allowed to trust it".

## 3.1 Why Pydantic exists

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

## 3.2 `BaseModel`: the shape you are willing to trust

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

## 3.3 `Field()`: validating the value, not only the type

Type validation says what kind of data arrived. Data validation says whether the value makes sense. An age of 1000 is a valid `int` but not a valid age.

```python
class BoundedAmount(BaseModel):
    amount: float = Field(gt=0, description="Must be positive")
    currency: str = Field(min_length=3, max_length=3)

BoundedAmount(amount=-50, currency="USD")   # type is fine, value is not: rejected
```

Another example from class, with length and range limits:

```python
class JobApplication(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    years_experience: int = Field(gt=0, le=50)
    portfolio_url: str
```

Two equivalent syntaxes exist: plain `Field(...)` and `Annotated[...]`. The mentor prefers plain `Field()` for readability but warns that AI-generated code often uses `Annotated`, so learn to read both.

### Built-in special types

These save you writing your own regular expressions:

- `EmailStr` checks for a valid email (needs the `email-validator` package).
- `HttpUrl` checks for a valid URL.
- `SecretStr` masks sensitive values such as API keys and passwords in logs and printed output. It is easy to overlook, and it matters here because you will handle API keys constantly.

*Source: `classes_summary/03`, `classes_transcription_summary/03`.*

## 3.4 `field_validator` and `model_validator`

A `field_validator` adds a custom rule for one field. It uses the same decorator idea as Chapter 2:

```python
KNOWN_CURRENCIES = {"USD", "INR", "EUR", "GBP", "JPY"}

class StrictAmount(BaseModel):
    amount: float = Field(gt=0)
    currency: str

    @field_validator("currency")
    @classmethod
    def must_be_known(cls, value: str) -> str:
        value = value.upper().strip()
        if value not in KNOWN_CURRENCIES:
            raise ValueError(f"{value!r} isn't a recognized currency: {KNOWN_CURRENCIES}")
        return value

normalized = StrictAmount(amount=100, currency="usd")   # "usd" becomes "USD"
```

A validator can both reject and **clean** a value (here it upper-cases and trims).

A `field_validator` sees one field at a time, so it cannot enforce a rule that spans two fields. The class example: someone applying with an `@infosys.com` email must have at least 5 years of experience. Neither validator alone can see both values. A `model_validator` sees the whole model:

```python
from pydantic import field_validator, model_validator

class SignupForm(BaseModel):
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def check_length(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
```

**Order is fixed:** every `field_validator` runs first, then the `model_validator` runs on the fully validated object. There is no point cross-checking fields that have not passed their own checks. I ran the `model_validator` and it rejected mismatched passwords.

Question from the class: should a `field_validator` be a `@staticmethod`? It can technically be, but stay with `@classmethod` plus `@field_validator` for consistency.

*Source: `classes_summary/03`, `classes_transcription_summary/03`.*

## 3.5 Nested models and inheritance

A model can contain another model as a field type. This mirrors nested JSON, which is the shape of most API payloads and LLM structured outputs.

```python
class ConversionRequest(BaseModel):
    source: StrictAmount
    target_currency: str

request = ConversionRequest(source={"amount": 250, "currency": "eur"}, target_currency="GBP")
print(f"{request.source.amount} {request.source.currency} -> {request.target_currency}")
```

Note that a plain dictionary is accepted for the inner model and is validated (and `"eur"` is cleaned to `"EUR"`). Normal Python inheritance also works: a model that inherits another keeps its fields and validators.

*Source: `classes_summary/03`, `classes_transcription_summary/03`.*

## 3.6 The use that matters most: validating an LLM's raw text

```python
llm_clean_output = '{"amount": 300, "currency": "usd"}'
print(StrictAmount.model_validate_json(llm_clean_output))       # works cleanly

llm_messy_output = '{"amount": "a few hundred", "currency": "dollars"}'
try:
    StrictAmount.model_validate_json(llm_messy_output)
except ValidationError as exc:
    print(f"Caught before it could break anything downstream:\n{exc}")
```

`model_validate_json` is the whole bridge between "an LLM said something" and "my code can trust it". I ran this with both inputs: the clean one is accepted and the messy one is rejected.

Pydantic models also define the request and response shapes of the FastAPI servers built later, and structured output from LLMs is parsed with them too.

*Source: `classes_summary/03`, `classes_transcription_summary/02` (Q&A).*

## 3.7 The code folder for this class

| File | What it covers |
|---|---|
| `_5_calling_a_real_api.py` | The Frankfurter API in a reusable function with error handling |
| `_6_fake_ai_call.py` | A no-dependency stand-in shaped like an OpenAI-style client: `.chat.completions.create(...).choices[0].message.content` |
| `_7_ai_call_free_and_paid.py` | Real calls to Groq, OpenRouter (`model="openrouter/free"` routes automatically) and OpenAI |
| `_8_pydantic_with_ai.py` | The full Pydantic walkthrough above |
| `_9_api_call_with_structure.py` | The API call from `_5`, now validated by Pydantic |
| `_10_tool_with_ai_call.py` | The `@tool` decorator used for real: a validated `convert_currency` tool sitting beside an AI call, not yet connected to it |
| `8_Pydantic/` | A standalone mini project: `BaseModel`, `EmailStr`, typed lists and dicts |

Note for next chapter: the tool and the AI call in `_10` both work, but neither knows the other exists. Connecting them is Chapter 4.

*Where the AI vocabulary went:* the class also taught five terms (LLM, tokens, vector embeddings, context window, parameters). They are in the LLM book: see [Inside the model](../llm/03-inside-the-model.md).

## Practice

1. Define a `BaseModel` with `Field()` limits from memory.
2. Write a `field_validator` and a `model_validator`, and say why each exists.
3. Nest one model inside another.
4. Run `_10_tool_with_ai_call.py` and check that tool and AI call are separate.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/02` for the dataclass-versus-Pydantic comparison
- Live-Class-2026, code folder `Weekend 01 - 27-28 Jun/02-03 - 28 Jun & 4 Jul - Python Refresher & Pydantic Deep Dive/`

Previous: [Chapter 2](02-python-refresher.md) · Next: [Chapter 4, Anatomy of an agent](04-anatomy-of-an-agent.md)
