# Chapter 4: Structured output

A model that answers in free text gives your code nothing solid to depend on. This chapter shows how LangChain makes a model reply in a defined, validated shape. It builds on the Pydantic book, where `BaseModel`, `Field` and validators are explained, and on [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md), where the same idea is done by hand with a JSON instruction.

The class ties this to a running example: Part 5 (structured output), Part 6 (tools) and Part 7 (agents) all use CineBot, a movie-ticket assistant that parses booking requests, checks showtimes and books seats, and finally becomes a real agent.

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

A Pydantic `BaseModel` checks every field strictly and rejects or retries on a mismatch. A `TypedDict` describes the same shape with **no validation at all**. It is faster and lighter, but nothing stops a malformed result getting through. Use Pydantic when correctness genuinely matters (production systems, anything where a wrong value has a real consequence). Use `TypedDict` for quick prototypes or when you are reasonably sure the model will behave and speed matters more. If unsure, default to Pydantic.

## 4.4 `ProviderStrategy` and `ToolStrategy`

There are two ways LangChain guarantees the shape:

| Strategy | How |
|---|---|
| `ProviderStrategy` | Uses the provider's own native structured-output feature. Fast, but only where the provider supports it |
| `ToolStrategy` | Fakes it with a synthetic tool call. Works almost anywhere, with a little more overhead |

LangChain chooses for you when you pass a bare schema: it uses `ProviderStrategy` if the model supports it and falls back to `ToolStrategy` otherwise. You pick one yourself only when you have a reason to force it:

```python
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy

tool_strategy_model     = openai_model.with_structured_output(ToolStrategy(SupportTicket))
provider_strategy_model = openai_model.with_structured_output(ProviderStrategy(SupportTicket))
```

For a simple case such as one support message, both give the same correct result. The difference matters more once structured output is combined with real tools in the same agent. The decision: does the provider have a native structured-output feature? If yes, `ProviderStrategy` uses it (fast and reliable, but only where supported). If no, `ToolStrategy` fakes it with a synthetic tool call (it works almost wherever tool calling works, with a little more overhead).

**A caveat from the notes.** There are community-reported cases from late 2025 where `ToolStrategy` combined with real tool calls in the same agent behaves unreliably on certain models, hitting recursion limits or failing to run correctly. Test your own model and use case before trusting that combination.

## 4.5 The whole pipeline: template in, structured output out

A template shapes the **question** consistently, and a schema shapes the **answer** consistently. Chain them with `|`:

```python
extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract a support ticket from the customer's message below."),
    ("human", "{customer_message}"),
])

pipeline = extraction_prompt | structured_model

for msg in messages:
    print(pipeline.invoke({"customer_message": msg}))
```

A raw, differently worded message goes into the template, the template's prompt goes into the structured model, and a validated `SupportTicket` comes out. There is no `if/else` for different message formats and no string parsing: the structure does the work. The prompt-template syntax is in [Chapter 3](03-models-messages-and-parameters.md), section 3.8.

## Practice

1. Run the three customer messages through plain text, then through `SupportTicket`, and compare.
2. Use `with_structured_output()` with a Pydantic model and check `type(response)`.
3. Rewrite `SupportTicket` as a `TypedDict` and find out what it no longer rejects.

## Sources and further reading

- Live-Class-2026, `classes_summary/08 - 19 Jul - Inside the Model.md`
- Live-Class-2026, `classes_transcription_summary/08 - 19 Jul - LangChain - Inside the Model.md`
- Live-Class-2026, notebooks `04_05_prompt_templates_structured_output_student_notes.ipynb` and `Langchain_structured_output_tools_agents.ipynb` in `Weekend 04 - 18-19 Jul/07-08 - .../Notebook For Reference/`

Previous: [Chapter 3](03-models-messages-and-parameters.md) · Next: [Chapter 5, Tools](05-tools.md)
