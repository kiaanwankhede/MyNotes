# Chapter 2: LangChain family and harness engineering

**After this chapter you can:**

- Tell LangChain, LangGraph, Deep Agents and LangSmith apart
- Say why tracing matters and turn it on
- Define "agent" and "harness" in one sentence each
- Spot an outdated tutorial from the timeline
- Set up and sanity-check your environment

**Builds on:** [Chapter 1](01-introduction-to-langchain.md). Model and message basics are in [Chapter 3](03-models-messages-and-parameters.md).

## 2.1 Four products, four jobs

They are **not competitors**. You use as many as the project needs.

- **LangGraph**
  - Low-level foundation: branching, loops, persistence, durable execution
  - Most agent builders do not touch it at first, because LangChain hides it until needed
- **LangChain**
  - `create_agent`: a configurable harness built **on top of** LangGraph
  - This book is built around it
- **Deep Agents**
  - Built on top of `create_agent`
  - Planning tools, a virtual file system and sub-agent spawning ready-made
- **LangSmith**
  - Observability and evaluation platform, **not** something you build with
  - Watches agents built with any of the above (it supports OpenTelemetry, so almost anything else too)

Why LangChain sits on LangGraph: to get durable execution, human-in-the-loop and persistence for free.

**Common mix-up:** LangFuse is **not** part of the LangChain family. It only shares "Lang" in the name. It is an independent open-source observability platform.

## 2.2 Why LangSmith exists

- An ordinary script: when it fails, you read the stack trace and the code
- An agent decides at run time, so the code shows what it **could** do, not what it **did**
- LangSmith records a **trace**: every model call, tool call and decision, timestamped
- It also shows latency and token cost per step
- `print` shows only what you thought to check. A trace shows everything (diary vs flight recorder)

Turn it on with two environment variables:

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-key-here
```

- Free Developer tier: 5,000 traces a month as of 2026 (class figure, check the current number)
- Enough for learning. Paid tiers matter only for production traffic

## 2.3 Agent and harness, in one sentence each

> An agent is a model calling tools in a loop until a task is complete. A harness is everything around that loop.

- **Model:** raw reasoning. It does not know what tools exist, has no behavioural instructions, cannot check anything outside its own knowledge
- **Harness:** system prompt, tools, middleware, memory, context. It makes the model useful
- `create_agent(model=..., tools=..., system_prompt=...)` configures the harness **around** a model. It never builds a model
- Memory aid: **model = engine, harness = everything else, agent = the car you can drive**

**Harness engineering** = how well you wrap a raw model. Parts to design:

- the model
- tools
- system prompt
- memory
- context (earlier messages, documents)
- sub-agents
- guardrails and checkpoints

`create_agent` exposes: model, tools, system prompt, structured output, invocation and streaming output.

**The brain sets the ceiling.** A weak model in a good harness is still a weak agent. Choose the model deliberately.

## 2.4 Why start with LangChain, and in what order

- Order: **LangChain → LangGraph → Deep Agents**
- Deep Agents is easy once the other two are solid
- Starting at Deep Agents gives you results with no control (ordering delivery vs cooking)
- LangChain is taught deeply because later frameworks (LangGraph, ADK, AutoGen, Amazon's agent SDK) get compared against it
- Learn one framework well and the next one is faster, like a second programming language

## 2.5 A real timeline

- **Oct 2022:** LangChain launches with LLM abstractions and "Chains" (fixed sequences of steps)
- **Dec 2022:** first general-purpose agents, based on the ReAct paper. The model writes JSON and LangChain parses it into a tool call
- **Feb 2024:** LangGraph released: streaming, durable execution, short-term memory, human-in-the-loop
- **Oct 2024:** LangGraph becomes the preferred way to build past a single call. Most old chains and agents deprecated
- **Oct 20, 2025:** LangChain v1.0, one unified agent abstraction. Old code needs the separate `langchain-classic` package
- **Mar 15, 2026:** Deep Agents released

(The Dec 2022 date is from the class summary. The transcript is vaguer, "late 2022 or 2023".)

Key ideas:

- **Chain** = fixed workflow, for example a RAG chain: retrieve documents, then generate an answer
- **2022 to 2024:** building an agent meant hand-parsing JSON into tool calls (`AgentExecutor`, `initialize_agent`). It did not scale, so LangGraph was built
- **ReAct** (Reason + Act): agents that reason and act. Still the shape of most real apps
- **Low level = more control.** Closer to the machine, less abstraction. That is why LangGraph gives more control than LangChain

**Spotting an outdated tutorial:**

```python
from langchain import AgentExecutor   # ImportError on v1.0+
```

- This is not your set-up. The code now deliberately lives in `langchain-classic`
- Classic code still runs but is legacy and unmaintained
- To keep old code running while you migrate: `uv add langchain-classic`

## 2.6 Set up and check your environment

**Where to run code**

- **Google Colab:** free, no local set-up, works on weak laptops. Best for learning line by line
- **VS Code:** real projects with several files and a front end
- Colab resets packages every session. Install once per session

**Project set-up** (same basics as [Chapter 1](01-introduction-to-langchain.md), section 1.4):

```bash
uv init langchain-course
cd langchain-course
uv add langchain langchain-openai langchain-community langgraph python-dotenv
uv add langchain-mcp-adapters langchain-chroma chromadb pypdf   # needed in later modules
```

```python
# Colab
!pip install -q langchain langchain-openai langchain-community langgraph python-dotenv langchain-chroma chromadb
```

**Loading keys**

```python
import os
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get("OPENAI_API_KEY")
print(key[:5] if key else "missing")      # first five characters only, never the whole key
```

- Prefer `.env` + `load_dotenv()` over typing the key into code
- Colab: use the built-in **Secrets** manager (key icon), not a key in a cell
- **Exact names matter.** LangChain looks for each provider's standard variable (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, ...). Rename it or switch provider without its variable and you get an authentication error

**Sanity check** (the official quickstart; if it runs, the environment is right):

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
result = agent.invoke({"messages": [{"role": "user", "content": "Weather in SF?"}]})
print(result["messages"][-1].content_blocks)   # [{'type': 'text', 'text': '...sunny in San Francisco.'}]
```

**If it fails**

- Retired model name: check docs.langchain.com for the current catalogue, change only that string
- Authentication error, usual causes:
  - `.env` is not in the folder you run from
  - `.env` was created after the session started, so **restart the kernel or runtime**
  - Wrong Python kernel in VS Code: pick the project's own `.venv` interpreter

## 2.7 Open and closed source models

- **Open source (open weights)**
  - You get the weights: self-host and fine-tune
  - Cost: often free, or just your hosting
- **Closed source**
  - Weights never provided, API only
  - You pay the provider per use. No fine-tuning of the weights
- Class examples: recent GPT-OSS releases are open-weight. Flagship GPT-5 line and Claude are closed and API-only

## 2.8 FAQs

- **LangChain is built on LangGraph. Why not learn LangGraph directly?**
  - `create_agent` hides LangGraph's complexity until you need it
  - You do not learn assembly before Python. Drop a layer only when the higher one cannot do the job
- **Is LangSmith just logging or `print`?** No. See 2.2
- **Is all this too much just to ask an LLM a question?**
  - One question: call the model directly
  - It pays off with several tool calls, memory across a conversation, or anything you will want to debug
- **Does LangChain cost anything?** No. You only pay your model provider
- **Is it used in production?** Yes
- **Official support if something breaks?** No, as with Python. Open a GitHub issue for a real bug. Support exists only with a company contract
- **Can we use several models and compare outputs?** Yes, common workflow
- **Anthropic or OpenAI? Paid or free?** Depends on use case, budget and needs
- **Does the chat model manage chat history?** No. That is still your job
- **LangSmith needed for the course?** No. The free tier is plenty
- **Old code after upgrading to v1.0?** It does not break silently, but things like `AgentExecutor` raise `ImportError`. Install `langchain-classic`
- **Is Deep Agents just LangGraph or LangChain with extra steps?** Neither. It is built on `create_agent`, one layer out, with planning, a virtual file system and sub-agents ready-made

## 2.9 Self-check

1. Quick agent with lots of customisation? **`create_agent`** (or Deep Agents for batteries included)
2. Agent misbehaved in production, what happened on that run? **LangSmith**
3. An agent is a model calling ___ in a ___ until a task is complete. **Tools, loop**
4. A tutorial uses `AgentExecutor`. What does that tell you? It **predates the Oct 2025 v1.0** unification into `create_agent`

## 2.10 Interview corner

**1. LangChain vs LangGraph vs Deep Agents vs LangSmith?**

- LangGraph: low-level orchestration and durable execution
- LangChain: configurable harness on LangGraph
- Deep Agents: batteries-included layer on `create_agent`
- LangSmith: observability and evaluation
- *Stronger answer:* you combine them. Pick the highest layer that still gives the control you need

**2. What is "harness engineering"?**

- Designing everything around the model: prompt, tools, memory, context, middleware, guardrails
- *Stronger answer:* the model sets the ceiling, the harness decides how close you get to it

**3. Why trace an agent instead of printing?**

- Agents decide at run time, so code does not show what happened
- A trace records every model and tool call with latency and cost
- *Stronger answer:* traces also feed evaluation and regression tests

**4. How do you recognise an outdated LangChain tutorial?**

- Imports like `AgentExecutor` or `initialize_agent` from `langchain` fail on v1.0+ because they moved to `langchain-classic`
- *Stronger answer:* check the date and the package version before copying code

**5. Open vs closed models?**

- Open weights: self-host, fine-tune, you carry the hosting
- Closed: API only, you pay per use
- *Stronger answer:* the choice is usually about data control, cost at scale and capability

## 2.11 Added by Claude, not from the sources

Not in the course material. Established practice, but check current docs.

- **Traces can contain sensitive data.** Prompts, tool arguments and outputs may include personal or confidential information. Decide what you send to a hosted tracing service, mask fields where you can, and check the retention and data-location terms
- **Pin versions.** This ecosystem moved fast (v1.0 in late 2025). Commit `uv.lock`, and pin a major range such as `langchain>=1,<2`, so a fresh install does not break your project
- **Keep tracing projects separate.** Use a different tracing project (or key) for experiments, staging and production so noise does not bury real runs

## Recap

- LangGraph = foundation, LangChain = harness on it, Deep Agents = on top of that, LangSmith = observability
- Agent = model calling tools in a loop. Harness = everything around the loop
- The model sets the ceiling
- Trace with `LANGSMITH_TRACING=true`
- Outdated tutorial? Look for `AgentExecutor`
- Sanity check = the quickstart agent. Restart the kernel after creating `.env`

## Practice

1. Set up a fresh project and run the sanity check in both Colab and VS Code
2. Turn on `LANGSMITH_TRACING=true` and read one trace from start to finish
3. Learn the timeline well enough to spot an outdated tutorial
4. Answer the four self-check questions without looking back

## How this chapter was checked

- Imports and the `create_agent` signature checked on `langchain` 1.4.7. No live model run
- Dates, free-tier numbers and model names are class figures. Check before relying on them

## Sources and further reading

- Live-Class-2026, `classes_summary/07 - 18 Jul - LangChain Family & Harness Engineering.md`
- Live-Class-2026, `classes_transcription_summary/07 - 18 Jul - LangChain Family & Harness Engineering.md`
- Live-Class-2026, notebooks `01_landscape_student_notes.ipynb`, `Revision_Parts_1-4.ipynb` and the `langchain-course` folder (`Common FAQs`, `commands.txt`, `setup_check.ipynb`) in `Weekend 04 - 18-19 Jul/07-08 - .../`
- Section 2.11 is added by Claude and is not from these sources

Previous: [Chapter 1](01-introduction-to-langchain.md) · Next: [Chapter 3, Models, messages and parameters](03-models-messages-and-parameters.md)
