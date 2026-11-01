# Chapter 7: Legacy vs modern MCP

**After this chapter you can:**

- Say what changed between the legacy spec (2025-11-25) and the modern spec (2026-07-28), and the one idea behind every change
- Explain why everything built so far still works
- Tell **removed** from **deprecated**, and say what replaces each deprecated feature
- Read a modern request, with no handshake and `_meta` on every call
- Choose a client connection mode: `auto` or `legacy`
- Explain what happens to elicitation, sampling, ping and timeouts in a modern client

**Builds on:** the handshake in [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md) (3.7 to 3.9), transports in [Chapter 4](04-operation-transports-and-shutdown.md), the client loop in [Chapter 6](06-deployment-and-building-a-client.md).

## 7.1 The real timeline

- **Everything built in this course still runs.** Nothing was wasted
- **Legacy spec:** version **2025-11-25**. This is what the course has taught so far
- **Modern spec:** version **2026-07-28**, published on 28 July 2026
- **Adoption is opt-in.** Nothing forced existing servers to change on that date. There is no blanket migration deadline
- **Only named features have a clock.** Anything marked deprecated gets a **minimum of twelve months** before it can be removed. Class: earliest removal is July 2027
- Most real servers, local and hosted, still run the legacy architecture. Rewriting a working system is real engineering work
- *Confirmed against the official changelog:* it lists the changes since 2025-11-25 and defines a feature lifecycle (Active, Deprecated, Removed) with a **minimum twelve-month deprecation window**

## 7.2 The one idea: from "remember me" to "tell me every time"

- **Legacy:** a handshake once, and the server **remembers** you for the whole session
- **Modern:** **no handshake.** Every message carries everything about itself
- Class analogy, a co-working space:
  - One building: the same receptionist waves you through because she knows your face. That is the legacy **`Mcp-Session-Id`**
  - Another building: everyone taps a badge at every door. A bit more tapping, but **any door** works, on any day, whoever is on shift
- **Why give up memory?** A server that must remember you can only be handled by whoever met you first. A server that reads a badge each time can be **any** server behind a load balancer
- Support-call analogy: a call connects you to one agent who remembers you, and if it drops you start again. A **ticket** holds everything, so any agent can pick it up
- The cost is a little more data per request. The gain is scaling out without anyone remembering a client
- Every other change below follows from this idea

*Checked on a legacy HTTP server:* the `initialize` reply carried an `mcp-session-id` header, which is what the class showed with `curl`.

## 7.3 What changed, side by side

| | Legacy (2025-11-25) | Modern (2026-07-28) |
|---|---|---|
| Opening | `initialize`, reply, `initialized` | No handshake. An optional `server/discover` |
| Version and capabilities | Sent once in the handshake | In **`_meta` on every request** |
| Session | `Mcp-Session-Id` header | None |
| Server asks the user mid-task | Server sends its own request (elicitation) | Only while answering a request the client sent |
| Cross-call state | Held by the session | Tools return a **handle** you pass back |
| Routing | Server reads the body | `Mcp-Method` and `Mcp-Name` headers |
| Caching | Nothing built in | `ttlMs` and `cacheScope` on results |
| Liveness | `ping` | Removed |
| Log level | `logging/setLevel` | Removed |

**A modern request over STDIO** (checked, below):

```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/list",
 "params": {"_meta": {
   "io.modelcontextprotocol/protocolVersion": "2026-07-28",
   "io.modelcontextprotocol/clientInfo": {"name": "t", "version": "0"},
   "io.modelcontextprotocol/clientCapabilities": {}}}}
```

*Checked on `fastmcp` 4.1.4 over STDIO, with no `initialize` and no `initialized`:*

- `tools/list` and `tools/call` both worked straight away
- Results carried `resultType: "complete"`, and the list carried **`ttlMs`** (0) and **`cacheScope`** (`private`)
- The same call **without `_meta`** was refused with error `-32602`: `params._meta` must carry the protocol version and client capabilities. So `_meta` is not optional
- `server/discover` returned `supportedVersions` and the server's capabilities (see [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.8)

**Limit of this test:** the same library's **HTTP** server did **not** accept modern requests. Over HTTP, `server/discover` got `400 Missing session ID` (stateful) or `Method not found` (stateless flag). So in this version HTTP served the legacy protocol. A modern client falls back, as in 7.6. Why, or whether a setting changes it, was not found out

### Asking mid-task: the restaurant rule

- If nothing is remembered, how does a server ask "how spicy do you want it?"
- A kitchen can send a waiter back **while your order is being cooked**. It cannot walk up to an empty table and start asking
- **Rule 1, "already cooking":** a server may ask only while handling something the client already requested
- **Rule 2, "real question":** the reply must hold an actual question, never a vague "something is needed"
- Class example: a TimeTrack tool asked to log 14 hours comes back with "that seems unusually high, do you want to log it?"
- Official name for this pattern: **Multi Round-Trip Requests (MRTR)**. It replaces server-initiated requests such as `roots/list`, `sampling/createMessage` and `elicitation/create`

### The OTP pattern: confirm and continue

- The app asks for a code. You fetch it, come back, and submit it **with your order reference**
- A **different backend server** can finish the order, because the ticket carries everything
- The assistant that asked is free to do other work meanwhile. Whoever is free when the answer arrives picks it up

### The small stuff

- **Faster routing:** `Mcp-Method` and `Mcp-Name` in the HTTP headers, like a coloured tag on a boarding pass. A load balancer reads just those two labels. Not tested here
- **Smarter caching:** `ttlMs` says how long an answer stays fresh. `cacheScope` says whether it is safe to **share across users** or **private to one**. Checked: both appeared in results
- **Finding what broke:** tracing built on the W3C standard. One tracking context follows a request across systems, like a parcel number. The changelog names `traceparent`, `tracestate` and `baggage` in `_meta`

## 7.4 Removed or deprecated?

- **Removed** (gone): the old handshake, `ping`, `logging/setLevel`, the session header (class). The changelog also names `notifications/roots/list_changed`
- **Deprecated** (still works, with a clock): **Roots, Sampling, Logging**, and the **HTTP + SSE** transport
- **Policy:** a minimum of twelve months from announcement, started July 2026. It is a **floor**, not a countdown to breakage
- **A library can drop code sooner.** The twelve months is the spec's promise. FastMCP removed its sampling support already (7.5)

| Deprecated | Suggested replacement |
|---|---|
| Roots | Pass paths as tool parameters |
| Sampling | Call the LLM provider's API directly |
| Logging | OpenTelemetry, or standard error |
| HTTP + SSE | Streamable HTTP |
| Dynamic Client Registration | Client ID Metadata Documents |

- The first four match the official changelog's suggested migrations. **Dynamic Client Registration** comes from the course interview file and a secondary article. It was **not** confirmed in the official page text I could read
- The class listed ping as removed. The official changelog confirms it

*Checked on `fastmcp` 4.1.4:*

- `logging/setLevel`: legacy connection returned an empty success. A modern request returned **"Method not found"**
- `ping`: legacy `True`. A modern connection: "Method not found"

## 7.5 A client that works with the current library

Every client does five things: **start, handshake, call, use the response, clean up.**

- `try`/`finally` and `async with client` are two ways to write the same five steps
- `async with` **guarantees step 5** whatever happens. That is why the course uses it

### Connection modes

*From the installed library's own documentation of the `mode` option of `Client` (version 4.1.4):*

- **`"auto"`** (default): probes `server/discover`, and falls back to the `initialize` handshake for any server that is not clearly modern. Safe against a mix of old and new servers
- **`"legacy"`**: forces the `initialize` handshake, as before version 4
- **A version string** such as `"2026-07-28"`: adopts that version without probing
- This is the "newer call first, then fall back" behaviour from [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.8

### Sampling: genuinely removed

- **Sampling:** a server borrows the **client's** model, so a light server needs no model key of its own
- **Modern way:** the tool calls an LLM provider **directly**, with its own key. This is also the spec's suggested migration
- Class proof: the old sampling pattern fails on the current library. Class's `summarize_week` tool was rewritten to call a provider
- *Checked:* the server `Context` class in `fastmcp` 4.1.4 has **no `sample` method**, but does have `elicit` and `report_progress`. The `Client` still accepts a `sampling_handler` argument. A full sampling run was not tested
- Whether a tool needs a completion is decided by **the tool's own code**. The framework does not call one for you

### Elicitation: only on a legacy connection

```python
client = Client(transport, elicitation_handler=elicitation_handler, mode="legacy")

async def elicitation_handler(message, response_type, params, context):
    print(f"Server is asking: {message}")
    return input("Type Y to confirm: ").strip().lower() == "y"
```

*The class showed only the client. This is the server tool I wrote to test it:*

```python
@mcp.tool
async def log_time(employee: str, hours: float, ctx: Context) -> str:
    """Log hours. Asks for confirmation above 10 hours."""
    if hours > 10:
        result = await ctx.elicit(f"{hours:g} hours in one day is unusually high, log it anyway?",
                                  response_type=bool)
        if result.action != "accept" or not result.data:
            return "cancelled, not confirmed by user"
    return f"logged {hours:g}h for {employee}"
```

*Checked, matching the class demo:*

- 4 hours: **no question**, logged
- 14 hours with the handler answering yes: the question was asked, then logged
- 14 hours with the handler answering no: `cancelled, not confirmed by user`
- The tool has a `Context` parameter. That is its channel back to the client
- On a **default (modern) connection**, the same tool failed with: *elicitation via server-initiated requests is unavailable on 2026-07-28 connections.* So the class statement holds. Modern elicitation goes through MRTR, which was not tested here

### Ping, timeout and cancellation

- **Ping** asks "are you still there?". Removed in the strict modern sense, since nothing persistent is left to ping. In legacy mode `client.ping()` returned `True` in class
  - *Checked:* `True` in `legacy`, and "Method not found" in `auto`
- **Timeout and cancellation:** a deliberately slow tool (5 seconds) against a client timeout of 1 second was cancelled with a clear error. A longer timeout let it finish
  - *Checked:* `Client(..., timeout=1)` and a 5-second tool gave `Request 'tools/call' timed out` after 1.0 seconds. With `timeout=10` and a 2-second tool it returned normally
  - **Rule:** every sent request should have a timeout. A cancellation notification stops waiting. A progress notification can reset the clock while the server is still working. Progress reporting was not tested

## 7.6 How LangChain fits in

- When LangChain is the host, **its agent is the host**. LangChain creates the MCP client itself using the **LangChain MCP Adapters** package, which is built on FastMCP
- `MultiServerMCPClient` with a config dictionary goes through the **same handshake and discovery** as any client. LangChain builds the harness for you ([Chapter 6](06-deployment-and-building-a-client.md), 6.7)
- **Every MCP server, whatever library wrote it, rests on the same official protocol.** FastMCP is an abstraction that makes writing it easier
- For an agent framework, MCP is "a connection to a set of tools", sourced from a standard protocol instead of hand-written functions
- LangChain's MCP support **consumes** servers. It does not build them. Building stays with MCP and FastMCP
- Next: [Langchain, Chapter 12](../langchain/12-mcp-in-langchain.md) (not written yet)

## 7.7 Follow-ups from class 22

- A **hard-coded database path** silently failed once deployed to Vercel. Fix: read the path from an environment variable ([Chapter 6](06-deployment-and-building-a-client.md), 6.3)
- **Homework:** make database calls asynchronous, and move from a local SQLite file to a hosted database. The class demoed **filess.io**, a free hosted SQL database of about 10 MB with ready-made connection code. Not tried here
- Class roadmap: this was the **last dedicated MCP class**, followed by multi-agent systems in LangChain and a project

## 7.8 Class questions

- **Do I need to master every previous version?** No. Adoption will take time, and knowing legacy is what makes modern make sense
- **Is sampling controlled in code or called automatically?** By the tool's own code
- **Are sampling and elicitation MCP ideas, or FastMCP's?** MCP's. A framework only implements them
- **Does the same handshake apply when LangChain is the host?** Yes, underneath
- **Does LangChain's MCP support create servers?** No, only consumes them
- **Can an OpenRouter key replace a provider key in the client exercises?** Yes, with a small change to the endpoint and model name

## 7.9 Interview corner

**1. What is the single idea behind the modern spec?**

- Stateless requests: no handshake and no session. Every message carries its version and capabilities
- *Stronger answer:* the gain is that any replica can serve any request, so no sticky routing

**2. Removed or deprecated?**

- Removed: the old handshake, ping, `logging/setLevel`, the session header. Deprecated: Roots, Sampling, Logging, HTTP + SSE
- *Stronger answer:* deprecated has a twelve-month minimum, and a library may drop code sooner

**3. What replaces sampling?**

- The tool calls an LLM provider directly with its own key

**4. How can a stateless server ask the user a question?**

- Only while handling a request the client sent. In the spec this is MRTR
- *Stronger answer:* a server never contacts a client out of nowhere

**5. A client meets an old server. What does it do?**

- In `auto` mode it tries `server/discover`, and on failure falls back to `initialize`
- *Checked:* a modern client really does this

**6. Why does every request now carry `_meta`?**

- Because nobody remembers the client. The version and capabilities travel with each call
- *Checked:* a request without it was refused

**7. How do you keep state without sessions?**

- Return a handle from a tool (such as a `basket_id`) and pass it back as an argument

**8. Will my legacy server break?**

- No. Adoption is opt-in. Plan to support both, and watch the deprecated list

## 7.10 Added by Claude, not from the sources

Items marked *checked* were run with `fastmcp` 4.1.4 and `mcp` 2.3.0.

- **A "legacy mode" client against a modern-only server will fail,** and the reverse is handled by `auto`. Keep `auto` unless you have a reason to pin
- **Check what your library really speaks.** *Checked:* this version's HTTP server spoke legacy only, while its STDIO server spoke both. Do not assume modern means HTTP
- **The class's "elicitation behind `mode="legacy"`" is one library's behaviour.** The spec's own answer is MRTR. Learn both names
- **Treat library and spec versions separately.** Several class commands changed between FastMCP 3 and 4 ([Chapter 2](02-primitives-and-architecture.md), 2.8)
- **Plan migration by risk:** list which servers use sampling, roots, logging, sessions or HTTP + SSE, then migrate those first
- **Official source to keep open:** the MCP specification's changelog page for 2026-07-28

## Recap

- Legacy 2025-11-25 and modern 2026-07-28 coexist. Adoption is opt-in. Nothing you built breaks
- One idea: **remember me** became **tell me every time**. No handshake, no session, `_meta` on every request
- Servers may ask mid-task only while answering a request (MRTR). State moves into handles returned by tools
- Removed: handshake, ping, `logging/setLevel`, session header. Deprecated: Roots, Sampling, Logging, HTTP + SSE. Minimum twelve months
- Replacements: tool parameters, direct provider calls, OpenTelemetry or stderr, Streamable HTTP
- Client `mode`: `auto` (probe, fall back), `legacy`, or a version string
- Sampling is gone from the current library. Elicitation and ping need a legacy connection. Every request needs a timeout
- LangChain's adapters build the client for you and only consume servers

## Practice

1. Send a modern `tools/list` request over STDIO with `_meta`, then without it. Compare the replies
2. Connect with `mode="auto"` and `mode="legacy"` to the same server. Call `ping()` in both
3. Build the elicitation demo with `mode="legacy"`. Test 4 hours, 14 hours with yes, and 14 hours with no
4. Make a client timeout shorter than a slow tool and read the error
5. Rewrite a tool that used sampling so it calls a provider directly
6. List the deprecated features your own servers use
7. Explain in your own words why removing the session header helps a load balancer
8. Read the 2026-07-28 changelog page and find each item from 7.3 and 7.4

## How this chapter was checked

- Run: a modern request with and without `_meta` over STDIO; the results' `resultType`, `ttlMs` and `cacheScope`; `server/discover` over STDIO and over HTTP; legacy session ids, a stale session id and the stateless flag; `logging/setLevel` on both connections; `ping` in `auto` and `legacy`; elicitation under `legacy` (three branches) and under the default connection; timeouts; the server `Context` methods; and the `mode` option's documentation
- Checked against the official specification changelog (read through search results): the handshake removal, `_meta`, removed items, deprecated items and suggested migrations, the twelve-month window, MRTR, state handles and tracing keys
- **Not run or not confirmed:** modern requests over HTTP, `Mcp-Method` and `Mcp-Name` headers, Client ID Metadata Documents, a full sampling run, MRTR elicitation, progress reporting, filess.io, Vercel, LangChain's adapters
- The class write-up is the source for everything else

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/22 - 20 Sep - Legacy vs Modern MCP.md`
- Live-Class-2026, `interview-questions/mcp.md` (the specification summary and the replacements list)
- Model Context Protocol specification, 2026-07-28, changelog: https://modelcontextprotocol.io/specification/2026-07-28/changelog
- Class resources, not opened: the "legacy vs modern" site and the FastMCP "what's new" page
- Sections marked *checked* and 7.10 are from testing

Previous: [Chapter 6, Deployment and building a client](06-deployment-and-building-a-client.md) · Next: [Chapter 8, Interview questions](08-interview-questions.md)
