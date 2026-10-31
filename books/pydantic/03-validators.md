# Chapter 3: `field_validator` and `model_validator`

Custom rules: one for a single field, and one for rules that span several fields.

## 3.1 `field_validator` and `model_validator`

A `field_validator` adds a custom rule for one field. It uses the same decorator idea as in the Python book, [Chapter 2](../python/02-python-refresher.md):

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

## Practice

1. Write a `field_validator` and a `model_validator` from memory, and say why each exists.
2. Add a password-match rule and check the order the validators run in.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`

Previous: [Chapter 2](02-field-and-special-types.md) · Next: [Chapter 4](04-nested-models-and-inheritance.md)
