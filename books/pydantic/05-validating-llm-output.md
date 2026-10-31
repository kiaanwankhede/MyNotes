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

## 5.2 Validate the arguments before calling an API

`_9_api_call_with_structure.py` revisits the `convert_currency` function from the Python book (Chapter 2, section 2.6). The API call itself does not change. What is new is that its **arguments** go through Pydantic before the function ever runs. The file says this is the moment "Pydantic" and "API call" stop being two separate lessons.

```python
KNOWN_CURRENCIES = {"USD", "INR", "EUR", "GBP", "JPY"}

class ConvertCurrencyArgs(BaseModel):
    """The trusted shape for this specific function's arguments."""
    amount: float = Field(gt=0)
    from_currency: str
    to_currency: str

    @field_validator("from_currency", "to_currency")
    @classmethod
    def must_be_known_currency(cls, value: str) -> str:
        value = value.upper().strip()
        if value not in KNOWN_CURRENCIES:
            raise ValueError(f"{value!r} isn't a currency this function recognizes: {KNOWN_CURRENCIES}")
        return value

def convert_currency_validated(raw_arguments: dict) -> float | str:
    """Validate BEFORE calling. Untrusted dict in, trusted call out."""
    try:
        validated = ConvertCurrencyArgs(**raw_arguments)
    except ValidationError as exc:
        return f"Rejected before the API was ever called: {exc}"

    return convert_currency(
        amount=validated.amount,
        from_currency=validated.from_currency,
        to_currency=validated.to_currency,
    )
```

Two details: one `field_validator` can cover several fields (`"from_currency", "to_currency"`), and `convert_currency` stays an ordinary function that does not know about Pydantic.

I ran the file. For `{"amount": -50, "from_currency": "dollars", "to_currency": "inr"}` it returns "Rejected before the API was ever called" with 2 validation errors (the amount must be greater than 0, and `'DOLLARS'` is not a known currency), and no network call is made. The good-arguments call needs the live API, which my sandbox could not reach, so I did not see a rate.

*Source: code file `_9_api_call_with_structure.py`.*

## 5.3 A validated tool next to an AI call

`_10_tool_with_ai_call.py` puts two things that work separately side by side: a validated tool (from `_9`) and a real AI call (from `_7`). Its new part is the `@tool` decorator from the Python book (Chapter 1, section 1.4) used for real: it registers the function by name and logs the call, here printing only the keyword arguments.

```python
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | str:
    """Convert `amount` between currencies using real, live ECB rates."""
    ...   # same request and error handling as _9

def call_tool_safely(raw_arguments: dict) -> float | str:
    try:
        validated = ConvertCurrencyArgs(**raw_arguments)
    except ValidationError as exc:
        return f"Rejected before the tool ran: {exc}"
    return convert_currency(
        amount=validated.amount, from_currency=validated.from_currency, to_currency=validated.to_currency
    )
```

The AI call, `ask_ai`, uses Groq if `GROQ_API_KEY` is set, and falls back to the fake client from the Python book if the key is missing or the call fails.

The file's point is its closing message: both parts work, but neither knows the other exists. The AI did not decide to use the tool; the code called both by hand, one after the other. Connecting them is the job of the later agent files (`_11` onward), which are not written up yet.

I ran the file with no key set. The AI part printed the fake client's reply, the tool logged `[tool call] convert_currency({'amount': 100.0, 'from_currency': 'USD', 'to_currency': 'INR'}) -> ...` (note the validated values are upper-cased and the amount became a float), and `Tools registered so far` printed `['convert_currency']`. The tool's own result was the "Couldn't reach the currency service" message because the sandbox has no network.

*Source: code file `_10_tool_with_ai_call.py`.*

## 5.4 Structuring the reply with Pydantic

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

The `ask_ai` helper in this file is a picker over four providers, duplicated here so the file runs on its own. It tries them in this order, using the first key it finds in `.env`: `GROQ_API_KEY`, then `OPENROUTER_API_KEY`, then `OPENAI_API_KEY`, then `ANTHROPIC_API_KEY`. If none is set it raises a `RuntimeError` that lists all four names. (The provider calls themselves are explained in the Python book, Chapter 3, section 3.4.)

The file's `__main__` block runs two messages through `extract_weather_question`: "What's the weather like in Tokyo right now?" and "Is it warm in Delhi today? I want it in Fahrenheit please." It prints the raw model reply and then the validated `WeatherQuestion` (or the "Rejected: ..." text). The copy in the repo also contains debugging `print` calls (it prints the question and the OpenAI answer inside `ask_openai`, and the raw reply in the extraction function).

Why the ` ```json ` fences are stripped: models often wrap JSON in a markdown code fence, and `json.loads` fails on the fence characters.

*Source: `classes_summary/04`, code file `Project 0/_03_structuring_with_pydantic.py` (Weekend 02). Not run here because it needs an API key.*

## 5.5 The code folder for this class

| File | What it covers |
|---|---|
| `_5_calling_a_real_api.py` | The Frankfurter API in a reusable function with error handling |
| `_6_fake_ai_call.py` | A no-dependency stand-in shaped like an OpenAI-style client: `.chat.completions.create(...).choices[0].message.content` |
| `_7_ai_call_free_and_paid.py` | Real calls to Groq, OpenRouter (`model="openrouter/free"` routes automatically) and OpenAI |
| `_8_pydantic_with_ai.py` | The full Pydantic walkthrough above |
| `_9_api_call_with_structure.py` | The API call from `_5`, now validated by Pydantic (section 5.2) |
| `_10_tool_with_ai_call.py` | The `@tool` decorator used for real: a validated `convert_currency` tool sitting beside an AI call, not yet connected to it (section 5.3) |
| `8_Pydantic/` | A standalone mini project: `BaseModel`, `EmailStr`, typed lists and dicts |

Note: the tool and the AI call in `_10` both work, but neither knows the other exists. Connecting them is covered in the Python book, [Chapter 3](../python/03-anatomy-of-an-agent.md).

*Where the AI vocabulary went:* the class also taught five terms (LLM, tokens, vector embeddings, context window, parameters). They are in the LLM book: see [Inside the model](../llm/03-inside-the-model.md).

## Practice

1. Validate a clean and a messy JSON string with `model_validate_json`.
2. Trace the extraction function and say why the code-fence markers are stripped.
3. Run `_10_tool_with_ai_call.py` and check that tool and AI call are separate.
4. Send `_9`'s validated function a bad currency and confirm no network call is made.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_summary/04 - 5 Jul - Anatomy of an Agent.md` (section 5.2)
- Live-Class-2026, code files `_8`, `_9` and `_10` in `Weekend 01 - 27-28 Jun/02-03 - .../`, and `_03_structuring_with_pydantic.py` in `Weekend 02 - 4-5 Jul/04-05 - .../Project 0/`

Previous: [Chapter 4](04-nested-models-and-inheritance.md)
