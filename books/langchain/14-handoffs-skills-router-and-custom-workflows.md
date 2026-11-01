# Chapter 14: Handoffs, skills, router and custom workflows

**After this chapter you can:**

- Build a handoff state machine where tools change the step and middleware changes the prompt and tools
- Hand control between separate agents with `Command(graph=Command.PARENT)`
- Load specialist knowledge on demand with skills, and track what was loaded
- Fan a query out to several agents in parallel with `Send`, and merge the results
- Wrap agents in a hand-built LangGraph workflow, including a retrieval pipeline
- Choose between the five patterns, and combine them

**Builds on:** [Chapter 7](07-middleware.md) and [Chapter 10](10-shell-tools-and-custom-middleware.md) (middleware hooks), [Chapter 11](11-runtime-and-human-in-the-loop.md) (`ToolRuntime`) and [Chapter 13](13-multi-agent-systems-and-subagents.md) (why multi-agent, subagents). Every example ran with a scripted stand-in model, no API key ([Chapter 13](13-multi-agent-systems-and-subagents.md), 13.5).

## 14.1 Pattern 2: handoffs

Behaviour changes **with state**. Tools update a state variable (`current_step` or `active_agent`) that survives across turns, and the system reads it to change the prompt and tools, or to route to another agent.

- The word "handoffs" was coined by OpenAI for tool calls such as `transfer_to_sales` that pass control between agents or states
- **Key traits:** state-driven behaviour, tool-based transitions, **direct conversation with the user** in every state, and state that persists across turns
- **Use it when:** sequential constraints (unlock a capability only after a precondition), or a multi-stage conversation, such as collecting a movie and showtime before unlocking seat choice
- **Against subagents:** there is **no supervisor reasoning about where to route**. State alone decides what is active now

| Approach | What it is | Use when |
|---|---|---|
| **One agent plus middleware** | The same agent, with prompt and tools swapped per state | Most cases. Simpler |
| **Separate agent subgraphs** | Distinct agents as graph nodes | Each agent is a bespoke build, perhaps a complex graph itself |

## 14.2 Handoffs with one agent: customer support

The agent collects the warranty status, classifies the issue, then gives a solution or escalates. **Each step is the same agent in a different configuration.**

```
warranty_collector → issue_classifier → resolution_specialist
   record_warranty_status   record_issue_type    provide_solution / escalate_to_human
```

**1. State.** `current_step` is the core of the machine.

```python
from typing import Literal
from typing_extensions import NotRequired
from langchain.agents import AgentState

class SupportState(AgentState):
    current_step: NotRequired[Literal["warranty_collector", "issue_classifier", "resolution_specialist"]]
    warranty_status: NotRequired[Literal["in_warranty", "out_of_warranty"]]
    issue_type: NotRequired[Literal["hardware", "software"]]
```

**2. Tools that move the workflow.** They return a `Command` that updates the data **and** `current_step`.

```python
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage
from langgraph.types import Command

@tool
def record_warranty_status(status: Literal["in_warranty", "out_of_warranty"],
                           runtime: ToolRuntime[None, SupportState]) -> Command:
    """Record the customer's warranty status and move to issue classification."""
    return Command(update={
        "messages": [ToolMessage(content=f"Warranty status recorded as: {status}",
                                 tool_call_id=runtime.tool_call_id)],
        "warranty_status": status,
        "current_step": "issue_classifier",
    })
```

- `record_issue_type` is the same shape and sets `current_step` to `resolution_specialist`
- **Every `Command` update needs a `ToolMessage`** carrying `tool_call_id=runtime.tool_call_id`. *Checked:* a tool that returned only `{"current_step": ...}` raised `ValueError`: "Expected to have a matching ToolMessage in Command.update ... Every tool call ... MUST have a corresponding ToolMessage". Without the message the history is malformed, because the model is still waiting for an answer to its tool call

**3. One table for all steps.** Each step has a prompt, its tools, and the state it needs.

```python
STEP_CONFIG = {
    "warranty_collector":    {"prompt": WARRANTY_PROMPT, "tools": [record_warranty_status], "requires": []},
    "issue_classifier":      {"prompt": CLASSIFIER_PROMPT,  # uses {warranty_status}
                              "tools": [record_issue_type], "requires": ["warranty_status"]},
    "resolution_specialist": {"prompt": RESOLUTION_PROMPT,  # uses {warranty_status}, {issue_type}
                              "tools": [provide_solution, escalate_to_human],
                              "requires": ["warranty_status", "issue_type"]},
}
```

- **Adding a step is adding a dictionary entry**

**4. Middleware applies the step.**

```python
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

@wrap_model_call
def apply_step_config(request: ModelRequest, handler) -> ModelResponse:
    step = request.state.get("current_step", "warranty_collector")
    cfg = STEP_CONFIG[step]
    for key in cfg["requires"]:
        if request.state.get(key) is None:
            raise ValueError(f"{key} must be set before reaching {step}")
    request = request.override(system_prompt=cfg["prompt"].format(**request.state),
                               tools=cfg["tools"])
    return handler(request)
```

- The `requires` check **fails loudly** if a step is skipped. *Checked:* starting at `resolution_specialist` with no warranty status raised "warranty_status must be set before reaching resolution_specialist"

**5. The agent needs a checkpointer.** Without it `current_step` would reset on every turn.

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
support_agent = create_agent(model, tools=all_tools, state_schema=SupportState,
                             middleware=[apply_step_config], checkpointer=checkpointer)
```

- *Checked over four turns on one thread:* `current_step` was unset after turn 1 (it stays at the default until a tool runs), then `issue_classifier`, then `resolution_specialist`, then `resolution_specialist` again
- *Checked:* the tools offered to the model changed per step: `record_warranty_status` only, then `record_issue_type` only, then `provide_solution` and `escalate_to_human`. **The model literally cannot call a tool from another step**

| Turn | `current_step` going in | What happens | After |
|---|---|---|---|
| 1 | default `warranty_collector` | Agent asks about warranty | unchanged until a tool call |
| 2 | `warranty_collector` | `record_warranty_status` | `issue_classifier` |
| 3 | `issue_classifier` | `record_issue_type` | `resolution_specialist` |
| 4 | `resolution_specialist` | `provide_solution` or `escalate_to_human` | stays (end) |

**The key line: state decides configuration, tools decide state.**

### Letting the customer go back

- Add `go_back_to_warranty` and `go_back_to_classification` as tools that set `current_step` backwards. Each needs a `ToolRuntime` and a `ToolMessage`, as above
- A workflow that needs arbitrary jumps between most steps is probably the wrong shape. This pattern fits **a clear forward path with occasional backward corrections**
- **Gotcha: middleware cannot add tools the agent was not built with.** The tempting shortcut is to extend `STEP_CONFIG[...]["tools"]` and keep the old agent. *Checked:* that raised "Middleware added tools that the agent doesn't know how to execute. Unknown tools: ['extra_tool'] Registered tools: [...]"
  - **Register every tool at `create_agent(...)`.** Middleware can only **narrow** which registered tools are visible per step
  - Rebuilding the agent is fine, but **reuse the same checkpointer object**, so the conversation survives. *Checked:* the rebuilt agent, given the same checkpointer and thread, moved `current_step` back to `warranty_collector`
- **Long conversations:** `SummarizationMiddleware` compresses older messages past a token threshold ([Chapter 8](08-prebuilt-middleware-limits-fallback-and-pii.md)). The class showed it for reference and did not run it. Note the trigger spelling: `("tokens", 4000)`

## 14.3 Handoffs between separate agents

Each agent is a graph node. A **handoff tool** moves control with `Command(goto=..., graph=Command.PARENT)`.

```python
from langchain.messages import AIMessage as AIMsg, ToolMessage as ToolMsg

@tool
def transfer_to_refunds(runtime: ToolRuntime) -> Command:
    """Transfer to the refunds agent."""
    last_ai = next(m for m in reversed(runtime.state["messages"]) if isinstance(m, AIMsg))
    return Command(
        goto="refunds_agent",
        update={"active_agent": "refunds_agent",
                "messages": [last_ai, ToolMsg(content="Transferred to refunds agent",
                                              tool_call_id=runtime.tool_call_id)]},
        graph=Command.PARENT,
    )
```

- **`graph=Command.PARENT`** is what lets a tool called **inside the booking agent's own subgraph** redirect the **outer** graph
- **Context engineering:** unlike the one-agent version, you decide **what messages pass between agents**. Pass the **`AIMessage` that triggered the handoff plus an artificial `ToolMessage`** acknowledging it. Models expect every tool call to have its response, so skipping either leaves the receiver with malformed history
- Do **not** pass the whole sub-agent history. It keeps the receiver focused

```python
def call_booking_agent(state: SupportState) -> dict:
    return booking_agent.invoke(state)

def route_after_agent(state) -> Literal["booking_agent", "refunds_agent", "__end__"]:
    msgs = state.get("messages", [])
    if msgs and isinstance(msgs[-1], AIMsg) and not msgs[-1].tool_calls:
        return "__end__"
    return state.get("active_agent") or "booking_agent"

builder = StateGraph(SupportState)
builder.add_node("booking_agent", call_booking_agent)
builder.add_node("refunds_agent", call_refunds_agent)
builder.add_conditional_edges(START, route_initial, ["booking_agent", "refunds_agent"])
builder.add_conditional_edges("booking_agent", route_after_agent, ["booking_agent", "refunds_agent", END])
builder.add_conditional_edges("refunds_agent", route_after_agent, ["booking_agent", "refunds_agent", END])
graph = builder.compile()
```

- *Checked:* the booking agent called `transfer_to_refunds`, the outer graph moved to `refunds_agent`, which answered. The message list had exactly four entries: the user, the triggering `AIMessage`, the artificial `ToolMessage`, and the refunds agent's reply. `active_agent` ended as `refunds_agent`
- **End a turn with an `AIMessage` that has no tool calls**, so the interface knows the agent is done
- **Prefer one agent plus middleware** for most cases. Use subgraphs when agents are structurally different, not just differently prompted

## 14.4 Pattern 3: skills

Specialist capability packaged as a **prompt the agent loads on demand**. It is **progressive disclosure**: the agent sees a short description up front, and the full content only when it asks.

- Same idea as Agent Skills, and as progressive disclosure in `llms.txt`, applied to prompts and domain knowledge. Class: it is also how Claude Code works inside
- **Traits:** prompt-driven, loaded when needed, **teams can maintain skills independently**, lighter than a sub-agent, and a skill can **point to other assets** (files, scripts) and say when to read them
- **Use it when:** one agent with many specialisations, no hard boundary needed between them. Examples: a skill per language, per knowledge domain, per output format
- **Use subagents instead** when a specialisation needs its **own conversation state**, or tools the main agent should not have by default

**The smallest version:**

```python
SKILLS = {
    "refund_policy": "Full refund if cancelled >2 hours before showtime; 50% store credit within 2 hours; none after the show starts.",
    "loyalty_program": "1 point per $1 spent; 100 points = one free ticket; points expire after 12 months.",
}

@tool
def load_skill(skill_name: str) -> str:
    """Load a specialized skill prompt.

    Available skills:
    - refund_policy: Refund and cancellation policy expert
    - loyalty_program: Loyalty points and rewards expert
    """
    return SKILLS.get(skill_name, f"Unknown skill: {skill_name}")
```

- **`load_skill(skill_name)` is the whole mechanism.** The skills are listed in the docstring or the system prompt

### The SQL assistant project

Two skills, `sales_analytics` and `inventory_management`. Each has a short `description` (shown up front) and long `content` (the schema, business rules and an example query, loaded on demand).

```python
class SkillMiddleware(AgentMiddleware):
    tools = [load_skill]                       # registered as a class variable

    def __init__(self):
        self.skills_prompt = "\n".join(f"- **{s['name']}**: {s['description']}" for s in SKILLS)

    def wrap_model_call(self, request, handler):
        addendum = (f"\n\n## Available Skills\n\n{self.skills_prompt}\n\n"
                    "Use the load_skill tool when you need detailed information.")
        new_content = list(request.system_message.content_blocks) + [{"type": "text", "text": addendum}]
        return handler(request.override(system_message=SystemMessage(content=new_content)))
```

- *Checked:* the system prompt on the **first** model call held the skill **names and descriptions** and **not** the schema text. After `load_skill("sales_analytics")`, the **tool result in the history** held the full schema
- **Why it is worth it:** less context (only the needed skills load), teams maintain skills separately, it scales to dozens or hundreds of skills, and the history stays simple, with one agent and one thread
- **Trade-offs:** the **first** load costs one extra tool round trip, and basic skills rely on **prompting, not hard rules**. Enforcing "always load A before B" needs custom logic

### Make loading a rule, not a request

Track what was loaded in state, and make a tool refuse to run otherwise.

```python
class CustomState(AgentState):
    skills_loaded: NotRequired[list[str]]

@tool
def write_sql_query(query: str, vertical: str, runtime: ToolRuntime) -> str:
    """Write and validate a SQL query for a business vertical."""
    if vertical not in runtime.state.get("skills_loaded", []):
        return f"Error: You must load the '{vertical}' skill first."
    return f"SQL Query for {vertical}: validated"
```

- *Checked:* writing before loading returned the error. Loading first, then writing, returned "validated". **The constraint is enforced in code, not just suggested in the prompt**
- **A real bug in the class code.** *Checked:* the notebook's `load_skill_tracked` returns `"skills_loaded": [skill_name]`. With no reducer, that **replaces** the list. Loading `sales_analytics` and then `inventory_management` left `skills_loaded == ['inventory_management']`, and a later sales query was **refused**
- **Two fixes, both checked** (both ended with both skills listed and "validated"):

```python
# Fix 1: give the state key a reducer, so updates append
import operator
from typing import Annotated
class CustomState(AgentState):
    skills_loaded: Annotated[list[str], operator.add]     # pass skills_loaded=[] in the first input

# Fix 2: make the tool append to what is already there
"skills_loaded": runtime.state.get("skills_loaded", []) + [skill_name]
```

### Skills that bring tools

- Idea: loading a skill should also give the agent new tools (loading `database_admin` adds `backup`, `restore`, `migrate`)
- **The notebook's demo does not do this.** `load_skill_with_tools` builds the `new_tools` list and never uses it. It only returns the skill text, and the cell prints what **would** be registered
- **The working way:** register **all** tools at `create_agent(...)` (see the gotcha in 14.2) and use the handoff-style middleware to **show only the tools whose skill is loaded**, reading `skills_loaded` from state. Not built here, though it combines two checked pieces

### Other shapes

| Dimension | Options |
|---|---|
| **Storage** | In memory (this project), files on disk (the Claude Code approach, skills as directories), remote (S3, a database, Notion, an API) |
| **Discovery** | List in the system prompt (this project), scan the file system, a registry service, or a `list_skills` tool |
| **Loading** | One load (this project), paginated for large skills, search inside a skill, or hierarchical (overview first, then drill in) |

- **Sizing guide from the notebook:** under about **1K tokens**, put it straight in the system prompt (and benefit from prompt caching). **1 to 10K:** on-demand loading starts to pay. **Over 10K:** paginate or search inside the skill
- **Hierarchical skills:** loading `data_science` could surface `pandas_expert` and `visualization`

## 14.5 Pattern 4: router

A **classification step** sends a query to specialised agents **in parallel**, and a **synthesis step** combines the answers. It suits distinct **verticals**.

- The router decomposes the query. Zero or more agents run **at the same time**. One response comes back
- **Router against subagents:** a router is a dedicated classification step, often **one structured-output call**, and keeps no conversation. A supervisor is a full agent that decides turn by turn. Use a router for clear categories and explicit parallelism, a supervisor for flexible orchestration
- The project: a **GitHub agent**, a **Notion agent** and a **Slack agent**. Asked "How do I authenticate API requests?", the router splits it into a sub-question per source

### Three state shapes

```python
import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict

class AgentInput(TypedDict):          # what each specialist receives
    query: str

class AgentOutput(TypedDict):         # what each returns
    source: str
    result: str

class Classification(TypedDict):      # one routing decision
    source: Literal["github", "notion", "slack"]
    query: str

class RouterState(TypedDict):
    query: str
    classifications: list[Classification]
    results: Annotated[list[AgentOutput], operator.add]    # reducer collects parallel results
    final_answer: str
```

- Import `TypedDict` from **`typing_extensions`**. The class notebook explains: on Python **before 3.12**, Pydantic v2 refuses the standard `typing.TypedDict` when it is used inside a model that `with_structured_output` enforces. Not run here (Python 3.13)

### The graph

```python
from langgraph.types import Send

def classify_query(state: RouterState) -> dict:
    structured = router_llm.with_structured_output(ClassificationResult)
    result = structured.invoke([{"role": "system", "content": CLASSIFY_PROMPT},
                                {"role": "user", "content": state["query"]}])
    return {"classifications": result.classifications}

def route_to_agents(state: RouterState) -> list[Send]:
    return [Send(c["source"], {"query": c["query"]}) for c in state["classifications"]]

workflow = (StateGraph(RouterState)
    .add_node("classify", classify_query)
    .add_node("github", query_github).add_node("notion", query_notion).add_node("slack", query_slack)
    .add_node("synthesize", synthesize_results)
    .add_edge(START, "classify")
    .add_conditional_edges("classify", route_to_agents, ["github", "notion", "slack"])
    .add_edge("github", "synthesize").add_edge("notion", "synthesize").add_edge("slack", "synthesize")
    .add_edge("synthesize", END)
    .compile())
```

- **Classify** uses structured output, not text parsing. Irrelevant sources are simply left out
- **`Send(node, payload)` fans out.** Returning several `Send` objects makes LangGraph run those nodes at once, each receiving **only** its own narrow input (`AgentInput`), not the whole router state
- **Synthesize** waits for every dispatched branch, and uses the original query so the answer addresses what was asked. Its prompt asks to combine without repeating, highlight what is actionable, and **note disagreements between sources**
- **`Command(goto=agent)`** routes to **one** agent. `[Send(...), ...]` fans out to several

### The reducer gotcha

*Checked:* the same fan-out with a plain `list[str]` state key raised `InvalidUpdateError: At key 'sub_answers': Can receive only one value per step. Use an Annotated key to handle multiple values.` With `Annotated[list[str], operator.add]` the answers were `from a | from b`.

- **Any state key written by more than one parallel node needs its own reducer.** It is the same thing `add_messages` does for `messages`
- The class README says the notebook found this error while verifying its own router

### Stateless and stateful routers

| Approach | Behaviour |
|---|---|
| **Stateless** | Each request routed alone, no memory |
| **Stateful, tool wrapper** | The stateless router becomes a **tool** of a conversational agent that has a checkpointer |
| **Stateful, full persistence** | The router itself holds message history. More complexity |

```python
@tool
def search_knowledge_base(query: str) -> str:
    """Search across multiple knowledge sources (GitHub, Notion, Slack)."""
    return workflow.invoke({"query": query})["final_answer"]

conversational_agent = create_agent(model, tools=[search_knowledge_base],
                                    system_prompt="Answer questions about our organization.",
                                    checkpointer=InMemorySaver())
```

- **The tool wrapper is recommended.** The agent handles memory, the router stays a clean reusable step
- Full persistence needs custom history handling, and conversations feel disjointed if agents have different tones. Consider handoffs or subagents first
- The specialist **tools** in the class project are stubs (`search_code`, `search_notion`, `search_slack` and so on) that return fixed text. Real use needs real APIs, which can come from MCP servers ([Chapter 12](12-mcp-in-langchain.md))

## 14.6 Pattern 5: custom workflow

A LangGraph graph you design by hand: sequential steps, branches, loops, parallel runs. It mixes **deterministic code** with **agents**, and can embed any other pattern as a node.

- **There is no separate API.** It is the same `StateGraph`, `START` and `END` used everywhere above. The router is itself a custom workflow
- **Use it when** the other four do not fit, or you want deterministic and agentic steps together

**An agent in a node:**

```python
def agent_node(state: SimpleState) -> dict:
    result = node_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    return {"answer": result["messages"][-1].content}
```

**A retrieval pipeline** with three kinds of node:

- **Model node (rewrite):** rewrite the query for better retrieval, ideally with structured output
- **Deterministic node (retrieve):** vector similarity search, no model
- **Agent node:** reasons over the retrieved text and can still call tools for live data

```python
rag_workflow = (StateGraph(RAGState)
    .add_node("rewrite", rewrite_query).add_node("retrieve", retrieve).add_node("agent", call_agent)
    .add_edge(START, "rewrite").add_edge("rewrite", "retrieve")
    .add_edge("retrieve", "agent").add_edge("agent", END)
    .compile())
```

- To run with no key, the class uses `DeterministicFakeEmbedding` in place of `OpenAIEmbeddings`. **Why:** building a vector store with `OpenAIEmbeddings` makes a real network call at once
- *Checked, and a limit the notebook does not state:* the fake embeddings give **arbitrary, not meaningful, neighbours**. "Interstellar showtimes" returned the Interstellar **review** and a refund policy, and "Can I get a refund?" returned a **Dune showtimes** line first. The plumbing is real. The relevance is not. **Do not read retrieval quality from a run with fake embeddings**
- *Checked:* the notebook's `rewrite_query` is `q.replace("it", "the movie")`. It also changes the letters "it" inside other words: "Is there a showing with it tonight?" became "Is there a showing wthe movieh the movie tonight?". Use a model call, or match whole words
- In production use a persistent vector store (managed Postgres with pgvector, Pinecone or similar) and `with_structured_output` for the rewrite

## 14.7 Choosing a pattern

| Optimise for | Subagents | Handoffs | Skills | Router |
|---|:-:|:-:|:-:|:-:|
| Single requests | | yes | yes | yes |
| Repeat requests | | yes | yes | |
| Parallel execution | yes | | | yes |
| Large-context domains | yes | | | yes |
| Simple, focused tasks | | | yes | |
| Direct user interaction | | yes | yes | |
| Sequential constraints | | yes | | |
| Independent team ownership | yes | | yes | some |
| Mixed deterministic and agentic logic | use a **custom workflow** | | | |

- **Model calls, from the notebook and the official documentation** (more calls means more latency and cost). *These counts were not re-run*

| Scenario | Subagents | Handoffs | Skills | Router |
|---|:-:|:-:|:-:|:-:|
| One request | 4 calls | 3 | 3 | 3 |
| The same request again | 8 (4+4) | 5 (3+2) | 5 (3+2) | 6 (3+3) |
| Three parallel topics | 5 calls, about 9K tokens | 7+, about 14K+ | 3, about 15K | 5, about 9K |

- **Subagents:** stateless by design, so strong isolation but the full flow repeats on every request. Best for parallel, large-context domains
- **Handoffs and skills:** **stateful**. Once a step or skill is active, a repeat request skips routing or loading, saving **40 to 50%** of calls on the second ask
- **Router:** stateless per request, with a classification call every time, but true parallel fan-out
- **Patterns combine freely.** A subagent can be a router inside. A handoff stage can use skills to manage its own context. **Pick per sub-problem, not once for the whole system**

## 14.8 Interview corner

**1. How do handoffs differ from subagents?**

- In handoffs one agent changes its prompt and tools from state, and talks to the user directly. In subagents a supervisor calls other agents as tools and the user only talks to the supervisor
- *Stronger answer:* handoffs have no live routing reasoning, state decides

**2. How does a handoff step change?**

- A tool returns a `Command` updating `current_step` plus a `ToolMessage`. Middleware reads the step on the next model call and swaps prompt and tools
- *Stronger answer:* tools decide state, state decides configuration

**3. Why can middleware not add a new tool at run time?**

- The agent only knows how to execute the tools it was built with. Middleware can only narrow the visible set
- *Stronger answer:* register everything up front, and keep the same checkpointer if you rebuild

**4. What must a handoff between separate agents pass on?**

- The `AIMessage` that triggered it and an artificial `ToolMessage`, not the whole history, and `graph=Command.PARENT` to redirect the outer graph

**5. What are skills, and how do they save context?**

- Short descriptions in the prompt, full content loaded through a tool only when needed
- *Stronger answer:* the first load costs a round trip, it relies on prompting unless you enforce it in state, and a tracked list needs a reducer

**6. How do you enforce "load the skill first"?**

- Track loaded skills in state and make the tool refuse otherwise
- *Stronger answer:* a plain list key gets replaced, not appended. Use a reducer

**7. Why does a parallel router need a reducer?**

- Two branches write the same key in one step, and LangGraph cannot merge them without one
- *Stronger answer:* it raises `InvalidUpdateError` otherwise

**8. How do you give a router memory?**

- Wrap the stateless router as a tool of a conversational agent with a checkpointer

**9. When would you build a custom workflow?**

- When the four patterns do not fit, or you need deterministic and agentic steps together
- *Stronger answer:* the router is itself a custom workflow

**10. Which pattern for repeated requests?**

- Handoffs or skills, since they are stateful and skip re-routing or re-loading

## 14.9 Added by Claude, not from the sources

Items marked *checked* were run with `langchain` 1.4.7 and `langgraph` 1.2.19, using a scripted stand-in model.

- **A skill list that must accumulate needs a reducer or an appending tool.** *Checked* (14.4)
- **Do not judge retrieval with fake embeddings.** *Checked* (14.6)
- **Match whole words, not substrings,** in any rewrite or classification rule. *Checked* (14.6)
- **Keep specialist descriptions disjoint,** and test them with real requests. The scripted model cannot choose
- **Make the step table the single source of truth.** In 14.2 the `STEP_CONFIG` and the registered tool list can drift. Build the registered list from the table, for example `[t for step in STEP_CONFIG.values() for t in step["tools"]]`, and drop duplicates by tool name
- **Validate transitions.** A tool that sets `current_step` can set any string. Use a `Literal` type and check allowed moves
- **Cap parallelism.** A router that fans out to many agents multiplies cost. Limit the sources a classifier may pick
- **Log each handoff.** The `active_agent` and `current_step` values are the story of a conversation. Record them with the thread id

## Recap

- **Handoffs:** state decides configuration, tools decide state. One agent with middleware, or separate agents with `Command(goto=..., graph=Command.PARENT)`
- Every `Command` update needs a `ToolMessage`. Register every tool at construction. Reuse the checkpointer if you rebuild
- Pass only the triggering `AIMessage` and an artificial `ToolMessage` between agents
- **Skills:** descriptions up front, `load_skill` for the content. Enforce loading in state, with a reducer
- **Router:** classify with structured output, `Send` to fan out, a **reducer** on any key written in parallel, then synthesise. Wrap it as a tool for memory
- **Custom workflow:** a hand-built graph with agents in nodes. It can hold all the others
- Fake embeddings test the plumbing, not relevance
- Patterns combine. Pick per sub-problem

## Practice

1. Build the support state machine. Print the tools offered at each step and the value of `current_step` after each turn
2. Offer a tool in middleware that was never registered. Read the error. Fix it
3. Return a `Command` with no `ToolMessage` and read the error
4. Build the two-agent handoff graph with `Command.PARENT`. Print the four messages
5. Build the SQL assistant with two skills. Load both, then try a query for the first. Fix the list with a reducer
6. Build a router with `Send`. Remove the reducer and read the error
7. Wrap the router as a tool of a conversational agent with a checkpointer
8. Build the retrieval pipeline with fake embeddings, then say why its results cannot be trusted
9. Combine two patterns: a supervisor whose sub-agent is a router

## How this chapter was checked

- Run with a scripted stand-in model: the four-turn support state machine and the tools offered at each step; the missing-`ToolMessage` error; the unregistered-tool error; the `requires` check; going back with the same checkpointer; the `Command.PARENT` subgraph handoff; router fan-out with and without a reducer; skills injected into the prompt and loaded into history; the tracked-skills gate, the replacement bug and two fixes; the fake-embedding retrieval; and the naive `replace`
- The model-call counts, token figures, skills-with-tools, summarisation, the Python-before-3.12 `TypedDict` message, and every "production wiring" cell with a real model were **not run**
- **No real model was used.** Whether a real model classifies or chooses well was not tested
- The class notebooks and README are the source for everything not marked *checked*

## Sources and further reading

- Live-Class-2026, `Weekend 14 - Oct 3 & Oct 4/Multi Agents in Langchain/`: `README.md`, `00_Multi_Agent_Overview.ipynb`, `02_Handoffs_Customer_Support.ipynb`, `03_Router_Knowledge_Base.ipynb`, `04_Skills_SQL_Assistant.ipynb`, `LangChain_MultiAgent_Patterns_VSCode.ipynb`
- Live-Class-2026, `classes_transcription_summary/23 - 27 Sep - MCP In LangChain.md` (pattern table and class questions, in [Chapter 13](13-multi-agent-systems-and-subagents.md))
- Sections marked *checked* and 14.9 are from testing

Previous: [Chapter 13, Multi-agent systems and subagents](13-multi-agent-systems-and-subagents.md) · Next: [Chapter 15, Interview questions](15-interview-questions.md)
