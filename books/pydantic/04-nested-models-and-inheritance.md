# Chapter 4: Nested models and inheritance

**After this chapter you can:**

- Nest one model inside another and pass a plain dict for the inner one
- Read a nested error path such as `('items', 1, 'amount')`
- Reuse fields and validators through inheritance
- Avoid the notebook's `pin_code` constraint mistake

**Builds on:** [Chapter 3](03-validators.md).

Real API payloads and LLM outputs are nested JSON. Models nest the same way.

## 4.1 Nested models

```python
class ConversionRequest(BaseModel):
    source: StrictAmount
    target_currency: str

request = ConversionRequest(source={"amount": 250, "currency": "eur"}, target_currency="GBP")
print(f"{request.source.amount} {request.source.currency} -> {request.target_currency}")
```

- A plain **dict** is accepted for the inner model and validated. `"eur"` is cleaned to `"EUR"`
- *Checked:* `model_dump()` gives a nested dict: `{'source': {'amount': 250.0, 'currency': 'EUR'}, 'target_currency': 'GBP'}`
- Errors name the path. *Checked:* a bad inner value gave `('source', 'amount')` and `('source', 'currency')`

*Source: `classes_summary/03`, `classes_transcription_summary/03`.*

## 4.2 Inheritance

- A model that inherits another keeps its fields **and** validators
- *Checked:* a child of a base with `amount: float = Field(gt=0)` and a rounding validator rejected `-1` (`greater_than`), rounded `1.236` to `1.24`, and had fields `['amount', 'note']`
- Use it for shared fields (ids, timestamps) and shared rules

## 4.3 Lists of models

```python
class Order(BaseModel):
    items: list[StrictAmount]
    note: str | None = None
```

- *Checked:* each dict in `items` was validated and cleaned (`usd` to `USD`, `eur` to `EUR`)
- *Checked:* the error path includes the index: `('items', 1, 'amount')` and `('items', 1, 'currency')` for the second item

## 4.4 A constraint that does not fit the type

The notebook's nested example:

```python
class Address(BaseModel):
    city: str
    state: str
    pin_code: str = Field(gt=1000, lt=43125315)   # as written

class Applicant(BaseModel):
    name: str
    email: str
    address: Address
```

- The notebook only defines the classes. It never builds an `Address`
- `gt` and `lt` are **number** limits. *Checked:* building an `Address` with a text `pin_code` fails with `TypeError: Unable to apply constraint 'gt'`
- Fix: `pin_code: int = Field(gt=1000, lt=43125315)`. *Checked:* `Applicant(name="a", email="b", address={"city": "Pune", "state": "MH", "pin_code": 411001})` builds
- For text, use `min_length` and `max_length` ([Chapter 2](02-field-and-special-types.md))

*Source: `Pydantic_From_Scratch.ipynb` (last cell).*

## 4.5 Interview corner

**Q1. How do you model nested JSON?**
- A model as the type of a field. Pass a dict and Pydantic builds and validates the inner model

**Q2. How do you find which nested field failed?**
- `e.errors()` returns `loc` as a path, like `('source', 'amount')` or `('items', 1, 'amount')`

**Q3. What does a child model inherit?**
- Fields, limits and validators. Add or override fields as needed

**Q4. Can you validate a list of models?**
- Yes: `list[Item]`. Each element is validated and the index appears in the error path

**Q5. A `Field(gt=...)` on a string field. What happens?**
- A `TypeError` when a value is checked. Use length limits for text

**Q6. Why do structured outputs from LLMs use nested models?**
- Real answers are nested (an order with items, a plan with steps). The schema must match ([Chapter 5](05-validating-llm-output.md))

## 4.6 Added by Claude, not from the sources

- **Optional nested model:** `address: Address | None = None` makes the whole block optional. *Checked:* absent gave `None`; a bad `pin` inside a given address was still rejected with path `('address', 'pin')`
- **Do not make deep trees for a model to fill.** Deeply nested schemas are harder for a model to follow and fail more often. Keep them flat where you can
- **Rebuild from a dump.** `Model(**model.model_dump())` should give an equal model. *Checked:* `P(**p.model_dump()) == p` was `True`. A quick test that validators are safe to run twice

## Recap

- A model as a field type: nested JSON in, validated tree out
- Errors carry a path with field names and list indexes
- Inheritance keeps fields and validators
- `list[Model]` validates every item
- Number limits go on numbers, length limits on text

## Practice

1. Nest one model inside another (an `Applicant` with an `Address`)
2. Inherit a model and check that fields and validators carry over
3. Make a model with `list[Item]` and read the error path for a bad second item
4. Fix the notebook's `pin_code` field

## How this chapter was checked

- **Run** (Pydantic 2.12.5): nested dict, dump and error paths, inheritance with a limit and a validator, a list of models with a bad item, the `pin_code` `TypeError` and the fixed version
- The optional-nested and rebuild-from-dump checks in 4.6 were run separately
- **Not checked:** the claim that deep schemas make models fail more often is general experience, not tested here
- **Rewritten** from the earlier chapter; the class summaries and notebook were not re-opened in this pass

## Sources and further reading

- Live-Class-2026, `classes_summary/03` and `classes_transcription_summary/03` (Pydantic Deep Dive)
- Live-Class-2026, notebook `8_Pydantic/Pydantic_From_Scratch.ipynb`

Previous: [Chapter 3](03-validators.md) · Next: [Chapter 5](05-validating-llm-output.md)
