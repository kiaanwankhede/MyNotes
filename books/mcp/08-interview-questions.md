# Chapter 8: Interview questions

**How to use this chapter**

- Eight production-style questions from the course's own interview file, each with a short answer
- Where I could test a claim, it is marked *checked*. Where a claim did not hold on the current library, the correction is shown
- A quick-fire list of concept questions follows, with the chapter that answers each
- Say the answer aloud. Then open the chapter and check what you missed

**Builds on:** every earlier MCP chapter. Chapters 1 to 7 each end with their own interview corner. This one adds the **production** questions.

**Tip from class:** concepts first. About 90% of candidates can define an MCP server. Fewer can explain what happens underneath, or the legacy-versus-modern history. Be ready to explain **why**, not only **what**.

## 8.1 How does the agent discover MCP servers and their capabilities?

- It does **not** go looking. Servers come from **configuration** or an **allowlisted registry**
- The **handshake** has both sides declare capabilities. On the modern protocol the version and capabilities travel in `_meta` on each request instead ([Chapter 7](07-legacy-vs-modern-mcp.md))
- **`tools/list`** returns each tool's name, description and input schema. **That is what the model sees**
- **Tool descriptions are prompt input.** Pin them and review them. A changed description can change what the model does or what an attacker can make it do
- Detail: [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.9, and [Chapter 4](04-operation-transports-and-shutdown.md), 4.1 to 4.2

## 8.2 How do you handle authentication and authorisation between agent and server?

*From the interview file. Not run here.*

- The MCP server acts as an **OAuth 2.1 resource server**
- A `401` with resource metadata leads the client to the **authorisation code flow with PKCE**
- The token is **short-lived** and **audience-bound** to that one server
- **No passthrough:** a downstream API gets its own token through a token exchange. Never forward the user's token
- Course context: static tokens in class were for learning scope gating only ([Chapter 5](05-building-mcp-servers.md), 5.10). The authentication code is planned for the code batch
- Class advice: read up on **JWT and OAuth**

## 8.3 How do you scope OAuth per capability, especially for sensitive actions?

*From the interview file. Not run here.*

- **One tool, one scope.** `payments:read` is not `payments:transfer`
- **Check the scope on every `tools/call`**, and **filter `tools/list` by scope** so the model never sees tools it may not use
- A missing scope returns **403 `insufficient_scope`**, followed by step-up and human approval
- **Limits** (amount, environment, tenant) live in **gateway policy**, with an audit log per user and per agent
- Link to class: per-user tool access is ordinary engineering with middleware, not an MCP feature ([Chapter 4](04-operation-transports-and-shutdown.md), 4.4)

## 8.4 How do you run several replicas when sessions are stateful?

**The problem:** by default a streamable HTTP server is **stateful**. `initialize` returns an `Mcp-Session-Id` and the server keeps that session in memory. A request that lands on another replica is rejected.

*Checked on `fastmcp` 4.1.4, over HTTP:*

- `initialize` returned a session id
- A request with an **unknown** session id: **HTTP 404**, error `-32600` "Session not found"
- A request with **no** session id: **HTTP 400**, "Missing session ID"
- That is exactly the replica problem

**Three ways out:**

1. **Run stateless** (preferred for request and response tool servers). Each request is self-contained, so any replica serves it
   - *Checked:* with the stateless flag the server returned **no session id**, and a `tools/list` with no handshake worked
   - **Correction:** the interview file writes `FastMCP(..., stateless_http=True)`. *Checked:* on `fastmcp` 4.1.4 this raises `TypeError`. The flag now goes to `run` or `http_app`:

```python
mcp.run(transport="http", host="0.0.0.0", port=8000, stateless_http=True)
# or: app = mcp.http_app(stateless_http=True)
```

   - You lose server-initiated messages, which most tool servers never use
2. **Sticky routing** on the `Mcp-Session-Id` header, at the ingress or service mesh
   - Avoid Kubernetes `sessionAffinity: ClientIP`. Every request from one agent pod would pin to one replica, so load is not balanced
3. **A shared session store** such as Redis. It works, but adds a dependency for little gain

- **Modern protocol:** there are no sessions, so none of this is needed ([Chapter 7](07-legacy-vs-modern-mcp.md))
- **Verify:** scale to two or more replicas and run a multi-turn conversation

## 8.5 How do you make sensitive calls such as transfers idempotent?

**The risk:** the database commits, the agent dies before the reply, and a retry moves the money twice.

- Pass an **idempotency key** as a tool argument. MCP has none built in
- Store the key **in the same transaction** as the transfer. A repeat returns the stored result
- **Re-check balances at execution**, not at approval

*A runnable version of that pattern (mine, not from the course), checked:*

```python
import sqlite3

def setup():
    c = sqlite3.connect(":memory:")
    c.executescript("""
      CREATE TABLE accounts (id TEXT PRIMARY KEY, balance REAL NOT NULL);
      CREATE TABLE transfers (idem_key TEXT PRIMARY KEY, src TEXT, dst TEXT, amount REAL, result TEXT);
      INSERT INTO accounts VALUES ('A', 100), ('B', 0);""")
    return c

def transfer(c, idem_key, src, dst, amount):
    with c:                                           # one transaction
        row = c.execute("SELECT result FROM transfers WHERE idem_key=?", (idem_key,)).fetchone()
        if row:                                       # a retry: return the stored result
            return row[0] + " (replayed)"
        bal = c.execute("SELECT balance FROM accounts WHERE id=?", (src,)).fetchone()[0]
        if bal < amount:                              # re-check the balance at execution
            raise ValueError("insufficient funds")
        c.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", (amount, src))
        c.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", (amount, dst))
        result = f"moved {amount} from {src} to {dst}"
        c.execute("INSERT INTO transfers VALUES (?,?,?,?,?)", (idem_key, src, dst, amount, result))
        return result

c = setup()
print(transfer(c, "k-1", "A", "B", 30))
print(transfer(c, "k-1", "A", "B", 30))              # the agent retried after a crash
print(c.execute("SELECT id, balance FROM accounts ORDER BY id").fetchall())
```

- *Checked output:* the second call printed `moved 30 from A to B (replayed)` and the balances were `A 70`, `B 30`. The money moved once
- The key must be **unique per intended action**, and the agent must **reuse** the same key on a retry

## 8.6 How do you keep the tool list in sync when a server changes?

Treat the tool **schema and description as an API contract.**

- **Only additive changes in place:** new tools, new optional parameters
  - A breaking change (renamed or removed parameter) ships as a **new tool name** next to the old one. Remove the old one once no agent uses it
- **Agents usually load tools once at start-up.** A server change takes effect after the agents restart. Either roll the agents, or handle `notifications/tools/list_changed` to refresh at run time
  - *Checked:* a tool added to a running server appeared when the client listed tools again. **No `list_changed` notification reached the client** in that in-memory test, and the server does not advertise it by default. Why was not investigated. Do not assume your library sends it
- **Descriptions change model behaviour.** A docstring edit can change routing. Run server changes through the same **evaluation suite** as agent changes
- **In CI, snapshot `tools/list` and diff it,** so contract changes show up in review
  - Related: converted tool names can be long and generated ([Chapter 5](05-building-mcp-servers.md), 5.9)

## 8.7 How do you tell tool failures from empty results?

Keep **three outcomes** distinct:

- **Success with data**
- **Success, but empty:** an explicit result such as `{"count": 0, "items": []}`, so the model can truthfully say "no transactions"
- **Failure:** a result with **`isError: true`** and a message the model can act on, for example "Account not found; call `list_accounts` first"

**Anti-pattern:** returning `{"error": ...}` as a normal successful result. The model may treat it as data, and your metrics count it as a success.

**Monitoring:**

- Emit a **per-tool metric** labelled `ok`, `empty` or `error`
- **HTTP status will not help,** because tool errors still travel as HTTP 200 (the interview file's claim, not tested over HTTP here)
- **Page** on infrastructure errors (database down, timeouts). **Let the model handle** user-input errors (unknown account, bad date)

**Correction on invalid parameters.** The interview file says invalid requests (bad parameters) are protocol-level JSON-RPC errors. *Checked on `fastmcp` 4.1.4 over STDIO:*

- A **wrong argument type** and a **missing argument** both came back as a normal result with **`isError: true`** and a readable validation message
- An unknown **tool name** also came back as `isError: true`
- Only an unknown **method** gave a JSON-RPC `error` (`-32601`)
- So handle **both** shapes in a client, and count `isError` results as failures ([Chapter 4](04-operation-transports-and-shutdown.md), 4.3)

## 8.8 What changed in the latest spec, and how does it affect running servers?

The July 2026 spec (**2026-07-28**) made MCP **stateless**: every request stands alone, like a normal HTTP API.

- **No `initialize` handshake.** Version and capabilities travel in `_meta` on every request
- **No sessions.** `Mcp-Session-Id` is gone, so **any replica serves any request**, and there is no sticky routing
- **State moves into tools.** Cross-call state becomes a **handle** the tool returns, for example `basket_id`
- **Deprecated:** Sampling, Roots, Logging, the old HTTP + SSE transport, and Dynamic Client Registration
- **Most production servers still run 2025-11-25,** where sessions are optional but stateful by default

**What replaces the deprecated features:**

- **Roots:** pass paths as tool parameters
- **Sampling:** call the provider's API directly
- **Logging:** OpenTelemetry, or standard error
- **HTTP + SSE:** Streamable HTTP
- **Dynamic Client Registration:** Client ID Metadata Documents

- *Checked:* over STDIO a modern server accepted requests with no handshake and refused them without `_meta`. Over HTTP the library tested spoke the legacy protocol only. Full detail and the official changelog link: [Chapter 7](07-legacy-vs-modern-mcp.md)
- Dynamic Client Registration and its replacement are from the interview file and were not confirmed in the official page text I could read

## 8.9 Quick-fire concept questions

One-line answers. The chapter that explains each is in brackets.

**Basics**

- What problem does MCP solve? It replaces about N times M custom integrations with about N plus M ([Chapter 1](01-why-mcp-exists.md))
- Is MCP a paid product or an orchestrator? Neither. It is a free, open specification ([Chapter 1](01-why-mcp-exists.md))
- Do I always need MCP? No. A plain tool suits a narrow, fixed action ([Chapter 6](06-deployment-and-building-a-client.md), 6.9)
- Host, client, server? App, one connection per server, a focused program ([Chapter 2](02-primitives-and-architecture.md))
- Why one client per server? Decoupling, safety, scalability, parallelism ([Chapter 2](02-primitives-and-architecture.md), 2.3)
- Three primitives? Tools (do), resources (read), prompts (a form) ([Chapter 2](02-primitives-and-architecture.md), 2.6)
- Who triggers each primitive? Model, application, user ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.1)

**Protocol**

- Why JSON-RPC and not REST? Lightweight, transport-agnostic, two-way, notifications, standard errors ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.6)
- What is the `id` for? To match a response to its request ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.5)
- The three lifecycle phases? Initialization, operation, shutdown ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.4)
- How does version negotiation work? Client proposes its latest, server answers, client accepts or disconnects ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.8)
- Why call `tools/list` after negotiation? Negotiation names categories, discovery names tools ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.9)
- Elicitation or human-in-the-loop? Server asks for missing information, against an approval layer in the app ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.9)

**Transports and shutdown**

- STDIO or Streamable HTTP? Local and personal, against remote and shared ([Chapter 4](04-operation-transports-and-shutdown.md), 4.11)
- How does STDIO shut down? Close input, terminate, kill ([Chapter 4](04-operation-transports-and-shutdown.md), 4.8)
- Why is there no JSON-RPC at shutdown? The transport does the closing ([Chapter 4](04-operation-transports-and-shutdown.md), 4.6)
- Does MCP send my data to the model provider? Yes ([Chapter 4](04-operation-transports-and-shutdown.md), 4.4)

**Building and deploying**

- Official SDK or FastMCP? SDK is the base, FastMCP the easy layer ([Chapter 5](05-building-mcp-servers.md), 5.1)
- Convert an API or write tools? Convert for speed, write for control and prompts ([Chapter 5](05-building-mcp-servers.md), 5.9)
- Two mounting mistakes in FastAPI? Path set twice, and `lifespan` not passed at construction ([Chapter 5](05-building-mcp-servers.md), 5.8)
- Who calls the tool, the model or the client? The client ([Chapter 6](06-deployment-and-building-a-client.md), 6.7)
- How do you make a server read-only? Do not register write tools ([Chapter 6](06-deployment-and-building-a-client.md), 6.9)

**Legacy and modern**

- What is the one idea behind the modern spec? Stateless requests ([Chapter 7](07-legacy-vs-modern-mcp.md), 7.2)
- Removed or deprecated? Different lists, twelve-month floor for deprecated ([Chapter 7](07-legacy-vs-modern-mcp.md), 7.4)

## 8.10 Added by Claude, not from the sources

Items marked *checked* were run with `fastmcp` 4.1.4.

- **Know the corrections.** In this chapter the tested library differed from the interview file in two places (the stateless flag on the constructor, and bad parameters as JSON-RPC errors) and did not send `list_changed` in my test. Saying "I checked it on the current version" lands well. Library details change, so say which version
- **Prepare one story per production topic:** authentication, replicas, idempotency, schema changes, errors and monitoring. A short real example beats a definition
- **Be honest about what you ran.** The class advice: describe a project as what it is, framed around the problem it solved. Shallow claims get exposed
- **Draw the three diagrams from memory:** host, client and server; the handshake; the legacy and modern difference. Interviewers often ask for a sketch
- **Practise both answers where the spec changed:** "how it worked" (stateful sessions) and "how it works now" (stateless requests)

## Recap

- Servers are configured, not discovered. Tool descriptions are prompt input
- Auth: OAuth 2.1 resource server, PKCE, short-lived audience-bound tokens, one scope per tool, no passthrough
- Replicas: run stateless, or use sticky routing, or a shared store. The stateless flag goes on `run` or `http_app` in the current library
- Idempotency: a key in the same transaction as the action, and a re-check at execution
- Contract changes: additive only, snapshot `tools/list`, evaluate descriptions
- Three outcomes: data, empty, error. Count `isError` results as failures. Handle both error shapes
- Modern spec: stateless, `_meta`, handles for state, deprecations with a twelve-month floor

## Practice

1. Answer 8.1 to 8.8 aloud in under a minute each. Then compare with this chapter
2. Run the idempotency example. Make the second call use a new key and watch the money move twice
3. Start a server with and without the stateless flag. Send a request with a made-up session id to each
4. Send a wrong-type argument to a tool and write down the reply shape
5. Snapshot a server's `tools/list` to a file, change a docstring, and diff
6. Draw the three diagrams in 8.10 on paper without notes

## How this chapter was checked

- Run: session id behaviour on a stateful HTTP server (404 for an unknown id, 400 for none); the stateless flag; the constructor flag error; bad-type and missing arguments; an unknown tool and an unknown method; a tool added at run time; and the idempotency example
- **Not run:** OAuth, PKCE, scopes, gateways, replicas behind a real load balancer, Redis, metrics, HTTP status of tool errors
- Sections 8.1 to 8.3 and 8.5 to 8.8 follow the interview file. Where the test disagrees, the correction is shown

## Sources and further reading

- Live-Class-2026, `interview-questions/mcp.md`
- Live-Class-2026, `classes_transcription_summary/22 - 20 Sep - Legacy vs Modern MCP.md` and `21 - 19 Sep - MCP Deployment.md`
- Model Context Protocol specification, 2026-07-28, changelog: https://modelcontextprotocol.io/specification/2026-07-28/changelog
- The idempotency example, the corrections and 8.10 are from testing, not from the interview file

Previous: [Chapter 7, Legacy vs modern MCP](07-legacy-vs-modern-mcp.md)
