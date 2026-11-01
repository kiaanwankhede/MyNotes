# Chapter 2: Primitives and architecture

**After this chapter you can:**

- Name the three participants (host, client, server) and say who talks to whom
- Explain why each server gets its own dedicated client
- Name the two transports and the protocol underneath
- Explain the token cost of connecting many servers
- Tell tools, resources and prompts apart, and say when each fits
- Build, run and inspect a first MCP server with FastMCP

**Builds on:** [Chapter 1](01-why-mcp-exists.md). The messages on the wire and the connection lifecycle are in [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md). Transports in depth are in [Chapter 4](04-transports-and-shutdown.md). Building servers properly is in [Chapter 5](05-building-mcp-servers.md).

## 2.1 The three participants

Every MCP conversation has exactly three participants:

- **Host:** the AI application a person actually uses
  - It receives the question, decides (using the language model underneath) whether it needs outside help, and coordinates what happens next
  - Examples: Claude Desktop, VS Code, Cursor, a Codex app, a custom chatbot, any LangChain, LangGraph or AutoGen app
- **Client:** a piece of code **inside the host** that holds the connection to **one** server
- **Server:** a program that does one focused job (or a closely related family of jobs) and exposes it so anything speaking the protocol can find and use it

```
Person → Host → Client → Server
```

Two pictures to hold together:

- **Phone, SIM card, network:** the phone is the host, the network is the server, and the **SIM card is the client**. A phone cannot reach the network without one
- **Universal remote:** a remote in a house full of smart gadgets, with a dedicated adapter behind each gadget. The person holding the remote is the host. They never rewire a gadget. They press a button and something else handles the rest. The server is the gadget. It does not care which brand of remote points at it

**The server** (more detail):

- Does one job well. A greeting-and-adding server is a fine server. It does not need to be a general assistant
- Can be built by **whoever understands the service best**, often the company that owns it. A team running a version-control platform builds a more correct and secure connector to its own system than every AI company reverse-engineering it separately
- Once a shared protocol exists, a service builds its official server **once**, and every host that speaks the protocol can use it

## 2.2 The host never talks to a server directly

- The host **delegates** entirely. If every host had to understand the wiring of every tool it might ever use, each new capability would be an engineering project
- A host only needs to know how to **ask**. That is what lets one app connect to a tool it has never seen, built by a team it has never spoken to
- **The client is one per server, not one shared line.** The host creates a **dedicated client for each server**. Each client keeps a private, 1:1 connection with exactly one server

```
Host
 ├─ Client 1 ──(dedicated connection)── Server A
 ├─ Client 2 ──(dedicated connection)── Server B
 └─ Client 3 ──(dedicated connection)── Server C
```

- A host connected to five servers runs **five clients**. Never one shared connection to all five
- From the MCP documentation (as quoted in the class notebook): each client keeps a dedicated 1:1 connection with its server. **Local servers** typically serve a single client. **Remote servers** typically serve many clients at once

## 2.3 Why dedicated connections?

Four reasons. Understand each one, do not just memorise the list.

- **Decoupling:** changing how one server works never requires touching how the host talks to another
- **Safety:** a crash in one server's connection stays **contained to that connection**
  - **Try it:** start `server.py`, connect the Inspector, then press **Ctrl+C** in the server's terminal. The Inspector does not crash. It shows that one connection as closed
  - With five servers connected, killing one leaves the other four untouched
- **Scalability:** if one server needs to handle much heavier use, that growth stays local to that one pair
- **Parallelism:** a host with three live connections can talk to all three **at once**. A shared connection would force them to take turns

## 2.4 The cost of connecting many servers

- The host asks every server what it offers, and then sends **the full tool list from every connected server to the model up front**, on the first message
- Live example: connecting just **two** MCP servers to a chat product added **tens of thousands of tokens** to a single "hi". The class showed it in the product's context inspector
- That is a real cost, and it can also **confuse the model** when there are many similar tools
- What helps:
  - **Good tool descriptions**, so the model chooses well
  - **Middleware or interceptors** that trim the list to the tools relevant to each request ([Langchain, Chapter 7](../langchain/07-middleware.md), 7.2, and [Chapter 9](../langchain/09-guardrails-to-do-lists-and-tool-resilience.md), 9.3)

## 2.5 The transport in one look

- Client and server speak **JSON-RPC 2.0**, not plain REST. "Is MCP a REST client?" At a very high level you can think so, but it is a distinct protocol with its own rules
- Two transport types:
  - **STDIO** (standard input and output): for servers that run **locally** on your own machine
  - **Streamable HTTP:** for **remote or hosted** servers
- Streamable HTTP **replaced the older HTTP + SSE** transport, which was deprecated in the specification released in **March 2025**. The practical cut-over date varies from server to server
- A remote server has a **URL**, like any other server. So it can have auth and everything else a web server has
- Chapters 3 and 4 go into the message format, the lifecycle and both transports

**What happens when a host starts** (the class sequence):

```
Host starts, connects to its configured server
Client → Server : list tools
Server → Client : tool names, descriptions, input schemas
Client → Host   : "here is what this server can do"
   ... the user asks the AI to send an email ...
Host → Client   : the model decides to call send_email with arguments
Client → Server : call the tool
Server → Client : the result
Client → Host   : result passed back to the model
```

On the wire those steps are JSON-RPC messages. *Checked:* talking to a real server over STDIO, the setup message is `initialize`, the tool list is `tools/list` and a call is `tools/call`. Each request carries `"jsonrpc": "2.0"` and an `id`. Chapter 3 covers them.

## 2.6 The three primitives

Once a client and server are connected, the protocol defines **exactly three things** a server can give the client:

- **Tools:** something that **does**
- **Resources:** something to **read**
- **Prompts:** a **form** to fill in

**Tools**

- Executable actions with a **real effect** when called, not just information returned
- Calling `add` does not fetch a fact that already existed. It runs logic and makes a new result
- Tools are the one primitive that lets an AI application **do** something, instead of only describing what it would involve. Without tools an AI can tell you in detail what sending an email looks like. With a tool it can send one

**Resources**

- **Read-only reference data.** No side effects, nothing performed. Where a tool *does*, a resource *is*
- Picture: the small display on a smart thermostat. You do not actively ask it the temperature, you glance, because it is always there
- **The problem they solve:** without one shared resource, every client that needs the same reference data **hard-codes its own copy**. Over time one copy updates and another does not, and they quietly **drift apart** until something breaks
- One resource, read fresh by everyone, means **one copy of the truth**

**Prompts**

- A **reusable template** that shapes **how** a request is phrased. Not data, not an action. A form with blank fields, supplied by the server
- Example: an AI logging a support escalation with no guidance might write "customer unhappy, refund maybe". If the server hands it a template with four fields (**issue, what was tried, customer sentiment, recommended next step**), every escalation has the same structure
- The model did not change, the question did not change. Only the presence of a form did
- The value is **consistency that survives who is asking**. The structure lives once, on the server, instead of being reinvented in every app

The whiteboard's three-row table, with an example for each: **tools** (an action such as "delete entry"), **resources** (a schema for data), **prompts** (instructions). A server ideally supports all three.

*In class, running code was shown only for tools. A tiny example of all three is in 2.9.*

## 2.7 Before building: tools or resources or prompts?

- **Does calling it change something, or compute something new?** A tool
- **Is it reference data that many clients should read the same way?** A resource
- **Do you want requests phrased the same way every time?** A prompt
- In practice **about 99%** of what you meet are tools. Resources and prompts are the other two primitives

## 2.8 Your first server (live demo)

**Setup** (using `uv`):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh        # macOS / Linux
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

uv init mcp-warmup && cd mcp-warmup
uv add fastmcp
```

**The server:**

```python
from fastmcp import FastMCP

mcp = FastMCP("Warm-Up Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to MCP."

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

- **No special MCP boilerplate** beyond `@mcp.tool`
- FastMCP reads each function's **docstring as the tool description** and its **type hints as the input schema**. *Checked:* the tool list showed `Greet someone by name.` and `{"name": {"type": "string"}}` with `name` required. Nothing was written a second time
- A bad argument is refused by the server with a validation error. *Checked:* `add("x", 3)` failed with "Input should be a valid integer"

**Run it with the MCP Inspector:**

```bash
uv run fastmcp dev server.py                      # as shown in class
# or, without FastMCP's wrapper:
npx -y @modelcontextprotocol/inspector uv run python server.py
```

- The **MCP Inspector** opens at `http://127.0.0.1:6274`. It connects to **any** MCP server so you can try its tools, with **no AI application** involved
- In the **Tools** tab call `greet` with your name, then `add` with two numbers
- You have just watched **two separate programs** finish a task over the real protocol: the **Inspector (host and client)** and **`server.py` (the server)**
- The description shown for each tool is exactly the docstring

> **Correction for current FastMCP.** *Checked on `fastmcp` 4.1.4:* `fastmcp dev server.py` fails with `Unknown command "server.py". Available commands: inspector, apps`. The command is now `fastmcp dev inspector server.py`. The class project pinned `fastmcp>=3.4.7`, so a fresh `uv add fastmcp` today installs a newer major version than the class used. The `npx ... inspector` line works either way

**Wire the same server into a real host:**

- **VS Code:** register the launch command `uv run python server.py` as a **STDIO** server (`Add Server`, then STDIO), with the working directory set to the folder that holds `server.py`. VS Code records it in its own `mcp.json`. A new chat can then see and call `greet` and `add`
- **Claude Desktop:** Manage Connectors, then **Add custom connector**, pointing at a remote MCP server URL (or the local-server pattern)
- **The same server works across hosts with no changes.** That was the point of the demo
- **Sharing with a small team:** a locally running server can be shared by port-forwarding or tunnelling. It is **not the most secure option**. Proper hosting and publishing as a package come later ([Chapter 6](06-deployment.md))

**Files in the class repo, for reference:**

- `mcp-warmup/server.py` (the version above) and a `pyproject.toml` that requires Python 3.13 or newer
- The repo's top-level copy of `mcp-warmup/server.py` was edited later: it has a `query_db(a, b, c)` tool in place of `add`

## 2.9 A closer look, without the Inspector

*Added for these notes. Checked on `fastmcp` 4.1.4.* You can test a server without a browser.

```bash
fastmcp list server.py
# Tools (2)
#   greet(name: str) -> dict    Greet someone by name.
#   add(a: int, b: int) -> dict Add two numbers together.
```

A small client that does what a host's client does (launch the server over STDIO, ask for its tools, call them):

```python
import asyncio, sys
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

async def main():
    transport = StdioTransport(command=sys.executable, args=["server.py"])
    async with Client(transport) as client:
        print([t.name for t in await client.list_tools()])        # ['greet', 'add']
        result = await client.call_tool("add", {"a": 2, "b": 3})
        print(result.data)                                        # 5

asyncio.run(main())
```

And one server with **all three primitives**:

```python
from fastmcp import FastMCP

mcp = FastMCP("Warm-Up Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to MCP."

@mcp.resource("config://app")
def app_config() -> str:
    """Read-only reference data: the same copy for every client."""
    return "currency=INR; region=IN"

@mcp.prompt
def escalation(issue: str, tried: str, sentiment: str, next_step: str) -> str:
    """A form for logging a support escalation."""
    return (f"Issue: {issue}\nTried: {tried}\n"
            f"Sentiment: {sentiment}\nRecommended next step: {next_step}")
```

- *Checked:* a client saw one tool, one resource (`config://app`) and one prompt with four arguments. Reading the resource returned the text, and getting the prompt filled the four fields into the template
- Resources and prompts get their full treatment in [Chapter 5](05-building-mcp-servers.md)

## 2.10 Questions from the class

- **How is an MCP server hosted?** Like any other server: a plain process, a Docker container, or a cloud service such as Cloud Run or AKS. MCP does not mandate a method
- **Can tool access depend on the user's role (read-only vs read-write)?** In principle yes. The client asks the server for the tool list, so the server can check the caller's token or scope first. MCP does not prescribe it, you build that check
- **Can a server "extend" another server?** Not by code inheritance. A server **can** contain an MCP client inside it that forwards some requests to another server. It works but is uncommon
- **Won't many servers blow up the context?** Yes (2.4)
- **When was HTTP + SSE deprecated?** In the specification released in March 2025. The practical cut-over varies
- **Is Streamable HTTP the same as REST?** No. The messages are JSON-RPC 2.0 whichever transport carries them
- **For interviews about MCP security,** read up on **JWT tokens and OAuth flows**. The course covers an authentication layer for MCP servers in a later session

## 2.11 Interview corner

**1. Name the participants in MCP and what each does.**

- Host: the AI app the user uses. Client: a connection inside the host, one per server. Server: a program exposing tools, resources and prompts
- *Stronger answer:* the host never talks to a server directly, it delegates to a client

**2. Why does each server get its own client?**

- Decoupling, safety (a crash stays contained), scalability and parallelism

**3. STDIO or Streamable HTTP?**

- STDIO for local servers on your machine. Streamable HTTP for remote or hosted servers
- *Stronger answer:* Streamable HTTP replaced HTTP + SSE (deprecated in the March 2025 specification). The messages are JSON-RPC 2.0 on both

**4. What are the three primitives?**

- Tools (do something), resources (read-only data), prompts (reusable templates)
- *Stronger answer:* resources keep one copy of reference data, prompts keep requests consistent across apps

**5. Why can connecting many servers hurt?**

- Every server's full tool list is sent to the model up front. That costs tokens and can confuse tool choice
- *Stronger answer:* trim with middleware, and write good tool descriptions

**6. What does the MCP Inspector do?**

- Connects to any MCP server so you can try its tools with no AI app. It plays host and client

**7. Can the same server work in VS Code and Claude Desktop?**

- Yes, with no changes. That is the point of a shared protocol

## 2.12 Added by Claude, not from the sources

Not in the course material. Established practice, but check current docs. Items marked *checked* were tested with `fastmcp` 4.1.4.

- **Pin the FastMCP version.** *Checked:* the Inspector command changed between major versions. Pin it (for example `fastmcp>=3.4,<4`) or follow the current docs, so a fresh install does not break your notes
- **Write tool descriptions for the model, not for yourself.** The description and input schema are all the model sees. Say what the tool does and when to use it, as with any tool ([Langchain, Chapter 5](../langchain/05-tools.md), 5.12)
- **STDIO servers must not print to standard output.** On STDIO, standard output **is** the protocol channel. A stray `print()` in a tool corrupts the messages. Log to standard error instead (a design point of the transport, covered in Chapter 4)
- **Keep servers small and named clearly.** One focused server per job makes it easier to approve, to trust and to trim
- **Test servers without a model.** The small client in 2.9 lets you check tools, schemas and errors in seconds

## Recap

- Three participants: **host** (the app), **client** (one connection per server, inside the host), **server** (one focused job)
- The host **delegates**. It never talks to a server directly
- Dedicated clients give **decoupling, safety, scalability and parallelism**. Ctrl+C on one server only closes that connection
- Transports: **STDIO** (local) and **Streamable HTTP** (remote). Messages are **JSON-RPC 2.0**. HTTP + SSE is deprecated
- The **whole tool list** of every connected server is sent up front: a real token cost
- Three primitives: **tools** (do), **resources** (read, one copy of truth), **prompts** (a form for consistent requests)
- First server: `@mcp.tool` on a function. Docstring becomes the description, type hints the schema
- Inspector = host and client in one tool. The same server works in any host

## Practice

1. Build `server.py` with `greet` and `add`. Run it with the Inspector and call both tools
2. Do the **Ctrl+C test**: stop the server while the Inspector is connected and watch only that connection close
3. Register the same server as a STDIO server in VS Code and/or as a custom connector in Claude Desktop
4. Run `fastmcp list server.py` and the small Python client from 2.9
5. Add a resource and a prompt to your server and read them with the client
6. Draw the host, client and server picture for three servers, and say what happens if one crashes
7. If you plan to interview on MCP, read up on JWT tokens and OAuth flows

## How this chapter was checked

- Run with `fastmcp` 4.1.4 (the class project pinned `>=3.4.7`): the warm-up server's tool list, descriptions and input schemas, calling `greet` and `add`, a bad-argument error, a real STDIO client and server, `fastmcp list`, the failing `fastmcp dev server.py` and the working `fastmcp dev inspector` command name, raw JSON-RPC messages over STDIO (`initialize`, `tools/list`, `tools/call`), and a server with a tool, a resource and a prompt read by a client
- **Not run:** the browser Inspector (it needs `npx` and a network download), VS Code, Claude Desktop, a remote server
- The architecture material (host, client, server, the four reasons, the transports) comes from the class notes. The Ctrl+C behaviour and the token cost are class demonstrations

## Sources and further reading

- Live-Class-2026, `classes_summary/16 - 23 Aug - MCP Introduction.md` and `classes_transcription_summary/16 - 23 Aug - MCP Introduction.md`
- Live-Class-2026, `Weekend 09 - 22-23 Aug/23rd Aug - MCP/`: `README.md`, `Complete MCP/p2_MCP_Architecture.ipynb`, `Complete MCP/Complete-MCP.pdf`, `Complete MCP/Commands.txt` and `Complete MCP/mcp-warmup/` (`README.md`, `server.py`, `src/mcp_warmup/__init__.py`, `pyproject.toml`)
- Sections 2.9 and 2.12 and the corrections marked *checked* are from testing, not from the class sources

Previous: [Chapter 1, Why MCP exists](01-why-mcp-exists.md) · Next: [Chapter 3, Lifecycle, JSON-RPC and capability negotiation](03-lifecycle-json-rpc-and-capability-negotiation.md)
