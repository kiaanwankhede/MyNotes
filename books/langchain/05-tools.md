# Chapter 5: Tools

A raw model has no idea what functions exist in your code. This chapter covers how LangChain tells a model about tools, what comes back, and how the result is returned to the model. It is the LangChain version of the by-hand loop in [LLM, Chapter 2](../llm/02-the-agentic-loop-in-pure-python.md).

*Status: only the class 08 material (binding and `ToolMessage`) is written. Class 10, Tools Deep Dive, is not processed yet and will extend this chapter.*

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

## Practice

1. Run `bind_tools()` on a simple function, call `.invoke()`, and inspect `response.tool_calls`. Remember that nothing has executed yet.
2. Call the real function yourself with the extracted arguments and send the result back as a `ToolMessage`.
3. Build a `ToolMessage` with an `.artifact` and confirm the model's answer never mentions it.

## Sources and further reading

- Live-Class-2026, `classes_summary/08 - 19 Jul - Inside the Model.md`
- Live-Class-2026, `classes_transcription_summary/08 - 19 Jul - LangChain - Inside the Model.md`

- Live-Class-2026, notebooks `02_03_environment_models_messages_student_notes.ipynb` and `Revision_Parts_1-4.ipynb` in `Weekend 04 - 18-19 Jul/07-08 - .../Notebook For Reference/`

Previous: [Chapter 4](04-structured-output.md) · Next: [Chapter 6, Agents and memory](06-agents-and-memory.md) (not written yet)
