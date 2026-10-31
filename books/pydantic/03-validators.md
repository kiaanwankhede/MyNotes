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

## 3.2 A validator on real data: rejecting disposable emails

The notebook builds an application form whose email validator blocks throwaway domains and cleans the rest:

```python
class JobApplication(BaseModel):
    full_name: str
    email: EmailStr
    years_experience: int = 0

    @field_validator("email")
    @classmethod
    def reject_disposable_domains(cls, value: str) -> str:
        blocked_domain = {"yopmail.com", "tempmail.com", "mailinator.com"}
        user_domain = value.split("@")[-1].lower()
        if user_domain in blocked_domain:
            raise ValueError(f"disposable email domains are not accepted ({user_domain})")
        return value.lower()
```

`value.split("@")[-1]` takes the part after the last `@`. The validator returns the lower-cased email, so it cleans as well as checks. I ran the same rule on a plain `str` field: `"Rohan@Example.COM"` became `"rohan@example.com"`, and `"rohan@yopmail.com"` was rejected with the message above. The notebook's next cell then builds an application with `rohan@yopmail.com` and prints "Valid:"; that cell has no recorded output, and by this rule it would be rejected.

*Source: `Pydantic_From_Scratch.ipynb` (`reject_disposable_domains` cell).*

### Pitfalls in the notebook's `SignupForm`

The notebook's password form (two `field_validator`s plus a `model_validator` that checks the passwords match) shows two traps. I ran both.

1. **Two methods with the same name.** The notebook defines `reject_disposable_domains` twice, once for `password` and once for `confirm_password`. The second silently replaces the first, and Pydantic prints a warning saying it overrides an existing validator (visible in the notebook's own output). In my test, with the same mistake, a 3-letter password was accepted. Give every validator its own name.
2. **`raise ValidationError`.** The notebook raises `ValidationError` for a short password. That cannot work: it fails with a `TypeError`. Inside a validator, raise `ValueError` and Pydantic turns it into a validation error.

*Source: `Pydantic_From_Scratch.ipynb` (`SignupForm` cell and its warning output).*

## 3.3 Computed fields

A `@computed_field` on a property adds a value worked out from other fields. It appears when you print the model and in `model_dump()`:

```python
from pydantic import BaseModel, computed_field

class JobApplication(BaseModel):
    full_name: str
    years_experience: int

    @computed_field
    @property
    def experience_tier(self) -> str:
        if self.years_experience < 2:
            return "junior"
        elif self.years_experience < 7:
            return "mid"
        return "senior"

app = JobApplication(full_name="Aditi Sharma", years_experience=6)
print(app)   # full_name='Aditi Sharma' years_experience=6 experience_tier='mid'
```

I ran it: 1 year gives `junior`, 2 and 6 give `mid`, 7 gives `senior`, and `model_dump()` includes `experience_tier`.

*Source: `Pydantic_From_Scratch.ipynb` (`computed_field` cells).*

## Practice

1. Write a `field_validator` and a `model_validator` from memory, and say why each exists.
2. Add a password-match rule and check the order the validators run in.
3. Write two validators with the same method name, see the warning, and fix it.
4. Add a `computed_field` to a model and look at it in `model_dump()`.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, notebook `8_Pydantic/Pydantic_From_Scratch.ipynb`

Previous: [Chapter 2](02-field-and-special-types.md) · Next: [Chapter 4](04-nested-models-and-inheritance.md)
