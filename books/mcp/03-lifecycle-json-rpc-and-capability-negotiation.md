# Chapter 3: Lifecycle, JSON-RPC and capability negotiation

**After this chapter you can:**

- Add a resource and a prompt to a tools-only server, and list and read them
- Say who triggers each primitive: the model, the application or the user
- Name the protocol calls behind each primitive (`tools/list`, `resources/read`, `prompts/get` and so on)
- Explain the three lifecycle phases in order
- Read a JSON-RPC request, response, notification and error
- Explain why MCP uses JSON-RPC and not plain REST
- Walk through the three-step initialization handshake and version negotiation
- Say what capability negotiation declares, and why `tools/list` is still needed after it
- Explain elicitation, and why it is not human-in-the-loop

**Builds on:** [Chapter 2](02-primitives-and-architecture.md). The operation phase, the transports and shutdown are in [Chapter 4](04-operation-transports-and-shutdown.md).

## 3.1 Who starts each primitive?

- **Tool:** the **model** decides, in the middle of a conversation
  - It is the one primitive where the AI "holds the wheel"
- **Resource:** the **application** (the host) decides to read it and feeds the content in as context
  - Example: a team style guide on a drive, read up front so every answer follows house style
- **Prompt:** offered to the **user** (through the host) to pick **before** the conversation starts
- A resource never changes anything. It is something to look at
- **Resources and prompts are optional.** GitHub's official MCP server ships **tools only**, and that is a valid, common design

## 3.2 The protocol calls behind each primitive

| Primitive | Discover | Use | Example |
|---|---|---|---|
| Tools | `tools/list` | `tools/call` | GitHub `create_issue` |
| Resources | `resources/list` | `resources/read` | a shared style guide |
| Prompts | `prompts/list` | `prompts/get` | `structured_escalation` |

- A client calls the `list` calls **first**. That is how a host learns what a server offers before using any of it
- **Resources have more:** **templates** (one resource pattern answers for a whole family, such as every customer record) and **subscriptions** (the client is told when a resource changes, instead of re-reading on a timer)
  - The class only named these. This chapter does not build them
- The handout whiteboard also lists the prompts functions as `list` and `get`, tools as `list` and `call`, and resources as `list`, `get`, template/list and listen

## 3.3 Tools, resources and prompts in one server

The class built this from the Chapter 2 warm-up server. **Two more decorators** is the whole difference.

```python
from fastmcp import FastMCP

mcp = FastMCP("Warm-Up Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to MCP."

@mcp.resource("file://server-notes")
def server_notes() -> str:
    """Read-only notes about this server, straight from a local file."""
    with open("server-notes.txt") as f:
        return f.read()

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.prompt
def structured_escalation(issue_summary: str, what_was_tried: str, customer_sentiment: str) -> str:
    """Guides the AI to log a customer escalation with every required field, in order."""
    return f"""Log this customer escalation with the following structure:
Issue Summary: {issue_summary}
What Was Already Tried: {what_was_tried}
Customer Sentiment: {customer_sentiment}
Recommended Next Action: [determine this from the details above]
"""

if __name__ == "__main__":
    mcp.run()
```

Create the file the resource reads, next to `server.py`:

```bash
printf 'This server was built across Parts 2 and 4A of the MCP crash course.\nIt demonstrates all three primitives: tools, resources, and prompts.' > server-notes.txt
```

- In the Inspector: `greet` and `add` under **Tools**, `file://server-notes` under **Resources**, `structured_escalation` under **Prompts**
- The prompt asks for exactly its three arguments. Filled in, it gives the same structure every time:

```
Issue Summary: Order #4521 arrived damaged
What Was Already Tried: Customer emailed support once, no reply in 3 days
Customer Sentiment: Frustrated, considering a refund request
Recommended Next Action: Escalate to logistics team, offer expedited replacement
```

- The model did not change. Only a form was added
- The `Recommended Next Action` line is left for the **model** to fill in
- Most tutorials stop at tools because tools are the easiest to demo

### Checked: what the code really does

*Checked on `fastmcp` 4.1.4.*

- The server lists **one resource, one prompt and two tools**. The prompt's three arguments are all required
- **The server reports the resource URI as `file://server-notes/`, with a trailing slash.** Reading it by raw JSON-RPC with the slash works. Without the slash it fails with error `-32602`, "Resource not found". The FastMCP `Client` accepts both
  - Rule: **use the URI exactly as `resources/list` returned it**
- **The relative path breaks when the working directory changes.** `open("server-notes.txt")` is relative to the process's working directory
  - Launched from another folder, the read fails with `FileNotFoundError`. A host that starts your server from its own folder will hit this
  - Fix: build the path from the script's own location, as in the snippet below
- `prompts/get` returns a message with role `user` whose text is the filled template

```python
from pathlib import Path

NOTES = Path(__file__).with_name("server-notes.txt")

@mcp.resource("file://server-notes")
def server_notes() -> str:
    """Read-only notes about this server, straight from a local file."""
    return NOTES.read_text()
```

## 3.4 The three lifecycle phases

- Every MCP connection goes through three phases, **always in this order**:
  1. **Initialization:** the handshake. Meet for the first time, agree on a version, declare capabilities
  2. **Operation:** the real work. Discover and use tools, resources and prompts
  3. **Shutdown:** the connection ends, cleanly or by force
- Picture: handshake and introduction, then the conversation, then saying goodbye. You cannot start the conversation before anyone is introduced
- The handout's sequence: `initialize` request, `initialize` response, `initialized` notification, normal protocol operations, shutdown, disconnect, connection closed
- **Why a connector shows a warning icon before you use it:** at start-up the host initializes a connection to **every** configured server. If the handshake fails, the host already knows
- Operation and shutdown get their own chapter

## 3.5 JSON-RPC 2.0

- **JSON-RPC 2.0** is the shared language between client and server. It sits in the **data layer**: the rules for how client and server exchange data
- **JSON:** the familiar text data format
- **RPC (remote procedure call):** run a function on another machine as if it were local, hiding the network details
  - Instead of spelling out low-level steps, the client says "query the database with these arguments"
- **JSON-RPC is not an MCP invention.** It is an existing, general specification that MCP adopted

**The shape of every message:**

```json
{ "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {} }
{ "jsonrpc": "2.0", "id": 1, "result": { "tools": [ ] } }
```

- **`jsonrpc`:** always `"2.0"`
- **`id`:** ties a response to its request. The handout types it as a string or a number
  - Responses may arrive **out of order**, so the id is the only way to match them
- **`method`, `params`:** what is being asked. `params` is optional
- A response holds **either** `result` **or** `error`, never both
- **Notification:** a message with **no `id`**. "Fire this and expect nothing back"

*Checked, by talking to a real server over STDIO:*

- An unknown **method** returns a JSON-RPC error: code `-32601`, "Method not found"
- An unknown **tool** does **not**. It returns a normal `result` with `"isError": true` and the text "Unknown tool". Tool failures travel in the result so the model can read them
- Two requests sent back to back came back with their own ids (99 then 98 here). Match by id, not by position

## 3.6 Why JSON-RPC and not plain REST?

Flagged in class as an interview-depth question.

- **Lightweight:** plain, readable JSON with none of the headers and overhead of a typical REST or XML call
- **Transport-agnostic:** the same messages work locally (STDIO) and remotely (HTTP)
- **Genuinely two-way:** in a normal HTTP API only the client calls and the server replies. In JSON-RPC **either side can start a request**
  - Useful for long tasks: the server can report progress itself, so the client does not poll
- **Notifications built in:** a message with no `id` expects no reply
- **Standard error codes:** inherited, like HTTP's 404 and 500

**Two things that are not the same as two-way:**

- **Not the same as asynchronous.** Async means the client sends a request, carries on and gets the answer later. The server still never starts anything
- **Not the same as a WebSocket.** A WebSocket is a permanent open connection. Two-way is a property of the protocol, not of keeping a socket open

## 3.7 The initialization handshake

Three steps, in this order:

```
Client → Server : 1. initialize  (id 1: protocol version, capabilities, client info)
Server → Client : 2. response    (id 1: protocol version, capabilities, server info)
Client → Server : 3. initialized (notification: no id, no reply)
                  ... normal operation can begin
```

- The **client speaks first**. It sends its latest supported protocol version, its capabilities and basic client info
- The **server answers with the same id**: its protocol version, its capabilities (tools? resources? prompts?) and its name
- The client sends `initialized` as a **notification**. This is the "notifications built in" idea in practice
- **Two ordering rules:** before the server answers `initialize`, the client sends nothing except pings. Before the server receives `initialized`, it sends nothing except pings
- In class this was shown live in Claude Desktop's MCP log on macOS (`~/Library/Logs/Claude/mcp.log`), against a real local server (Apple Notes over STDIO)

*Checked:* a real server answered `initialize` with its version, the capabilities `logging`, `prompts`, `resources` and `tools`, and its name. The client then sent `{"jsonrpc":"2.0","method":"notifications/initialized"}` with no id.

## 3.8 Version negotiation

- The client sends **only the latest** version it supports. Never a list of everything it has ever supported
- **Server supports that version:** it answers with the same one
- **Server does not:** it answers with the latest version **it** supports. The client checks that against its own supported list
  - In the handout flowchart, `SUPPORTED_PROTOCOL_VERSIONS` is checked **exactly once**
  - Match: send `initialized` and go on. No match: **disconnect**, send nothing further
- Analogy from class: Windows and a game agreeing on DirectX. They settle on the highest version both share
- Real consequence: a serious client, such as one built for a company, must decide **which historical versions it supports** and handle each difference in behaviour. "Connect to whatever URL I am given" is not enough. Class flagged this as interview depth

*Checked:* asking a real server for version `2099-01-01` made it answer with `2025-11-25`, its own latest.
- **Modern clients try a newer call first.** *Checked with `mcp` 2.3.0:* the client's first message to a server was **`server/discover`** (version `2026-07-28`), not `initialize`
  - A server that answered "Method not found" made the client **fall back** to the old handshake: `initialize` with version `2025-11-25`
  - A current `fastmcp` 4.1.4 server answered `server/discover` directly, with `supportedVersions` and its capabilities
  - This is the "newer discovery call, then fall back" that class 18 saw in a debugging tool. The legacy and modern handshakes get their own chapter ([Chapter 7](07-legacy-vs-modern-mcp.md), not written yet)
  - The 3.7 handshake is the **legacy** pattern, still what most servers use. Class estimate for the ecosystem to move: **8 months to a year**, with only the most actively maintained servers moving in the first couple of months

## 3.9 Capability negotiation

- Class picture: **both sides hand over an honest menu before anyone orders**
- Each side declares what it **can** do, not what it is about to do. Nothing is used until it is needed later
- **Client can declare** (class 18):
  - `roots`: it can expose file-system access
  - `sampling`: it can handle an LLM sampling request
  - `elicitation`: it can ask the user for information on the server's behalf
  - `tasks`, and `experimental` (non-standard features)
- **Server can declare:**
  - `tools`, `resources`, `prompts`: the three primitives
  - `logging`
  - `completions`: argument auto-completion
  - `experimental`
- **The two lists differ between sources.** The class 17 handout showed a shorter list (client: roots, sampling, experimental; server: tools, resources, prompts, logging) and noted that roots, sampling and logging are being **deprecated** in the newest spec revision. Class 18 showed the longer list above. Treat both as snapshots and check the current specification
- **"Deprecated" does not mean "unused".** Most servers in the wild still run the older pattern

**Capability negotiation is not discovery:**

- Negotiation says a **category** exists ("this server has tools")
- Discovery (`tools/list`) says **which** tools, their names, descriptions and argument schemas
- A client therefore still calls `tools/list` after the handshake (class 18 student question)

*Checked:* a real server's answer listed the capabilities `logging`, `prompts`, `resources` and `tools`, and no `completions`. A server only declares what it has. In the newer `server/discover` answer each capability carried flags such as `listChanged` and `subscribe` (all `false` here).

### Elicitation

- **Elicitation:** the server asks for **more information from the user, through the client, in the middle of a task**
  - It is the two-way nature of JSON-RPC made concrete: the server reaches out, instead of only replying
- In LangChain it surfaces as a **LangGraph interrupt**: a person answers, then the run resumes. The class cited LangChain's documentation for this. Not re-checked here
- **Not the same as human-in-the-loop (HITL):**
  - HITL is a safety layer in the AI application: approve, edit or reject a tool call ([Langchain, Chapter 11](../langchain/11-runtime-and-human-in-the-loop.md))
  - Elicitation is a native MCP request from a **server** for information it is missing
- Not run in these notes. It needs a client with an elicitation handler

## 3.10 Seeing the real messages: the wiretap

- **The problem:** from a Claude Desktop update on 26 June 2026, its own log files stopped writing the full JSON body of each message. They keep only a short summary (method, id, whether params or a result are present)
- **The idea:** a small script that sits **between** the host and the real server, relays every byte unchanged, and prints a pretty copy of each message
- **Wiring:** in the host's config, point `command` and `args` at the wiretap script instead of the real server. Everything after `--` is the real command that used to be there
  - The host never knows the difference
- A sanitised sample config from the class shows two servers: a filesystem server run **through** the wiretap with a `--log` file, and a plain FastMCP server

```json
{
  "mcpServers": {
    "demo-filesystem-wiretapped": {
      "command": "python3",
      "args": [
        "/path/to/mcp_wiretap.py", "--log", "/path/to/wiretap-live.log", "--",
        "npx", "-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"
      ]
    }
  }
}
```

- **Restart the host fully**, then use it normally. The terminal or the log file shows the handshake, capability discovery, every tool call and shutdown
- Replace the `/path/to/...` values with your own. Do not copy someone else's machine paths
- **The script, read and run:** `mcp_wiretap.py` (165 lines, standard library only)
  - Usage: `python3 mcp_wiretap.py [--log FILE] [--no-color] -- <real command> [args...]`
  - It starts the real server as a sub-process, then two threads relay lines: host stdin to server, and server stdout to host
  - Each message is printed pretty and coloured to **stderr**, never stdout. stdout is the protocol channel, and anything extra there would break the connection
  - `--log FILE` appends the same text to a file. It writes the **colour codes too**, meant for `tail -f` in a terminal
  - `--no-color` is for plain text editors. `mcp_wiretap_no_color.py` is the same tool with colour removed from the code (4.5 KB against 6.7 KB)
  - When the real server exits, it prints and logs `real server exited with code N`
- *Checked:* I put it in front of the RecipeBox server and sent `initialize`, `initialized` and a `tools/call`. The replies came back unchanged
  - Log: 3 client-to-server and 2 server-to-client banners (the `initialized` notification has no reply)
  - Colour codes were in stderr and log by default. With `--no-color`, and in the `no_color` file, there were none
- **Limits:** it reads **line by line**, so it fits STDIO servers that send one JSON message per line. It does not tap HTTP servers
- The class folder holds two copies of each script, byte-identical

## 3.11 Project: AI updates, with no code

A whiteboard project from the handout. Aim: **MCP concepts without writing a line of code**, using Claude Desktop **connectors**, which are MCP servers.

- **Flow (as drawn):**
  - The user asks for an **AI update email**
  - Several **search** steps run in parallel. The whiteboard labels them as internet search with **Tavily**
  - The results are combined into a **readable letter**
  - Outputs: **save as a draft** in Gmail, a **calendar meeting** to read it every day at 8 am, and a **LinkedIn post saved in Apple Notes**
  - A **schedule** is added so it repeats
- **Homework on the board:** a stock recommendation, plus buying
- **Class 18 built it live** with four connectors switched on as MCP servers: **Gmail, Google Calendar, Tavily, Apple Notes**
  - Claude turned the rough diagram into a structured **system prompt**
  - The flow: research AI news with Tavily, categorise it, draft an HTML email, create a recurring calendar reminder, produce a LinkedIn post and a Substack-style article
- **"Brain decides, tools act."** The model decides which tool, with what arguments, and how to read a result. Data moves only through tool calls
  - A search tool does not write the story. The model assembles the results into one
- **Lesson from the live run:** with no instruction on how many headlines per category, the model made its **own assumption** and quietly dropped real stories
  - Fix: say exactly how much detail you want per category, then test
- The boxes on the whiteboard are unlabelled and the brain icons mark the steps where the model works. The detail of the steps was not written on the page

## 3.12 Class questions

- **Can one MCP server call another?** Yes. A server can act as a client to another server inside it
- **Is FastMCP the only way?** No. The official MCP SDK is the base. FastMCP is the popular layer on top, like Keras over TensorFlow
- **Why bother with MCP if we have REST and a chatbot?** Integration count. N apps and M tool sets need about **N times M** custom integrations. With a shared protocol it is about **N plus M**. It also makes access usable by non-technical people. The class admitted it can feel like extra abstraction for a pure API call
- **How does a client know which server to connect to?** The address or URL is given when the client is configured. It is not discovered at connect time
- **How does a server tell which client a request came from?** The transport layer keeps session details once connected
- **My own email domain: how do I make it MCP compatible?** You do not make a domain compatible. You **build an MCP server** for it
- **Why call `tools/list` if negotiation already said the server has tools?** Negotiation names the category. Discovery fetches the actual tools (3.9)
- **How is elicitation different from HITL?** Elicitation is the server asking for missing information. HITL approves, edits or rejects tool calls (3.9)
- **Logs used to show full JSON-RPC and now do not. Did the protocol version change?** No. The class's answer: Anthropic's own client changed how much it writes to disk. It is unrelated to the MCP specification and to version negotiation
- **Who builds what for Gmail?** The service provider builds the **server**. The host builds the **client**. Claude's Gmail client is Anthropic's work
- **Reference server from the class:** `Link.txt` points to a Gmail MCP server on GitHub (`theposch/gmail-mcp`). It was shared as a reference and not read for these notes

## 3.13 Interview corner

**1. Who decides when a tool, a resource and a prompt are used?**

- The model decides tools. The application decides resources. The user picks prompts
- *Stronger answer:* a resource never changes anything, and resources and prompts are optional

**2. What are the three lifecycle phases?**

- Initialization, operation, shutdown, always in that order

**3. Walk me through the handshake.**

- Client sends `initialize` with a version, capabilities and info. Server replies with the same id. Client sends an `initialized` notification
- *Stronger answer:* before each side hears the other, only pings are allowed

**4. Why JSON-RPC and not REST?**

- Lightweight, transport-agnostic, two-way, notifications built in, standard error codes
- *Stronger answer:* two-way means the server can start a request, which suits progress on long tasks. It is not the same as async or a WebSocket

**5. What is the `id` for? What if it is missing?**

- It matches a response to its request, since responses can arrive out of order
- A message with no id is a notification and gets no reply

**6. How does version negotiation work?**

- Client sends its latest version. Server answers with that or its own latest. Client accepts or disconnects
- *Stronger answer:* a real client must decide which historical versions it supports

**7. Is JSON-RPC an MCP invention?**

- No. It is a general existing specification that MCP adopted

**8. Why does the client call `tools/list` if negotiation said the server has tools?**

- Negotiation names a category. Discovery fetches the names, descriptions and schemas

**9. What is elicitation, and is it human-in-the-loop?**

- A server asking the user for missing information through the client, mid-task. No. HITL is an application-side approval layer on tool calls

**10. A client connects to an old server. What happens?**

- *Checked:* a modern client tries `server/discover` first. On "Method not found" it falls back to `initialize`. A serious client supports both

## 3.14 Added by Claude, not from the sources

Not in the course material. Items marked *checked* were tested with `fastmcp` 4.1.4.

- **Read resources by the URI the server lists.** *Checked:* the server normalised `file://server-notes` to `file://server-notes/`, and the raw request without the slash failed
- **Never rely on the working directory in a server.** *Checked:* a relative path failed when the server was started from another folder. Use `Path(__file__)`
- **Two kinds of failure, two shapes.** *Checked:* a protocol problem (unknown method) is a JSON-RPC `error`. A tool problem (unknown tool) is a `result` with `isError: true`. Handle both in a client
- **Match responses by id.** Never assume replies arrive in the order you sent requests
- **Watch the wire with a model-free client.** The raw STDIO test below needs no host and no model. It is the fastest way to see the real messages
- **Check the current specification.** Version dates and which features are deprecated change. The version strings above come from the test, not from this chapter's sources

A minimal raw client that you can run against any STDIO server:

```python
import subprocess, json, sys

p = subprocess.Popen([sys.executable, "server.py"], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                     text=True, bufsize=1)

def send(msg): p.stdin.write(json.dumps(msg) + "\n"); p.stdin.flush()
def recv(): return json.loads(p.stdout.readline())

send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                 "clientInfo": {"name": "raw-test", "version": "0"}}})
print(recv()["result"]["protocolVersion"])            # step 2: the server's answer
send({"jsonrpc": "2.0", "method": "notifications/initialized"})   # step 3: no id
send({"jsonrpc": "2.0", "id": 2, "method": "prompts/list"})
print([x["name"] for x in recv()["result"]["prompts"]])
p.terminate()
```

## Recap

- **Tool:** model decides. **Resource:** application reads. **Prompt:** user picks. Resources and prompts are optional
- Calls: `tools/list` and `tools/call`, `resources/list` and `resources/read`, `prompts/list` and `prompts/get`
- Two decorators (`@mcp.resource`, `@mcp.prompt`) turn a tools-only server into a three-primitive one
- Lifecycle: **initialization, operation, shutdown**, in that order
- JSON-RPC 2.0: `jsonrpc`, `id`, `method`, `params`; a response has `result` or `error`; no `id` means notification
- Chosen over REST: lightweight, transport-agnostic, two-way, notifications, standard errors. It is not an MCP invention
- Handshake: `initialize`, response, `initialized` notification. Version: client proposes its latest, server answers, client accepts or disconnects
- Capability negotiation is a two-way menu: it names categories, `tools/list` names the tools. Elicitation lets a server ask the user for missing information
- A modern client tries `server/discover` first and falls back to `initialize`
- The wiretap sits between host and server and prints the real messages

## Practice

1. Add `server_notes` and `structured_escalation` to your warm-up server. Confirm all three primitives in the Inspector
2. Move the notes path to `Path(__file__)` and start the server from a different folder
3. Run the raw client from 3.14. Add `resources/list`, `resources/read` and `prompts/get`
4. Trigger an unknown method and an unknown tool. Compare the two reply shapes
5. Find the three handshake messages in your own host's MCP log
6. Write by hand a JSON-RPC request and response for a hypothetical `send_email` tool, with a matching `id`
7. Say out loud why JSON-RPC was chosen over REST
8. For a service you use daily, list what would be a tool, a resource and a prompt
9. Open a real server's published capabilities (GitHub's or Gmail's) and check whether it ships tools only
10. Add a free, no-auth server such as Context7 in VS Code and watch the tools appear before you ask anything
11. Build the no-code AI-news project with three or more connectors. State how many items per category you want

## How this chapter was checked

- Run with `fastmcp` 4.1.4: the full three-primitive server from the class notebook; `resources/list`, `resources/read`, `prompts/list` and `prompts/get` over raw JSON-RPC on STDIO; the `initialize` answer and capabilities; the `initialized` notification; an unknown method and an unknown tool; two back-to-back requests; a future protocol version; the first message a current client sends (`server/discover`) and its fallback to `initialize`; the trailing-slash URI behaviour; and the working-directory failure with a read from a different folder
- **Not run:** elicitation, the Inspector in a browser, Claude Desktop and its log files, the wiretap scripts, the Tavily and Gmail project, templates and subscriptions
- The class write-ups, notebook and handouts are the source for everything not marked *checked*. The three handout PDFs are whiteboard images, read as text and as images

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/18 - 6 Sep - MCP Capability Negotiation.md` (capability negotiation, elicitation, the no-code project, class Q&A)
- Live-Class-2026, `classes_summary/17 - 6 Sep - MCP Primitives, Architecture & Wiretap.md`
- Live-Class-2026, `classes_transcription_summary/17 - 5 Sep - MCP Deep Dive — Primitives, Lifecycle & JSON-RPC.md`
- Live-Class-2026, `Weekend 10 - 5-6 Sep/README.md`, and under `06 Sep - MCP Primitives & Architecture/`: `README.md`, `v4a_primitives_notebook.ipynb`, `MCP-Lifecycle.pdf`, `MCP-Primitives.pdf`, `AI-Updater-Project.pdf`, `claude_desktop_config.example.json`, `Link.txt`
- Sections 3.3 (Checked), 3.5 and 3.7 to 3.8 (the *checked* lines) and 3.14 are from testing, not from the class sources

Previous: [Chapter 2, Primitives and architecture](02-primitives-and-architecture.md) · Next: [Chapter 4, Operation, transports and shutdown](04-operation-transports-and-shutdown.md)
