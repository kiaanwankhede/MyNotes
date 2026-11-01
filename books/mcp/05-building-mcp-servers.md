# Chapter 5: Building MCP servers

**After this chapter you can:**

- Say how the official `mcp` SDK and FastMCP relate, and why FastMCP is the usual choice
- Build a three-tool server with a resource and a prompt
- Inspect it, and install it into Claude Desktop
- Build one app where a website and an MCP server share a database
- Avoid the two mounting mistakes when FastMCP is mounted inside FastAPI
- Say what is left for later: authentication and deployment

**Builds on:** [Chapter 2](02-primitives-and-architecture.md) (first server), [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md) (primitives in code), [Chapter 4](04-operation-transports-and-shutdown.md) (transports).

**Not covered yet in this chapter:** the code of the low-level server, role-scoped authentication, and the live TimeTrack class. Those come from code files and later classes, planned for later batches.

## 5.1 Two libraries, one protocol

- **Official `mcp` SDK:** Anthropic's own Python SDK. Correct, but **low-level**: you write much by hand
- **FastMCP:** a separate library that makes defining servers far easier
- Class analogy: **TensorFlow and Keras again**. The SDK is the base. FastMCP makes building on it easy
- **History, as told in class:**
  - FastMCP was built by an independent developer, **Jeremiah Lowin**, a Prefect co-founder
  - It became so popular that a version of it was folded into the official SDK, with an internal class renamed to avoid confusion
  - The standalone FastMCP is still what most real servers use
- **FastMCP and FastAPI are not from the same team.** They share a naming style and work well together, because an MCP tool is close to an API endpoint. Do not mix them up in an interview
- *Checked:* the installed `fastmcp` 4.1.4 lists Jeremiah Lowin among its authors. The installed `mcp` 2.3.0 has a class named `MCPServer`, which fits the "renamed" story. The Prefect detail and the folding-in story were not verified
- **Language does not matter** to the protocol. Python or Node is a team choice

## 5.2 The legacy way, and why it hurt

- The class showed the low-level way on purpose: not to memorise, but to **feel the difficulty**. This style **still appears in real companies**
- With the official low-level SDK, a three-tool server needed:
  - a hand-written `list_tools` function that lists every tool
  - a large nested `if` and `elif` block to match each incoming tool name to its code
  - hand-written JSON Schema
  - explicit transport wiring with `stdio_server()`
- Working, but long and easy to get wrong
- The class folder's README gives a comparison for the same three tools: about **72 lines** of real code low-level against **31** with FastMCP. That count is from the README. It was not re-counted here because the code files are planned for a later batch

## 5.3 The FastMCP way: RecipeBox

One decorator per function. `@mcp.tool` reads the **signature** and the **docstring**, and handles `tools/list` and `tools/call`.

```python
from fastmcp import FastMCP

mcp = FastMCP("Recipe Box")

recipes = {
    "123": {"title": "Weeknight Pasta", "minutes": 20, "tags": ["quick", "weeknight"]},
    "124": {"title": "5-Minute Salsa", "minutes": 5, "tags": ["quick", "no-cook"]},
}

@mcp.tool
def list_recipes() -> list[dict]:
    """List all recipe IDs and titles."""
    return [{"id": k, "title": v["title"]} for k, v in recipes.items()]

@mcp.tool
def get_recipe(recipe_id: str) -> dict:
    """Get full details for one recipe by its ID."""
    return recipes[recipe_id]

@mcp.tool
def search_recipes(tag: str) -> list[dict]:
    """Search recipes by tag, e.g. 'quick'."""
    return [{"id": k, "title": v["title"]} for k, v in recipes.items() if tag in v["tags"]]

if __name__ == "__main__":
    mcp.run()
```

- The class data had more recipes (`# ...` in the notes). Two are enough to run
- *Checked:* a client saw the three tools, and `search_recipes("quick")` returned both recipes
- `get_recipe("999")` raised a `KeyError` inside the tool, which the client saw as a `ToolError`. A friendlier tool would check the id and return a clear message. That is an improvement of mine, not from the class

### Add a resource and a prompt

```python
@mcp.resource("recipe://tags")
def valid_tags() -> list[str]:
    """The full list of valid recipe tags, so an LLM knows what it can search for."""
    return ["quick", "weeknight", "no-cook", "vegan", "dessert"]

@mcp.prompt
def plan_weekly_meals() -> str:
    """A template for planning a full week of meals from the recipe box."""
    return "Using the available recipes, plan a balanced set of meals for the next 7 days..."
```

- *Checked:* the client listed the resource `recipe://tags` and the prompt `plan_weekly_meals`, and reading the resource returned the five tags
- In class the new resource appeared in the Inspector after reconnecting, with **no server restart**. The prompt needed a fresh connect and disconnect. Not re-run here

**Why the resource matters, concretely:**

- A recipe's `tags` only exist **inside** a tool's returned data. A model cannot know the valid tag values until it has already called a tool
- The `recipe://tags` resource lets it learn the valid values **first**
- Then "give me something for the holidays" can become a tag the server actually understands, not a guess at something missing from the data
- The class folder also adds two more prompts in the live build (`search_for_quick_recipes` and `send_email`). Their code is in a file planned for a later batch

## 5.4 Inspect it, and the port conflict

```bash
npx @modelcontextprotocol/inspector python3 recipebox_fastmcp.py
```

- **Class failure:** the Inspector would not start, because port `6274` was already in use. A second tool (MCP Jam) was using the same port
- **The fix was ordinary debugging:** find what holds the port, close it or move the new one. The class used `--client-port 9999`
- Two programs cannot share a port, just as two websites cannot both be `google.com`. This is **not** an MCP problem
- *Checked on `fastmcp` 4.1.4:* its own wrapper now has `fastmcp dev inspector` with `--ui-port` and `--server-port`. The `--client-port` flag from class was not run. Check `--help` for your version

## 5.5 Install into Claude Desktop

```bash
uv run fastmcp install claude-desktop recipebox_fastmcp.py
```

- One command registers the server in Claude Desktop's configuration. After a restart it appears with the other servers and works in a real chat
- The entry it writes, as shown in class:

```json
"RecipeBox_Updated": {
  "command": "/opt/homebrew/bin/uv",
  "args": ["run", "--with", "fastmcp", "fastmcp", "run", "/path/to/recipebox_fastmcp.py"],
  "transport": "stdio"
}
```

- Two things to notice:
  - It is a **STDIO** server, as Chapter 4 says is natural for a local server
  - The host launches it exactly as you would in a terminal: `uv run --with fastmcp fastmcp run <file>`
- *Checked:* `fastmcp install mcp-json recipebox.py` printed an entry with `command: uv` and the same `run --with fastmcp fastmcp run <path>` arguments. It had **no** `transport` key. The command also has `--name`, `--with`, `--env` and `--config-path` options. The Claude Desktop install itself was not run
- Use an **absolute path** to the file, and expect the host's own working directory ([Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.3)

## 5.6 Reaching a local server from outside: a preview

- A server on `localhost` cannot be reached by someone else
- Class answer: **tunnelling**, for example **ngrok**, which gives a local port a real shareable URL without deploying to a cloud server
- It matters when a LangChain agent or another person must reach the server
- Proper hosting is in [Chapter 6](06-deployment.md). Not run here

## 5.7 TimeTrack: one database, two front doors

A timesheet tool. **A browser and an AI assistant read and write the same data.**

- One **SQLite** database
- One **FastAPI** app. It serves a website on one path and an MCP server on `/mcp`
- Both front doors call the **same** database functions, so nothing is written twice

| Primitive | Name | What it does |
|---|---|---|
| Tool | `log_time` | Log a new entry. It shows on the website at once |
| Tool | `get_timesheet` | One employee's entries, optionally within a date range |
| Tool | `get_project_summary` | Total hours per project, split by employee (a real `GROUP BY`) |
| Tool | `list_projects` | Every project with at least one entry |
| Resource | `timesheet://projects` | The known project names |
| Prompt | `generate_weekly_report` | Structures a weekly hours report request |

**Setup:**

```bash
uv init .
uv add fastmcp fastapi "uvicorn[standard]"
uv run fastmcp version
uv run uvicorn main:app --reload
# website: http://127.0.0.1:8000     MCP: http://127.0.0.1:8000/mcp
```

**The shape of `main.py`:**

```python
import database as db
from fastapi import FastAPI
from fastmcp import FastMCP

db.init_db()

mcp = FastMCP("TimeTrack")

@mcp.tool
def get_project_summary(project: str) -> dict:
    """Get total hours logged against a project, broken down by employee."""
    return db.get_project_summary(project)

# ... log_time, get_timesheet, list_projects, a resource and a prompt, the same way

mcp_app = mcp.http_app(path="/")                 # rule 1
app = FastAPI(title="TimeTrack", lifespan=mcp_app.lifespan)   # rule 2
# ... REST routes such as /api/entries call the same db functions
app.mount("/mcp", mcp_app)
```

- **Build the MCP server first**, then the FastAPI app, because the app needs the MCP app's `lifespan`

### The two rules

1. **`mcp.http_app(path="/")`, not `"/mcp"`.** `app.mount("/mcp", ...)` already adds the prefix. Set both and the endpoint becomes `/mcp/mcp`
2. **Pass `lifespan=mcp_app.lifespan` when you create `FastAPI(...)`**, not afterwards. Otherwise the MCP session manager never starts

*Checked by running all three variants:*

| Variant | `POST /mcp/` | `POST /mcp/mcp` |
|---|---|---|
| Correct code | 200 | 404 |
| `path="/mcp"` | **404** | **200** |
| No `lifespan` | **500** | 404 |

- Rule 1 is exactly as claimed: the endpoint moved to `/mcp/mcp`
- **Rule 2 is not "silent" on this version.** The app started fine, and the **first MCP request** failed with HTTP 500 and the message "Task group is not initialized". The class README calls it silent. It is silent at start-up and loud on first use
- `POST /mcp` without the trailing slash got **307** to `/mcp/`. See Chapter 4, 4.14

### The database layer

- The notebook builds `database.py` with `sqlite3`: a `time_entries` table, seed data, `list_all_entries`, `log_time`, `get_timesheet`, `list_projects`, `get_project_summary`
- `log_time` rejects hours of zero or less. `get_project_summary` raises if a project has no entries
- *Checked by running the notebook's own code and asserts:*
  - 5 seed entries, and a second `init_db()` does **not** duplicate them
  - Asha Patel's timesheet has 3 entries totalling 16.5 hours, and the date filter works
  - `get_project_summary("Website Redesign")` gives 19.0 hours: Asha 13.5 and Rahul 5.5
  - A missing project and a negative number of hours both raise `ValueError`
  - A new entry survives a fresh read, and the summary updates
- `fastmcp inspect` on the app listed **4 tools, 1 prompt, 1 resource**. That matches the table

### Connect Claude Desktop

```json
{ "mcpServers": { "timetrack": { "url": "http://127.0.0.1:8000/mcp" } } }
```

Not run here. See the trailing-slash note above if a client does not follow redirects.

### Going live

- The class README documents **Prefect Horizon** (formerly FastMCP Cloud):
  1. Push to GitHub
  2. Sign in with GitHub
  3. Connect the repository. Dependencies are found from `pyproject.toml`
  4. Optional check first: `fastmcp inspect main.py:mcp`
  5. Deploy. It goes live at `https://your-project.fastmcp.app/mcp`
- **Open question the README itself raises:** whether the **website's static files** deploy with the MCP part, since Horizon is built for MCP. The fallback is a general host such as Railway
- Not run here. Deployment is covered properly in [Chapter 6](06-deployment.md)

## 5.8 Authentication: a preview

From the class summary only. The code file is held for a later batch, so this was **not run or read in full**.

- The warm-up server from classes 16 and 17 gains **role-scoped authentication**
- It uses a static token checker with three tokens: `user-token`, `analyst-token`, `admin-token`
- Each tool is gated with `@mcp.tool(auth=require_scopes("user"))`, on the same `greet` and `add` tools
- The file marks itself **development only**. Static tokens teach the scope pattern and are **not** a production login system
- For interviews, the class advised reading up on **JWT and OAuth**

## 5.9 Interview corner

**1. How do the official SDK and FastMCP relate?**

- The SDK is the base. FastMCP is the popular layer that makes servers easy. Compare Keras and TensorFlow
- *Stronger answer:* FastMCP and FastAPI are different projects that work well together

**2. What does `@mcp.tool` do for you?**

- It reads the signature and docstring and handles `tools/list` and `tools/call`. No hand-written schema or dispatch

**3. Why add a resource to a tool-only server?**

- It tells the model the valid values (such as tags) before it calls anything, so it does not guess

**4. How does a host launch a local MCP server?**

- As a STDIO sub-process: `uv run --with fastmcp fastmcp run <file>`, as recorded in the host's config

**5. How would you let a website and an AI assistant share one dataset?**

- Put the data functions in one module. Call them from both REST routes and MCP tools. Mount the MCP app in the web app

**6. What are the two mistakes when mounting FastMCP in FastAPI?**

- Setting the path twice (`/mcp/mcp`) and not passing the MCP `lifespan` when creating the app
- *Stronger answer:* the second one fails on the first MCP request, not at start-up

**7. Why is a static-token check not enough for production?**

- It is for learning scope gating. Production needs real tokens and a real flow (JWT, OAuth)

## 5.10 Added by Claude, not from the sources

Items marked *checked* were run with `fastmcp` 4.1.4.

- **Return clear tool errors.** *Checked:* a missing key surfaced as `KeyError: '999'` inside a `ToolError`. Check inputs and raise a message the model can act on
- **Keep one module for data, thin wrappers for tools.** It is what makes TimeTrack's two front doors safe to change
- **Pass an explicit transport to the FastMCP client.** *Checked:* `Client("recipebox.py")` warns that string inference is deprecated and goes in FastMCP 5. Use `StdioTransport` or a `Path`
- **Use `fastmcp inspect` before deploying.** *Checked:* it printed the counts of tools, prompts and resources and the library versions
- **Use absolute paths and `__file__`-based paths** in anything the host launches

## Recap

- Official `mcp` SDK is the low-level base. **FastMCP** makes servers easy. Both can serve STDIO
- The legacy way means hand-written tool lists, schemas and dispatch. FastMCP needs **one decorator per function**
- A **resource** can teach the model valid values before it calls a tool
- `fastmcp install claude-desktop <file>` registers a STDIO server in the host's config
- TimeTrack: one SQLite database, REST routes and MCP tools sharing the same functions, FastMCP mounted in FastAPI
- Mount rules: `path="/"` in `http_app`, and `lifespan` at `FastAPI(...)`
- Authentication and deployment come next, with static tokens as a development-only pattern

## Practice

1. Build RecipeBox with the three tools. Add the `recipe://tags` resource and the `plan_weekly_meals` prompt
2. Run the Inspector on it. If a port is busy, find what holds it and change the port
3. Print the config entry with `fastmcp install mcp-json`, then install it into Claude Desktop
4. Build TimeTrack's database layer and run the checks from 5.7
5. Mount your FastMCP app in FastAPI. Break each rule on purpose and read the result
6. Log an entry on the website, then read it back with a `get_timesheet` call from an MCP client
7. Make `get_recipe` return a clear error for an unknown id

## How this chapter was checked

- Run: the RecipeBox tools, resource and prompt through a client; the notebook's TimeTrack database code with its own asserts; the generated `main.py` served by `uvicorn` in three variants (correct, `path="/mcp"`, no `lifespan`); the REST route; `POST /mcp` with and without the trailing slash; `fastmcp inspect`; `fastmcp install mcp-json`; and the `fastmcp dev inspector` and `fastmcp install claude-desktop` help text
- **Not run:** the Inspector in a browser, the port conflict, Claude Desktop (install or connection), ngrok, Prefect Horizon, the website's static files (a stub page stood in), hot reload of a new resource
- **Not read yet:** all `.py` files in the class folders (low-level RecipeBox, the FastMCP RecipeBox with extra prompts, authentication, the TimeTrack source files), the web files (`.js`, `.html`, `.css`) and the two empty READMEs
- The class folder's `first-mcp-server/README.md` and `mcp-warmup-primitives/README.md` are **empty** (0 bytes)

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/19 - 12 Sep - MCP - Shutdown, Transport Layer.md` (the two libraries, RecipeBox, resource and prompt, port conflict, install, ngrok)
- Live-Class-2026, `classes_summary/18 - 12-13 Sep - Building & Deploying MCP Servers.md` (RecipeBox comparison, authentication, TimeTrack)
- Live-Class-2026, `Weekend 11 - 12-13 Sep/`: `README.md`, `12-13 Sep - Building & Deploying MCP Servers/README.md`, `MCP-Precoded/README.md`, `TimeTrackProject/timetrack/README.md`, `TimeTrackProject/timetrack_notebook.ipynb`
- Sections marked *checked*, 5.1's *Checked* line and 5.10 are from testing

Previous: [Chapter 4, Operation, transports and shutdown](04-operation-transports-and-shutdown.md) · Next: [Chapter 6, Deployment](06-deployment.md) (not written yet)
