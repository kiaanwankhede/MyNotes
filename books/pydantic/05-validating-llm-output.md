# Chapter 5: Validating LLM output

This is the use that matters most: a model returns text, and Pydantic decides whether your code may trust it.

## 5.1 The use that matters most: validating an LLM's raw text

```python
llm_clean_output = '{"amount": 300, "currency": "usd"}'
print(StrictAmount.model_validate_json(llm_clean_output))       # works cleanly

llm_messy_output = '{"amount": "a few hundred", "currency": "dollars"}'
try:
    StrictAmount.model_validate_json(llm_messy_output)
except ValidationError as exc:
    print(f"Caught before it could break anything downstream:\n{exc}")
```

`model_validate_json` is the whole bridge between "an LLM said something" and "my code can trust it". I ran this with both inputs: the clean one is accepted and the messy one is rejected.

Pydantic models also define the request and response shapes of the FastAPI servers built later, and structured output from LLMs is parsed with them too.

*Source: `classes_summary/03`, `classes_transcription_summary/02` (Q&A).*

## 5.2 Structuring the reply with Pydantic

`_03_structuring_with_pydantic.py` (Project 0 in the agent class) asks the model for **only** a JSON object and validates it before trusting any field:

```python
class WeatherQuestion(BaseModel):
    city: str
    wants_fahrenheit: bool = False

def extract_weather_question(user_message: str) -> WeatherQuestion | str:
    instruction = (
        "Read the user's message and reply with ONLY a JSON object -- no other text -- "
        'in this exact shape: {"city": "<city name>", "wants_fahrenheit": <true or false>}. '
        f"User's message: {user_message!r}"
    )
    raw_reply = ask_ai(instruction)
    try:
        cleaned = raw_reply.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(cleaned)
        return WeatherQuestion(**data)
    except (json.JSONDecodeError, ValidationError) as exc:
        return f"Rejected: {exc}"
```

Why the ` ```json ` fences are stripped: models often wrap JSON in a markdown code fence, and `json.loads` fails on the fence characters.

*Source: `classes_summary/04`, code file `Project 0/_03_structuring_with_pydantic.py` (Weekend 02). Not run here because it needs an API key.*

## 5.3 The code folder for this class

| File | What it covers |
|---|---|
| `_5_calling_a_real_api.py` | The Frankfurter API in a reusable function with error handling |
| `_6_fake_ai_call.py` | A no-dependency stand-in shaped like an OpenAI-style client: `.chat.completions.create(...).choices[0].message.content` |
| `_7_ai_call_free_and_paid.py` | Real calls to Groq, OpenRouter (`model="openrouter/free"` routes automatically) and OpenAI |
| `_8_pydantic_with_ai.py` | The full Pydantic walkthrough above |
| `_9_api_call_with_structure.py` | The API call from `_5`, now validated by Pydantic |
| `_10_tool_with_ai_call.py` | The `@tool` decorator used for real: a validated `convert_currency` tool sitting beside an AI call, not yet connected to it |
| `8_Pydantic/` | A standalone mini project: `BaseModel`, `EmailStr`, typed lists and dicts |

Note: the tool and the AI call in `_10` both work, but neither knows the other exists. Connecting them is covered in the Python book, [Chapter 3](../python/03-anatomy-of-an-agent.md).

*Where the AI vocabulary went:* the class also taught five terms (LLM, tokens, vector embeddings, context window, parameters). They are in the LLM book: see [Inside the model](../llm/03-inside-the-model.md).

## Practice

1. Validate a clean and a messy JSON string with `model_validate_json`.
2. Trace the extraction function and say why the code-fence markers are stripped.
3. Run `_10_tool_with_ai_call.py` and check that tool and AI call are separate.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_summary/04 - 5 Jul - Anatomy of an Agent.md` (section 5.2)
- Live-Class-2026, code folders `Weekend 01 - 27-28 Jun/02-03 - .../` and `Weekend 02 - 4-5 Jul/04-05 - .../Project 0/`

Previous: [Chapter 4](04-nested-models-and-inheritance.md)
