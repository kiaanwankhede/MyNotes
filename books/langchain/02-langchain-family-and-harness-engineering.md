# Chapter 2: LangChain family and harness engineering

Class 07 sorts out four products that sound alike, gives the one sentence the mentor calls the most important in the course, and walks through the history and the environment set-up. It builds on [Chapter 1](01-introduction-to-langchain.md).

*Status: written from class 07. The model and message parts of class 07 are in [Chapter 3](03-models-messages-and-parameters.md), section 3.1.*

## 2.1 Four products, four jobs

The class notebook opens with the exact confusion it exists to clear: "LangChain vs LangGraph vs LangSmith: which one should I use?" The answer is that they are not competitors. You do not pick one. You use as many as the project needs.

| Product | Job |
|---|---|
| LangGraph | The low-level foundation: branching, loops, persistence, durable execution. Most people building agents do not touch it at first, because LangChain hides it until it is needed |
| LangChain | `create_agent`, a highly configurable harness built **on top of** LangGraph. The course is built around it |
| Deep Agents | Built on top of `create_agent`, with planning tools, a virtual file system and sub-agent spawning ready-made |
| LangSmith | Different from the other three: an observability and evaluation platform, not something you build with |

**A common mix-up.** LangFuse is **not** part of the LangChain family. It only shares "Lang" in the name and is an independent open-source observability platform.

*Source: Live-Class-2026, `classes_summary/07`, `classes_transcription_summary/07`.*

## 2.2 Why LangSmith exists

With an ordinary script, when something goes wrong you read the stack trace and the code. An agent decides what to do at run time, so the code only describes what it **could** do, not what it **did**. LangSmith records a **trace**: a complete, timestamped record of every model call, tool call and decision. The class called it a flight's black box. It also shows latency and token cost for each step.

Two environment variables turn it on:

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-key-here
```

The class said the free Developer tier included 5,000 traces a month as of 2026, which is plenty for learning (check the current figure). A `print` statement shows only what you thought to check, whereas a trace shows everything, like the difference between a diary and a flight recorder.

*Source: `classes_summary/07`, `classes_transcription_summary/07`.*

## 2.3 The most important sentence

> An agent is a model calling tools in a loop until a given task is complete. A harness is everything around that loop.

The **model** is raw reasoning power that cannot do anything: it does not know what tools exist, has no behavioural instructions, and cannot check anything outside its own knowledge. The **harness** (system prompt, tools, middleware) turns that into something useful. `create_agent(model=..., tools=..., system_prompt=...)` configures the harness **around** a model. It never builds a new model.

The mentor's analogy: the model is the engine, the harness is everything else, and the agent is the car you can drive. Even Claude Code and ChatGPT are, at their core, a brain wrapped in connectors, skills, memory and web search.

**Harness engineering** is the name for how well you wrap a raw model with the right system prompt, tools, middleware, guardrails and checkpoints. The components named in class: the model, tools, a system prompt, memory, context (earlier messages and documents) and sub-agents. `create_agent` officially exposes the model, tools, system prompt, structured output, invocation and streaming output, and each gets its own deep dive later.

**The brain sets the ceiling.** The mentor warned: do not say you used a small model and expected the smartest agent. The capability of your agent always depends on the brain you chose.

*Source: `classes_summary/07`, `classes_transcription_summary/07`.*

## 2.4 Why start with LangChain, and in what order

Starting at Deep Agents would be like beginning a job as a chef who only knows how to order delivery: you get food and no control. LangChain is the kitchen, and LangGraph goes lower still, to choosing which vegetables to buy. The intended order is **LangChain, then LangGraph, then Deep Agents**, because Deep Agents becomes easy once the other two are solid.

The class plans to teach LangChain in real depth over three or four classes, because every later framework (LangGraph, ADK, AutoGen, Amazon's agent SDK) will be compared against it. The language analogy: once you understand one language deeply, the next is easier.

*Source: `classes_transcription_summary/07`.*

## 2.5 A real timeline

| Date | What happened |
|---|---|
| Oct 2022 | LangChain launches with LLM abstractions and "Chains", fixed sequences of steps |
| Dec 2022 | First general-purpose agents, based on the ReAct paper. The model generates JSON and LangChain parses it into a tool call |
| Feb 2024 | LangGraph released: streaming, durable execution, short-term memory, human-in-the-loop |
| Oct 2024 | LangGraph becomes the preferred way to build past a single call. Most old chains and agents are deprecated |
| Oct 20, 2025 | LangChain v1.0: one unified agent abstraction. Old code needs the separate `langchain-classic` package |
| Mar 15, 2026 | Deep Agents released |

The summary dates the first agents to Dec 2022. The transcript is vaguer ("late 2022 or 2023"), so I used the summary's date.

Old "Chains" were a fixed workflow: prompt, then node, node, node. ReAct (Reason plus Act) then gave agents that could reason and act, which is still the shape of most real applications.

**Spotting an outdated tutorial.** If a 2026 tutorial imports `AgentExecutor` directly from `langchain`, running it raises an `ImportError`. That is not a fault in your set-up. That code now deliberately lives in `langchain-classic`, kept apart so the v1.0 package stays clean. Old Classic code still runs, but it is legacy and unmaintained (the mentor's analogy: an old iPhone still charges, but nobody is fixing its bugs).

**Low-level or high-level.** The lowest level gives the most control. It sits closer to the machine with little abstraction. That is why LangGraph gives more control than LangChain.

*Source: `classes_summary/07`, `classes_transcription_summary/07`.*

## 2.6 Setting up and checking your environment

**Where to run code.** Google Colab is best for learning line by line: it is free, needs no local set-up and works on weak laptops. VS Code is for real projects with several dependent files and a front end. All notebooks are also on GitHub. The mentor's advice was not to code along live but to watch and then practise from the recording.

**Project set-up** is the same as Chapter 1, section 1.5: `uv init`, `uv add langchain langchain-openai langchain-anthropic`, then `.env`, `.gitignore` and `.env.example`.

**Loading keys.** `load_dotenv()` then `os.environ.get("OPENAI_API_KEY")`. As a safe check, print only the first five characters of the key, never the whole key. Setting `os.environ["OPENAI_API_KEY"] = "..."` also works, but `.env` with `load_dotenv()` is the safer, reusable pattern. In Colab use the built-in **Secrets** manager (the key icon), not a key typed into a cell.

**A live debug.** A notebook failed to read `.env` because the wrong Python kernel was selected in VS Code. The fix was to pick the project's own `.venv` interpreter.

**Exact key names.** LangChain finds the key by the standard variable name for each provider (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY` and so on). Renaming the variable (the class tried `OPENAI_API_KEY_2`), or switching provider without its matching variable, gives an authentication error. The mentor showed this by switching to Claude without setting `ANTHROPIC_API_KEY`.

**A sanity check that the whole set-up works:**

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"It's always sunny in {city}"

agent = create_agent(
    model="openai:gpt-5.5",
    tools=[get_weather],
    system_prompt="You are a helpful assistant.",
)
agent.invoke({"messages": [{"role": "user", "content": "Weather in SF?"}]})
```

If this runs in both Colab and VS Code, the environment is wired correctly.

*Source: `classes_transcription_summary/07`. Not run: LangChain is not installed in my sandbox.*

## 2.7 Open and closed source models

| | Open source | Closed source |
|---|---|---|
| Access to the weights | Yes. You can self-host and fine-tune | No, never provided |
| Hosting | Your own infrastructure is possible | Only through the provider's API |
| Cost | Often free, or only your hosting cost | You pay the company per use |
| Fine-tuning | Possible | Not possible |

The examples given: recent GPT-OSS releases are open-weight, while most flagship models (the GPT-5 line and Claude) remain closed and API-only.

*Source: `classes_transcription_summary/07`.*

## 2.8 FAQs and questions from the class

From the course's own FAQ notes for the session:

- **If LangChain is built on LangGraph, why not learn LangGraph directly?** Because `create_agent` is designed to hide LangGraph's complexity until you need it. You do not learn assembly before Python. Drop to the lower layer only when the higher one cannot do what you need.
- **Is LangSmith the same as built-in logging or print statements?** No. See section 2.2.
- **Is all this too much just to ask an LLM a question?** For one single question, yes: call the model directly. It earns its cost once you need reliability, such as multiple tool calls, memory across a conversation, or anything you will want to debug later.

| Question | Answer |
|---|---|
| Is LangChain foundational, with LangGraph on top? | The other way round: LangGraph is the foundation and LangChain sits on it |
| Does LangChain cost anything? | No. You only pay your model provider |
| Is LangChain still used in production? | Yes |
| Is there official support if something breaks? | No, as with Python itself. Open a GitHub issue for a real bug. Support exists only with a company contract |
| Can we use several models and compare outputs? | Yes, it is a common workflow |
| Which is better, Anthropic or OpenAI? | It depends on use case, budget and needs |
| Paid or free models in a real project? | It depends on requirements and budget |
| Does the chat model manage chat history for you? | No. History management is still your job |

*Source: `classes_summary/07`, `classes_transcription_summary/07`.*

## 2.9 Self-check

1. To build an agent quickly with a lot of customisation, which tool do you reach for? **`create_agent`**, or Deep Agents for batteries included.
2. If your agent misbehaves in production and you need to know what happened on one run? **LangSmith.**
3. Fill in the blank: an agent is a model calling ___ in a ___ until a task is complete. **Tools, loop.**
4. Why would a tutorial using `AgentExecutor` suggest outdated content? It predates the October 2025 v1.0 unification into `create_agent`.

## Practice

1. Set up a fresh LangChain project and run the sanity check in both Colab and VS Code.
2. Turn on `LANGSMITH_TRACING=true` and read one trace from start to finish.
3. Learn the timeline well enough to spot an outdated tutorial on sight.
4. Answer the four self-check questions without looking back.

## Sources and further reading

- Live-Class-2026, `classes_summary/07 - 18 Jul - LangChain Family & Harness Engineering.md`
- Live-Class-2026, `classes_transcription_summary/07 - 18 Jul - LangChain Family & Harness Engineering.md`
- Live-Class-2026, notebook `Weekend 04 - 18-19 Jul/07-08 - .../Notebook For Reference/01_landscape_student_notes.ipynb` (named in the summary, not opened)

Previous: [Chapter 1](01-introduction-to-langchain.md) · Next: [Chapter 3, Models, messages and parameters](03-models-messages-and-parameters.md)
