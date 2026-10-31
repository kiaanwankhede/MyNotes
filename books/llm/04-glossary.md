# Chapter 4: Glossary

An alphabetical list of the terms that the books already explain. Each entry gives a one-line meaning and where to read more. Terms that belong to the LangChain, MCP and Projects books are added when those chapters are written, so this list is not the whole course vocabulary yet.

*Source: Live-Class-2026, `GLOSSARY.md` and `classes_transcription_summary/glossary.md`. Definitions are reworded. The source glossaries link to a different GitHub repository, and I have not reused those links.*

## A

**\*args and \*\*kwargs.** `*args` collects positional arguments and `**kwargs` collects keyword arguments as a dictionary. A decorator's wrapper uses them to pass any call through unchanged. See [Python, Chapter 2](../python/02-python-refresher.md).

**Agent.** Orchestration code that joins a brain (the LLM), memory (the chat history) and tools, so the model can act and not only talk. The agent itself is not intelligent. See [Python, Chapter 3](../python/03-anatomy-of-an-agent.md).

**Agentic loop.** The cycle behind every agent: send the messages and tool schemas to the model, run any tool it asks for, append the result, and call the model again, until it replies with plain text. See [LLM, Chapter 2](02-the-agentic-loop-in-pure-python.md).

**AgentOps.** The production side the course pairs with agent building: deployment and monitoring, taught after the fundamentals and framework phases. See [LLM, Chapter 1](01-course-roadmap-and-prerequisites.md).

**AI model, chatbot, agent.** Three layers. A model makes one stateless prediction. A chatbot is a model plus history. An agent is a model plus history plus tools it can choose to use. See [Python, Chapter 3](../python/03-anatomy-of-an-agent.md).

## B

**BaseModel.** The Pydantic class that checks every field's type when you create an object and raises an error at once on bad data. See [Pydantic, Chapter 1](../pydantic/01-why-pydantic-and-basemodel.md).

**Brain, memory, tools.** The mental model every agent framework maps onto. See [Python, Chapter 3](../python/03-anatomy-of-an-agent.md).

## C

**Chatbot.** See "AI model, chatbot, agent".

**Context window.** The model's fixed-size whiteboard. When it fills, the oldest content is dropped. It is not the same as memory. See [Inside the model](03-inside-the-model.md).

## D

**Dataclass.** A decorator that writes `__init__` for you from type-hinted fields. It does not check types at run time. See [Python, Chapter 2](../python/02-python-refresher.md).

**Decorator.** A function that wraps another function to add behaviour around it without changing it. The `@tool` pattern is built on it. See [Python, Chapter 2](../python/02-python-refresher.md).

**Deep Agents.** The batteries-included layer built on LangChain agents, with context compression, a virtual file system and sub-agents, at the cost of the least control. See [Langchain, Chapter 1](../langchain/01-introduction-to-langchain.md) and [Chapter 2](../langchain/02-langchain-family-and-harness-engineering.md).

## E

**EmailStr, HttpUrl, SecretStr.** Pydantic's special types. `EmailStr` checks an email, `HttpUrl` checks a URL, and `SecretStr` hides a secret such as an API key when printed. See [Pydantic, Chapter 2](../pydantic/02-field-and-special-types.md).

**Embeddings.** See "Vector embeddings".

## F

**f-string.** A string written `f"..."` where anything in `{ }` is replaced by its value. See [Python, Chapter 1](../python/01-setup-and-api-basics.md).

**Field().** Adds limits on the value itself (for example `gt=0` or `min_length=2`), not just the type. See [Pydantic, Chapter 2](../pydantic/02-field-and-special-types.md).

**field_validator and model_validator.** A `field_validator` checks one field. A `model_validator` runs afterwards and sees the whole model, so it can check rules across fields such as "password matches confirm password". See [Pydantic, Chapter 3](../pydantic/03-validators.md).

**Forward-Deployed Engineer (FDE).** A role the course covers, along with Harness Engineering. See [LLM, Chapter 1](01-course-roadmap-and-prerequisites.md).

**functools.wraps.** Keeps the original function's name when you wrap it in a decorator. See [Python, Chapter 2](../python/02-python-refresher.md).

## G

**Groq.** A fast, free inference provider (not Elon Musk's "Grok") that hosts mostly open-source models behind an OpenAI-compatible API. Point the OpenAI client at its `base_url` with its key and the same code works. See [Python, Chapter 3](../python/03-anatomy-of-an-agent.md).

## H

**Harness.** Everything wrapped around a raw model (system prompt, tools, memory, middleware, guardrails) that turns it into an agent. "Harness engineering" is how well you do that wrapping. See [Langchain, Chapter 2](../langchain/02-langchain-family-and-harness-engineering.md).

## K

**Knowledge cutoff.** The date a model's training data ends. It cannot know anything later, which is one reason agents need tools such as web search. See [LLM, Chapter 2](02-the-agentic-loop-in-pure-python.md).

## L

**LangChain.** The middle layer of the family: a customisable harness (`create_agent`) built on LangGraph. See [Langchain, Chapter 1](../langchain/01-introduction-to-langchain.md).

**LangChain Classic.** LangChain before v1.0 (October 2025). Most online tutorials still teach it. It still runs but is legacy. See [Langchain, Chapter 2](../langchain/02-langchain-family-and-harness-engineering.md).

**LangFuse.** An independent open-source observability platform. Despite the name it is not part of the LangChain family. See [Langchain, Chapter 2](../langchain/02-langchain-family-and-harness-engineering.md).

**LangGraph.** The low-level foundation the family is built on: total control of every step and the steepest learning curve. See [Langchain, Chapter 2](../langchain/02-langchain-family-and-harness-engineering.md).

**LangSmith.** An observability and evaluation platform that records a trace of every model call, tool call and decision, like a flight's black box. It is not for building agents. See [Langchain, Chapter 2](../langchain/02-langchain-family-and-harness-engineering.md).

**LLM.** A large language model. It predicts the next token from patterns in text. See [Inside the model](03-inside-the-model.md).

## M

**max_tokens and max_turns.** `max_tokens` caps the length of a model's output, which also limits runaway cost. `max_turns` (called `max_iterations` in the class pseudo-code) caps how many times the agent loop may call the model. See [LLM, Chapter 2](02-the-agentic-loop-in-pure-python.md).

## N

**Nested models.** A Pydantic model used as the type of a field in another model, which matches nested JSON. See [Pydantic, Chapter 4](../pydantic/04-nested-models-and-inheritance.md).

## O

**OpenRouter.** One API endpoint and one key for models from many providers, with an exact token count per call. See [Inside the model](03-inside-the-model.md).

## P

**Parameters.** The billions of fixed weights set during training. Not the same as tokens. See [Inside the model](03-inside-the-model.md).

**Pydantic.** A library that checks both the type and the value of data at run time and raises `ValidationError` on bad input. See [Pydantic, Chapter 1](../pydantic/01-why-pydantic-and-basemodel.md).

**pyproject.toml.** The project file that records the Python version and the dependencies, so another machine can rebuild the same environment. See [Python, Chapter 1](../python/01-setup-and-api-basics.md).

## R

**ReAct.** "Reason plus Act", the first general-purpose agent pattern, from a paper right after ChatGPT appeared. The model reasons and acts instead of following a fixed chain. See [Langchain, Chapter 2](../langchain/02-langchain-family-and-harness-engineering.md).

## S

**Stateless.** A raw model call remembers nothing. What looks like memory is the whole history being sent again each time. See [Python, Chapter 3](../python/03-anatomy-of-an-agent.md) and [Inside the model](03-inside-the-model.md).

**Structured output.** Making a model's reply fit a defined shape. Here that means asking for JSON and validating it with Pydantic before trusting it. See [Pydantic, Chapter 5](../pydantic/05-validating-llm-output.md). The LangChain way of doing it is not written up yet.

**System, user and assistant messages.** The three roles of message sent to a model on every call: the rules (system, optional), what the person typed (user), and the model's earlier replies (assistant). See [LLM, Chapter 2](02-the-agentic-loop-in-pure-python.md).

## T

**Token.** The unit a model reads, writes and bills in, about three quarters of a word. Output tokens cost more than input tokens. See [Inside the model](03-inside-the-model.md).

**Tool.** A function an agent can use. In plain Python it is a function with a docstring, and a decorator can register it by name. See [Python, Chapter 1](../python/01-setup-and-api-basics.md). The LangChain `@tool` is not written up yet.

**Tool schema.** The name, description and parameters of a tool, sent to the model so it can decide whether and how to call it. The model never sees the function itself. See [LLM, Chapter 2](02-the-agentic-loop-in-pure-python.md).

## U

**UV.** One fast tool for Python versions, virtual environments and dependencies, replacing the mix of `pip`, `venv` and `conda`. See [Python, Chapter 1](../python/01-setup-and-api-basics.md).

## V

**ValidationError.** The error Pydantic raises the moment data fails a type or value check. See [Pydantic, Chapter 1](../pydantic/01-why-pydantic-and-basemodel.md).

**Vector embeddings.** A word or idea turned into a list of numbers, a point in a high-dimensional space, where similar meanings sit close together. See [Inside the model](03-inside-the-model.md).

## Terms waiting for their books

The source glossaries also define about 100 terms from the LangChain and MCP classes, for example middleware, hooks, checkpointing, human-in-the-loop, runtime, MCP primitives, capability negotiation and transports. They are not defined here yet, because those chapters are not written. Vibe coding is also not explained in a book yet.

## Sources and further reading

- Live-Class-2026, `GLOSSARY.md`
- Live-Class-2026, `classes_transcription_summary/glossary.md`

Previous: [Chapter 3, Inside the model](03-inside-the-model.md)
