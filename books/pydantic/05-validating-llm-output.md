# Chapter 5: Validating LLM output

**After this chapter you can:**

- Validate a model's raw JSON text with `model_validate_json`
- Check a tool's arguments before calling an API
- Extract a structured request from a user message, and handle bad replies
- Retry by feeding validation errors back to the model
- Get a JSON schema from a model to hand to an LLM

**Builds on:** [Chapters 1 to 4](01-why-pydantic-and-basemodel.md). **Leads to:** [Langchain Ch 4](../langchain/04-structured-output.md) (structured output) and [LLM Ch 2](../llm/02-the-agentic-loop-in-pure-python.md).

The use that matters most: a model returns text, and Pydantic decides whether your code may trust it.

## 5.1 Validating an LLM's raw text

```python
llm_clean_output = '{"amount": 300, "currency": "usd"}'
print(StrictAmount.model_validate_json(llm_clean_output))       # works

llm_messy_output = '{"amount": "a few hundred", "currency": "dollars"}'
try:
    StrictAmount.model_validate_json(llm_messy_output)
except ValidationError as exc:
    print(f"Caught before it could break anything downstream:\n{exc}")
```

- `model_validate_json` is the bridge between "an LLM said something" and "my code can trust it"
- *Checked:* the clean text passed; the messy one was rejected
- *Checked:* the same call also rejects text that is not JSON (`json_invalid`), a trailing comma, and trailing characters
- Pydantic models also define the request and response shapes of the FastAPI servers built later

*Source: `classes_summary/03`, `classes_transcription_summary/02` (Q&A).*

## 5.2 Validate the arguments before calling an API

`_9_api_call_with_structure.py` revisits `convert_currency` ([Python Ch 2](../python/02-python-refresher.md), 2.6). The call is unchanged. New: its **arguments** go through Pydantic first. The file says this is where "Pydantic" and "API call" stop being separate lessons.

```python
KNOWN_CURRENCIES = {"USD", "INR", "EUR", "GBP", "JPY"}

class ConvertCurrencyArgs(BaseModel):
    """The trusted shape for this function's arguments."""
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

- One `field_validator` can cover several fields (`"from_currency", "to_currency"`)
- `convert_currency` stays an ordinary function that knows nothing about Pydantic
- *Checked:* `{"amount": -50, "from_currency": "dollars", "to_currency": "inr"}` returned "Rejected before the API was ever called" with **2 errors** (amount must be greater than 0; `'DOLLARS'` unknown). No network call
- The good-arguments call needs the live API. My sandbox could not reach it (a proxy error came back), so I did not see a rate

*Source: `_9_api_call_with_structure.py`.*

## 5.3 A validated tool next to an AI call

`_10_tool_with_ai_call.py` puts a validated tool (from `_9`) beside a real AI call (from `_7`). New: the `@tool` decorator from [Python Ch 1](../python/01-setup-and-api-basics.md) (1.4) used for real. It registers the function by name and logs the call.

```python
@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | str:
    """Convert `amount` between currencies using real, live ECB rates."""
    ...

def call_tool_safely(raw_arguments: dict) -> float | str:
    try:
        validated = ConvertCurrencyArgs(**raw_arguments)
    except ValidationError as exc:
        return f"Rejected before the tool ran: {exc}"
    return convert_currency(amount=validated.amount, from_currency=validated.from_currency,
                            to_currency=validated.to_currency)
```

- `ask_ai` uses Groq if `GROQ_API_KEY` is set, else a fake client from the Python book
- The file's point (its closing message): both parts work, but **neither knows the other exists**. The AI did not choose the tool; the code called both by hand
- Connecting them is the agent loop: [LLM Ch 2](../llm/02-the-agentic-loop-in-pure-python.md). The class files `_11` to `_14` do it, and are not written up (see "Open items" below)
- *Checked:* with no key, the AI part printed the fake client's reply. The tool logged `[tool call] convert_currency({'amount': 100.0, 'from_currency': 'USD', 'to_currency': 'INR'}) -> ...`. Validated values are upper-cased and the amount became a float. `Tools registered so far` printed `['convert_currency']`. The tool's own result was "Couldn't reach the currency service" (no network)

*Source: `_10_tool_with_ai_call.py`.*

## 5.4 Structuring the reply with Pydantic

`_03_structuring_with_pydantic.py` (Project Zero) asks for **only** a JSON object and validates it before trusting any field:

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

- `ask_ai` picks the first key found in `.env`: `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, then `ANTHROPIC_API_KEY`. None set: a `RuntimeError` listing all four. *Checked*
- Provider calls: [Python Ch 3](../python/03-anatomy-of-an-agent.md), 3.4
- `__main__` runs two messages (Tokyo; Delhi in Fahrenheit) and prints the raw reply, then the model or "Rejected: ..."
- The repo copy has leftover debugging `print` calls
- Why strip ` ```json `: models often wrap JSON in a code fence, and `json.loads` fails on it

**Checked** with scripted replies (the real function, `ask_ai` replaced):

| Reply | Result |
|---|---|
| clean JSON | `WeatherQuestion(city='Tokyo', wants_fahrenheit=False)` |
| fenced JSON | parsed correctly |
| `"wants_fahrenheit":"true"` (string) | converted to `True` |
| extra key `mood` | ignored |
| `Sure! {...}` (text before JSON) | `Rejected: Expecting value` |
| missing `city` / `"maybe"` for the bool | `Rejected` (validation error) |
| a JSON **list** `[{"city":"Tokyo"}]` | **crashes** with `TypeError`: only `JSONDecodeError` and `ValidationError` are caught |

*Source: `classes_summary/04`, `Project 0/_03_structuring_with_pydantic.py`.*

## 5.5 The code folder for this class

| File | What it covers |
|---|---|
| `_5_calling_a_real_api.py` | The Frankfurter API as a reusable function with error handling |
| `_6_fake_ai_call.py` | A no-dependency stand-in shaped like an OpenAI client |
| `_7_ai_call_free_and_paid.py` | Real calls to Groq, OpenRouter and OpenAI |
| `_8_pydantic_with_ai.py` | The Pydantic walkthrough (5.1) |
| `_9_api_call_with_structure.py` | The API call, validated (5.2) |
| `_10_tool_with_ai_call.py` | `@tool` and an AI call, not yet connected (5.3) |
| `8_Pydantic/` | A standalone mini project |

- `_8` printed its walkthrough here: the valid amount, the caught `five hundred`, `'100'` becoming `100.0`, the `Field` constraint and the custom validator
- The AI vocabulary from this class (LLM, tokens, embeddings, context window, parameters) is in [LLM Ch 3](../llm/03-inside-the-model.md)

## 5.6 Interview corner

**Q1. Why validate an LLM's output?**
- A model returns text that may be malformed, off-type or out of range. Validation stops bad data reaching your code

**Q2. `model_validate_json` or `json.loads` plus `Model(**data)`?**
- `model_validate_json` parses and validates in one step and reports JSON errors as validation errors. The two-step form lets you clean text first (strip code fences)

**Q3. What do you do when validation fails?**
- Reject, return a clear error, or retry: send the error back to the model and ask again (5.7)

**Q4. Why validate tool arguments before calling an API?**
- The model chooses the arguments. Bad ones should fail fast, with no network call, cost or side effect

**Q5. How does a Pydantic model help structured output?**
- Its JSON schema tells the model the shape; validation checks the reply matches it

**Q6. Why can the model's JSON still pass but be wrong?**
- Validation proves shape and rules, not truth. A valid `city` can still be the wrong city

**Q7. What exceptions must a parse-and-validate function catch?**
- JSON errors and `ValidationError` at least, and a wrong top-level type (a list instead of an object)

## 5.7 Added by Claude, not from the sources

All *checked* with Pydantic 2.12.5 and a scripted stand-in for the model.

- **Retry with the error.** First reply `{"amount": "a few hundred", ...}` failed; the loop sent back `[{"field": "amount", "problem": "Input should be a valid number..."}]`; the second reply passed. 2 tries

```python
for attempt in range(max_tries):
    raw = ask_model(prompt)
    try:
        return Model.model_validate_json(raw)
    except ValidationError as e:
        problems = [{"field": ".".join(map(str, x["loc"])), "problem": x["msg"]} for x in e.errors()]
        prompt = question + "\nYour last reply was invalid:\n" + json.dumps(problems)
```

- **Hand the model the schema.** `WeatherQuestion.model_json_schema()` gives `properties` with `title`, `type`, `default` and any `description`, plus `required: ["city"]`. Frameworks send this for you ([Langchain Ch 4](../langchain/04-structured-output.md))
- **Use `extra="forbid"`** when an unexpected key should be an error, not ignored ([Chapter 1](01-why-pydantic-and-basemodel.md))
- **Validate non-model data** with `TypeAdapter`. `TypeAdapter(list[int]).validate_python(["1","2"])` gave `[1, 2]`; a bad item gave path `(0,)` and type `int_parsing`
- **Catch the wrong top-level type** in `_03`: add `TypeError` (or check `isinstance(data, dict)`) before `WeatherQuestion(**data)`
- **Strip text before JSON** if the model adds "Sure!": find the first `{` and last `}` and parse that slice
- **Cap retries.** Two or three. A model that cannot fix its reply in a few tries needs a better prompt

## Open items

- Class files `_11_agent_class_ai_only.py` to `_14_agent_with_memory.py` (agent class, one tool, more tools, memory) are marked "Excluded" in the master and were **not read**. [Python Ch 2](../python/02-python-refresher.md) lists them as not written

## Recap

- `model_validate_json` turns model text into a trusted object or a clear error
- Validate tool arguments **before** calling the API: no cost on bad input
- Strip code fences, catch JSON and validation errors, and a wrong top-level type
- Retry by sending the structured errors back; cap the tries
- Valid does not mean true. Validation checks shape and rules

## Practice

1. Validate a clean and a messy JSON string with `model_validate_json`
2. Trace the extraction function and say why the code-fence markers are stripped
3. Run `_10_tool_with_ai_call.py` and check that tool and AI call are separate
4. Send `_9`'s validated function a bad currency and confirm no network call is made
5. Add the `TypeError` fix to `_03` and test it with a JSON list
6. Write the retry loop with a scripted model that fails once, then succeeds

## How this chapter was checked

- **Run** (Pydantic 2.12.5): `_8`, `_9` and `_10` from the repo with no keys; `_03` with no key (the `RuntimeError`) and with eight scripted replies; `model_validate_json` on five texts; the retry loop; the JSON schema; `TypeAdapter`
- **Not run:** the live currency API (no network), any real model, files `_5`, `_6`, `_7`
- **Rewritten** from the earlier chapter; the class summaries were not re-opened in this pass

## Sources and further reading

- Live-Class-2026, `classes_summary/03` and `classes_transcription_summary/03` (Pydantic Deep Dive)
- Live-Class-2026, `classes_summary/04 - 5 Jul - Anatomy of an Agent.md` (5.4)
- Live-Class-2026, code files `_8`, `_9`, `_10` in `Weekend 01 - 27-28 Jun/02-03 - .../`, and `_03_structuring_with_pydantic.py` in `Weekend 02 - 4-5 Jul/04-05 - .../Project 0/`

Previous: [Chapter 4](04-nested-models-and-inheritance.md)
