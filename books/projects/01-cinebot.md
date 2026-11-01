# Chapter 1: CineBot

**After this chapter you can:**

- Find every CineBot example in the LangChain book
- Assemble the pieces into one working agent
- Explain each design choice (tool gating, human approval, memory)

**Builds on:** [LangChain Ch4](../langchain/04-structured-output.md), [Ch5](../langchain/05-tools.md), [Ch7](../langchain/07-middleware.md), [Ch11](../langchain/11-runtime-and-human-in-the-loop.md).

## 1.1 What it is

- A movie-ticket assistant used as the **running example** in the LangChain classes
- Tools: `check_showtimes`, `book_seats`, `cancel_booking`, a refund policy, and a VIP lounge tool
- The course keeps it to explain concepts. It is not a deployed product

## 1.2 Where each idea appears

| Idea | Chapter |
|---|---|
| Three reply shapes (Union structured output) | LangChain Ch4, 4.6 |
| Tools and `return_direct` | LangChain Ch5 |
| Checks before booking, memory | LangChain Ch6 |
| Hide the VIP tool for non-members | LangChain Ch7 |
| Limits, fallback, PII | LangChain Ch8 |
| Guardrails, retries | LangChain Ch9 |
| Context and human approval | LangChain Ch11 |
| CineBot as an MCP server | LangChain Ch12 |

## 1.3 The assembled agent

```python
class CineState(AgentState):
    is_vip_member: bool

@wrap_model_call
def gate_vip_tools(request, handler):
    if not request.state.get("is_vip_member", False):
        request = request.override(
            tools=[t for t in request.tools if t.name != "vip_lounge_booking"])
    return handler(request)

agent = create_agent(
    model, tools=[check_showtimes, book_seats, cancel_booking,
                  get_exact_refund_policy, vip_lounge_booking],
    system_prompt="You are CineBot, a friendly cinema assistant. Check showtimes before booking.",
    state_schema=CineState,
    middleware=[gate_vip_tools,
                HumanInTheLoopMiddleware(interrupt_on={"cancel_booking": True})],
    checkpointer=InMemorySaver(),
)
```

## 1.4 Checked behaviour

Run offline with a scripted stand-in model, `langchain` 1.4.7:

- **Booking:** showtimes, then booking, both ran in order
- **Regular member** was offered 4 tools; the VIP tool was hidden
- **VIP member** was offered all 5
- **Refund policy** came back **verbatim** (`return_direct=True` skips the model's rewrite)
- **Cancel** paused for approval with no tool run. After `approve` it ran
- **Reject** returned a "User rejected the tool call" message

## 1.5 Design choices

- **Tool gating belongs in middleware**, not the prompt. A prompt rule can be talked around; a missing tool cannot be called
- **`return_direct`** for text that must not be paraphrased (policy)
- **Approval on irreversible tools** only
- **A checkpointer** is needed for the pause and resume to work, and each conversation needs a `thread_id`

## 1.6 Interview corner

**Q1. How do you stop non-members using a VIP tool?**
- Remove the tool from the request in a model-call hook
- Do not rely on the prompt alone

**Q2. Why does human approval need a checkpointer?**
- The run pauses and must resume later from saved state

**Q3. When use `return_direct`?**
- When the tool output is the final answer and must stay exact

**Q4. Why test with a scripted model?**
- Fast, free, deterministic. It tests the wiring, not the model

## 1.7 Added by Claude, not from the sources

- The assembled agent in 1.3 is **my combination** of the course's pieces, not a course file
- A scripted model proves wiring only. It says nothing about how a real model would choose tools
- The `hash`-based booking id in my test is not stable between runs; use a real id in practice

## Recap

- CineBot is the course's running example; one agent can combine state, middleware, approval and memory
- Gate tools in middleware; approve irreversible ones; use a checkpointer

## Practice

1. Rebuild 1.3 with your own model
2. Add a `refund_booking` tool that needs approval
3. Make the stand-in model call two tools in one turn
4. Add a custom state field `is_admin` and gate a tool on it

## How this chapter was checked

- Run: the five scenarios in 1.4
- **Not run:** a real model, the Colab notebooks

## Sources and further reading

- The LangChain chapters listed in 1.2

Next: [Chapter 2, Time Tracker (MCP)](02-time-tracker-mcp.md)
