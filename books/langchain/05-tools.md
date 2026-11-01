# Chapter 5: Tools

A raw model has no idea what functions exist in your code. This chapter covers how LangChain tells a model about tools, what comes back, and how the result is returned to the model. It is the LangChain version of the by-hand loop in [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md).

*Status: class 08 (sections 5.1–5.3) and class 10, Tools Deep Dive (sections 5.4–5.10), are written. The Student_Reference notebook and the TripMate project are not processed yet.*

## 5.1 Binding: making the model aware

A model cannot know a `get_weather()` function exists just because it sits in the same file. **Binding** is the explicit act of telling the model which tools exist and what each does. Binding only makes the model **aware**. It never connects the model to live execution.

```python
def get_weather(location: str) -> str:
    """Get the current weather at a given location."""
    return f"It's sunny in {location}"

# Step 1: bind the tool(s): the model now knows they exist
model_with_tools = model.bind_tools([get_weather])

# Step 2: invoke as usual: the model decides whether a tool is needed
response = model_with_tools.invoke("What is the weather in Delhi?")

# Step 3: inspect what the model decided
print(response.tool_calls)
# [{'name': 'get_weather', 'args': {'location': 'Delhi'}, 'id': '...'}]
```

What happens on `.invoke()`: the model reads the user's message together with the schema of every bound tool and chooses one of two things. It replies in plain text, or it replies with a **tool call** instead of content. When it chooses a tool call, `response.content` comes back **empty** and everything useful lives in `response.tool_calls`: the tool's name, the arguments, and a unique ID. The class showed this live, with an empty `content` and `location: "Delhi"` in `tool_calls`.

**Binding does not run the tool.** Calling `.invoke()` after binding only asks the model to decide whether and how it would call a tool. Your code has to read `response.tool_calls`, call the real function, capture the return value and feed the result back. That is exactly the loop built by hand in LLM Chapter 2. `create_agent()` automates the whole cycle, but binding alone does not.

Other points from class:

- A plain Python function can be bound directly, with no hand-written JSON schema, unlike the raw approach in LLM Chapter 2. This works through LangChain's `ChatOpenAI` wrapper, not a bare OpenAI SDK object. The class confirmed that by inspecting the object's metadata, which shows LangChain fields on top of the OpenAI response.
- A **docstring still matters**. A tool without one risks the model guessing its purpose wrongly.
- Binding takes a list. A second tool (the class used a `set_password(new_pass: str)` function) goes in the same `bind_tools([...])` call, and the model picks the one that matches the request from each tool's name and docstring.

## 5.2 Returning the result: `ToolMessage`

A learner asked the mentor to show what happens between "call this tool" and the final answer. He live-coded it:

1. The model decides a tool is needed. `response.content` is empty and the instruction is in `response.tool_calls`, with the name, the arguments and an ID.
2. You look up and call the real function with those arguments (`get_weather(location=...)`). This is not automatic just because a tool was bound.
3. You wrap the function's return value in a **`ToolMessage`** and send it back. A plain string appended to the messages is not enough, because `ToolMessage` carries the `content` (the result) together with the same `tool_call_id` the model issued, so the model can match the answer to its own request.

`ToolMessage` can also carry a **`status`** field (success or failure) and an **`artifact`** field, which are useful for tracing and observability in a real agent later.

### Two audiences for one result

```python
from langchain_core.messages import ToolMessage

tool_message = ToolMessage(
    content="It was the best of times, it was the worst of times.",
    tool_call_id="call_123",
    name="search_books",
    artifact={"document_id": "doc_123", "page": 0},   # the MODEL never sees this
)
print("What the MODEL sees:", tool_message.content)
print("What your APP can use:", tool_message.artifact)
```

`.content` goes to the model and `.artifact` is for your application. This matters when a tool has more to hand back than the model needs. A retrieval tool can return the passage as `.content` and attach a document ID as `.artifact` so the app can build a citation link later.

*Source: Live-Class-2026, `classes_summary/08`, `classes_transcription_summary/08`. Not run: LangChain is not installed in my sandbox.*

## 5.3 Completing the loop by hand, once

The revision notebook walks the whole mechanism once, so that `create_agent` later feels like a shortcut for real work and not magic. Bind two tools, ask for something, run the tool the model requested, wrap the result, and send everything back:

```python
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def get_weather(location: str) -> str:
    """Get the weather at a location."""
    return f"Sunny in {location}"

def set_password(new_pass: str) -> str:
    """Set a new password."""
    return "Password changed"

TOOLS = {"get_weather": get_weather, "set_password": set_password}
model_with_tools = model.bind_tools([get_weather, set_password])

question = HumanMessage("Set the password to admin123")
response = model_with_tools.invoke([question])

# 1. the model's REQUEST: nothing has run yet
requested_call = response.tool_calls[0]

# 2. run the tool the model asked for (this is the step create_agent automates)
tool_result = TOOLS[requested_call["name"]](**requested_call["args"])

# 3. wrap it as a ToolMessage with the EXACT tool_call_id from the request
tool_message = ToolMessage(content=tool_result, tool_call_id=requested_call["id"])

# 4. send the question, the AI's tool request and the result back for the final answer
conversation = [question, AIMessage(content="", tool_calls=[requested_call]), tool_message]
final_response = model.invoke(conversation)
print(final_response.content)
```

Request, run, wrap, send back: that is the loop from LLM Chapter 2, written with LangChain's message classes.

**Source quirk.** In the notebook, step 2 reads `get_weather(**requested_call["args"])` even though the model asked for `set_password` (the argument is `new_pass`, not `location`). I tested the call: it raises `TypeError: get_weather() got an unexpected keyword argument 'new_pass'`. The version above looks the tool up by the name the model gave, which is the correct way.

*Source: `Revision_Parts_1-4.ipynb`. Not run against a model: LangChain is not installed and the call needs a key. I checked the tool lookup on its own.*

## 5.4 A tool is a function with a job description

Class 10 starts from CineBot being asked "Is Interstellar showing tonight at 7pm?" and honestly answering that it has no live showtimes. A model is a brain with no hands. A tool is the hand, and it is nothing more than a function: if you can write a function that calls an API or a database, you can make it a tool.

```python
from langchain_core.tools import tool

@tool
def check_showtimes(movie_title: str) -> str:
    """Get available showtimes for a given movie."""
    return "Interstellar: 7:00 PM, 9:30 PM"
```

By default the **function name** becomes the tool's name and the **docstring** becomes its description. The description is what is sent to the model, so it is the model's only clue about what the tool does and when to use it.

You can override both without touching the function, which helps when you wrap code someone else named:

```python
@tool("book_seats", description="Book or reserve a seat. Use whenever a customer wants to book.")
def reserve(movie: str, seats: int) -> str:
    """A short internal docstring."""
    return f"Reserved {seats} seat(s) for {movie}"
```

LangChain also ships ready-made tools. The class's example was web search through Tavily (`from langchain_tavily import TavilySearch`; install the package and set an API key).

## 5.5 Argument schemas: `args_schema` and `Field()`

Plain type hints work, but tell the model little. A Pydantic schema passed as `args_schema` gives it descriptions, limits and defaults:

```python
from pydantic import BaseModel, Field
from typing import Literal

class SeatBookingInput(BaseModel):
    movie_title: str = Field(description="Exact movie title")
    seat_count: int = Field(gt=0, description="Number of seats")
    preferred_row: Literal["front", "middle", "back"] = Field(default="middle")

@tool(args_schema=SeatBookingInput)
def book_seats(movie_title: str, seat_count: int, preferred_row: str) -> str:
    """Book seats for a movie."""
    return f"Booked {seat_count} seat(s) for {movie_title} in the {preferred_row} row"
```

Print `book_seats.args`. Without `args_schema` it shows little; with it you see the descriptions, the "greater than zero" limit and the default. Two rules from the Q&A: the schema's field names must match the function's parameter names exactly (no automatic mapping), and plain Python does not check types at runtime, so it is Pydantic that adds enforcement.

A richer schema costs a few extra tokens. The class's argument: aim for the right answer in the fewest total round-trips. Skipping the schema, getting malformed input and retrying costs more than the extra 20–30 tokens (the mentor's figure). A function with no `@tool` at all is also accepted, but you lose this argument detail.

## 5.6 Two names you cannot use: `config` and `runtime`

```python
@tool
def get_weather(location: str, config: str) -> str:
    """Get weather for a location."""
```

This **defines without any error** and fails only when an agent actually calls it. `config` and `runtime` are reserved parameter names that LangChain uses itself. Why not catch it at definition time? The explanation given: LangChain cannot know at definition time how the function will be used, because the same function might be reused in another framework where those names are not reserved, so it raises the error only once it runs inside a LangChain agent. Python also has no compile-time type checking of its own. The fix is simply a different name.

*Source quirk.* The class write-up says only that it is a "runtime error". The assignment answer key says the framework intercepts `config` and you typically get a `TypeError` about a missing required argument. I could not run it, so I state only that the call fails. Whether nesting `config` or `runtime` inside a schema gets around the restriction was left unconfirmed in class.

## 5.7 Binding versus running, once more

The class repeated the point from 5.1 because it is the most misunderstood one: after `bind_tools`, the model **can never run a tool itself**. It can only request a call. For the CineBot request "Is Interstellar showing tonight, can you book two seats?" the `content` came back empty and `response.tool_calls` held the tool name (`book_seats`) and arguments (movie "Interstellar", two seats, middle row), plus a `config` value the model tried to fill in, a live reminder of why that name is off limits. Something has to read the request, run the function and send back the result. That something is the agent harness from Chapter 6.

## 5.8 Four kinds of tool

| Kind | What it is |
|---|---|
| Custom function | Your own `@tool` function (this chapter so far) |
| Built-in LangChain tool | Pre-built, such as Tavily web search |
| Server-side (provider) tool | Runs on the model provider's servers, such as web search or a code interpreter in a chat product. You neither write nor run it |
| JSON-schema tool | The schema is written directly as JSON, with no Python function. Valid, but the class prefers Pydantic as easier to read |

The server-side kind is the odd one out: when a chat product searches the web, that search is not on your machine and not a tool you control.

## 5.9 `ToolRuntime`: what the tool sees that the model does not

The class's analogy: the model only sees its own reflection in a mirror. It sees only the arguments a tool declares. The tool itself can see more, through a `runtime` parameter:

```python
from langchain.tools import ToolRuntime

@tool
def get_weather(location: str, runtime: ToolRuntime) -> str:
    """Get weather for a location."""
```

Print this tool's `.args` and only `location` appears. The assignment answer key says LangChain hides it by recognising the `ToolRuntime` type annotation on the parameter named `runtime` (the Weekend 05 folder README says the same: any `ToolRuntime`-annotated parameter is excluded).

What `runtime` holds:

| Part | What it is | How long it lasts |
|---|---|---|
| `state` | The conversation so far, mutable | This conversation only |
| `context` | Immutable settings given when the agent is invoked, such as whether a user is on a paid plan | One invocation; pass it again on every call |
| `store` | Long-term memory | Across separate conversations |
| `stream_writer` | Live progress updates such as "searching..." | While the tool runs |
| execution info | Thread ID, run ID, attempt number | The run |
| server info | Metadata when running on a LangGraph server | The run |

The class says every serious agent framework has some version of this. LangChain is just the concrete example.

## 5.10 A tool with memory, `return_direct` and gating

With `runtime.store` a tool stops being stateless. This is the class demo, with the memory written and read by two tools:

```python
from langgraph.store.memory import InMemoryStore
from langchain.tools import ToolRuntime, tool

loyalty_store = InMemoryStore()

@tool
def save_favorite_genre(customer_id: str, genre: str, runtime: ToolRuntime) -> str:
    """Save a customer's favorite movie genre for future visits."""
    runtime.store.put((customer_id, "preferences"), "favorite_genre", {"value": genre})
    return f"Got it! I'll remember you like {genre} movies."

@tool
def recall_favorite_genre(customer_id: str, runtime: ToolRuntime) -> str:
    """Recall a customer's favorite genre if previously saved."""
    result = runtime.store.get((customer_id, "preferences"), "favorite_genre")
    return f"Your favorite genre is {result.value['value']}" if result else "No saved preference."

agent = create_agent(model=model, tools=[save_favorite_genre, recall_favorite_genre], store=loyalty_store)
```

*Source quirk.* The class write-up's snippet calls `runtime.store.put(customer_id, "preferences", {...})` (three loose arguments). The Weekend 05 folder README (code from the class 10 reference notebook) and the assignment solution both use a **tuple namespace** as in the code above, `put((customer_id, "preferences"), key, value)`, so that is the form to use. The key `"favorite_genre"` and the `{"value": genre}` shape follow that README; the class write-up used slightly different names.

`InMemoryStore` is a dictionary in RAM. Nothing survives a restart, so production uses a database-backed store such as Postgres. How well a store scales is a database question, not LangChain's. It is general-purpose storage, not only for chat history, and using LangGraph's store inside LangChain is not mixing frameworks, since LangChain is built on LangGraph.

**`return_direct`.** The Q&A explains this option as sending a tool's raw output straight to the user and skipping the model's final pass. The reason to use it is when the model rewording an output (a refund policy, say) could change its meaning. It cannot be combined with a model double-check, because that puts the model back in the loop. The class did not show the syntax, so I give none here.

**Gating a tool.** Telling the model in the system prompt not to use a tool relies on the model obeying. Removing the tool before the call does not. The class's VIP example:

```python
@wrap_model_call
def gate_vip_tools(request, handler):
    is_vip = request.state.get("is_vip_member", False)
    if not is_vip:
        request = request.override(tools=[t for t in request.tools if t.name != "vip_lounge_booking"])
    return handler(request)
```

For a non-VIP the tool is not on the model's menu at all. Mentioning VIP status in the prompt does not make a VIP tool available either; a tool that is not in the list is not available. This is middleware, which is the next class's topic.

*Source quirk.* The assignment solution for B3.2 passes `"is_premium_member": True` inside the invoke input next to `messages`. For that to be readable in `request.state`, the field would need to exist in the agent's state. I have not verified this. Treat it as unverified until tested.

### Loading and calling tools

The Q&A separates two ideas. Dynamic tool **calling** is the default: the model picks which available tool to use. Dynamic tool **loading** decides, before the model is called, which subset of a large set (25–50 tools, the class's range) to show it. MCP is not an alternative to loading: it is a packaged set of tools, and loading is about which of any tools are exposed.

### Assignment questions on this chapter (Q18–Q24)

The answer key's short answers, for revision:

- **The docstring as the tool's pitch to the model.** Largely true, since the model reads it to decide whether and when to call the tool. Even a tool that is always the only option can suffer if the docstring is poor.
- **Plain string versus `Command`.** A string only answers. A `Command` can write to agent state. The key's example: a tool that raises a customer's loyalty tier and must also store the new tier for later tools. `Command` has not been taught in the course material I have processed so far; treat this as an answer-key pointer only.
- **`wrap_model_call` versus the system prompt.** The first removes the tool structurally; the second only asks.
- **Headless tool.** Per the key: the schema is registered on the server, but execution happens on the client (a browser, for example) through an interrupt and resume. Its example is reading the browser's geolocation. This was also not covered in the class material I have read so far.

## Practice

1. Run `bind_tools()` on a simple function, call `.invoke()`, and inspect `response.tool_calls`. Remember that nothing has executed yet.
2. Call the real function yourself with the extracted arguments and send the result back as a `ToolMessage`.
3. Build a `ToolMessage` with an `.artifact` and confirm the model's answer never mentions it.
4. Write a `@tool` with a clear docstring, then override its name and description and compare what the model sees.
5. Make an `args_schema` with a constraint and a default. Print `.args` with and without it.
6. Give a tool a parameter called `config` or `runtime` (as a normal argument) and watch the failure when an agent calls it.
7. Add `runtime: ToolRuntime` to a tool and print `.args` to confirm the model never sees it.
8. Rebuild the save and recall genre tools with `InMemoryStore` and prove the memory survives two separate `.invoke()` calls.
9. Assignment B1.1, B2.2, B3.1 and B3.2: a table-availability tool, an order tool with `args_schema`, a dietary-preference memory pair, and a gated private-dining tool, all for the GreenPlate restaurant assistant.

## Sources and further reading

- Live-Class-2026, `classes_summary/08 - 19 Jul - Inside the Model.md`
- Live-Class-2026, `classes_transcription_summary/08 - 19 Jul - LangChain - Inside the Model.md`
- Live-Class-2026, `classes_summary/10 - 26 Jul - Tools Deep Dive.md` and the matching `classes_transcription_summary/10`
- Live-Class-2026, `Weekend 05 - 25-26 Jul/` overview and folder READMEs, `Langchain-Tools.ipynb` (two Mermaid diagrams only), and the `Assignment & Questions/` assignment and solutions notebooks
- Colab used in class (Student Reference, class 10): https://colab.research.google.com/drive/1KlOpWf5-KIwsA0UaqWH98eISyZZQphXD?usp=sharing

- Live-Class-2026, notebooks `02_03_environment_models_messages_student_notes.ipynb` and `Revision_Parts_1-4.ipynb` in `Weekend 04 - 18-19 Jul/07-08 - .../Notebook For Reference/`

Previous: [Chapter 4](04-structured-output.md) · Next: [Chapter 6, Agents and memory](06-agents-and-memory.md) (not written yet)
