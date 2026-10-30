# Testing agents
> lead: How to test something nondeterministic: unit tests with fake models, integration tests against real APIs, and evals that score the path the agent took. From the LangChain documentation.

meta: LangChain docs | read 30 Oct 2026 | 15 min read | Not covered in class | Partly from search excerpts

:::note How this chapter was built
The testing pages could not be fetched whole in this session, so this chapter is built from the page excerpts that were retrievable. The unit-testing material is the most complete; integration testing and evals are summaries. Check the linked pages for full code.
:::

## Why it matters

Agents let a model choose its own next steps, so a small prompt change can alter the whole path. The docs name three layers of testing. Interviewers like this topic because most candidates can build an agent but have no answer for "how do you know it still works after a change".

## Core ideas

### 1. Three layers

| Layer | What it checks | Uses real model? |
| --- | --- | --- |
| **Unit tests** | Small deterministic pieces (tools, middleware, loop logic) with scripted replies | No, an in-memory fake |
| **Integration tests** | Components, credentials, schemas and latency working together | Yes, real network calls |
| **Evals** | The agent's **trajectory** (the path of messages and tool calls) judged by matching or by an LLM | Yes |

The docs note agent apps lean more on integration tests than ordinary software, because they chain many components and must cope with LLM flakiness.

### 2. Unit tests with a fake chat model

`GenericFakeChatModel` returns scripted responses from an iterator, one per call. Items can be `AIMessage` objects (including tool calls) or plain strings. It supports normal and streaming use.

```python
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain.messages import AIMessage, ToolCall

model = GenericFakeChatModel(messages=iter([
    AIMessage(content="", tool_calls=[ToolCall(name="foo", args={"bar": "baz"}, id="call_1")]),
    "bar",
]))
model.invoke("hello")   # first scripted reply: the tool call
model.invoke("again")   # second scripted reply: "bar"
```

- `FakeListChatModel` **cycles** through its list, starting again from the first reply when it runs out. Use `GenericFakeChatModel` when you need exact control of each turn, such as tool calls.
- To test a full tool loop, script **two** replies: a tool call, then a final answer.

:::trap GenericFakeChatModel has no bind_tools
`create_agent` calls `bind_tools` when you pass tools, and `GenericFakeChatModel` does not implement it. The docs' fix is to subclass it so `bind_tools` returns the model unchanged.
:::

:::trap Keep the pytest fixture at function scope
A fake model reads from an iterator, and an exhausted iterator cannot be reused. A module or session scope would share one iterator, and later tests would fail once it ran out. Default function scope builds a fresh model for each test.
:::

### 3. Testing memory across turns

Give the agent an `InMemorySaver` checkpointer and reuse a `thread_id` to simulate several turns and check state-dependent behaviour, without any database.

```python
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(model, tools=[...], checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "t1"}}
agent.invoke({"messages": [...]}, config)
```

### 4. Integration tests

Run the agent against real provider APIs. The docs' page covers organising the tests, managing keys, handling flakiness and controlling cost. Keep these few and targeted, since each call costs money and may vary.

### 5. Evals with agentevals

`pip install agentevals`. It provides evaluators for trajectories on live models.

- **Trajectory match**: `create_trajectory_match_evaluator` compares your agent's trajectory to a reference. There are **four modes**; the three the excerpts illustrate are:
  - **Strict**: same tool calls in the same order (for example a policy lookup must come before authorising an action).
  - **Unordered**: same tool calls, any order (weather and events both needed, order irrelevant).
  - **Subset**: the agent called no tools beyond those in the reference.
- **LLM-as-judge**: a model qualitatively checks the trajectory. Use it when you care about overall reasonableness without strict ordering.

LangSmith runs evals at scale, tracks results over time and compares experiments.

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Testing only with the real model | Slow, costly, flaky suite | Unit-test logic with fakes; keep few integration tests |
| Sharing one fake model across tests | Later tests fail when the iterator runs out | Function-scoped fixture |
| Fake model with tools | Error on `bind_tools` | Subclass so `bind_tools` returns itself |
| Asserting exact wording of LLM text | Brittle tests | Assert tool calls and structure; use an LLM judge for quality |
| No trajectory check for ordered rules | Skipped policy step goes unnoticed | Strict trajectory match |

## Hands-on lab

1. Script a fake model with a tool call then an answer and run `create_agent` against it.
2. Add the `bind_tools` subclass and confirm the loop completes.
3. Write a function-scoped pytest fixture and run two tests with it.
4. Use `InMemorySaver` and two invokes on one thread to test that the second turn sees the first.
5. Install `agentevals` and write a strict and an unordered trajectory match for one question.

## Interview corner

:::pitch
I test agents at three layers. Unit tests use a fake chat model that returns scripted tool calls and answers, with an in-memory checkpointer for multi-turn behaviour. Integration tests hit real APIs sparingly to check keys, schemas and latency. Evals score the trajectory with agentevals, using strict or unordered matching for rules and an LLM judge for quality, tracked in LangSmith.
:::

### Basics

:::qa What are the three testing approaches for agents?
Unit tests (fakes, deterministic), integration tests (real API calls) and evals (trajectory matching or an LLM judge).
:::

:::qa How do you unit-test an agent without calling a model?
Use `GenericFakeChatModel` with scripted replies (including tool calls), plus `InMemorySaver` for multi-turn state.
:::

### Intermediate

:::qa Why does `GenericFakeChatModel` fail with `create_agent` and tools?
`create_agent` calls `bind_tools` and the fake does not implement it. Subclass it so `bind_tools` returns the model unchanged.
:::

:::qa What is a trajectory?
The sequence of messages and tool calls the agent produced. Evals compare it to a reference or have an LLM judge it.
:::

### Tricky

:::qa Strict vs unordered vs subset trajectory match?
Strict needs the same tools in the same order. Unordered needs the same tools in any order. Subset allows no tools beyond the reference. Choose by whether order and extra calls matter for your rule.
:::

:::qa Why should agent tests lean on integration more than normal apps?
Agents chain many components and the model is nondeterministic, so wiring problems (keys, schemas, latency) show up only with real calls. Because they are flaky and costly, keep them targeted.
:::

## Quick revision

- [ ] I can name unit, integration and eval layers
- [ ] I can script a fake model with a tool call and an answer
- [ ] I know the `bind_tools` fix and the fixture-scope rule
- [ ] I can test multi-turn state with `InMemorySaver`
- [ ] I can describe trajectory match modes and LLM-as-judge

## Sources and further reading

- [Test overview (LangChain docs)](https://docs.langchain.com/oss/python/langchain/test)
- [Unit testing (LangChain docs)](https://docs.langchain.com/oss/python/langchain/test/unit-testing)
- [Integration testing (LangChain docs)](https://docs.langchain.com/oss/python/langchain/test/integration-testing)
- [Agent evals (LangChain docs)](https://docs.langchain.com/oss/python/langchain/test/evals)
