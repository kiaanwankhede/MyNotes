# Chapter 6: Deployment and building a client

**After this chapter you can:**

- Explain why a local server is not enough, and when to use STDIO or HTTP
- Run the same server as a STDIO-only server or as a full web application
- Prepare a clean repository and deploy an MCP server to Prefect Horizon
- Connect a host to a deployed server
- Explain why you sometimes need your own MCP client, and build the agent loop
- Answer common questions about gateways, read-only servers and state

**Builds on:** [Chapter 4](04-operation-transports-and-shutdown.md) (transports), [Chapter 5](05-building-mcp-servers.md) (TimeTrack and mounting rules).

## 6.1 From "works on my machine" to "anyone can use it"

- A working local server only helps the machine it runs on
- Getting further needs two decisions: **which transport**, and **where it runs**

| | Local STDIO | Remote HTTP |
|---|---|---|
| Runs | On your machine, as a sub-process | Somewhere else, reachable over the internet |
| Speed | Fast, no network hop | A real network round trip on every call |
| Who can use it | Only whatever launched it | Many clients, from anywhere, at once |
| Where the power lives | Split across each person running it | Centralised: one server can be powerful and serve everyone |
| Typical use | A personal tool | A team or company tool |

- This is why most serious **shared** servers run over HTTP. The transports themselves are in [Chapter 4](04-operation-transports-and-shutdown.md), 4.7 to 4.11

## 6.2 The same file, two transports

```bash
uv run fastmcp run main.py          # the MCP server object only, over STDIO
uv run uvicorn main:app --reload    # the whole application: website, REST API and MCP, over HTTP
```

- `fastmcp run main.py` starts **just the MCP server object** (`mcp`)
- `uvicorn main:app` starts **the FastAPI app** that has the website, the REST API and the mounted MCP server together. The MCP endpoint is `/mcp`
- *Checked on `fastmcp` 4.1.4 with the TimeTrack `main.py`:*
  - `fastmcp run main.py` answered an `initialize` request over STDIO
  - `fastmcp run main.py --transport http --port 8766` served `/mcp` (HTTP 200) and **no website** (`/` gave 404). The website only exists when you run the FastAPI app
  - So a FastMCP server alone can already be served over HTTP, with one flag. FastAPI is needed only when you also want a website and REST routes

## 6.3 The code, and what to know about it

- The full `main.py` is in [Chapter 5](05-building-mcp-servers.md), 5.8: tools, a resource, a prompt, `http_app(path="/")`, `FastAPI(lifespan=...)` and the `/mcp` mount
- The class repeated the two rules: **`path="/"`** and **`lifespan` at construction** (both checked in Chapter 5)
- **Where the database lives:** the deployed version reads its file path from an **environment variable**, with a fallback

```python
import os
from pathlib import Path

DB_PATH = Path(os.environ.get("TIMETRACK_DB_PATH", "/tmp/timetrack.db"))
```

- *Checked:* with no variable the file was `/tmp/timetrack.db`. With `TIMETRACK_DB_PATH` set, it used that path
- Small guardrails in `database.py` (class): `log_time` rejects hours of zero or less, and `get_project_summary` uses a real `GROUP BY`. A tool exposed to an AI will sometimes receive bad input

## 6.4 Deploying to Prefect Horizon

**Horizon** is the hosting platform FastMCP's documentation points to. It was called **FastMCP Cloud** before, and is built by Prefect, the company behind FastMCP. *Checked:* the banner printed by `fastmcp` 4.1.4 links to `horizon.prefect.io`.

The class free-tier note (class 20, not verified): **one developer, up to 200 MCP servers, one-hour log retention.** Code changes deploy automatically through the GitHub connection.

**The steps:**

1. **Make a clean, separate repository** with only the server
   - `main.py`, `database.py`, `pyproject.toml`, `uv.lock`
   - The platform builds from exactly what is in the repo, so scratch files and notes do not belong
   - `pyproject.toml` lists the libraries. `uv.lock` pins the exact versions. Together they let the platform rebuild your environment
2. **Add a `.gitignore`:** virtual environment, local database files, caches, editor folders
3. **Connect the repo to Horizon.** Sign in with GitHub and pick the repository. Dependencies are found from `pyproject.toml`
4. **Configure and deploy:** name the server and set the **entry point to `main.py:mcp`**
   - Point at the **`mcp` object**, not the whole `app`
   - Optional check before deploying: `fastmcp inspect main.py:mcp`. *Checked:* it printed 4 tools, 1 prompt and 1 resource for TimeTrack
   - Horizon installs the libraries and starts the server. Logs are visible during the build
5. **Get the URL:** `https://your-project-name.fastmcp.app/mcp`. Paste it into any host's connector settings (Claude Desktop, Claude on the web, ChatGPT, Cursor)

**Two things to know:**

- **Local and hosted databases are completely separate files.** Data you add locally never appears on the server, and the reverse. The database is created fresh where the server runs
- **Horizon is built for the MCP piece.** Check whether a website's static files deploy with it. If not, a general host such as Vercel or Railway can run the whole application. The class resources list a deployed demo and its repository. Neither was opened for these notes

*None of the Horizon steps were run here.*

## 6.5 Connect a host to the deployed server

```json
{
  "mcpServers": {
    "timetrack": { "url": "https://your-project-name.fastmcp.app/mcp" }
  }
}
```

- Class demonstration: ask "what projects exist?", ask the AI to log 10 hours against a new project, then list projects again. The new project appears at once
- **Anyone with the URL can connect** and log their own hours through their own AI assistant. All of it writes to the **same shared, hosted database**
- A public time-tracking server for a real company needs **access control**. The class planned authentication as a next step ([Chapter 5](05-building-mcp-servers.md), 5.10)
- If a client does not follow redirects, use the URL with a trailing slash ([Chapter 4](04-operation-transports-and-shutdown.md), 4.14)

## 6.6 MCP does not need an API underneath

A bare-bones second server, deployed the same way:

```python
from fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

- No API, no database. "What is 5 plus 3?" becomes a `tools/call` to `add`
- **An MCP server is just a server.** What it does inside is up to you
- *Checked:* a client called `add` on this server and got the result back. A bad argument (`"x"`) came back as a tool error flagged `is_error`

## 6.7 Why build your own client?

- Until now clients were taken for granted. Claude Desktop and VS Code **are** MCP clients. They do the handshake, discovery and tool calls for you
- **Harness engineering:** you have a raw model (an API key, no chat app) and a capable MCP server. Neither can do anything for the other
  - The model does not know the server exists. The server cannot decide anything
  - **Something in the middle must connect them.** Building that layer yourself is harness engineering
- Every chat app is a harness around a raw model. Claude Desktop and ChatGPT just build and hide it for you

**The loop (class diagram, as steps):**

```
client → server : list_tools()
client → model  : the user message + the tools, formatted for the provider
model  → client : "call log_time with these arguments"   (tool_use)
client → server : call_tool("log_time", args)             ← the CLIENT calls it
server → client : result
client → model  : the result, appended to the messages
model  → client : the final answer (stop reason is not tool_use)  → loop ends
```

- **The model never calls the tool. The client does.** The model only says which tool it wants
- This is the same agentic loop built earlier in the course. MCP only standardises how the **tool list and the tool call** travel between client and server
- Framework "MCP adapters" (LangChain's, for example) wrap exactly this pattern in a few lines, as `create_agent()` wraps the raw loop. That is in the next Langchain chapter ([Chapter 12](../langchain/12-mcp-in-langchain.md), not written yet)

### The class code

```python
from fastmcp import Client
from anthropic import Anthropic

anthropic_client = Anthropic()

async def run_agent(user_message: str):
    async with Client("main.py") as mcp_client:
        mcp_tools = await mcp_client.list_tools()
        anthropic_tools = [
            {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
            for t in mcp_tools
        ]
        messages = [{"role": "user", "content": user_message}]
        while True:
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-6", messages=messages, tools=anthropic_tools)
            if response.stop_reason != "tool_use":
                return response.content
            for block in response.content:
                if block.type == "tool_use":
                    result = await mcp_client.call_tool(block.name, block.input)
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": [
                        {"type": "tool_result", "tool_use_id": block.id, "content": str(result)}]})
```

*Not run against the real Anthropic API (no key here). Run with a stand-in for the model and a real FastMCP client and server. Two problems showed up:*

1. **Two tool calls in one model turn break the message order.** The class code appends the assistant message **inside** the loop over blocks, and one user message per result
   - *Checked:* with a model turn that asked for two tools, the messages became `user, assistant, user, assistant, user`
   - The model provider's tool-use format expects **one** assistant message followed by **one** user message holding **all** the `tool_result` blocks. Check the current API documentation. This was not tested against the live API
2. **`str(result)` sends a repr to the model.** *Checked:* it produced `CallToolResult(content=[TextContent(type='text', text='8.0', ...`. Send the text instead

### A corrected loop

*Checked with a stand-in model that asks for two tools in one turn, then answers:*

```python
async def run_agent(anthropic_client, mcp_client, user_message: str, model: str):
    mcp_tools = await mcp_client.list_tools()
    tools = [{"name": t.name, "description": t.description, "input_schema": t.inputSchema}
             for t in mcp_tools]
    messages = [{"role": "user", "content": user_message}]
    while True:
        response = anthropic_client.messages.create(model=model, messages=messages, tools=tools)
        if response.stop_reason != "tool_use":
            return response.content
        messages.append({"role": "assistant", "content": response.content})   # once per model turn
        results = []
        for block in response.content:
            if block.type == "tool_use":
                out = await mcp_client.call_tool(block.name, block.input, raise_on_error=False)
                text = "".join(c.text for c in out.content if getattr(c, "type", "") == "text")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": text, "is_error": out.is_error})
        messages.append({"role": "user", "content": results})                  # all results together
```

- The messages the model saw on its second turn were `user`, `assistant` (two blocks), `user` (two results)
- With `raise_on_error=False`, a bad argument came back as a result with `is_error` true and a readable message. The loop can pass that to the model instead of crashing
- The class passed `Client("main.py")`. *Checked:* a string path prints a deprecation warning in `fastmcp` 4.1.4. Use `StdioTransport` or a `Path`
- The model name in the class code is the class's choice. Use a current model name from the provider's documentation. Keep the API key in an environment variable, never in code

## 6.8 Where this leaves you

- **Host** = the app plus its built-in client. **Client** = the harness that connects the model to a server. **Server** = tools, resources and prompts over a shared protocol
- Each piece stops being mysterious once you have built it by hand once
- **Two honest gaps in the class project:** the database is a local SQLite file, not a production database, and database calls are **synchronous**
  - Class claim: "two requests cannot genuinely run at the same time"
  - *Checked, and different:* three calls at once to a tool that blocks for one second took about **1.0 second** whether the tool was `def` or `async def`. `fastmcp` 4.1.4 ran the synchronous tools concurrently. Calls to one SQLite file can still collide on writes. That was not tested

## 6.9 FAQ from class 21

- **A Postgres MCP server runs on my laptop and reaches a remote database. Is it local?** Yes. "Local" means where the **MCP server process** runs, not where the data is
- **Where do the tools in a Postgres MCP server come from?** From whoever built it, such as the vendor or the community. You get functions like `execute` and `list_tables` for free
- **Always use MCP, or sometimes a plain tool?** A plain tool suits a narrow, fixed action (one email channel). MCP earns its place when a **broad surface** must be supported without hand-building dozens of tools
- **One setup that reaches Postgres, Oracle and a mainframe?** Two options: one custom server with all of them wired in, or an **MCP gateway** that puts several servers behind one entry point
- **How to stop an AI from changing data on a production database?** A common pattern is an **environment variable** such as `READ_ONLY=true`, read at start-up, that decides which tools are registered. Write tools are never exposed
  - *Checked:* with the variable unset the server listed `list_rows` and `delete_row`. With `READ_ONLY=true` it listed only `list_rows`
- **`uv` against `uvx`?** `uv` works inside your project. `uvx` runs a tool in an isolated temporary environment, like `npx`. Use `uvx` for a one-off run. *Checked:* both commands exist on this machine. Behaviour not tested
- **Does a hosting platform care whether my server calls an AI model?** No. A call to a model provider is just another API call
- **State at three levels (one call, one thread, the whole app)?** Application state lives as long as the process. Session state ties to a session id. **Thread state is the hardest** and has no free built-in mechanism, so you design it in

## 6.10 Interview corner

**1. When do you choose STDIO and when HTTP?**

- STDIO for a personal tool on one machine. HTTP for a shared, hosted server
- *Stronger answer:* HTTP has a network round trip but centralises power and serves many clients

**2. What does `fastmcp run main.py` start, and what does `uvicorn main:app` start?**

- The first starts only the MCP server object. The second starts the whole app: website, REST and the mounted MCP server

**3. Walk me through deploying an MCP server.**

- Clean repo with `main.py`, `database.py`, `pyproject.toml`, `uv.lock`. `.gitignore` for the environment and local data. Connect to the platform. Entry point `main.py:mcp`. Get a URL ending in `/mcp`
- *Stronger answer:* the hosted database is a separate file from your local one

**4. Why would you build your own MCP client?**

- A raw model and a server cannot work together alone. The client is the harness that discovers tools, sends them to the model, runs the calls and feeds back the results

**5. Who calls the tool, the model or the client?**

- The client. The model only names the tool and arguments

**6. How do you stop a model from writing to a production database?**

- Do not register write tools, driven by an environment variable. Then the option never exists

**7. Auto-convert or hand-write the tools?** See [Chapter 5](05-building-mcp-servers.md), 5.11

**8. How would you serve several databases behind one MCP entry point?**

- A custom server over all of them, or an MCP gateway in front of several servers

## 6.11 Added by Claude, not from the sources

Items marked *checked* were run with `fastmcp` 4.1.4. Check current documentation for deployment details.

- **Measuring concurrency yourself.** The class has `scripts/concurrency_showcase.py`, a dev-only script that fires N `log_time` calls one after another, then N at once, then reads every write back. It prints a speedup and flags lost writes
  - *Checked* against the class server run locally (N = 8): sequential 0.49 s, concurrent 0.22 s, speedup 2.22x, and **all 8 writes persisted**
  - The script says "largely serializing" when the speedup is below half of N. With calls this fast (about 60 ms each, each opening its own client) setup cost dominates, so the verdict is a rough hint locally and means more against a slow remote server
  - Its default URL is a Vercel deployment (`time-track-server-iota`). It was not reachable from my environment
- **Hosted disks may be temporary.** The class default path is `/tmp/timetrack.db`. On many platforms a restart clears that folder. Treat SQLite on a hosted disk as a demo, and use a managed database for real data. This is general practice, not from the class
- **Never commit secrets.** Keep API keys in environment variables. Add `.env` to `.gitignore`. Rotate a key that was ever committed
- **Add authentication before sharing a public URL.** Anyone with the URL can write to the shared database
- **Test the client loop with a stand-in model.** *Checked:* it needs no API key and shows message order problems at once
- **Handle tool errors in the loop.** *Checked:* `raise_on_error=False` returns an error result the model can read
- **Pin the MCP library versions** in `pyproject.toml` and `uv.lock`, and expect behaviour differences between major versions. Several things in these notes changed between FastMCP 3 and 4

## Recap

- Local STDIO is fast and private. Remote HTTP centralises and serves many. Most shared servers run over HTTP
- `fastmcp run main.py` serves the MCP object. `uvicorn main:app` serves the whole app. A FastMCP server can also run over HTTP alone
- Deploy: clean repo, `.gitignore`, connect to Horizon, entry point `main.py:mcp`, URL ending in `/mcp`. Hosted and local databases are separate
- Hosts connect with a URL. Anyone with it can use the server, so add access control
- MCP needs no API underneath
- Your own client is a **harness**: discover tools, send to the model, the **client** runs the tool, feed the result back, loop
- Fix the class loop: one assistant message per turn, all results in one user message, send text not a repr
- Read-only mode: do not register write tools. Gateways put several servers behind one entry point

## Practice

1. Run TimeTrack both ways: `fastmcp run main.py` and `uvicorn main:app`. Say what each one starts
2. Run `fastmcp run main.py --transport http` and post an `initialize` request to `/mcp`
3. Prepare a clean repo for TimeTrack with a proper `.gitignore`. Run `fastmcp inspect main.py:mcp`
4. Deploy to Horizon (free tier). Paste the URL into a host and log an entry
5. Build the corrected client loop against a calculator server. First use a stand-in model, then a real one
6. Make the stand-in ask for two tools in one turn and check the message order
7. Add a `READ_ONLY` switch to a server with a write tool and check both modes
8. Draw the host, client and server picture, and mark where the harness sits

## How this chapter was checked

- Run with `fastmcp` 4.1.4 and `mcp` 2.3.0: the TimeTrack `main.py` with `fastmcp run` (STDIO and HTTP); `fastmcp inspect`; the environment-variable database path; the calculator server and a bad argument; the class client loop and the corrected loop, both with a stand-in for the Anthropic client and a real FastMCP client and server; message order with two tool calls; the read-only switch; and three concurrent calls to a synchronous and an asynchronous tool
- **Not run:** Prefect Horizon, any deployed URL, Claude Desktop, the real Anthropic API, Vercel, Railway, a gateway, `uvx`, authentication
- The class transcripts are the source for everything not marked *checked*. Where the class and the test disagree (the concurrency claim in 6.8), both are shown

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/21 - 19 Sep - MCP Deployment.md` (deployment, the client, FAQ)
- Live-Class-2026, `classes_transcription_summary/20 - 13 Sep - MCP - The Time Tracker Project.md` (the Horizon free-tier note, auto-conversion)
- Sections marked *checked* and 6.11 are from testing

Previous: [Chapter 5, Building MCP servers](05-building-mcp-servers.md) · Next: [Chapter 7, Legacy vs modern MCP](07-legacy-vs-modern-mcp.md) (not written yet)
