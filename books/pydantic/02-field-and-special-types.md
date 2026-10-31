# Chapter 2: `Field()` and special types

Type checks say what kind of data arrived. This chapter adds checks on the value itself.

## 2.1 `Field()`: validating the value, not only the type

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

- `EmailStr` checks for a valid email. It needs the email add-on: `pip install "pydantic[email]"` (the notebook's command). I could not run `EmailStr` here because that package is not installed in my sandbox.
- `HttpUrl` checks for a valid URL.
- `SecretStr` masks sensitive values such as API keys and passwords in logs and printed output. It is easy to overlook, and it matters here because you will handle API keys constantly.

### `SecretStr` in detail

The notebook runs `SecretStr` on a password. I ran the same code:

```python
class UserAccount(BaseModel):
    username: str
    password: SecretStr

account = UserAccount(username="rohan99", password="super-secret-123")
print(account)                     # username='rohan99' password=SecretStr('**********')
account.model_dump()               # {'username': 'rohan99', 'password': SecretStr('**********')}
account.password.get_secret_value()   # 'super-secret-123', the real value, on purpose
```

**Pitfall:** the notebook goes on to write the model to a file with `json.dump(account.model_dump(mode="json"), f, indent=4)`. I ran `model_dump(mode="json")` and it gives `{'username': 'rohan99', 'password': '**********'}`. The file would hold the masked text, not the password. If you need the real value, read it with `get_secret_value()` deliberately.

*Source: `Pydantic_From_Scratch.ipynb` (`SecretStr` and `account.json` cells).*

## Practice

1. Define a `BaseModel` with `Field()` limits from memory.
2. Rewrite one field with `Annotated` to see both syntaxes.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, notebook `8_Pydantic/Pydantic_From_Scratch.ipynb`

Previous: [Chapter 1](01-why-pydantic-and-basemodel.md) · Next: [Chapter 3](03-validators.md)
