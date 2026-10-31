# Chapter 3: Anatomy of an agent

This chapter builds the agent idea in plain Python, with no framework. The background on how models, tokens and context windows work is in the LLM book: [Inside the model](../llm/03-inside-the-model.md).

## 3.1 The big idea: LLM calls are stateless

Every call to an LLM takes an input and gives an output. The model remembers nothing on its own. What looks like memory in a chat window is the **entire history being sent again with every message**. Message 2 really sends message 1, reply 1 and message 2.

A new Google search does not remember your last search. A new LLM call is the same.

The class proved this live. A single "hi" in one chat tool used tens of thousands of tokens because of hidden system prompts and tool context, and the token count rose as the chat grew. The full details of how the context window fills up are in the LLM book.

Practical consequence: long chats get slow, costly and forgetful, so starting a new chat resets the resent history.

*Source: `classes_summary/04`, `classes_transcription_summary/04`.*

## 3.2 Model, chatbot, agent: three levels in real code

`_01_ai_model_vs_chatbot_vs_agent.py` draws all three in Python with no API calls, so the structural difference shows without network noise:

```python
def ai_model(question: str) -> str:
    """A single one-shot prediction. Remembers NOTHING between calls."""
    return f"[Mock prediction for]: {question}"

class Chatbot:
    """Wraps ai_model() with conversation history."""
    def __init__(self) -> None:
        self.history: list[dict] = []

    def ask(self, question: str) -> str:
        self.history.append({"role": "user", "content": question})
        answer = ai_model(question)
        self.history.append({"role": "assistant", "content": answer})
        return answer

class Agent:
    """Wraps ai_model() with history AND a set of tools it can choose to use."""
    def __init__(self, tools: dict[str, callable]) -> None:
        self.history: list[dict] = []
        self.tools = tools

    def decide_tool(self, question: str) -> str | None:
        for name in self.tools:
            if name in question.lower():   # a KEYWORD match -- deliberately naive for now
                return name
        return None

    def ask(self, question: str) -> str:
        self.history.append({"role": "user", "content": question})
        tool_name = self.decide_tool(question)
        if tool_name is not None:
            result = self.tools[tool_name]()
            answer = f"[used tool: {tool_name}] {result}"
        else:
            answer = ai_model(question)
        self.history.append({"role": "assistant", "content": answer})
        return answer
```

`decide_tool` is a placeholder. String matching is not how real decisions work; the next class replaces it with the model choosing by meaning.

*Source: `classes_summary/04`, code file `Project 0/_01_ai_model_vs_chatbot_vs_agent.py`.*

## 3.3 Brain, memory, tools

An agent has three parts:

- **Brain**: the LLM (OpenAI, Claude and so on). The only part that decides anything.
- **Memory**: the chat history, kept in a database or in memory.
- **Tools**: web search, a calculator, a calendar.

The agent itself is only plumbing that moves data between these three. The mentor's analogy is hiring an intern. A laptop with no skills (a weak brain) cannot do much. A brilliant brain with no tools cannot act in the world. The brain sets a hard ceiling on what the agent can do, so a cheap, weak model fails on complex tasks however good the orchestration is. Frameworks such as LangChain, LangGraph and CrewAI all do exactly this.

### The three-step build-up shown in class

1. **Brain only.** Say "Hi, I am Mayank", then ask "Who am I?" and the agent cannot answer, because no history is attached.
2. **Add memory.** Before each call the agent fetches the earlier messages, sends them with the new one, then saves the exchange. The brain is called once per turn. This is short-term memory only: a fresh chat starts blank. Long-term memory is a later topic.
3. **Add tools.** Each tool has a description, and that description is what tells the brain the tool exists. For a casual greeting the brain replies directly. For a factual question it chooses a tool, the tool returns raw results, and the brain is called a second time to turn them into an answer. That is the flow: brain, decide, maybe tool, brain again, respond.

*Source: `classes_transcription_summary/04`. The demos in class used a visual workflow tool purely as illustration and are not code in this book.*

## 3.4 Calling a real model: four providers, one shape

`_02_calling_the_ai_paid_and_free.py` puts the providers side by side. OpenAI and Groq use the same SDK and the same response shape. Groq is free and only needs a different `base_url`. Anthropic's SDK is the one exception:

```python
def ask_openai(question: str) -> str:
    """Paid. Standard shape: a list of messages in, one string answer out."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(model="gpt-4o-mini", max_tokens=200,
                                              messages=[{"role": "user", "content": question}])
    return response.choices[0].message.content

def ask_anthropic(question: str) -> str:
    """Paid. The ONE exception: .messages.create() instead of .chat.completions.create(),
    and .content[0].text instead of .choices[0].message.content."""
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(model="claude-3-5-haiku-20241022", max_tokens=200,
                                      messages=[{"role": "user", "content": question}])
    return response.content[0].text

def ask_groq(question: str) -> str:
    """Free. Uses the OpenAI SDK, pointed at Groq's own base_url."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    response = client.chat.completions.create(model="llama-3.3-70b-versatile", max_tokens=200,
                                              messages=[{"role": "user", "content": question}])
    return response.choices[0].message.content
```

### A fake client with the same shape (`_6_fake_ai_call.py`)

Before any real call, the class builds a stand-in with no dependencies that has exactly the shape of the real client, so the real call in the next file feels familiar. `FakeAIClient` has a `chat` object with `completions`, whose `create(...)` takes `model`, `max_tokens` and `messages` and returns an object with `choices[0].message.content`. It answers by simple rules on the last user message: a question mentioning currency or convert says it would reach for a currency tool, one mentioning weather says it would reach for a weather tool, and anything else says it is only a stand-in.

```python
client = FakeAIClient()
response = client.chat.completions.create(
    model="fake-model", max_tokens=200,
    messages=[{"role": "user", "content": "Convert 50 dollars to euros."}],
)
print(response.choices[0].message.content)
# Shape: client.chat.completions.create(...) -> .choices[0].message.content
```

That shape is what Groq, OpenRouter and OpenAI all actually use. (Anthropic's SDK, shown above, is the exception.)

The same file also has a second, plain-dictionary version of the fake with no classes: `fake_ai(model, max_tokens, messages)` returns `{"choices": [{"message": {"content": reply}}]}`, read as `response['choices'][0]['message']['content']`. **Pitfall:** the file runs this second version at module level, outside its `if __name__ == "__main__":` block. When another file imports `_6_fake_ai_call` (as `_7` does), the second version runs too and prints its extra lines. I saw this when running `_7` without keys.

*Source: code file `_6_fake_ai_call.py`. Run offline; output matches the description.*

### Free and paid providers in one file (`_7_ai_call_free_and_paid.py`)

The real version of the fake client. The shape is the same every time and only the client set-up changes. Three providers, from free to paid:

| Provider | Cost | Set-up |
|---|---|---|
| Groq | Free, email sign-up, no card | OpenAI SDK with `base_url="https://api.groq.com/openai/v1"` |
| OpenRouter | Free tier too | OpenAI SDK with `base_url="https://openrouter.ai/api/v1"` and `model="openrouter/free"`, which routes to whichever free model is available now, so the code does not go stale when free model names change |
| OpenAI | Paid, shown for completeness and not run automatically | OpenAI SDK with no `base_url` override |

Set-up: `uv add openai python-dotenv`, then put `GROQ_API_KEY` and/or `OPENROUTER_API_KEY` in a `.env` file. The file loads it with `load_dotenv()` and reads keys with `os.environ`. Each provider has its own small function (`call_groq`, `call_openrouter`, `call_openai_paid`).

**Fall-back.** If a key is missing, or the call raises an error, the file uses the fake client from `_6` instead, so it always runs:

```python
def call_fallback(question: str) -> str:
    from _6_fake_ai_call import FakeAIClient
    client = FakeAIClient()
    response = client.chat.completions.create(
        model="fallback", max_tokens=200, messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content
```

I ran `_7` with no keys set. It printed "No GROQ_API_KEY set. Stand-in: ..." and "No OPENROUTER_API_KEY set. Stand-in: ..." and a note that the paid OpenAI call is not made. The real calls were not run because they need keys.

The OpenRouter walk-through from the live class (create a key, call a free model, read the token counts) is in the LLM book.

*Source: code file `_7_ai_call_free_and_paid.py`.*

In the agent class a helper, `ask_ai()`, picks whichever key is set in `.env`, free providers first. That pattern is reused for the rest of the course.

**Check before you copy:** model names such as `claude-3-5-haiku-20241022` and `gpt-4o-mini` were current when the class ran in July 2026 and may have been retired since. Look up the current names before running.

*Source: `classes_summary/04`, code file `Project 0/_02_calling_the_ai_paid_and_free.py`. Not run here (needs API keys).*

## 3.5 Structuring the reply with Pydantic

The class asks the model to reply with **only** a JSON object and validates it with a Pydantic model (`WeatherQuestion`, with `city` and `wants_fahrenheit`) before trusting any field. That code and its explanation now live in the Pydantic book: [Validating LLM output](../pydantic/05-validating-llm-output.md). The next section uses its `extract_weather_question` function.

## 3.6 Giving it a tool, by hand

`_04_giving_it_a_tool.py` connects the extraction above to a real tool, but **you** decide to call the tool, not the model:

```python
def answer_weather_question(user_message: str) -> str:
    """Extract a trusted city with Pydantic, then WE decide to call get_weather
    and WE pass the extracted field in. The model decides nothing beyond extraction."""
    extracted = extract_weather_question(user_message)
    if not isinstance(extracted, WeatherQuestion):
        return f"Could not extract a city: {extracted}"
    return get_weather(extracted.city)
```

The line `return get_weather(extracted.city)` is the "we decided" step. The next class (The agentic loop, in the LLM book) lets the model decide when to use the tool.

*Source: `classes_summary/04`, code file `Project 0/_04_giving_it_a_tool.py`.*

## 3.7 Questions from the class

| Question | Answer |
|---|---|
| Does Copilot or Claude send a company's private code to a shared database? | No. Providers do not pool your code in a shared repository across companies |
| Why are input tokens charged? | Every token has to be processed, including an uploaded PDF |
| Are the LLM and the embedding model the same? | No, they are separate specialised models |
| Do parameters change as users chat? | No. They are fixed after training |

## Practice

1. Explain "LLM calls are stateless" in your own words, with an example.
2. Run `_02` and compare Anthropic's response shape with the others.
3. Trace `_03` (see the Pydantic book, Validating LLM output) and explain why the code-fence markers are stripped.
4. Run `_04` and point to the one line that means "we decided".

## Sources and further reading

- Live-Class-2026, `classes_summary/04 - 5 Jul - Anatomy of an Agent.md`
- Live-Class-2026, `classes_transcription_summary/04 - 5 Jul - Anatomy of an Agent.md`
- Live-Class-2026, code folder `Weekend 02 - 4-5 Jul/04-05 - 5 Jul & 11 Jul - .../Project 0/`
- Live-Class-2026, code files `_6_fake_ai_call.py` and `_7_ai_call_free_and_paid.py` in the class 02-03 folder

Previous: [Chapter 2](02-python-refresher.md)
