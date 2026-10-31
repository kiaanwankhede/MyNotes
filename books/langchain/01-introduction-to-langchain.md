# Chapter 1: Introduction to LangChain

Class 06 is where the course moves from hand-built Python to its first framework. LangChain's `create_agent()` runs the same loop you built in [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md), in a few lines. This chapter covers why a framework, what you get, what you give up, and the first working agents.

The mentor's framing: having built it by hand, you will now appreciate LangChain instead of copying it.

*Status: written from class 06. Class 07's material is in [Chapter 2](02-langchain-family-and-harness-engineering.md).*

## 1.1 Why a framework at all

The raw-Python agent works, but the mentor's point is that it does not scale as a long-term way to build. A framework fills that gap. A whiteboard from the class puts it simply: there are lots of agents around us, and because agents exploded so quickly there are now many frameworks for defining them. LangChain is the first one the course teaches, and it is taught deeply because the later frameworks are compared against it.

A sanity check posed to the class: if ChatGPT told you to search Google yourself and paste the results back, it would not be useful. The whole point of an agent is that **it** calls the tool and you do not.

Class 06 also finished the pure-Python agent first. The loop was wrapped in a `run_agent(messages, max_turns=4)` function, and `max_turns` caps how many times the loop may call the model again. In the live demo, a question about converting 1 USD to INR with no currency tool defined got a plain-text answer and not an invented tool call.

*Source: Live-Class-2026, `classes_summary/06`, `classes_transcription_summary/06`, `Untitled-scene.pdf` (a one-page whiteboard).*

## 1.2 Agent = model + harness

LangChain's own definition, as read out in class: an agent is a **model plus a harness**. `create_agent` is a minimal, highly configurable harness: everything around the model loop, meaning the prompts, the tools, and any middleware that shapes behaviour. A model on its own has no memory and no tools. The harness adds them.

## 1.3 Three levels of control

| Layer | Analogy used in class | What you get |
|---|---|---|
| Deep Agents | A delivery app (Swiggy) | Batteries included: context compression, a virtual file system, sub-agents. You control almost nothing inside |
| LangChain | A home-cooked meal | A customisable harness: you pick the spice level and the ingredients. The course starts here |
| LangGraph | Raw vegetables | Low-level orchestration with total control of every step and the steepest learning curve |

LangSmith is separate: it is for monitoring and observing agents, not for building them. The mentor's reason for starting at the middle layer: real software needs the control LangChain gives, and with Deep Agents you cannot control what happens inside, as with delivered food. Chapter 2 covers the family in detail.

**Version note.** Everything before LangChain v1 is now called **LangChain Classic**. Most YouTube tutorials still teach Classic, and this course teaches the latest version only.

*Source: `classes_summary/06`, `classes_transcription_summary/06`.*

## 1.4 A short career note

The mentor said clients care about control, such as how fast an agent runs, not about how many frameworks you know. He builds his own agents, or skips frameworks, in real client work, even while teaching one here. His advice: master the fundamentals (the raw-Python work), after which frameworks become easy, and depth is what gets you hired more than a list of framework names on a CV.

*Source: `classes_transcription_summary/06`. I left out the credentials he listed.*

## 1.5 Setting up a LangChain project

```bash
uv init                                              # new project
uv add langchain langchain-openai langchain-anthropic
uv sync                                              # no manual venv activation needed
```

Then create three files:

1. `.env` with your provider keys.
2. `.gitignore` that excludes `.env` and `.venv`.
3. `.env.example`, a safe template of placeholders that you do commit.

Notes from class:

- Three installs pulled in about 45 dependencies. That is normal, since each provider package has its own.
- `pyproject.toml` already records everything a `requirements.txt` would.
- The mentor accidentally pushed a real API key earlier in the session and had to delete it. It was his live example of why `.gitignore` and `.env.example` matter. A whiteboard in the folder shows GitHub's "Push Blocked: Secret Detected" message, the kind of block that appears when you try to push a key.
- The `.env.example` in the class folder lists five keys with empty values: OpenAI, Groq, Anthropic, Gemini and OpenRouter. I checked it and it holds no real keys.

See also [Chapter 3](03-models-messages-and-parameters.md), section 3.2, on keeping the key out of git.

*Source: `classes_transcription_summary/06`, `classes_summary/06`, `Agentic-Python.pdf`, `.env.example`.*

## 1.6 `create_agent()`, the one-liner

```python
from langchain.agents import create_agent

agent = create_agent(
    model="openai:gpt-4o-mini",     # or anthropic, groq, gemini, ollama...
    tools=[get_weather],
    system_prompt="You are a helpful weather assistant.",
)

result = agent.invoke({"messages": [{"role": "user", "content": "Weather in San Francisco?"}]})
```

The mentor's words: this is the same weather agent that took hours to build by hand, in a few lines. `agent.invoke()` runs the loop you wrote yourself: check for a tool call, run it, feed the result back, repeat.

- **Swap the provider by changing the string prefix.** Supported ones named in class: OpenAI, Anthropic, Gemini, Groq, Ollama, Azure, Bedrock, Hugging Face and Fireworks. You always need your own key for the provider, because LangChain is only the harness.
- **Tools can be plain Python functions.** There is no hand-written JSON schema as in LLM Chapter 2. LangChain works out the structure from the function signature. The `@tool` decorator and a **docstring** are what supply the description to the model (Chapter 5 covers tools).

The model names in the class files (`openai:gpt-5.5`, `openai:gpt-4o-mini`) were current in July 2026 and may have changed. Check before running.

### What is really in the result

Printing `result["messages"]` shows the same anatomy as the hand-built loop:

1. A **HumanMessage** with the question.
2. An **AIMessage** with empty content and a finish reason of tool call.
3. A **ToolMessage** with the tool's result and the same `tool_call_id` as step 2.
4. A final **AIMessage** with the answer.

Each message carries `prompt_tokens`, `completion_tokens` and `total_tokens`. The class confirmed that this call ran the loop twice: one AI message to request the tool, then a second using its result.

**Trade-offs, as named in class.** You lose some visibility and fine control, because LangChain infers most of the tool schema for you and you cannot see it as plainly as in the raw notebook. LangChain calls can also feel slower, because of the extra work around each call: generating IDs, structuring messages and internal bookkeeping.

*Source: `classes_summary/06`, `classes_transcription_summary/06`. Not run: LangChain is not installed in my sandbox and the calls need keys.*

## 1.7 The class 06 code folder

The five steps of LangChain's own quickstart, which both files follow: a detailed system prompt, create tools (`@tool` on any function), configure the model (`init_chat_model` with temperature, timeout and `max_tokens`), add memory, then assemble and run the agent.

### `langchain_agents.py`: the first working agent

A plain mock tool plus a real one, a URL fetcher:

```python
from langchain.agents import create_agent
from langchain.tools import tool
import urllib.request, urllib.error

@tool
def fetch_text_from_url(url: str) -> str:
    """Fetch the document from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; quickstart-research/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"
    return raw.decode("utf-8", errors="replace")

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_agent(
    model="openai:gpt-5.5",
    tools=[get_weather, fetch_text_from_url],
    system_prompt="You are a helpful assistant",
)
result = agent.invoke({"messages": [{"role": "user", "content": "Who am I?"}]})
print(result["messages"][-1].content_blocks)
```

`get_weather` is a plain function with no decorator, and `fetch_text_from_url` uses `@tool`. The question "Who am I?" needs no tool, so the agent answers directly. The file also imports `pprint` but leaves its use commented out.

### `langchain_basics.py`: a research agent that must not guess

The same fetcher is pointed at a harder job, counting things in a real text of about 280 KB. The system prompt tells the model to ground line counts and positions in tool results and not guess:

```python
SYSTEM_PROMPT = """You are a literary data assistant.

## Capabilities
- `fetch_text_from_url`: loads document text from a URL into the conversation.
Do not guess line counts or positions--ground them in tool results from the saved file."""

model = init_chat_model("openai:gpt-5.5", temperature=0.5, timeout=300, max_tokens=25000)

agent = create_agent(
    model=model,
    tools=[fetch_text_from_url],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer,
)
```

The user message gives the Project Gutenberg link for *The Great Gatsby* and asks for (1) how many lines contain `Gatsby`, (2) the line number of the first line with `Daisy`, and (3) a two-sentence synopsis. It also says that if an exact answer cannot be **verified** with the tools, the model must not invent numbers: use `null` and explain the limitation. That is a hands-on guardrail pattern, shown long before guardrails get a chapter of their own. The call passes a `thread_id` (`"great-gatsby-lc"`) in its config so a checkpointer can keep the conversation.

**Source quirks in `langchain_basics.py`.**

1. It passes `checkpointer=checkpointer` but never defines `checkpointer`, so running it raises `NameError`. (A checkpointer is what stores a conversation between calls. A later chapter covers it.)
2. The prompt refers to a field called `how_you_computed_counts`, but nothing defines a structured output with that field.
3. It imports `create_agent` three times and imports `create_deep_agent` from `deepagents`, which it never uses. The class presented that import as a preview of the third tier of the family.

*Source: `classes_summary/06`, code files `langchain_agents.py` and `langchain_basics.py`. Checked by reading and by a name check for undefined names. Not run.*

| File | What it is |
|---|---|
| `langchain_basics.py` | The Gatsby research agent |
| `langchain_agents.py` | `get_weather` plus `fetch_text_from_url`, the first working `create_agent()` |
| `main.py` | A "Hello from class-6-langchain-starts!" scaffold |
| `.env.example` | The provider key template |

## 1.8 Memory and caching

**Memory.** In a live demo, "Hi, I am Mayank" and then "Who am I?" were sent in two **separate script runs**. The agent had no idea, because the memory only exists while the Python process runs (an in-memory list that disappears when the script ends). Real persistence needs a database, a file, or a checkpoint mechanism, which comes in a later class.

**Caching tool results: it depends how fast the data changes.**

| Data | Suggested caching |
|---|---|
| Stock prices | Never cache (they change every second) |
| Weather | Perhaps a day (a time-to-live, TTL) |
| Currency conversion | Perhaps ten minutes |

The rule: do not cache everything just because it is easy. Think about how fast the underlying data actually changes.

*Source: `classes_transcription_summary/06`.*

## 1.9 Questions from the class

| Question | Answer |
|---|---|
| Do I need an API key to use LangChain itself? | LangChain is only the harness. You always need your own model provider key |
| Can `create_agent` use Groq, Gemini, OpenRouter or Ollama? | Yes. Swap the model string or config |
| Is the default loop count the same in every framework? | No. Some cap it near 100. The mentor's raw version used 4 as a sane default |
| Do I have to write a tool schema as in raw Python? | No. Pass a plain function, optionally with `@tool`. The docstring becomes the description |
| Should tool results always be cached? | No. It depends on how quickly the data changes |
| Why does a LangChain agent feel slower than raw Python? | Extra overhead: IDs, message structure, bookkeeping |

*Source: `classes_transcription_summary/06`.*

## Practice

1. `uv add langchain langchain-openai langchain-anthropic` in a fresh project, with `.env`, `.gitignore` and `.env.example`.
2. Build the weather agent with `create_agent()`, print `result["messages"]`, and match each message to the hand-built loop.
3. Wrap one of your own functions with `@tool` and a clear docstring.
4. Run the Gatsby agent after defining a checkpointer, then check its line counts against the real file. Does it ground the numbers, or guess?

## Sources and further reading

- Live-Class-2026, `classes_summary/06 - 12 Jul - Introduction to LangChain.md`
- Live-Class-2026, `classes_transcription_summary/06 - 12 Jul - Introduction to LangChain.md`
- Live-Class-2026, code folder `Weekend 03 - 11-12 Jul/06 - 12 Jul - Introduction to LangChain/` (the two Python files, `main.py`, `.env.example`, its `README.md` and the whiteboard `Untitled-scene.pdf`)

Previous: [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md) · Next: [Chapter 2, LangChain family and harness engineering](02-langchain-family-and-harness-engineering.md)
