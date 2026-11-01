# Chapter 4: Operation, transports and shutdown

**After this chapter you can:**

- Describe the operation phase: discovery, then calling
- Explain what a tool schema is and why its description matters
- Say what a failed call looks like on the wire
- Explain the privacy cost of sending tool results to a model
- Describe STDIO and Streamable HTTP, and when to pick each
- Explain how shutdown works on each transport, and why JSON-RPC is not involved

**Builds on:** [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md) (handshake, JSON-RPC). **Next:** [Chapter 5](05-building-mcp-servers.md) builds real servers.

## 4.1 The operation phase: two steps

- After the handshake, operation has exactly two steps:
  - **Discovery:** `tools/list` (and `resources/list`, `prompts/list`)
  - **Calling:** `tools/call`

```
Handshake complete
Client → Server : tools/list                       (automatic, before any question)
Server → Client : [list_notes, get_note_content, add_note, update_note_content]
      ... later the user asks "list my Apple Notes in Personal" ...
Client → Server : tools/call  list_notes {"folder": "Personal"}
Server → Client : note titles, ids, dates
Client → Host   : result, turned into an answer by the model
```

- **Discovery fires by itself** the moment the handshake ends, before the user asks anything
  - It costs **no LLM tokens**. No model is involved. The client asks, the server answers
- **Calling** happens only when a request needs a tool. It always needs two things: the tool's **name** and its **arguments**
- A tool call by itself is a plain client-to-server exchange. Tokens are spent only when the **model** reasons or writes
- *Capability negotiation says a category exists. Discovery says which tools.* ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.9)

## 4.2 What a tool looks like to the model

- Every tool on every server (Gmail, Calendar, Apple Notes) has the **same shape**: a **name**, a **description** and an **input schema**
- Live class example, from Claude Desktop's own log: Apple Notes `list_notes`
  - `folder`: string, optional, "filter notes by folder"
  - `limit`: number, default 20
  - The class folder keeps this schema as `Untitled-1.json` (a copy of `list_notes`: `folder` as an optional string, `limit` as a number with default 20). It is a scratch file, not part of a server
- Asking for the "Personal" folder sent `folder: "Personal"` with no `limit`, so the server's default of 20 applied
- **The description decides whether the model picks the right tool.** Write it for the model
- The model only learns a tool exists through discovery. It cannot call something it was never told about

## 4.3 When a call goes wrong

- A bad request does not fail silently. It comes back as an error
- Class claim: a wrong tool name returns a "method not found"-style JSON-RPC error
- *Checked on `fastmcp` 4.1.4, and different from the class claim:*
  - A wrong **method** (`does/notexist`) returns a JSON-RPC `error`, code `-32601`
  - A wrong **tool name** returns a normal `result` with `"isError": true` and the text "Unknown tool"
  - A **tool that raises** (RecipeBox `get_recipe("999")`) reaches the client as a `ToolError` that carries the Python `KeyError` text
- So a client must handle **both**: protocol `error` objects and results flagged `isError`
- The tool-error and retry middleware in LangChain exists for exactly this point ([Langchain, Chapter 9](../langchain/09-guardrails-to-do-lists-and-tool-resilience.md))

## 4.4 What leaves your machine

A student asked: "so with MCP, we are exposing our data to the LLM?" The class answer: **yes.**

- Whatever a tool returns goes from the client to the host, and the host sends it to the **model provider**
- It is real information flow, so there are real ways to limit it:
  - **Restrict what the connection can see.** Demonstrated live: a locked Apple Notes note is invisible to every MCP call
  - **Middleware** on your own side: PII detection and custom guardrails before a model call ([Langchain, Chapter 8](../langchain/08-prebuilt-middleware-limits-fallback-and-pii.md))
  - **Build your own server.** For a locked-down enterprise, class advice: a **custom, self-hosted MCP server**, possibly in its own container, so data never passes through a third-party connector
- **Per-user tool access** (read-only vs read-write) is not an MCP feature. The class called it ordinary software engineering, solved with middleware such as guardrails and dynamic tool loading
- **Caching:** not built in, as far as the class could confirm live. Build it yourself if you need it

## 4.5 Watching operation live

Three live demonstrations from class:

- **VS Code with Context7:** adding the server shows connect and tool discovery happening **before any request**
  - Context7 is free, needs no authentication and returns the **latest documentation** for a library. Class named it among the most-used servers
  - It fixes the lag between a model's training data and a library's current API
- **Claude Desktop with Apple Notes:** the tool list `list_notes`, `get_note_content`, `add_note`, `update_note_content` was visible before any note question
- **A third-party inspector tool** on a two-tool time server (`getCurrentTime`, `convertTime`). The request "convert current Indian time to Chicago time" produced:
  1. an LLM call to understand the request
  2. `tools/call getCurrentTime`
  3. an LLM call to read that result
  4. `tools/call convertTime`
  5. a final LLM call to write the answer
  - The exact JSON-RPC bodies were visible at every step. **The `id` kept increasing across every call**, whatever the primitive
- **Why none of this is hand-written:** it is built into the protocol. Learn the steps anyway, because production failures happen at exactly these steps
- **Why Claude's own logs were not enough:** see the wiretap in [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.10

## 4.6 Why shutdown needs transports first

- Shutdown is not about what is said. It is about **how the connection closes**, and that depends on **how the two were connected**
- Class analogy: on WhatsApp, closing the connection means closing your internet. On a phone call, closing your internet does nothing, you hang up
- **JSON-RPC is the language and grammar. The transport is how the two sides are physically connected to say it**
- **No JSON-RPC messages are exchanged during shutdown.** The transport layer does all of it

## 4.7 Transport 1: STDIO

- **STDIO** is standard input and output. The same thing behind `#include <stdio.h>` in a C program

**The class demo:**

```python
name = input("Please tell me your name: ")
print(name)
print("Hello Mayank from Python file")
```

- Run it from a terminal. The **terminal is the client**, the Python file is started as a **sub-process** and is the **server**
- What the terminal sends becomes the file's input. What the file prints is what the terminal shows
- **Every STDIO MCP connection is this pattern:** launch a sub-process, send in on `stdin`, read out on `stdout`. Only the content is JSON-RPC
- *Checked:* the script, given `Mayank` on standard input, printed the prompt, the name and the greeting

**Benefits:**

- **Fast:** same machine, no network round trip
- **Secure:** nothing is exposed outside the machine
- **Simple:** no address, no network setup. Only a command

**Trade-off:** both sides must run on the **same machine**. It does not serve "anyone on the internet". By default STDIO needs the parent and sub-process relationship on one machine

## 4.8 STDIO shutdown

Almost always started by the **client**, in this order:

1. **Stop sending input** (close the server's `stdin`)
2. Send a **terminate** signal
3. Send **kill**, as a last resort

- **Server-initiated** shutdown is rare: the server closes its own output stream and exits
- Closing Claude Desktop just tells its servers' processes to stop. No JSON-RPC is involved

*Checked on a real FastMCP server over STDIO:*

| Action | Result |
|---|---|
| Close `stdin` | Server exited by itself, code 0 |
| Terminate (SIGTERM) | Exit code -15 |
| Kill (SIGKILL) | Exit code -9 |

**Standard output is the protocol channel.** Never write your own text there from a hand-written server. Log to standard error. *Checked:* `fastmcp` 4.1.4 sent a stray `print()` from inside a tool to standard error and the call still worked. Other libraries may not do this. That case was not tested

## 4.9 Transport 2: Streamable HTTP

- Built on ordinary **HTTP**. Because HTTP already works across the internet, a client can reach a server **anywhere**, not only on the same machine
- The client sends a **POST** to a single endpoint, almost always **`/mcp`**, with the JSON-RPC message as the request **body**
- Normal HTTP tools apply: headers, and standard auth such as OAuth or an API key
- It **replaces the older HTTP + SSE** (server-sent events) transport, now deprecated. Most existing servers still use the old one
- Live in class, with an Excalidraw MCP server:
  - `initialize` was a real POST call, then an `initialized` notification, then a `tools/list` POST that returned 5 tools, then a `resources/list` POST
  - The class's own LangChain MCP server URL also ended in `/mcp`

**Checked, by hand with `httpx` against a FastMCP server on `http://127.0.0.1:8765/mcp`:**

```python
import httpx, json
u = "http://127.0.0.1:8765/mcp"
H = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
r = httpx.post(u, headers=H, json={"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                "clientInfo": {"name": "t", "version": "0"}}})
sid = r.headers["mcp-session-id"]                      # the server hands out a session id
H["mcp-session-id"] = sid
httpx.post(u, headers=H, json={"jsonrpc": "2.0", "method": "notifications/initialized"})   # 202, empty
httpx.post(u, headers=H, json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
```

- The `initialize` reply came back as `text/event-stream`: a line `event: message` and a line `data: {...JSON-RPC...}`. **Even a plain POST is answered in that format**
- The server returned a **`mcp-session-id`** header. The client sends it on every later request
- The `initialized` notification got **HTTP 202** with an empty body (a notification expects no reply)
- `tools/list` then `tools/call` for `add(2, 3)` worked. Structured result: `{'result': 5}`
- A plain `GET /mcp` without the right `Accept` header: **406**. A wrong path: **404**
- `DELETE /mcp` with the session id: **200**, ending the session
- **The messages are the same JSON-RPC as over STDIO.** Only the carrier changed. That is what "transport-agnostic" means

## 4.10 Streamable HTTP shutdown

- Simply **close the HTTP connection**. Like closing a browser tab or turning off Wi-Fi to end a chat
- **If a server closes unexpectedly**, something went wrong on its side. A well-built client should **try to reconnect**, not fail silently
- With this, all three lifecycle phases are covered: **initialization, operation, shutdown**

## 4.11 Choosing a transport

| | STDIO | Streamable HTTP |
|---|---|---|
| Where the server runs | Same machine, as a sub-process | Anywhere with a URL |
| Setup | Only the command | URL, plus auth |
| Clients per server | Typically one | Many at once |
| Shutdown | Close input, terminate, kill | Close the connection |
| Typical use | Local tools, personal setups | Hosted and shared servers |

## 4.12 Class questions

- **Does STDIO only work on one machine?** Yes, by default, unless something proxies it
- **Why would an LLM call `list_recipes` before `get_recipe`?** It only knows `get_recipe` exists through discovery. At real scale there are thousands of records, not three
- **Is one tool needed per read operation on a database?** Yes, one tool per meaningful operation, and the model decides which fits
- **How does an LLM know what kind of file a resource holds?** Through the resource's declared **MIME type**
- **Does language matter (Python or Node)?** No. The protocol does not care. It is a team stack choice
- **Should I name FastMCP in an interview?** Concepts first: why MCP is built the way it is, and the legacy-versus-modern history. Class remark: about 90% can define an MCP server but cannot explain what happens underneath
- **Can I create an MCP server inside Claude?** No. You can **connect** your server to Claude. You do not build or host it there
- **Are connectors the same as MCP servers?** Yes. Claude uses friendlier words for a general audience
- **Is a "production-grade" project claim on a resume fine if it was not deployed at scale?** Describe it honestly and frame it around the problem solved. Shallow claims get exposed

## 4.13 Interview corner

**1. What are the two steps of the operation phase?**

- Discovery (`tools/list` and friends), then calling (`tools/call` with a name and arguments)
- *Stronger answer:* discovery is automatic and uses no LLM tokens

**2. Does MCP send my data to the model?**

- Yes. Tool results go to the host, then to the model provider. Restrict access, add middleware, or self-host your server

**3. Why does shutdown depend on the transport?**

- No JSON-RPC messages are exchanged at shutdown. Closing is done by the transport

**4. How does a STDIO server shut down?**

- Client closes input, then sends terminate, then kill. Server-initiated shutdown is rare
- *Stronger answer:* the three signals were tested: close gives exit 0, terminate -15, kill -9

**5. How does a request travel over Streamable HTTP?**

- A POST to `/mcp` with the JSON-RPC body. The server returns a session id header. The reply is in event-stream format

**6. STDIO or Streamable HTTP?**

- STDIO for local and personal. Streamable HTTP for remote, shared, hosted. Same JSON-RPC either way

**7. What does a tool failure look like to a client?**

- An `error` object for protocol failures, and a result flagged `isError` for tool failures. Handle both

**8. How would you give a locked-down company an MCP integration?**

- Build a custom, self-hosted server, possibly containerised, so data stays inside the organisation

## 4.14 Added by Claude, not from the sources

Items marked *checked* were tested with `fastmcp` 4.1.4 and `mcp` 2.3.0. Check current documentation.

- **Use the session id.** *Checked:* over HTTP the server issued `mcp-session-id`. A client that drops it on later requests loses its session
- **Send the `Accept` header with both types.** The client in 4.9 asks for `application/json, text/event-stream`. A plain GET without it got 406
- **A mounted app redirects `/mcp` to `/mcp/`.** *Checked* on the TimeTrack app ([Chapter 5](05-building-mcp-servers.md)): `POST /mcp` returned **307** to `/mcp/`. Clients that do not follow redirects on POST will fail. Configure the URL with the trailing slash
- **Pass an explicit transport to the FastMCP client.** *Checked:* `Client("server.py")` printed a deprecation warning that string inference will go in FastMCP 5. Use `StdioTransport` or a `Path`
- **STDIO sub-process rule:** the working directory and the environment belong to the **host** that launched the server. See the relative-path failure in Chapter 3, 3.3
- **Treat tool output as untrusted input to the model.** A tool that returns text from a web page or an email can carry instructions. Add guardrails before the model sees it. This is general practice, not from the sources

## Recap

- Operation = **discovery** (automatic, free) then **calling** (name plus arguments)
- A tool is a name, a description and an input schema. The description decides whether it is chosen
- Failures: a JSON-RPC `error`, or a result with `isError`. Handle both
- Tool results reach the model provider. Limit with access controls, middleware or a self-hosted server
- **Shutdown depends on the transport.** No JSON-RPC at shutdown
- **STDIO:** sub-process, `stdin` and `stdout`, local, fast, simple. Shutdown: close input, terminate, kill
- **Streamable HTTP:** POST to `/mcp`, session id, event-stream replies, works anywhere. Shutdown: close the connection, reconnect if unexpected
- Same JSON-RPC on both transports. HTTP + SSE is deprecated but still widespread

## Practice

1. Recreate the `input()` and `print()` demo. Say aloud which part is the client and which is the server
2. Start a FastMCP server with `mcp.run(transport="http", port=8765)` and repeat the `httpx` calls in 4.9. Note the session id and the status codes
3. Connect Context7 in VS Code and watch discovery happen
4. Close `stdin` of a STDIO server, then try terminate and kill. Compare exit codes
5. Trigger an unknown tool and a tool that raises. Write down the two reply shapes
6. In any inspector, trace one multi-step request and count the LLM calls and the tool calls
7. Find the three shutdown steps for STDIO and say why there is no JSON-RPC in them

## How this chapter was checked

- Run: the `input()` demo; a RecipeBox server through a FastMCP client; an unknown method, an unknown tool and a raising tool; the STDIO shutdown ladder (close input, SIGTERM, SIGKILL); a FastMCP server over Streamable HTTP with raw POST, GET and DELETE calls; the `mcp-session-id` header; and the `print()` inside a tool on STDIO
- **Not run:** Context7, Apple Notes, Claude Desktop, any third-party inspector, the Excalidraw server, reconnect after an unexpected close, MIME types, the old HTTP + SSE transport
- The class material is the source for everything not marked *checked*. Where the class and the test disagree (4.3), both are shown

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/18 - 6 Sep - MCP Capability Negotiation.md` (operation phase, privacy, live demos)
- Live-Class-2026, `classes_transcription_summary/19 - 12 Sep - MCP - Shutdown, Transport Layer.md` (shutdown, STDIO, Streamable HTTP, questions)
- Sections marked *checked* and 4.14 are from testing, not from the class sources

Previous: [Chapter 3, Lifecycle, JSON-RPC and capability negotiation](03-lifecycle-json-rpc-and-capability-negotiation.md) · Next: [Chapter 5, Building MCP servers](05-building-mcp-servers.md)
