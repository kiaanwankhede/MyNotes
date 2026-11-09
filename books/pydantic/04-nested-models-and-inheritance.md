# Chapter 4: Nested models, unions and inheritance

*Real payloads and LLM replies are trees, not flat forms. Models nest the same way.*

> [!NOTE]
> **📍 At a glance**
> - **You will learn:** nested and list models, inheritance vs composition, discriminated unions for agent actions, recursive models, shaping nested output
> - **Level:** intermediate · **Time:** about 15 minutes
> - **Builds on:** [Chapter 3](03-validators.md)

---

## 4.1 Nesting and lists

```python
class LineItem(BaseModel):
    amount: Decimal = Field(gt=0)
    currency: str

class Order(BaseModel):
    items: list[LineItem] = Field(min_length=1)
    note: str | None = None

Order(items=[{"amount": "9.50", "currency": "EUR"}])      # inner dicts are validated too
```

- Errors carry the full path: `('items', 1, 'amount')`
- A code like an Indian PIN is an **identifier**: `str = Field(pattern=r"^\d{6}$")`, not an `int` (leading zeros), and never number limits on a `str`

## 4.2 Inheritance vs composition

| Inheritance ("is a") | Composition ("has a") |
|---|---|
| `AdminUser(User)` gets fields **and** validators | `Order` has `items` |
| Good for shared base fields (`id`, `created_at`) | Small, reusable, testable parts |

- Rule of thumb: one level of inheritance; compose everything else

## 4.3 Discriminated unions: one of several shapes

```python
class SearchAction(BaseModel):
    kind: Literal["search"]
    query: str

class EmailAction(BaseModel):
    kind: Literal["email"]
    to: str
    body: str

Action = Annotated[Union[SearchAction, EmailAction], Field(discriminator="kind")]

class Step(BaseModel):
    action: Action

Step(action={"kind": "email", "to": "a@b.c", "body": "hi"}).action   # EmailAction
```

- Pydantic reads `kind` first and validates **only** that branch: faster, with readable errors
- The pattern for **agent actions, webhooks and queue events**: one entry point, many types; add a branch to extend
- In LLM structured output the model picks `kind` first, then fills only that branch

## 4.4 Recursive models

```python
class Node(BaseModel):
    name: str
    children: list["Node"] = []
```

- Plan steps, comment threads, folder trees; shown as `$defs` + `$ref` in the JSON schema

## 4.5 Shaping output

```python
order.model_dump(include={"items": {0: {"amount"}}})   # nested include
order.model_dump(exclude_none=True)                    # shorter API responses
order.model_dump(exclude_unset=True)                   # only what the caller sent (PATCH)
```

> [!IMPORTANT]
> **🏭 In production:** keep schemas an LLM must fill **shallow**; deep nesting fails more often. Flatten where you can, and use a tagged union rather than many optional fields.

## Interview corner

<details class="qa"><summary>1. Why a discriminated union instead of a plain <code>Union</code>?</summary>

- The tag picks one branch directly: faster, deterministic, clear errors; a plain union tries every branch

</details>

<details class="qa"><summary>2. Inheritance or composition?</summary>

- Inheritance for a shared base; composition for "has a"; avoid deep chains

</details>

<details class="qa"><summary>3. Model an agent that can search, email or finish.</summary>

- One `Literal` tag per action model, a discriminated `Action` union, strict validation, approval on the email branch

</details>

---

*Source: Live-Class-2026 class 03 notebook (nested `Applicant`/`Address`); unions, recursion, output shaping and production notes added by Claude (tested with Pydantic 2.13).*

Previous: [Chapter 3](03-validators.md) · Next: [Chapter 5](05-validating-llm-output.md)
