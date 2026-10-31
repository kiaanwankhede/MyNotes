# Chapter 4: Nested models and inheritance

Real API payloads and LLM outputs are nested JSON. Models can nest the same way.

## 4.1 Nested models and inheritance

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

### A constraint that does not fit the type

The notebook's nested example gives the inner model a `pin_code` that is a `str` but limits it with `Field(gt=1000, lt=43125315)`:

```python
class Address(BaseModel):
    city: str
    state: str
    pin_code: str = Field(gt=1000, lt=43125315)   # as written in the notebook

class Applicant(BaseModel):
    name: str
    email: str
    address: Address
```

The notebook only defines these classes and never builds an `Address`. I did: `gt` and `lt` are number limits, and creating an `Address` with a text `pin_code` fails with a `TypeError`. Declaring `pin_code: int = Field(gt=1000, lt=43125315)` works, and `Applicant(name="a", email="b", address={"city": "Pune", "state": "MH", "pin_code": 411001})` builds correctly. For a text field use the text limits from Chapter 2 (`min_length`, `max_length`).

*Source: `Pydantic_From_Scratch.ipynb` (last cell).*

## Practice

1. Nest one model inside another (for example an `Applicant` containing an `Address`).
2. Inherit a model and check that fields and validators carry over.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, notebook `8_Pydantic/Pydantic_From_Scratch.ipynb`

Previous: [Chapter 3](03-validators.md) · Next: [Chapter 5](05-validating-llm-output.md)
