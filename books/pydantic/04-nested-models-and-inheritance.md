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

## Practice

1. Nest one model inside another (for example an `Applicant` containing an `Address`).
2. Inherit a model and check that fields and validators carry over.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`

Previous: [Chapter 3](03-validators.md) · Next: [Chapter 5](05-validating-llm-output.md)
