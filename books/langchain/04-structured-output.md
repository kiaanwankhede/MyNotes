# Chapter 4: Structured output

A model that answers in free text gives your code nothing solid to depend on. This chapter shows how LangChain makes a model reply in a defined, validated shape. It builds on the Pydantic book, where `BaseModel`, `Field` and validators are explained, and on [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md), where the same idea is done by hand with a JSON instruction.

*Status: only the class 08 material is written. Class 09 (Structured Output Mastery, CineBot) is not processed yet and will extend this chapter.*

## 4.1 The problem, shown live

The class sent three differently phrased customer messages through plain-text extraction:

```python
messages = [
    "Hi, I'm Rina, my order arrived broken and I need a refund ASAP.",
    "hey its dave, package never showed up, kinda annoyed tbh",
    "This is Comfort. My item was fine but delivery took 3 weeks - just flagging it, not urgent.",
]
for msg in messages:
    r = openai_model.invoke(f"Extract the customer's name and issue from: {msg}")
    print(r.content)
```

No two replies are guaranteed to share a shape. One might read "Name: Rina, Issue: broken order" and another be a full sentence. The notebook's line: free text is not wrong, it is just not a contract.

## 4.2 `with_structured_output`

Define the shape once with Pydantic and hand it to the model:

```python
from pydantic import BaseModel, Field
from typing import Literal

class SupportTicket(BaseModel):
    customer_name: str = Field(description="The customer's first name")
    issue_category: Literal["refund", "delivery", "product_defect", "other"]   # closed set
    urgency: Literal["low", "medium", "high"]
    needs_human: bool = Field(description="True if this needs a human agent, not a bot")

structured_model = openai_model.with_structured_output(SupportTicket)
for msg in messages:
    print(structured_model.invoke(f"Extract a support ticket from this message: {msg}"))
```

The same three messy inputs and the same model now give the same `SupportTicket` object every time. A `Literal` list is a closed set, so the model cannot invent a fifth category.

The class opened this with a connecting question: given what you know about Pydantic's validation, shouldn't a model reply in that shape instead of free text? A simpler example from class:

```python
class Email(BaseModel):
    subject: str = Field(description="The email subject line")
    body: str = Field(description="The email body")

structured_model = model.with_structured_output(Email)
response = structured_model.invoke("Write a leave email to my manager")
print(type(response))   # <class '__main__.Email'>, an object and not a string
```

Why it matters downstream: if your logic expects an `Email` object, it will not fail on a malformed string, because the model itself is constrained to that shape.

## 4.3 `BaseModel` or `TypedDict`

A Pydantic `BaseModel` checks every field strictly and rejects or retries on a mismatch. A `TypedDict` describes the same shape with **no validation at all**. It is faster and lighter, but nothing stops a malformed result getting through. Default to Pydantic when correctness matters.

## 4.4 `ProviderStrategy` and `ToolStrategy`

There are two ways LangChain guarantees the shape:

| Strategy | How |
|---|---|
| `ProviderStrategy` | Uses the provider's own native structured-output feature. Fast, but only where the provider supports it |
| `ToolStrategy` | Fakes it with a synthetic tool call. Works almost anywhere, with a little more overhead |

LangChain chooses for you when you pass a bare schema, unless you force one.

**A caveat from the notes.** There are community-reported cases from late 2025 where `ToolStrategy` combined with real tool calls in the same agent behaves unreliably on certain models, hitting recursion limits or failing to run correctly. Test your own model and use case before trusting that combination.

## Practice

1. Run the three customer messages through plain text, then through `SupportTicket`, and compare.
2. Use `with_structured_output()` with a Pydantic model and check `type(response)`.
3. Rewrite `SupportTicket` as a `TypedDict` and find out what it no longer rejects.

## Sources and further reading

- Live-Class-2026, `classes_summary/08 - 19 Jul - Inside the Model.md`
- Live-Class-2026, `classes_transcription_summary/08 - 19 Jul - LangChain - Inside the Model.md`
- Live-Class-2026, notebook `04_05_prompt_templates_structured_output_student_notes.ipynb` (named in the summary, not opened)

Previous: [Chapter 3](03-models-messages-and-parameters.md) · Next: [Chapter 5, Tools](05-tools.md)
