# Cheat sheet
> lead: The key ideas and the agent loop on one page, for revision before moving to the Pydantic and LangChain books. Every item links back to its chapter.
meta: Quick reference | Code is condensed. See the chapters for the full versions

## Setup in five lines ([Ch 1](#foundations-f1))

```text
uv sync                      # rebuild the exact environment from pyproject.toml + uv.lock
cp .env.example .env         # then paste ONE provider key (Groq or OpenRouter are free)
uv run main.py               # .env is git-ignored, so the key cannot be committed
```

Use Git Bash or Windows Terminal on Windows; use VS Code, not only notebooks. Any key that was ever committed or shared is compromised: revoke it.

## An API call in your head ([Ch 1A](#foundations-f1a))

| Part | Remember |
| --- | --- |
| Endpoint | A fixed URL; options go after `?` or in the body |
| Verbs | GET read, POST create, PUT replace, PATCH change a bit, DELETE remove |
| Headers | `Content-Type: application/json`, `Authorization: Bearer ...`; never put a key in the URL |
| Status | 2xx fine, 4xx fix your request (401 key, 429 slow down), 5xx wait and retry |
| Auth ladder | none, API key, bearer token, OAuth 2.0 |

## LLM facts that explain most bugs ([Ch 2](#foundations-f2))

- **Stateless:** every call starts blank; memory is the message list you resend.
- **Tokens:** the unit of cost and of limits; output usually costs more than input.
- **Context window:** a fixed whiteboard; when full, the oldest text goes first, and then the model may guess (hallucinate).
- **Temperature:** low for facts and code, higher for brainstorming.
- **Embedding:** numbers for meaning. Numbers from two different models cannot be compared.
- **Subscription vs API:** an app plan is flat-rate; code calls are paid per token.

## What an agent is ([Ch 3](#foundations-f3))

| | Model | Chatbot | Agent |
| --- | --- | --- | --- |
| History | no | yes | yes |
| Tools | no | no | yes |
| Decides next step | no | no | yes |

**Agent = brain (LLM) + memory (message list) + tools.** The model only *requests* a tool; **your code runs it** and appends the result.

## The loop ([Ch 3](#foundations-f3), [Ch 4](#foundations-f4))

```python
def run_agent(messages, max_turns=4):
    for _ in range(max_turns):
        message = client.chat.completions.create(
            model=model, messages=messages, tools=TOOL_SCHEMAS).choices[0].message
        if not message.tool_calls:                    # plain text = final answer
            return message.content
        messages.append(message)                      # keep the model's tool request
        for call in message.tool_calls:               # may be several in one reply
            result = TOOLS_BY_NAME[call.function.name](**json.loads(call.function.arguments))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})
    return "Reached max_turns without a final answer."
```

Run in a test with a stub client (key-free): a tool request, then a final answer, gives two model calls; a model that always asks for a tool stops at `max_turns`.

## A tool schema

```python
{"type": "function", "function": {
    "name": "get_weather",
    "description": "Get the current weather for a city. Use this whenever the user asks about weather.",
    "parameters": {"type": "object",
                   "properties": {"city": {"type": "string"}}, "required": ["city"]}}}
```

The **description** is what the model reads to decide when to call it; write it like an instruction.

## Common traps

- "The model calls the function": it does not; it returns a request.
- No tool in the list means no tool call.
- Forgetting `max_turns` means a runaway cost.
- Keys in a notebook or Colab cell: treat as compromised.
- Next: [Pydantic](#pydantic-home), then [Agentic AI with LangChain](#agentic-ai-home).
