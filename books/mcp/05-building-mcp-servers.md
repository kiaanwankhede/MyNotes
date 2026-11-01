# Chapter 5: Building MCP servers

**After this chapter you can:**

- Say how the official `mcp` SDK and FastMCP relate, and why FastMCP is the usual choice
- Build a three-tool server with a resource and a prompt
- Inspect it, and install it into Claude Desktop
- Connect a server to a host with a connector or a config file
- Build one app where a website and an MCP server share a database
- Wrap an existing REST API as an MCP server in two ways, and choose between them
- Avoid the two mounting mistakes when FastMCP is mounted inside FastAPI
- Say what is left for later: authentication code and deployment

**Builds on:** [Chapter 2](02-primitives-and-architecture.md) (first server), [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md) (primitives in code), [Chapter 4](04-operation-transports-and-shutdown.md) (transports).

**Deployment** is in [Chapter 6](06-deployment-and-building-a-client.md). The low-level server (5.2) and role-scoped authentication (5.10) were added after the `.py` files were read and run.

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
- The class folder's README gives a comparison for the same three tools: about **72 lines** low-level against **31** with FastMCP
  - *Checked:* counting non-blank, non-comment lines **including the docstring** gives exactly 72 and 31. Without the docstrings it is about 59 against 22

```python
# the low-level file (mcp 1.x style), the three parts
server = Server("RecipeBox")

@server.list_tools()                       # part 1: describe each tool by hand
async def list_tools() -> list[types.Tool]:
    return [types.Tool(name="get_recipe", description="...",
            inputSchema={"type": "object",
                         "properties": {"recipe_id": {"type": "integer"}},
                         "required": ["recipe_id"]}), ...]

@server.call_tool()                        # part 2: dispatch by name
async def call_tool(name: str, arguments: dict):
    if name == "get_recipe": ...
    elif name == "search_recipes": ...
    else: raise ValueError(f"Unknown tool: {name}")
    return [types.TextContent(type="text", text=str(result))]

async def main():                          # part 3: transport wiring
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())
```

- **Checked, with `mcp` 1.30.0:** the file runs. It listed the 3 tools, and `search_recipes("vegan")` worked
  - The result is `str(result)`, a **Python repr as text**, not JSON, and there is no structured output. FastMCP returned the real objects
  - A missing id came back as `isError: true` with the message
- **Checked, with `mcp` 2.3.0 (the version these notes use): the file does not start.** `Server` has no `list_tools` decorator, so it fails at import with `AttributeError`
  - So the class's low-level file is tied to the older SDK. The 2.x package also has `MCPServer`. Which new API replaces the decorators was not studied here
  - The FastMCP file works with the same package set

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
- The class folder also adds two more prompts in the live build, `search_for_quick_recipes` and `send_email`
  - **Code read:** the server is named `RecipeBox_Updated`, the resource returns a plain list of five valid tags, and `search_recipes` mentions `recipe://tags` in its docstring
  - **Quirk:** `send_email` has nothing to do with email. Its description says "Plan a week's worth of meals" and the text it returns says the same. The name looks like a leftover
  - *Checked:* both prompts and the resource listed correctly, and the resource returned `["quick","vegetarian","sunday","meat","vegan"]`
  - The Precoded version has no resource and no prompts. Its `@mcp.tool` has no brackets; the updated one uses `@mcp.tool()`. Both work in 4.1.4
  - The file ends with comments holding the Inspector and `fastmcp install claude-desktop` commands

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

## 5.6 Connecting a server to a host

Class 20 recap. There are two ways, and they are the same thing underneath.

- **Connector:** the easy way. Click "Add", paste a name and a hosted URL. It suits a public, already-hosted server (Firecrawl was the live example)
- **Config file:** `claude_desktop_config.json` on a Mac, with an equivalent on Windows. A developer edits it to run a server **they built and run locally**, since a local server has no public URL to paste
- **A connector added in the interface also ends up as an entry in this file.** A connector and a config entry are the same underlying thing
- **Five connectors means five server entries.** The host starts each one independently, as in [Chapter 2](02-primitives-and-architecture.md), 2.2
- The entry lists the server's name and the exact command that starts it (see the example in 5.5, and the wiretapped one in [Chapter 3](03-lifecycle-json-rpc-and-capability-negotiation.md), 3.10)

**The most common setup bug (class, not run here):**

- A bare `uv` command often **fails quietly** inside Claude Desktop, because the host does not know where `uv` is installed
- Run `which uv` in a terminal to get the full path, for example `/opt/homebrew/bin/uv`, and put that in the entry's `command`. Restart the host
- The same applies to `python`. Use `which python`

**VS Code, the same idea:**

- Open the command palette (`Cmd` or `Ctrl` + `Shift` + `P`), choose **MCP: Add Server**, choose **STDIO**, and give the exact command that starts the server file
- VS Code writes its own `mcp.json`. After a restart, the tools appear in VS Code's AI features
- Every host runs the same architecture with a different settings screen around it

**A doubt settled in class:** the server **never decides** which tool to call. It waits. The client sends `tools/call` naming a tool and its arguments. The deciding happened earlier, on the model side

## 5.7 Reaching a local server from outside: a preview

- A server on `localhost` cannot be reached by someone else
- Class answer: **tunnelling**, for example **ngrok**, which gives a local port a real shareable URL without deploying to a cloud server
- It matters when a LangChain agent or another person must reach the server
- Proper hosting is in [Chapter 6](06-deployment-and-building-a-client.md). Not run here

## 5.8 TimeTrack: one database, two front doors

A timesheet tool, in the same category as Toggl or Clockify. **A browser and an AI assistant read and write the same data.**

**How class 20 built it, in layers:**

1. **Database layer:** SQLite, a `time_entries` table (id, employee name, project, date, hours, description), seeded on first run so the app never starts empty. A small `row_to_dict` helper turns SQLite rows into plain dictionaries
2. **REST layer with FastAPI, and no MCP yet.** This is how almost every real integration starts: a working product with its own API, built with no thought of MCP. Gmail's and Slack's APIs were not designed "for AI". MCP is added **afterwards**
   - `uv run fastapi dev main.py` gave a Swagger page at `/docs` and a plain HTML, CSS and `app.js` front end. The browser's network tab showed the REST calls behind each action
   - *Checked:* a FastAPI app with the class's routes served `/docs` (HTTP 200) and listed `/api/entries`, `/api/projects` and `/api/projects/{project}/summary` in its OpenAPI document
3. **MCP layer on top**, in two ways (5.9)

*The class attitude, worth keeping:* AI-assisted coding is expected in this course. The goal is to understand the architecture and decisions well enough to explain and defend them, not to memorise syntax.

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
- Not run here. Deployment is covered properly in [Chapter 6](06-deployment-and-building-a-client.md)

## 5.9 Wrapping an existing API: two ways

With the REST API working, class 20 added MCP on top **two ways** and discussed when to choose each.

### Option 1: write the tools by hand (full control)

```python
from fastmcp import FastMCP
import database as db

mcp = FastMCP("Time Tracker")

@mcp.tool
def log_time(employee_name: str, project: str, entry_date: str,
             hours: float, description: str) -> dict:
    """Log a new time entry for an employee against a project."""
    return db.log_time(employee_name, project, entry_date, hours, description)

@mcp.tool
def get_project_summary(project: str) -> dict:
    """Get total hours and a per-employee breakdown for one project."""
    return db.get_project_summary(project)

@mcp.prompt
def generate_weekly_report(employee_name: str, week_start: str) -> str:
    """A template guiding the AI to pull an employee's week and write a clean summary report."""
    return f"Generate a weekly report for {employee_name} starting {week_start}, using their timesheet and project summaries..."
```

- In the Inspector the same lifecycle appeared as for every other server: `initialize`, discovery, then a real `tools/call`
- The class highlighted the **prompt**: it cannot be copied from a plain API. It guides the AI to **combine several tool calls** into one well-structured answer
- The class version of `get_timesheet` took `week_start`. The version in 5.8 takes `start_date` and `end_date`. The tool set evolved during the class

### Option 2: convert the API automatically (speed)

```python
from fastmcp import FastMCP

mcp = FastMCP.from_fastapi(app)     # app is your existing FastAPI instance
```

- Every existing endpoint became an MCP tool, with **no prompts and no resources** (a REST API has no such idea)

*Checked on `fastmcp` 4.1.4, using the class's four routes:*

- Four tools appeared: `list_all_entries_api_entries_get`, `log_time_api_entries_post`, `list_projects_api_projects_get` and `get_project_summary_api_projects`
  - **The names are generated from the route, not from your function names.** They are long, and the last one has no `_get`. The model sees these names
  - Argument schemas came through correctly (`project` for the summary, five fields for logging)
- **Descriptions** came from the route's docstring when it had one. Without a docstring the description was just an auto title (`Get Project Summary`). The class's routes had no docstrings
- Calling the converted tools worked: the summary for "Website Redesign" returned 19.0 hours with the per-employee split
- Prompts: 0. Resources: 0

### Choosing between them (class guidance)

- **Convert automatically** to make already-working, already-trusted APIs available to AI **quickly**, with no wish to reshape them. It needs no change to the API code, which is why it is a safe starting point
- **Write by hand** when you need:
  - one tool that **combines two or more API calls**
  - richer, more AI-friendly descriptions than the API ever needed for human developers
  - **prompts**, which automatic conversion cannot make
- **A reason companies pick the manual route:** teams are reluctant to change a working, deployed API just to improve its descriptions. A separate hand-built MCP layer leaves trusted code alone
- If you do convert, **add docstrings** to the routes. *Checked:* a docstring became the tool description

## 5.10 Authentication: role-scoped tools

From `server_with_auth.py`. *Checked* by running it over HTTP on port 8000 with `fastmcp` 4.1.4.

```python
auth = StaticTokenVerifier(tokens={
    "user-token":    {"client_id": "normal-user",   "scopes": ["user"]},
    "analyst-token": {"client_id": "data-analyst",  "scopes": ["user", "analyst"]},
    "admin-token":   {"client_id": "administrator", "scopes": ["user", "analyst", "admin"]},
})
mcp = FastMCP("Warm-Up Server", auth=auth)

@mcp.tool(auth=require_scopes("analyst"))
def query_db(a: int, b: int, c: int) -> int: ...
```

- Eight tools in three tiers: **user** (`greet`, `add_numbers`, `who_am_i`), **analyst** (`query_db`, `calculate_average`, `sales_report`), **admin** (`list_users`, `delete_user`)
  - `who_am_i` uses `get_access_token()` to return the caller's `client_id` and `scopes`
  - It runs on HTTP, host `127.0.0.1`, port 8000. Auth needs HTTP; it has no place on STDIO
- The file marks itself **development only**. Static tokens teach the pattern. They are **not** a production login

**What the run showed:**

| Caller | Tools it could see | Calling a higher tool |
|---|---|---|
| No token | rejected with an error | n/a |
| Bad token | rejected with an error | n/a |
| `user-token` | 3 | `query_db` and `delete_user` denied |
| `analyst-token` | 6 | `delete_user` denied, `query_db` returned 6 |
| `admin-token` | 8 | `delete_user` worked |

- **Two layers:** a tool above your scope is **hidden** from `tools/list`, and calling it by name is also **denied**. Hiding alone would not be security
- The data in `list_users` and `sales_report` is hard-coded sample data
- For interviews, the class advised reading up on **JWT and OAuth**. Real servers verify signed tokens from an identity provider, not a fixed dictionary

## 5.11 Interview corner

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

**8. When would you auto-convert a REST API, and when write tools by hand?**

- Auto-convert for speed and to leave trusted code alone. Write by hand to combine calls, write better descriptions, or add prompts
- *Stronger answer:* converted tool names come from the routes and can be long and unclear, so check what the model will see

**9. Does the MCP server decide which tool to call?**

- No. The model decides. The client sends `tools/call`. The server only executes

**10. A server works in a terminal but does not show up in Claude Desktop. What do you check?**

- Whether `command` is a bare `uv` or `python`. Use the full path from `which`

## 5.12 Added by Claude, not from the sources

Items marked *checked* were run with `fastmcp` 4.1.4.

- **Return clear tool errors.** *Checked:* a missing key surfaced as `KeyError: '999'` inside a `ToolError`. Check inputs and raise a message the model can act on
- **Keep one module for data, thin wrappers for tools.** It is what makes TimeTrack's two front doors safe to change
- **Pass an explicit transport to the FastMCP client.** *Checked:* `Client("recipebox.py")` warns that string inference is deprecated and goes in FastMCP 5. Use `StdioTransport` or a `Path`
- **Use `fastmcp inspect` before deploying.** *Checked:* it printed the counts of tools, prompts and resources and the library versions
- **Use absolute paths and `__file__`-based paths** in anything the host launches
- **Check converted tool names.** *Checked:* `from_fastapi` produced names such as `get_project_summary_api_projects`. If the names matter, set explicit operation ids on your routes or write the tools by hand. Not tested here
- **Keep one source of truth.** Whether you convert or wrap, both front doors must call the same data functions

## Recap

- Official `mcp` SDK is the low-level base. **FastMCP** makes servers easy. Both can serve STDIO
- The legacy way means hand-written tool lists, schemas and dispatch. FastMCP needs **one decorator per function**
- A **resource** can teach the model valid values before it calls a tool
- `fastmcp install claude-desktop <file>` registers a STDIO server in the host's config
- A connector and a config-file entry are the same thing. Use the full path for `uv` or `python` in a host's config
- Wrap an existing API by hand (control, prompts, good descriptions) or with `FastMCP.from_fastapi` (fast, no prompts, generated names)
- TimeTrack: one SQLite database, REST routes and MCP tools sharing the same functions, FastMCP mounted in FastAPI
- Mount rules: `path="/"` in `http_app`, and `lifespan` at `FastAPI(...)`
- Authentication and deployment come next, with static tokens as a development-only pattern

## Practice

1. Build RecipeBox with the three tools. Add the `recipe://tags` resource and the `plan_weekly_meals` prompt
2. Run the Inspector on it. If a port is busy, find what holds it and change the port
3. Print the config entry with `fastmcp install mcp-json`, then install it into Claude Desktop
4. Build TimeTrack's database layer and run the checks from 5.8
5. Mount your FastMCP app in FastAPI. Break each rule on purpose and read the result
6. Log an entry on the website, then read it back with a `get_timesheet` call from an MCP client
7. Make `get_recipe` return a clear error for an unknown id
8. Wrap a small FastAPI app both ways. Compare the two tool lists. Add a docstring to one route and watch the description change
9. Break your config on purpose with a bare `uv`, then fix it with the full path from `which uv`

## How this chapter was checked

- Run: the RecipeBox tools, resource and prompt through a client; the notebook's TimeTrack database code with its own asserts; the generated `main.py` served by `uvicorn` in three variants (correct, `path="/mcp"`, no `lifespan`); the REST route; `POST /mcp` with and without the trailing slash; `fastmcp inspect`; `fastmcp install mcp-json`; and the `fastmcp dev inspector` and `fastmcp install claude-desktop` help text
- Run for class 20: a FastAPI app with the class's four routes, its `/docs` page and OpenAPI paths, `FastMCP.from_fastapi` with calls to the converted tools, and a docstring's effect on the description
- **Not run:** the Inspector in a browser, the port conflict, the `which uv` failure, VS Code's `MCP: Add Server`, Firecrawl, Claude Desktop (install or connection), ngrok, Prefect Horizon, the website's static files (a stub page stood in), hot reload of a new resource
- **Read and run since:** the low-level and both FastMCP RecipeBox files, the auth server (5.2, 5.3, 5.10). **Not read yet:** the TimeTrack source files and the web files (`.js`, `.html`, `.css`)
- The class folder's `first-mcp-server/README.md` and `mcp-warmup-primitives/README.md` are **empty** (0 bytes)

## Sources and further reading

- Live-Class-2026, `classes_transcription_summary/19 - 12 Sep - MCP - Shutdown, Transport Layer.md` (the two libraries, RecipeBox, resource and prompt, port conflict, install, ngrok)
- Live-Class-2026, `classes_transcription_summary/20 - 13 Sep - MCP - The Time Tracker Project.md` (connectors and config files, the layered build, the two ways to wrap an API)
- Live-Class-2026, `classes_summary/18 - 12-13 Sep - Building & Deploying MCP Servers.md` (RecipeBox comparison, authentication, TimeTrack)
- Live-Class-2026, `Weekend 11 - 12-13 Sep/`: `README.md`, `12-13 Sep - Building & Deploying MCP Servers/README.md`, `MCP-Precoded/README.md`, `TimeTrackProject/timetrack/README.md`, `TimeTrackProject/timetrack_notebook.ipynb`
- Sections marked *checked*, 5.1's *Checked* line and 5.10 are from testing

Previous: [Chapter 4, Operation, transports and shutdown](04-operation-transports-and-shutdown.md) · Next: [Chapter 6, Deployment and building a client](06-deployment-and-building-a-client.md)
