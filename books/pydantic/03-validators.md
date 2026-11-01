# Chapter 3: `field_validator` and `model_validator`

**After this chapter you can:**

- Write a `field_validator` that rejects and cleans one field
- Write a `model_validator` for a rule across fields
- Say the order validators run in
- Avoid two notebook traps: duplicate method names, and `raise ValidationError`
- Add a `computed_field`, and read `ValidationError.errors()`

**Builds on:** [Chapter 2](02-field-and-special-types.md), and decorators in [Python Ch 2](../python/02-python-refresher.md).

## 3.1 `field_validator` and `model_validator`

A `field_validator` adds a custom rule for one field:

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

StrictAmount(amount=100, currency="usd")   # "usd" becomes "USD"
```

- A validator can **reject and clean**. *Checked:* `" usd "` became `USD`; `dollars` was rejected
- It sees **one field**. It cannot enforce a rule across two
- Class example: an `@infosys.com` email needs 5+ years of experience. Neither field validator sees both values

A `model_validator` sees the whole model:

```python
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

**Order**

- Every `field_validator` runs first. The `model_validator` runs on the fully validated object
- *Checked:* with a matching-length password and a mismatch, the order was `field:password`, then `model`
- *Checked:* with a **short** password, the `model_validator` **never ran**. If a field fails, the cross-field check is skipped
- Class question: should a `field_validator` be a `@staticmethod`? Technically it can, but keep `@classmethod` plus `@field_validator`

## 3.2 A validator on real data: rejecting disposable emails

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

- `value.split("@")[-1]` takes the part after the last `@`
- It returns the lower-cased email, so it **cleans as well as checks**
- *Checked:* `rohan@yopmail.com` was rejected; `Rohan@Example.COM` became `rohan@example.com`
- The notebook's next cell builds `rohan@yopmail.com` and prints "Valid:", but that cell has no recorded output. By this rule it would be rejected

*Source: `Pydantic_From_Scratch.ipynb` (`reject_disposable_domains` cell).*

### Two traps in the notebook's `SignupForm`

1. **Two methods with the same name.**
   - The notebook defines `reject_disposable_domains` twice, for `password` and `confirm_password`
   - The second **silently replaces** the first. Pydantic warns (the notebook's own output shows it)
   - *Checked:* with the same mistake, a 3-letter password was accepted. Warning text: "`check` overrides an existing Pydantic `@field_validator` decorator"
   - Give every validator its own name
2. **`raise ValidationError`.**
   - The notebook raises `ValidationError` for a short password. That cannot work
   - *Checked:* it fails with `TypeError` (`ValidationError.__new__() missing ... argument`)
   - Inside a validator, raise `ValueError`. Pydantic turns it into a validation error

*Source: `Pydantic_From_Scratch.ipynb` (`SignupForm` cell and its warning output).*

## 3.3 Computed fields

A `@computed_field` on a property adds a value worked out from other fields:

```python
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

print(JobApplication(full_name="Aditi Sharma", years_experience=6))
# full_name='Aditi Sharma' years_experience=6 experience_tier='mid'
```

- *Checked:* 1 gives `junior`, 2 and 6 give `mid`, 7 gives `senior`. `model_dump()` includes `experience_tier`
- It is output only. You cannot pass it in

*Source: `Pydantic_From_Scratch.ipynb` (`computed_field` cells).*

## 3.4 Interview corner

**Q1. `field_validator` or `model_validator`?**
- One field, or the whole model. Use the second for rules like "passwords match"

**Q2. In what order do they run?**
- All field validators first, then the model validator (`mode="after"`). If a field fails, the model validator is skipped

**Q3. Why `@classmethod` under `@field_validator`?**
- The validator receives the class and the value, not an instance, because the object does not exist yet

**Q4. Reject or clean?**
- A validator can do both: raise `ValueError` to reject, or return a changed value to clean

**Q5. Why does a duplicate validator name cause a bug?**
- A class body keeps the last method with a name. The first validator is lost; Pydantic only warns

**Q6. Why not raise `ValidationError` in a validator?**
- You cannot build it by hand that way. Raise `ValueError` (or `AssertionError`) and Pydantic wraps it

**Q7. What is a computed field?**
- A property included in the output (`print`, `model_dump`) but not an input

## 3.5 Added by Claude, not from the sources

All *checked* with Pydantic 2.12.5.

- **`mode="before"` runs before type parsing.** A validator on `n: int` with `mode="before"` turned `"1,200"` into `1200` by stripping the comma first. The default (`after`) runs on the parsed value
- **Read errors as data.** `ValidationError.errors()` returns a list of dicts with `loc`, `msg`, `type`, `input`, `ctx` and `url`. `e.error_count()` gave 2 for a model with a bad `amount` and `currency`
  - `loc` is a path, for example `('amount',)`. This is what you send back to a model to fix its reply ([Chapter 5](05-validating-llm-output.md))
- **Cross-field rule worked as the class described:** `a@infosys.com` with 2 years was rejected; `a@other.com` with 2 years passed
- **Prefer small, named validators.** One rule per validator makes the error message and the fix obvious

## Recap

- `field_validator`: one field, can reject and clean
- `model_validator(mode="after")`: whole model, cross-field rules
- Field validators first; a failing field skips the model validator
- Unique method names. Raise `ValueError`, not `ValidationError`
- `computed_field` adds output-only values. `errors()` gives structured errors

## Practice

1. Write a `field_validator` and a `model_validator` from memory and say why each exists
2. Add a password-match rule and print the order the validators run in
3. Write two validators with the same method name, read the warning, then fix it
4. Add a `computed_field` and look at it in `model_dump()`
5. Make a `mode="before"` validator that accepts `"1,200"` for an `int`
6. Catch a `ValidationError` and print `e.errors()`

## How this chapter was checked

- **Run** (Pydantic 2.12.5, `email-validator` installed): the currency validator, validator order with a matching and a short password, the duplicate-name warning and its effect, `raise ValidationError`, the disposable-email rule, computed tiers, a `before` validator, `errors()` and the cross-field rule
- **Rewritten** from the earlier chapter; the class summaries and notebook were not re-opened in this pass

## Sources and further reading

- Live-Class-2026, `classes_summary/03` and `classes_transcription_summary/03` (Pydantic Deep Dive)
- Live-Class-2026, notebook `8_Pydantic/Pydantic_From_Scratch.ipynb`

Previous: [Chapter 2](02-field-and-special-types.md) · Next: [Chapter 4](04-nested-models-and-inheritance.md)
