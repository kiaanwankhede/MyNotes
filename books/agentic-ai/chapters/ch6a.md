# Context engineering
> lead: The idea that ties memory, middleware, tools and multi-agent together: reliable agents fail mostly because the model was given the wrong context, so you control what it sees at every step. From the LangChain documentation.

meta: LangChain docs | read 30 Oct 2026 | 20 min read | Not covered in class

:::note How this chapter was built
The docs page for context engineering could not be fetched directly in this session. This chapter uses the page's search excerpts plus the fully read pages on agents, middleware, tools, runtime and memory, which this topic is built on. Treat the page itself as the reference for anything not shown here.
:::

## Why it matters

When an agent misbehaves, the docs give two reasons: the model is not capable enough, or **the right context was not passed to it**. They say the second is the more common cause. **Context engineering** means giving the model the right information and tools, in the right format, so it can do the task. Everything you built in Chapters 5 to 10 (tools, memory, middleware, runtime) is a context-engineering tool. This chapter names the pattern, which is exactly what interviewers mean by the phrase.

## Core ideas

### 1. The loop you are controlling

An agent loop has two steps: a **model call** (prompt plus tools in, a reply or a tool request out) and **tool execution** (run what was asked, return results). To build a reliable agent you control what happens **at each step** and **between steps**.

### 2. Three kinds of context

| Type | What it is | Lifetime |
| --- | --- | --- |
| **Model context** | What goes into a model call: instructions, message history, tools, model, response format | **Transient** (this call only) |
| **Tool context** | What tools can read and write: state, store, runtime context | **Persistent** |
| **Life-cycle context** | What happens between model and tool calls: summarisation, guardrails, logging | **Persistent** |

:::key Transient vs persistent is the whole trick
Changing **model context** alters what the model sees for one call, and nothing is saved in state. Changing **life-cycle or tool context** writes to state, so the change lasts across turns. The docs' own example: trimming messages for a call is transient, while summarisation permanently replaces old messages with a summary.
:::

### 3. Where the data comes from

All three kinds draw on the same three sources:

| Source | Also called | Scope | Examples |
| --- | --- | --- | --- |
| **State** | Short-term memory | One conversation | Messages, uploaded files, auth status, tool results |
| **Store** | Long-term memory | Across conversations | User preferences, past facts |
| **Runtime context** | Static configuration | One run | User id, role, environment, DB connection |

These are the three pieces from Chapters 6 and 10, now seen as inputs to context.

### 4. Model context: five levers

All are done with middleware (Chapter 7 and 9).

1. **System prompt**, rebuilt on every call with `@dynamic_prompt`. It can read state, store or runtime context.
2. **Messages**, adjusted for one call with `wrap_model_call` (for example inject uploaded-file context only when the query needs it).
3. **Tools**, filtered or added per call (see below).
4. **Model**, chosen per call (a bigger model for long conversations, a cheaper one for short ones).
5. **Response format**, the schema of the final answer.

```python
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    # request.messages is a shortcut for request.state["messages"]
    base = "You are a helpful assistant."
    if len(request.messages) > 10:
        base += " This is a long conversation, be concise."
    return base
```

:::tip Models once, outside the middleware
The docs create each model once at module level and pick between them inside `wrap_model_call`, instead of calling `init_chat_model` on every request.
:::

### 5. Tool context

- **Reads**: a tool declares `runtime: ToolRuntime` and reads `runtime.state`, `runtime.context` or `runtime.store`. The parameter is hidden from the model.
- **Writes**: a tool returns `Command(update={...})` with a matching `ToolMessage`, so later steps see the result.
- **Names and descriptions are context too.** Each tool needs a clear name, description, argument names and argument descriptions, because they guide the model on **when and how** to use it. `@tool(parse_docstring=True)` reads argument descriptions from a docstring.
- **Too many tools** overload the model and increase errors; too few limit it. Adapt the toolset to authentication, permissions, feature flags or the conversation stage.

```python
@wrap_model_call
def only_allowed_tools(request: ModelRequest, handler):
    allowed = [t for t in request.tools if t.name in request.runtime.context.allowed]
    return handler(request.override(tools=allowed))
```

:::trap Filtering is not enough on its own
The tool-selection pattern in the docs filters tools that were **already registered** on `create_agent`. If you add a tool that was never registered, the agent cannot execute it unless you also handle it in `wrap_tool_call` (from the Tools page). Register everything, then filter what the model sees.
:::

### 6. Life-cycle context

Middleware can do two things between steps:

1. **Update context**: modify state, inject messages, summarise.
2. **Jump**: move to a different step (for example skip tools when a condition is met, or repeat the model call with changed context).

The standard example is **summarisation**: when history gets long, `SummarizationMiddleware` replaces old turns with a summary **in state**, permanently. A wrap hook can also pair a model response with a state update by returning `ExtendedModelResponse` with a `Command`.

### 7. Best practices from the docs

- **Test incrementally**: add one context technique at a time.
- **Monitor**: track model calls, token usage and latency.
- **Use built-in middleware first** (summarisation, tool selector).
- **Document your strategy**: what context goes in, and why.
- **Know transient vs persistent** before you choose a hook.

## A decision table

| Problem you see | Context lever | Hook |
| --- | --- | --- |
| Agent ignores the user's role | Runtime context into the prompt | `@dynamic_prompt` |
| Long chats get slow and costly | Summarise (persistent) or trim (transient) | `SummarizationMiddleware` or `before_model` |
| Model picks the wrong tool among 40 | Reduce the toolset | `LLMToolSelectorMiddleware` or `wrap_model_call` |
| Needs facts from a past session | Store | `runtime.store` in a tool |
| One query needs the big model | Choose model per call | `wrap_model_call` with `request.override(model=...)` |

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Putting everything in one giant system prompt | Cost and confusion grow | Build it per call from state, store and context |
| Using trimming when you need the facts later | Information lost forever | Summarise into state instead |
| Registering all tools and showing all of them | Wrong tool picks | Filter per call |
| Changing several context features at once | Cannot tell what helped | Add one at a time and measure |
| Mixing up transient and persistent | Edits "disappear" or "stick" unexpectedly | Decide first whether the change must last |

## Hands-on lab

1. Write a `@dynamic_prompt` that reads the user's role from `context_schema` and changes the instructions.
2. Add a `wrap_model_call` that switches to a bigger model after 10 messages.
3. Filter the toolset by a `role` in runtime context and show that a basic user never sees an admin tool.
4. Compare `SummarizationMiddleware` with a `before_model` trim on a 30-message thread and list what each loses.
5. Make a tool write a field to state with `Command(update=...)` and use it in the next prompt.

## Interview corner

:::pitch
Agents usually fail because the model got the wrong context, not because the model is weak. I treat context as three layers: model context (what one call sees, transient), tool context (what tools read and write, persistent) and life-cycle context (what happens between steps, persistent). All of it draws on state, store and runtime context, and I implement it with middleware: dynamic prompts, per-call tool and model selection, summarisation and guardrails.
:::

### Basics

:::qa What is context engineering?
Providing the right information and tools, in the right format, so the model can complete the task. The docs call poor context the more common cause of unreliable agents.
:::

:::qa Name the three types of context.
Model context (what goes into a call, transient), tool context (what tools read and write, persistent) and life-cycle context (what happens between model and tool calls, persistent).
:::

:::qa Name the three data sources.
State (short-term, per conversation), store (long-term, across conversations) and runtime context (static per-run configuration).
:::

### Intermediate

:::qa Transient vs persistent context?
Model-context changes affect one call and are not saved. Tool writes and life-cycle changes update state, so they last across turns. Trimming for one call is transient; summarisation replaces messages in state and is persistent.
:::

:::qa How do you stop a model from being overwhelmed by many tools?
Select tools per call: an LLM tool selector, or a `wrap_model_call` that filters the pre-registered tools by state, store or runtime context.
:::

### Tricky

:::qa Why might a tool added in `wrap_model_call` fail at execution?
The model can request it, but execution needs a matching `wrap_tool_call` that routes the call to the tool. Registering the tool up front on the agent and filtering is the simpler approach.
:::

:::qa How would you decide between trimming and summarising?
If old turns can safely be dropped, trim for one call (transient, cheap). If later turns depend on facts from them, summarise into state so the information survives.
:::

## Quick revision

- [ ] I can state why context is the main reliability lever
- [ ] I can name the three context types and their lifetimes
- [ ] I can list state, store and runtime context and their scope
- [ ] I can name the five model-context levers
- [ ] I can explain why too many tools hurt
- [ ] I can choose trimming or summarising with a reason

## Sources and further reading

- [Context engineering in agents (LangChain docs)](https://docs.langchain.com/oss/python/langchain/context-engineering)
- [Tools: dynamic tool selection (LangChain docs)](https://docs.langchain.com/oss/python/langchain/tools)
- [Custom middleware (LangChain docs)](https://docs.langchain.com/oss/python/langchain/middleware/custom)
- [Runtime (LangChain docs)](https://docs.langchain.com/oss/python/langchain/runtime)
