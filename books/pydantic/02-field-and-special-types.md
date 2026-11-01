# Chapter 2: `Field()` and special types

**After this chapter you can:**

- Add limits on a value with `Field()` (`gt`, `le`, `min_length`, `max_length`)
- Read both `Field()` and `Annotated[...]` syntax
- Use `EmailStr`, `HttpUrl` and `SecretStr`, and avoid the `SecretStr` file pitfall

**Builds on:** [Chapter 1](01-why-pydantic-and-basemodel.md).

Type checks say what kind of data arrived. This chapter checks the value itself.

## 2.1 `Field()`: validating the value, not only the type

- Type validation: what kind of data. Data validation: does the value make sense
- An age of 1000 is a valid `int` but not a valid age

```python
class BoundedAmount(BaseModel):
    amount: float = Field(gt=0, description="Must be positive")
    currency: str = Field(min_length=3, max_length=3)

BoundedAmount(amount=-50, currency="USD")   # type fine, value not: rejected
```

Another class example:

```python
class JobApplication(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    years_experience: int = Field(gt=0, le=50)
    portfolio_url: str
```

| Limit | Means |
|---|---|
| `gt`, `ge` | greater than, greater or equal |
| `lt`, `le` | less than, less or equal |
| `min_length`, `max_length` | length of a string or list |

- *Checked:* `years=51` and `years=0` were rejected; `years=50` passed (`le` includes the limit, `gt` does not)
- `description=` is not a check. It documents the field and goes into the JSON schema

### Two syntaxes

```python
years: int = Field(gt=0, le=50)                 # plain Field
years: Annotated[int, Field(gt=0, le=50)]       # Annotated
```

- The mentor prefers plain `Field()` for readability
- AI-generated code often uses `Annotated`. Learn to read both
- *Checked:* both gave the same rule and the same error for `years=51`

## 2.2 Built-in special types

They save you writing regular expressions.

- **`EmailStr`:** checks for a valid email
  - Needs the add-on: `pip install "pydantic[email]"`
  - *Checked:* with `email-validator` installed, `Rohan@Example.COM` became `Rohan@example.com` (the domain was lower-cased, the local part kept), and `not-an-email` was rejected
- **`HttpUrl`:** checks for a valid URL
  - *Checked:* `https://example.com` became `https://example.com/` (a trailing slash was added); `ftp//x` was rejected
- **`SecretStr`:** hides a value in prints and logs. Easy to overlook; you will handle API keys constantly

### `SecretStr` in detail

```python
class UserAccount(BaseModel):
    username: str
    password: SecretStr

account = UserAccount(username="rohan99", password="super-secret-123")
print(account)                       # username='rohan99' password=SecretStr('**********')
account.model_dump()                 # {'username': 'rohan99', 'password': SecretStr('**********')}
account.password.get_secret_value()  # 'super-secret-123', the real value, on purpose
```

**Pitfall.** The notebook writes the model to a file:

```python
json.dump(account.model_dump(mode="json"), f, indent=4)
```

- *Checked:* `model_dump(mode="json")` gives `{'username': 'rohan99', 'password': '**********'}`
- The file would hold the **masked** text, not the password
- To get the real value, call `get_secret_value()` deliberately

*Source: `Pydantic_From_Scratch.ipynb` (`SecretStr` and `account.json` cells).*

## 2.3 Interview corner

**Q1. Type validation or data validation?**
- Type: it is an `int`. Data: it is between 1 and 50. `Field()` handles data rules

**Q2. `gt` or `ge`?**
- `gt` excludes the limit, `ge` includes it. Same for `lt` and `le`

**Q3. `Field(...)` or `Annotated`?**
- Same result. Plain `Field` is easier to read; `Annotated` is common in generated code

**Q4. Why `SecretStr` for an API key?**
- It stays hidden in prints, logs and `model_dump_json()`. Read the value only where you must

**Q5. Why does `EmailStr` need an extra install?**
- It uses the `email-validator` package. Without it the import fails

**Q6. A `SecretStr` is saved to JSON and the file shows stars. Why?**
- `model_dump(mode="json")` masks it. Use `get_secret_value()` when you truly need the real text

**Q7. What does `description` in `Field()` do?**
- Documents the field and appears in the JSON schema that tools and structured output send to a model

## 2.4 Added by Claude, not from the sources

- **`Field(gt=...)` belongs on numbers.** *Checked:* putting `gt=3` on a `str` field raised `TypeError: Unable to apply constraint 'gt'` when a value was checked. Use `min_length` and `max_length` for text
- **`model_dump_json()` masks secrets too.** *Checked:* the JSON string held `"password":"**********"`
- **`description` helps the model.** When a model is the caller, the description in the schema tells it what a field means (see [Chapter 5](05-validating-llm-output.md))
- **Keep real secrets out of models you log.** Even with `SecretStr`, do not print `get_secret_value()` into logs

## Recap

- `Field()` checks the value: `gt`, `ge`, `lt`, `le`, `min_length`, `max_length`
- `Annotated` is the same rule in another syntax
- `EmailStr` (needs the add-on), `HttpUrl`, `SecretStr` (hides, but `get_secret_value()` reveals)
- Dumping to JSON masks a `SecretStr`

## Practice

1. Define a model with `Field()` limits from memory
2. Rewrite one field with `Annotated` and compare the errors
3. Save a model with a `SecretStr` to JSON and explain what the file holds
4. Put `gt` on a text field and read the error

## How this chapter was checked

- **Run** (Pydantic 2.12.5, `email-validator` installed): the limits and edge values, both syntaxes, `EmailStr`, `HttpUrl`, `SecretStr` through print, `model_dump`, `model_dump(mode="json")`, `model_dump_json`, `get_secret_value`, and `gt` on a text field
- **Rewritten** from the earlier chapter; the class summaries and notebook were not re-opened in this pass

## Sources and further reading

- Live-Class-2026, `classes_summary/03` and `classes_transcription_summary/03` (Pydantic Deep Dive)
- Live-Class-2026, notebook `8_Pydantic/Pydantic_From_Scratch.ipynb`

Previous: [Chapter 1](01-why-pydantic-and-basemodel.md) · Next: [Chapter 3](03-validators.md)
