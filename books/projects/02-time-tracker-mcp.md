# Chapter 2: Time Tracker (MCP)

**After this chapter you can:**

- Describe the TimeTrack project and how it grew across the classes
- Explain "one database, two front doors" (REST and MCP)
- Name the nine client demos and what each teaches
- Know the two open issues the README flags

**Builds on:** [MCP Ch5](../mcp/05-building-mcp-servers.md) (building TimeTrack), [MCP Ch6](../mcp/06-deployment-and-building-a-client.md) (deploy and client), [MCP Ch7](../mcp/07-legacy-vs-modern-mcp.md) (versions).

## 2.1 What it is

- A time-logging app: employees log hours against projects
- **SQLite** database, a **FastAPI REST** API, and a **FastMCP** server mounted at `/mcp`
- Tools: `log_time`, `get_timesheet`, `list_projects`, `get_project_summary`

## 2.2 How it grew

| Stage | What was added | Where explained |
|---|---|---|
| Server | Tools, SQLite, mounting at `/mcp` | MCP Ch5, 5.8 |
| Deploy | Horizon / Vercel, clean repo | MCP Ch6 |
| Client | Own client, agent loop | MCP Ch6 (client section) |
| Advanced | Sampling, elicitation, ping, timeout, progress | MCP Ch3, Ch7 |

## 2.3 One database, two front doors

- REST and MCP both call the **same database functions**
- A write through one is visible through the other

**Checked** (my test, local, `fastmcp` 4.1.4):

- `POST /api/entries` returned 200. The MCP `list_projects` then showed the new project
- `get_timesheet("Priya Nair")` returned `[('MCP Mastery', 3.5)]`
- An entry logged **through MCP** appeared in `GET /api/entries` (7 entries)
- The REST summary matched: 3.5 hours, one employee

## 2.4 The client demos (folder `mcp-client-and-advanced`)

| File | Teaches |
|---|---|
| `01_raw_client.py` | The verbose, three-layer way |
| `02_fastmcp_client_explained.py` | Builds up to `async with` |
| `03_fastmcp_client_http.py` | Connects to the deployed server |
| `04_agent_loop.py` | A real agent, no framework |
| `05_sampling_demo.py` | Server borrows the client's model |
| `06_elicitation_demo.py` | Server asks a question mid-task |
| `07_ping_and_errors.py` | A ping and an error |
| `08_timeout_and_cancellation.py` | A timeout that cancels |
| `09_progress_notifications.py` | Progress updates, watched live |

- Every demo except 03 starts `main.py` as a sub-process. No manual server start
- An **older 8-file version** of this README exists (without `02_..._explained` and `pyproject.toml`). Use the 9-file one
- The `.py` files themselves are **not read yet** (code batch)

## 2.5 Two open issues the README flags

- **`01_raw_client.py` may hang on macOS.** The README blames the SDK's low-level `stdio_client()` (issue #1452). If it hangs, move to file 02
- **`ctx.sample()`** gives a deprecation warning, which the README calls a real ecosystem transition
  - **Check:** in `fastmcp` 4.1.4 the `Context` object has **no `sample`** at all (tested in MCP Ch7). The README's version may differ

## 2.6 Interview corner

**Q1. Why mount MCP in the same app as REST?**
- Share one database and one deployment. Different clients use different doors

**Q2. When would you not run both?**
- When only agents use it. Then a plain MCP server is enough

**Q3. What does elicitation need from the client?**
- A handler that can ask the user and return the answer

**Q4. How do you test an MCP client without an API key?**
- Use a stand-in model that returns scripted tool calls

## 2.7 Added by Claude, not from the sources

- A public URL with no login lets anyone write to the shared database. Add access control before sharing
- The live Vercel URL in demo 03 was **not reachable from my environment**, so it was not tested
- Duplicate copies of this project exist in the course folders. The README and notebook in the `timetrack mcp server` folder were byte-identical to the Weekend 11 copies

## Recap

- One SQLite database, REST plus MCP front doors, both verified to see each other's writes
- Nine client demos from raw protocol to progress notifications
- Two caveats: macOS hang in demo 01, and `ctx.sample` differences

## Practice

1. Start TimeTrack. Log an entry by REST, read it by MCP
2. Do it the other way round
3. Run demos 02, 04 and 09. Describe each output
4. Write a stand-in model for demo 04

## How this chapter was checked

- Read fully: both client READMEs
- Run: the shared-data test in 2.3
- **Not run:** demos 01-09, Vercel URL

## Sources and further reading

- Live-Class-2026, `Complete MCP/TimeTrackProject/mcp-client-and-advanced/README.md`
- Older version: `.../timetrack mcp server/mcp-client-and-advanced/README.md`

Previous: [Chapter 1, CineBot](01-cinebot.md) · Next: [Chapter 3, Meridian AI learner](03-meridian-ai-learner.md)
