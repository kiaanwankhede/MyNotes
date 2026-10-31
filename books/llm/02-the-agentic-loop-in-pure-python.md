# Chapter 2: The agentic loop in pure Python

This chapter builds a working agent with plain Python and no framework: a model that can choose a tool, run it, read the result and answer. Every framework you meet later (LangChain, LangGraph, CrewAI) does this same loop underneath. The mentor's reason for teaching it by hand: once you have built it, the framework is a convenience and not a mystery.

Read the Python book, Chapter 3 first. It covers the stateless call, the three layers (model, chatbot, agent), the four providers and the manual tool call. This chapter picks up where that one ends: letting the **model** decide when to use the tool.

## 2.1 What the model needs to know first

### Message roles

Every call to a model carries messages with one of three roles:

| Role | What it holds |
|---|---|
| System | The rules and behaviour ("You are a helpful assistant..."). It is optional but good practice |
| User | What the person typed |
| Assistant | What the model replied earlier in the conversation |

All of them are sent on **every** call, because the model is stateless. In the class demo a single "hi" still sent three messages when the raw request was inspected in a playground. The mentor's doubt-solving chatbot works the same way: its custom instructions are a system message telling it to explain through analogies.

### Knowledge cutoff

A model is trained on data up to a fixed date and knows nothing after it. Every model card lists its cutoff, and the class checked one on a just-released model. Asked about a recent sports result, a model said honestly that it had no real-time access. By default a raw model cannot browse the web. The ChatGPT web app adds browsing on top, but the plain API call does not. This gap is exactly why agents need tools.

### The raw response and `max_tokens`

The class created an OpenAI key, called `client.chat.completions.create(model=..., max_tokens=200, messages=[...])` and printed the whole response object. Its shape: an `id`, the `model`, `choices[0].message.content`, and a `usage` block with `prompt_tokens`, `completion_tokens` and `total_tokens`. The counts matched the provider dashboard's usage log. Groq (the free provider, not Elon Musk's Grok) uses the same OpenAI-compatible code with a different `base_url` and key. The takeaway in the mentor's words: every AI model is, for you, just an API call. Providers differ slightly in the response shape, so check each one.

`max_tokens` caps the **output** length. It also works as a safety net against runaway cost if a key ever leaks. The provider calls are in [Python, Chapter 3](../python/03-anatomy-of-an-agent.md), section 3.4.

*Source: `classes_summary/05`, `classes_transcription_summary/05`.*

## 2.2 Structured output: why plain text is not enough

If your app needs the temperature, would you rather pull "Today weather is 25 degrees" out of a sentence, or receive `{"temperature": 25}`? A free-text reply makes parsing fragile. A structured reply can be used directly.

Two ways to get structure, as taught:

1. **Prompt instruction.** Put an instruction in the user message, such as "reply with only a JSON object in this exact shape", then parse the string back into Python. This is what the class built by hand.
2. **A Pydantic schema.** Define a `BaseModel` once (for example `WeatherQuery` with `city` and `wants_fahrenheit`) and reuse it, instead of retyping the instruction. You get reuse, defaults and validation. The code is in [Pydantic, Chapter 5](../pydantic/05-validating-llm-output.md).

The class also said providers have a native structured-output mode where you pass the schema directly as `response_format`, and that LangChain makes it easy. That is written up with the Langchain book, not here.

*Source: `classes_transcription_summary/05`.*

## 2.3 Letting the model choose a tool

In the manual version the code decided to call the tool. Now the model decides. You do not give it the function. You give it a **tool schema**: the name, a description, and the parameters. The description's wording is what tells the model when the tool is relevant.

The tool itself is still a plain function that knows nothing about AI, here with sample data so the demo never depends on classroom internet:

```python
SAMPLE_WEATHER = {
    "tokyo": {"celsius": 22, "conditions": "partly cloudy"},
    "delhi": {"celsius": 34, "conditions": "clear skies"},
    "london": {"celsius": 15, "conditions": "light rain"},
}

def get_weather(city: str) -> str:
    data = SAMPLE_WEATHER.get(city.lower())
    if data is None:
        return f"No weather data for {city!r}."
    return f"{city.title()}: {data['celsius']}C, {data['conditions']}"
```

Its schema, the "menu" handed to the model:

```python
get_weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this whenever the user asks "
                       "about weather, temperature, or conditions in a specific place.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "The city name, e.g. 'Tokyo'."}},
            "required": ["city"],
        },
    },
}

def ask_ai_to_choose(question: str):
    client, model = get_client_and_model()
    response = client.chat.completions.create(
        model=model, max_tokens=300,
        messages=[{"role": "user", "content": question}],
        tools=[get_weather_schema],          # the menu goes in with the question
    )
    return response.choices[0].message
```

The reply may hold a `tool_calls` list instead of text. That list is the model's **decision to call**, not an executed result. Your code reads it, runs the function itself, and gets the answer.

The file's comment block keeps real replies from class. A casual "Hi How are you ?" came back as plain text with `tool_calls=None`. "what is the weather like in Tokyo right now?" came back with `content=None` and one call, `get_weather` with arguments `{"city":"Tokyo"}`. "What is 2 times 2?" came back as a `calculator` call with `{"expression":"2 * 2"}`. The class also showed that when no matching tool exists (a currency question with no currency tool), the model answers in plain text and does not invent a tool call.

**Several calls in one reply.** Asked "What is the capital of Japan?", the model returned three `get_capital` calls at once, with `country` set to `Japan`, `Tokyo` and `Delhi`. A model can ask for more than one call in a single reply, which is why the loop below handles every call in the list. This particular answer is also messy, because two of the three are wrong.

The file needs an OpenAI-compatible provider (Groq, OpenRouter or OpenAI). Anthropic's tool-calling response has a different shape, which the file says is covered in a later module.

**Source quirk.** In the repo file, `get_weather_schema` is nested wrongly: the `parameters` block sits beside `function` instead of inside it. I loaded it and the keys are `type`, `function` and `parameters`, with only `name` and `description` inside `function`. The model would not receive the parameters. The file's later `get_complete_weather_schema` is the correct one and matches the version above.

*Source: `classes_summary/05`, code file `Project 0/_05_teaching_it_to_choose.py`. Not run against a real model (needs a key).*

## 2.4 The agentic loop

This is the core. The mentor warned it is hard to teach and that no agent course starts from raw Python, but it is what makes LangChain stop feeling like magic.

1. Send the message history **and** the tool schemas to the model.
2. If the reply is plain text, that is the final answer. Return it.
3. If the reply asks for a tool, run it with the arguments the model gave, **append the result to the messages**, and go back to step 1.

The model is called repeatedly, deciding each time whether it has enough information or needs another tool. A cap stops runaway loops. The class pseudo-code called it `max_iterations` (set to 4), and the real files call it `max_turns`.

```python
def run_agent(messages: list, max_turns: int = 5) -> str:
    client, model = get_client_and_model()

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=model, max_tokens=300, messages=messages, tools=TOOL_SCHEMAS
        )
        message = response.choices[0].message

        if not message.tool_calls:                       # plain text: we are done
            messages.append({"role": "assistant", "content": message.content})
            return message.content

        messages.append({                                # remember what the model asked for
            "role": "assistant", "content": message.content,
            "tool_calls": [{"id": call.id, "type": "function",
                            "function": {"name": call.function.name,
                                         "arguments": call.function.arguments}}
                           for call in message.tool_calls],
        })

        for call in message.tool_calls:                  # run EVERY requested tool
            arguments = json.loads(call.function.arguments)
            result = TOOLS_BY_NAME[call.function.name](**arguments)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    return "Reached max_turns without a final answer."
```

**Why call the model again after the tool ran?** The model is stateless and does not know the tool ran. Its output only reaches it when you append it as a new message and send everything back. Each tool result carries the `tool_call_id` of the request it answers, so the model can match the two.

I checked this loop (the version in `_07`) with a fake model. A reply asking for `get_weather` for Tokyo produced exactly this history: the user message, an assistant message with `content` empty and the `tool_calls` list, a `tool` message saying `Tokyo: 22C, partly cloudy`, and then the final assistant text. When the fake model kept asking for tools every turn, the function stopped at the cap and returned "Reached max_turns without a final answer."

*Source: `classes_summary/05`, `classes_transcription_summary/05`, code file `Project 0/_07_streamlit_app.py`.*

### What the saved memory looks like

The folder includes a file named `output`, a saved copy of the agent's memory after a short chat. It shows the shapes in order:

```json
[
  {"role": "user", "content": "Hi I am Mayank"},
  {"role": "assistant", "content": "It's nice to meet you, Mayank. ..."},
  {"role": "user", "content": "who am I ?"},
  {"role": "assistant", "content": "You are Mayank, the person I'm currently chatting with. ..."},
  {"role": "user", "content": "What is the weather in Tokyo"},
  {"role": "assistant", "content": null,
   "tool_calls": [{"id": "9x47zy7j9", "type": "function",
                   "function": {"name": "get_weather", "arguments": "{\"city\":\"Tokyo\"}"}}]},
  {"role": "tool", "tool_call_id": "9x47zy7j9", "content": "Tokyo: 22C, partly cloudy"},
  {"role": "assistant", "content": "The current weather in Tokyo is partly cloudy with a temperature of 22 degrees Celsius."}
]
```

Three things to notice. The agent knew the name only because the first messages were sent again. The tool-call turn has `content` empty and a `tool_calls` list. The `tool` message repeats the same id.

*Source: `Project 0/output`.*

## 2.5 A terminal chat: one list is the whole memory

`_06_project_zero_agent.py` wraps `run_agent` in a minimal terminal chat. The agent's entire memory is one plain list that grows on every turn:

```python
def chat() -> None:
    conversation_memory: list[dict] = []
    print("Type a question (Ctrl+C to quit).")
    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        conversation_memory.append({"role": "user", "content": user_input})
        answer = run_agent(conversation_memory)
        print(f"Agent: {answer}\n")
    print(conversation_memory)     # shows the memory on exit
```

This file has one tool (weather). I ran it with a fake model and found problems that the class summary's excerpt does not show.

**Source quirks in `_06`.**

1. **It crashes the first time the model asks for a tool.** A leftover scratch line builds a `tool_calls` list with `"type": function` (no quotes), and `function` is not defined, so Python raises `NameError`. A reply with no tool call works. The loop in `_07` has no such line and works, so use that one.
2. **`get_currency` is defined twice.** The second version is just `pass` and returns `None`. It is registered in `TOOLS_BY_NAME` but not in `TOOL_SCHEMAS`, so the model is never told it exists.
3. There are other scratch leftovers: a stray `from email import message`, a small list-comprehension exercise (`l1`, `l2`), some empty nested loops at module level, and an unused function `call_tools_async` that is not asynchronous.

*Source: code file `Project 0/_06_project_zero_agent.py`, run with a fake model.*

## 2.6 The Streamlit app: three tools

`_07_streamlit_app.py` runs the same loop behind a chat page with three tools:

| Tool | What it does |
|---|---|
| `get_weather` | Sample data, not a live API |
| `calculator` | Checks the text first, then `eval()`. Only digits, `+ - * /`, brackets, dots and spaces get through |
| `convert_currency` | A live call to the Frankfurter API. Tools can mix live and static data |

```python
def calculator(expression: str) -> str:
    allowed_characters = set("0123456789+-*/(). ")
    if not set(expression) <= allowed_characters:
        return f"Rejected -- expression contains disallowed characters: {expression!r}"
    try:
        return str(eval(expression))
    except Exception as exc:
        return f"Could not evaluate: {exc}"
```

The calculator returns the rejection text as the tool result, so the model can read it and react. I ran it: `2 * (3 + 4)` gave `14`, and `1; import os` was rejected.

**Memory in a web page.** Streamlit re-runs the script on every interaction, which would wipe an ordinary variable. The app keeps its memory in `st.session_state.messages`, which survives the re-runs:

```python
if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Ask about the weather, do some maths, or convert a currency...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = run_agent(st.session_state.messages)
        st.write(answer)
```

Run it with `uv run streamlit run _07_streamlit_app.py`. The currency tool and the page itself were not run here (no network and no Streamlit).

*Source: `classes_summary/05`, code file `Project 0/_07_streamlit_app.py`.*

## 2.7 The Project Zero files

Project Zero was built across classes 04 and 05. Each file runs on its own.

| File | Contents | Where in these notes |
|---|---|---|
| `_01_ai_model_vs_chatbot_vs_agent.py` | Model, chatbot, agent, no API calls | Python Ch 3, section 3.2 |
| `_02_calling_the_ai_paid_and_free.py` | Real calls: OpenAI, Anthropic, Groq, OpenRouter | Python Ch 3, section 3.4 |
| `_03_structuring_with_pydantic.py` | Structured JSON extraction, validated | Pydantic Ch 5, section 5.4 |
| `_04_giving_it_a_tool.py` | A weather tool, called manually | Python Ch 3, section 3.6 |
| `_05_teaching_it_to_choose.py` | Tool schema, the model chooses | This chapter, 2.3 |
| `_06_project_zero_agent.py` | The loop, terminal chat, one tool | This chapter, 2.5 |
| `_07_streamlit_app.py` | The loop with Streamlit, three tools | This chapter, 2.6 |

```bash
uv sync
cp .env.example .env      # fill in at least one key; GROQ_API_KEY is free and fastest
uv run _01_ai_model_vs_chatbot_vs_agent.py
uv run streamlit run _07_streamlit_app.py
```

Unlike the class 02-03 files, these **require a real API key**. The folder's README says there is no offline stand-in.

*Source: `Project 0/README.md` and the folder's overview README.*

## 2.8 Questions from the class

| Question | Answer |
|---|---|
| Why call the model again after the tool ran? | The model is stateless. It does not know the result until it is appended to the messages and sent back |
| Can the model return several tool calls at once? | Yes, depending on the model and provider |
| Is the reply format handled by custom code or a framework here? | By hand-written code. LangChain handles it natively from the next class |
| Why use Pydantic and not just write the JSON instruction in the prompt? | Reuse, defaults, validation and cleaner code |
| Is the system message required? | No, it is optional but good practice |
| Do all providers return the same response structure? | No. OpenAI, Groq and Anthropic each differ slightly |

*Source: `classes_transcription_summary/05`.*

## Practice

1. Run `_05` and ask a question that could trigger two tools at once. Inspect `message.tool_calls`.
2. Trace `run_agent` by hand: what is appended to `messages` on a tool-call turn and on a final-answer turn?
3. Run the Streamlit app and use all three tools in one conversation.
4. Explain, without notes, why the loop calls the model again after a tool runs.
5. Fix the `_05` schema nesting and the `_06` crash.

## Sources and further reading

- Live-Class-2026, `classes_summary/05 - 11 Jul - The Agentic Loop.md`
- Live-Class-2026, `classes_transcription_summary/05 - 11 Jul - The Agentic Loop (Pure Python).md`
- Live-Class-2026, code folder `Weekend 02 - 4-5 Jul/04-05 - 5 Jul & 11 Jul - .../Project 0/` (files `_05` to `_07`, `README.md`, `output`) and its overview `README.md`

Previous: [Chapter 1](01-course-roadmap-and-prerequisites.md) · Next: [Chapter 3, Inside the model](03-inside-the-model.md)
