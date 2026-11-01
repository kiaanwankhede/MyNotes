# Chapter 12: MCP in LangChain

**After this chapter you can:**

- Explain that, to an agent, an MCP server is just another source of tools
- Name the two LangChain MCP packages and say which one this chapter uses
- Connect an agent to one server, several servers, or a group of servers
- Say what the adapter turns MCP results, errors and structured data into
- Spot destructive tools from their annotations and guard them with human-in-the-loop
- Explain why the class's elicitation demo fails on a modern connection, and the two ways that work
- Add bearer authentication, and explain why per-user credentials matter in a deployed app

**Builds on:** [Chapter 5](05-tools.md) (tools), [Chapter 11](11-runtime-and-human-in-the-loop.md) (human-in-the-loop, interrupts) and the whole [MCP book](../mcp/01-why-mcp-exists.md), especially [Chapter 6](../mcp/06-deployment-and-building-a-client.md) (your own client) and [Chapter 7](../mcp/07-legacy-vs-modern-mcp.md) (legacy and modern).

**Not covered yet:** the multi-agent half of class 23 (context isolation, patterns). It goes in [Chapter 13](13-multi-agent-patterns.md).

## 12.1 An agent just needs tools

- An agent has a **brain** (the model). It reads each tool's **name and description** and decides which to call
- For a long time those tools were functions written by hand
- **MCP changes where tools come from.** The agent connects to tools that others built and published
- Once connected, the agent uses an MCP server's tools **exactly like any other tool**. The agent loop does not change
- The only question: how does a LangChain agent, which speaks messages, tools and tool messages, connect to a server that speaks MCP?

## 12.2 The adapter: a translator on top of the FastMCP client

- **The adapter** sits between the agent and any MCP server, local or remote
- It is built on the **FastMCP client** ([MCP, Chapter 6](../mcp/06-deployment-and-building-a-client.md)), which handles four jobs so LangChain does not:
  - **transport inference:** STDIO or HTTP
  - **protocol negotiation:** legacy or modern ([MCP, Chapter 7](../mcp/07-legacy-vs-modern-mcp.md))
  - **connection management**
  - **authentication**
- Class picture: **a universal translator.** Everything the server returns is re-expressed in LangChain's own words
- **`adapter.list_tools()` and not `client.list_tools()`.** A plain client returns tools too, but not as LangChain tools. The adapter's whole job is compatibility. Class analogy: a **decorator** around the MCP client
- The `async` syntax is ordinary asynchronous Python. Study it separately if it is new
- **The same idea works for any framework.** A CrewAI, AutoGen or ADK adapter would be a translator from MCP into that framework's own vocabulary

## 12.3 Two packages, and why the class demo failed

| | `langchain.mcp` (this chapter) | `langchain-mcp-adapters` (older) |
|---|---|---|
| Install | `pip install "langchain[mcp]>=1.4.0"` | `pip install langchain-mcp-adapters` |
| Entry point | `MCPAdapter(target)` then `await adapter.list_tools()` | `MultiServerMCPClient({...})` then `await client.get_tools()` |
| Built on | FastMCP | the official `mcp` SDK |
| Status | **Beta**. It warns that the API may change | Mature |

- **Why the first class demo failed:** the notebook was written for `langchain` **0.3.25**. That version has no `mcp` extra, and the pip output printed "does not provide the extra 'mcp'". The `langchain.mcp` module needs a newer `langchain`. The class transcript also said this: the package was in beta and needed a newer release than the notebook environment had
- *Checked:* with `langchain` **1.4.7** installed through `langchain[mcp]`, `from langchain.mcp import MCPAdapter` worked. It printed a beta warning. The module exposes `MCPAdapter`, `MCPToolArtifact`, `as_langchain_tool` and an `elicitation` module
- *Checked:* `MCPAdapter` has only **two public members: `list_tools` and `client`.** There is no `get_resources` or `get_prompt` (see 12.10)
- **The class's own illustration** (`MCPAdapter(server)`, `list_tools()`, `create_agent(...)`) matches this API. The class notes say the import path was not legible in the recording

> **Do not install both packages in one environment with FastMCP 4.** *Checked:* installing `langchain-mcp-adapters` replaced `mcp` 2.3.0 with 1.30.0, and `import fastmcp` then failed with "FastMCP server support is not installed". Use a separate virtual environment for each

## 12.4 Connecting: the quick start

```python
from pathlib import Path
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from fastmcp.client.transports import PythonStdioTransport

transport = PythonStdioTransport(script_path=Path("cinebot_mcp_server.py"),
                                 log_file=Path("cinebot_mcp_server.log"))

async with MCPAdapter(transport) as adapter:
    tools = await adapter.list_tools()
    print("Available tools:", [t.name for t in tools])
    agent = create_agent(model="openai:gpt-5-mini", tools=tools)
    result = await agent.ainvoke({"messages": [("user", "What are the showtimes for Interstellar?")]})
```

- The server is the CineBot example. It has three tools: `check_showtimes`, `cancel_booking` (marked destructive) and `get_seat_map` (returns structured data)

```python
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

mcp = FastMCP("CineBot")

@mcp.tool()
def check_showtimes(movie_title: str) -> str:
    """Check available showtimes for a movie."""
    fake_showtimes = {"interstellar": "7:00 PM and 10:15 PM", "dune part two": "9:30 PM"}
    return fake_showtimes.get(movie_title.lower(), "No showtimes found.")

@mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
def cancel_booking(booking_id: str) -> str:
    """Cancel an existing booking. Irreversible."""
    return f"Booking {booking_id} cancelled."

@mcp.tool()
def get_seat_map(movie_title: str) -> dict:
    """Get the seat map for a movie -- returns structured data, not just text."""
    return {"movie": movie_title, "available_rows": ["A", "B", "C"], "sold_out_rows": ["D"]}

if __name__ == "__main__":
    mcp.run()
```

- *Checked:* `list_tools()` returned the three tools as `StructuredTool` objects, ready for `create_agent`
- **The repo's `cinebot_mcp_server.py` is a different version.** It holds only `check_showtimes`, because the multi-server notebook overwrote it. Its log file shows an earlier crash: `ToolAnnotations` was used before it was imported. Add the `mcp.types` import, as above
- **What the target can be** (checked from the adapter's own documentation):
  - an `http` or `https` **URL**
  - a **`Path`** to a local script, launched over STDIO
  - a **FastMCP transport**, an **in-process FastMCP server**, an already built **client**, or an **MCP config** dictionary
  - a **bare string that is not a URL is refused.** *Checked:* `MCPAdapter("/path/to/server.py")` raised `ValueError`. The reason in its documentation: a string often comes from configuration or from a model, and a path string would launch a local program

### Call a tool without any agent

```python
async with MCPAdapter(transport) as adapter:
    tools = await adapter.list_tools()
    showtime = next(t for t in tools if t.name == "check_showtimes")
    print(await showtime.ainvoke({"movie_title": "interstellar"}))
    # [{'type': 'text', 'text': '7:00 PM and 10:15 PM', 'id': 'lc_...'}]
```

- Handy for testing a tool before any model is involved
- To get a full `ToolMessage` back (with status and artifact), pass a **tool call dictionary**: `{"name": ..., "args": {...}, "id": "c1", "type": "tool_call"}`

## 12.5 What the adapter translates

| MCP side | What the adapter makes |
|---|---|
| Tool result | Content blocks the model can read |
| Structured content | An **artifact** on the tool message, not part of the text the model reads |
| A tool that ran and reported failure | A tool message with `status="error"` |
| A transport or session failure | An **exception** (nothing came back to convert) |
| An elicitation request | A LangGraph **interrupt** (12.7) |

**Content types** (from the class notebook's table):

- `TextContent` becomes a text block
- `ImageContent` becomes an image block (base64 and mime type)
- `ResourceLink` with an image mime type becomes an image block by URL. Any other link becomes a file block
- `EmbeddedResource` text becomes a text block. A blob becomes an image or file block by mime type
- `AudioContent` is **not yet supported** and raises `NotImplementedError`
- Only text was run here. The rest is from the notebook's table

**Structured data** *(checked)*. For `get_seat_map`:

```python
msg = await seat_map_tool.ainvoke({"name": "get_seat_map",
                                   "args": {"movie_title": "Interstellar"},
                                   "id": "c1", "type": "tool_call"})
msg.content    # [{'type': 'text', 'text': '{"movie":"Interstellar","available_rows":["A","B","C"],...}'}]
msg.artifact   # {'structured_content': {'movie': 'Interstellar', 'available_rows': ['A', 'B', 'C'], ...}}
msg.artifact["structured_content"]["available_rows"]   # ['A', 'B', 'C']
```

- **Content is what the model reads. The artifact is what your code can use.** Your code gets real data and the model's context is not widened

**Errors** *(checked)*. A server whose tool raises `ValueError`:

- The result came back as a `ToolMessage` with **`status='error'`** and the text "Error calling tool 'risky_lookup': Invalid booking ID format: '12345'. Expected it to start with 'BK'."
- A good call on the same tool gave `status='success'`
- The agent can **read the error and correct itself**, like any tool error in this course
- A **transport failure** raises an exception, because there is no message to give the model. Not run here

## 12.6 Destructive tools and human-in-the-loop

- Tool **annotations** travel with each tool. *Checked:* the adapter puts them at `tool.metadata["mcp"]["tool"]["annotations"]`, and the key is **`destructive_hint`** (snake case), not `destructiveHint`
- Use it to build the human-in-the-loop configuration **from what the server declared**, instead of listing tool names by hand:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

def is_destructive(tool):
    ann = (tool.metadata or {}).get("mcp", {}).get("tool", {}).get("annotations", {})
    return bool(ann.get("destructive_hint"))

async with MCPAdapter(transport) as adapter:
    tools = await adapter.list_tools()
    interrupt_on = {t.name: {"allowed_decisions": ["approve", "edit", "reject"]}
                    for t in tools if is_destructive(t)}
    agent = create_agent(model, tools=tools,
                         middleware=[HumanInTheLoopMiddleware(interrupt_on=interrupt_on)],
                         checkpointer=InMemorySaver())
```

- *Checked, with a scripted stand-in model:* `interrupt_on` was `{'cancel_booking': {...}}` and nothing else. The agent ran `check_showtimes` freely, then **paused** at `cancel_booking`. After `Command(resume={"decisions": [{"type": "approve"}]})` the cancellation ran and returned "Booking BK9 cancelled."
- A **checkpointer** and a `thread_id` are needed to pause and resume ([Chapter 11](11-runtime-and-human-in-the-loop.md), 11.11)
- **Caveat:** an annotation is a hint from the server's author. A server can leave it off. Treat it as one input, not a guarantee

## 12.7 Elicitation as a LangGraph interrupt

- **Elicitation:** a server pauses a tool call to ask the user something ([MCP, Chapter 3](../mcp/03-lifecycle-json-rpc-and-capability-negotiation.md), 3.9)
- **The adapter's design:** it answers elicitation with a **LangGraph `interrupt()`**. The person already reviewing the agent's work answers, and the run **resumes**. It ties back to human-in-the-loop
- **Why it must be a LangGraph interrupt:** a LangChain agent stops only for **its own kind** of interrupt. Class analogy: telling a Hindi speaker "ruko". A generic interrupt might be caught, but the agent **keeps working**
- **All the concepts are the same as in MCP.** The adapter re-expresses them in the agent's language

```
Agent → adapter : call cancel_booking(...)
adapter → server: tools/call
server → adapter: "I need more input"        (an input-required result)
adapter → agent : interrupt()                (the graph pauses)
      ... a person answers, outside the graph ...
agent → adapter : Command(resume={"responses": {key: answer}})
adapter → server: tools/call again, with the answer
server → adapter: final result
```

*Not run end to end here. The shape is from the class notebook.*

### Why the class demo showed an error

The notebook's own output for the elicitation cell was `status: error`, with the text *elicitation via server-initiated requests is unavailable on 2026-07-28 connections.* *Checked: the same result here.* The reasons:

- The class server asks with **`ctx.elicit(...)`**, which is the **legacy** way: the server sends its own request to the client
- A **modern** connection has no such back channel ([MCP, Chapter 7](../mcp/07-legacy-vs-modern-mcp.md), 7.3)
- The adapter's interrupt loop is built for the modern way: a server that returns an **input-required result** and expects the call to be **retried with the answers**

**Two ways that work** *(checked)*:

1. **Make the server return its request as an `InputRequiredResult`.** The installed library's documentation names this route. *Not built or run here*
2. **Give the client its own `elicitation_handler`** and use legacy mode. The adapter respects a handler you supply:

```python
from fastmcp.client import Client

async def handler(message, response_type, params, context):
    print("asked:", message)
    return True

client = Client(transport, mode="legacy", elicitation_handler=handler)
async with MCPAdapter(client) as adapter:
    ...
```

- *Checked:* with this client the same tool printed "asked: Confirm cancellation of booking BK1?" and returned "Booking BK1: cancelled."
- *Checked:* a legacy client **without** a handler gave `status: error` with the message "This MCP server asked for input over the legacy server-initiated elicitation path, which interrupt-based elicitation cannot answer. It needs a server that returns its requests as an `InputRequiredResult`, or a pre-built client with your own `elicitation_handler`."
- **Only elicitation is answered.** The adapter refuses sampling and roots requests

## 12.8 Several servers: config or client group

| | MCP config dictionary | Client group |
|---|---|---|
| What it is | One **aggregate** connection across several servers | **Independent** connections, one per server |
| Tool names | Prefixed by the key you chose | `server_tool` automatically |
| Protocol era | **Shared**: the fleet negotiates down to the oldest era any member needs | **Independent**: each member keeps its own era and auth |
| Use when | Simple fleets | Servers that need different credentials or modes |

```python
from fastmcp.client import Client
from fastmcp.client.group import ClientGroup

group = ClientGroup({
    "cinebot": Client(Path("cinebot_mcp_server.py")),
    "errors":  Client(Path("cinebot_error_server.py"), mode="legacy"),
})
async with MCPAdapter(group) as adapter:
    tools = await adapter.list_tools()
```

- *Checked:* both ways gave `cinebot_check_showtimes`, `cinebot_cancel_booking`, `cinebot_get_seat_map` and `errors_risky_lookup`. A call through the group to `errors_risky_lookup` returned "Booking BK7: confirmed."
- *Checked:* a group can mix a default client with a **legacy** one. **This is how a legacy and a modern server run side by side**
- A group **routes each call back to the client that advertised that tool**, and namespaced names stop two servers' identical tool names from colliding
- **Version handling stays out of the agent's way.** FastMCP negotiates per connection. As the class put it, the agent should only worry about getting tools
- A **single server** target accepts one URL, path or in-memory server. You cannot pass several this way
- **An in-memory server** defined in your own code can be passed straight in

### A demo that survives a bad network

The multi-server notebook connects to **each server in its own `try` and `except`** and merges whatever succeeds, instead of a group:

```python
all_tools, status = [], {}
for name, target in targets.items():
    try:
        async with MCPAdapter(target) as adapter:
            tools = await adapter.list_tools()
            all_tools.extend(tools)
            status[name] = f"OK -- {[t.name for t in tools]}"
    except Exception as e:
        status[name] = f"FAILED -- {type(e).__name__}: {e}"
```

- One server being down does not stop the demo. It is useful in front of an audience
- The notebook's three servers: the local CineBot over STDIO, **Context7** (free, public, works without a key at lower rate limits), and the class TimeTrack server on a hosted URL
- In its live output the agent's tool list showed Context7's two tools **three times**. That is probably from re-running the cell that appends to the list. Reset the list before reconnecting
- The two remote servers were **not run here** (no network access to them)
- In the live run the agent asked a clarifying question about "MCP" before using Context7. Give such questions context, or the model will guess

## 12.9 Authentication, and the per-user trap

**Auth is set on the FastMCP client, not on the adapter.** The adapter wraps whatever client you give it. Anything FastMCP's client accepts works.

| Need | Pattern |
|---|---|
| Bearer token | `Client(url, auth=token)` |
| OAuth 2.1 (discovery, browser, token exchange) | `Client(url, auth="oauth")` |
| OAuth that survives restarts | A pre-built OAuth provider with a token store. By default tokens sit in memory, so every run repeats the browser step |
| A different auth per server | A client group, each member with its own `auth=` |
| Per-user auth in a deployment | See below |

- *Checked, bearer token:* a server with a static token check. The client with the right token listed `check_showtimes`. A **wrong token** and **no token** both failed with an MCP error
- OAuth was shown in class by connecting a Drive connector in Claude: the browser opens, you authorise, tokens are exchanged. Not run here
- The notebook's server code for the check:

```python
from fastmcp import FastMCP
from fastmcp.server.auth import AccessToken, TokenVerifier

AUTH_TOKEN = "cinebot-secret-token"      # a teaching value; never use a fixed token like this for real

class StaticTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken | None:
        if token == AUTH_TOKEN:
            return AccessToken(token=token, client_id="cinebot-client", scopes=[])
        return None

mcp = FastMCP("CineBot", auth=StaticTokenVerifier())
```

- **Bearer tokens only apply over HTTP.** The auth check is at a network boundary, so the notebook's server serves HTTP on port 8000 for this demo

### The per-user trap

```
❌ One shared credential: you authorise Gmail once, and everyone using the app can reach your Gmail
✅ Per-user credentials: each run reaches the MCP server as the user who started it
```

- **Class example:** if the deployed TimeTrack app let one person log in to an MCP server and then saved that token **application-wide**, every visitor would inherit that person's access
- Claude itself authorises **per user and per server** for this reason
- **Two steps for a deployment:**
  1. **Authenticate the caller at the LangGraph server** with a custom auth handler, so the user identity is in the runtime
  2. **Mint or exchange a credential for that user.** Inside the graph factory, build the MCP client with a **per-user token**
- **Rule:** authorise at the user level. Never store one person's authorisation where everyone can use it
- Not built here

## 12.10 `langchain.mcp` against `langchain-mcp-adapters`

From the class notebook's last section, with each point from the older package checked in a separate environment.

| | `langchain-mcp-adapters` (older) | `langchain.mcp` (beta, built in) |
|---|---|---|
| Resources | Supported (`get_resources`) | **Not exposed.** Use the underlying `client` |
| Prompts | Supported (`get_prompt`) | **Not exposed.** Same workaround |
| Tool call interceptors | Supported (`tool_interceptors`) | **No hook in this beta.** Wrap tools yourself after `list_tools()` |
| Error handling | `handle_tool_errors` flag | `isError` becomes `status="error"` automatically |
| Tool metadata | Ungrouped | One `tool.metadata["mcp"]` namespace |
| Elicitation | Not built in | Automatic through an interrupt (12.7) |

- *Checked on `langchain-mcp-adapters` 0.3.2:* `MultiServerMCPClient` has `get_tools`, `get_resources`, `get_prompt`, `get_server_info` and `session`, and its constructor takes `tool_interceptors`, `tool_name_prefix` and `handle_tool_errors`. That matches the notebook's table. The older package was **not run** against a server here
- **Honest takeaway for a client project:** if you need resources, prompts or interceptor-style middleware **today**, the older package still does things the new one does not. If you only need tools, the built-in path is where LangChain is heading. It is **not a full superset yet**
- **Dropping to the client:** `adapter.client` gives the underlying FastMCP client. Use it for resources and prompts

## 12.11 A secret in the class code

- The multi-server notebook has a **Context7 API key written into its source**, inside the call that reads an environment variable
- It was **not copied** into these notes. If that key is yours, **revoke and replace it**, and keep keys in a `.env` file that is never committed
- The notebook's other tokens (`cinebot-secret-token`) are teaching values for a local demo

## 12.12 Questions from the class

- **Why is `adapter.list_tools()` used and not `client.list_tools()`?** The adapter returns LangChain-compatible tools (12.2)
- **Does a LangChain agent do the same handshake as any client?** Yes, underneath ([MCP, Chapter 7](../mcp/07-legacy-vs-modern-mcp.md), 7.8)
- **Does LangChain's MCP support create servers?** No. It consumes them
- **Do I need to know how FastMCP wraps the raw client?** Not in depth. FastMCP and the official SDK are now very similar
- **How do I restrict which tools a user may call?** It is ordinary engineering with middleware, not an MCP feature ([MCP, Chapter 4](../mcp/04-operation-transports-and-shutdown.md), 4.4)
- **Interview question left for the project:** in an agentic loop, how do you handle two tools returning conflicting results? Class deferred it to the GCP project. Next weekend's project was on Google Cloud, with a free-trial account needed beforehand

## 12.13 Interview corner

**1. What does the LangChain MCP adapter do?**

- It translates between MCP and LangChain. It discovers a server's tools and returns them as LangChain tools, and converts results, errors and elicitation into messages, statuses and interrupts
- *Stronger answer:* it sits on top of the FastMCP client, which does transport, protocol version, connection and auth

**2. Why `adapter.list_tools()` and not the client's?**

- The adapter returns tools in LangChain's form. The client's tools are MCP objects

**3. Single server, config, or client group?**

- One target for one server. A config dictionary for an aggregate with a shared protocol era. A client group when servers need their own auth or protocol mode
- *Stronger answer:* a group routes each call to the client that advertised the tool and namespaces names

**4. How does an MCP tool error reach the agent?**

- A tool-reported failure becomes a tool message with `status="error"`. The agent can read it and retry. A transport failure raises an exception

**5. How do you guard destructive MCP tools?**

- Read each tool's `destructive_hint` annotation and build a human-in-the-loop `interrupt_on` map from it
- *Stronger answer:* an annotation is a hint, not a guarantee

**6. How does elicitation work in LangChain?**

- The adapter turns the server's question into a LangGraph interrupt. A person answers and the run resumes
- *Stronger answer:* it needs a server that returns an input-required result, or a client with your own handler. A legacy `ctx.elicit` server fails on a modern connection

**7. Why per-user credentials?**

- A shared token lets every user of the app act as whoever authorised it
- *Stronger answer:* authenticate the caller at the server, then mint or exchange a token per user when building the client

**8. What is missing from `langchain.mcp` compared with the older package?**

- Resources, prompts and interceptors. It is beta and not a full superset

## 12.14 Added by Claude, not from the sources

Items marked *checked* were run with `langchain` 1.4.7, `langgraph` 1.2.19, `fastmcp` 4.1.4 and a scripted stand-in model. No real model key was used.

- **Test MCP tools without a model.** *Checked:* `ainvoke` on a tool, with a tool-call dictionary, shows content, artifact and status in seconds
- **Use virtual environments per package family.** *Checked:* installing the older adapters package broke `fastmcp` 4 in a shared environment
- **Read the tool's annotations before you trust it.** *Checked:* the adapter exposes them. Combine them with an allow-list of tools you have reviewed, as in [MCP, Chapter 8](../mcp/08-interview-questions.md), 8.1
- **Treat tool output as untrusted text** that goes into the model. A remote server's result can contain instructions. Add guardrails ([Chapter 9](09-guardrails-to-do-lists-and-tool-resilience.md))
- **Pin versions.** The beta module, FastMCP 3 and 4, and the spec era all changed behaviour in this course. Record the versions you tested
- **Close adapters properly.** Use `async with`, as in every example here, so STDIO sub-processes are shut down

## Recap

- To an agent, MCP is a **source of tools**. The loop is unchanged
- **`langchain.mcp`** (beta, `langchain[mcp]>=1.4.0`) is the built-in adapter on FastMCP. **`langchain-mcp-adapters`** is the older, separate package. Do not mix them in one environment
- `MCPAdapter(target)`, then `await adapter.list_tools()`, then `create_agent(...)`. A bare string must be an http(s) URL
- Results become content blocks, **structured content becomes an artifact**, a tool failure becomes `status="error"`, a transport failure raises
- Read `destructive_hint` to build human-in-the-loop for dangerous tools
- Elicitation maps to a **LangGraph interrupt**, but needs an input-required server or your own client handler. The class `ctx.elicit` server fails on a modern connection
- Several servers: **config** (shared era, prefixed names) or **client group** (independent era and auth, namespaced names)
- Auth lives on the FastMCP client. **Per-user** credentials in any deployed app
- `langchain.mcp` has no resources, prompts or interceptors yet

## Practice

1. Install `langchain[mcp]>=1.4.0` in a fresh environment. Connect to the CineBot server and list its tools
2. Call each tool with `ainvoke`. Read the content and the artifact of `get_seat_map`
3. Add a tool that raises an error. Check the `status` of its tool message
4. Build the `interrupt_on` map from `destructive_hint`, run an agent, and approve a cancellation
5. Run the elicitation tool through the adapter with and without your own `elicitation_handler`. Compare the results
6. Connect two servers with a config and with a client group. Compare the tool names. Make one member legacy
7. Put a bearer-token check on an HTTP server and connect with the right, wrong and no token
8. Sketch how you would give each user their own MCP credential in an app you know

## How this chapter was checked

- Run with `langchain` 1.4.7 (installed as `langchain[mcp]`): the adapter's public members and documentation; listing tools over STDIO; direct `ainvoke`; structured content as an artifact; an error and a success from the same tool; destructive annotations; an agent with human-in-the-loop (scripted stand-in model, pause and approve); elicitation under a default client, a legacy client, and a legacy client with a handler; an MCP config and a client group, including a legacy member; a bare path string; and bearer authentication over HTTP with right, wrong and no token
- Run in a separate environment: the older package's public methods and constructor
- **Not run:** a real model, any remote server (Context7, the hosted TimeTrack server, the LangChain docs server), OAuth, an input-required server, the interrupt resume with `{"responses": {key: answer}}`, per-user credentials, audio or image content, interceptors, transport-failure exceptions
- The class transcript and the two notebooks are the source for everything not marked *checked*
- **Open:** the first class notebook (`Langchain MCP.ipynb`) is a failed demo on the old LangChain version. Its README is an empty file (0 bytes)

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/23 - 27 Sep - MCP In LangChain.md` (first half: the adapter, translation, authentication, elicitation)
- Live-Class-2026, `Weekend 14 - Oct 3 & Oct 4/MCP in Langchain/`: `MCP_in_Langchain.ipynb`, `MCP_MultiServer_Live_Demo.ipynb`, `cinebot_mcp_server.py`, `cinebot_error_server.py`, `cinebot_elicit_server.py`, `cinebot_mcp_server.log` and `pyproject.toml`
- Live-Class-2026, `Weekend 13 - 27th Sep/Langchain MCP.ipynb`
- The installed `langchain.mcp` module's own documentation (adapter targets, elicitation behaviour)
- Sections marked *checked* and 12.14 are from testing

Previous: [Chapter 11, Runtime and human-in-the-loop](11-runtime-and-human-in-the-loop.md) · Next: [Chapter 13, Multi-agent patterns](13-multi-agent-patterns.md) (not written yet)
