# Debug, trace and deploy
> lead: The path from a working local agent to a hosted one: LangSmith Studio for local debugging, LangSmith tracing for observability, and LangSmith Deployment for hosting. From the LangChain documentation.

meta: LangChain docs | read 30 Oct 2026 | 15 min read | Not covered in class | Partly from search excerpts

:::note How this chapter was built
The Studio, observability and deployment pages could not be fetched whole in this session. This chapter uses their search excerpts, so setup steps and settings are reliable but fine detail is missing. Follow the linked pages for the full walkthrough.
:::

## Why it matters

Building the agent is half the job. Interviewers ask "how do you debug it, monitor it and ship it". The LangChain answer is a stack: **Studio** to debug locally, **LangSmith tracing** to see every step, **LangSmith Deployment** to host it. This chapter gives you the commands and the vocabulary.

## Core ideas

### 1. LangSmith Studio: debug locally

Studio is a free visual interface that connects to **your locally running agent** and shows each step: prompts sent to the model, tool calls and results, and the final output. You can test inputs, inspect intermediate state and re-run a thread from any step.

Setup in six steps:

1. **Install the CLI** (Python 3.11 or newer): `pip install --upgrade "langgraph-cli[inmem]"`
2. **Have an agent**, for example a `create_agent(...)` in `src/agent.py`.
3. **Environment**: a `.env` with `LANGSMITH_API_KEY=...`. Do not commit it.
4. **Config file** `langgraph.json`:

```json
{
  "dependencies": ["."],
  "graphs": { "agent": "./src/agent.py:agent" },
  "env": ".env"
}
```

5. **Install dependencies** (`pip install langchain langchain-openai`, or `uv add`).
6. **Run** `langgraph dev`.

The local server then answers on `http://127.0.0.1:2024` as an API and opens in Studio at `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`.

:::key Why this works
`create_agent` returns a **compiled LangGraph graph**, and that is exactly what the `graphs` key in `langgraph.json` expects. The key name (`agent`) becomes the assistant id you use later when calling the server.
:::

:::tip Handy details
- The dev server **hot-reloads**: edit a prompt or tool signature and Studio picks it up, and you can re-run a thread from any step.
- **Safari** blocks localhost connections to Studio. Run `langgraph dev --tunnel` to use a secure tunnel (you may also need to add the tunnel URL to allowed origins in the Studio UI).
- Set `LANGSMITH_TRACING=false` and **no data leaves your local server**.
:::

### 2. Tracing with LangSmith

A trace records every step: the user input, every model call, tool call and decision, up to the final reply. Agents built with `create_agent` support it automatically; you need no extra code.

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-api-key>
export LANGSMITH_PROJECT=my-agent-project   # optional project name
```

**Trace only some calls** with a context manager:

```python
import langsmith as ls

with ls.tracing_context(enabled=True):          # this call is traced
    agent.invoke({"messages": [...]})

with ls.tracing_context(project_name="email-agent-test", enabled=True,
                        tags=["production"], metadata={"user_id": "user_123"}):
    agent.invoke({"messages": [...]})
```

**Label every trace** by passing tags and metadata in the invoke config:

```python
agent.invoke(
    {"messages": [...]},
    config={"tags": ["production", "v1.0"],
            "metadata": {"user_id": "user_123", "environment": "production"}},
)
```

:::trap Traces are readable by anyone with project access
Never put emails, keys or passwords in tags or metadata. Use opaque ids. For payloads, LangSmith also supports an anonymizer (`create_anonymizer`) that masks patterns such as SSNs before data is sent.
:::

Custom middleware has its own tracing controls (from the Custom middleware page, `langchain>=1.3.15`): hook spans record inputs and outputs by default, and a `TracePolicy` can transform them (`process_inputs`, `process_outputs`) or drop them (`omit_payload`), per middleware or as a global default with `configure_trace_policy`.

### 3. Deploying to LangSmith

LangSmith Deployment is a managed hosting platform for agents. Your code lives in a **GitHub repository** (public or private) and LangSmith handles infrastructure and scaling.

What the repo needs:

- the agent code
- `langgraph.json` (graphs, dependencies, env)
- a dependency file: `requirements.txt` or `pyproject.toml`

Deploy in the UI:

1. Log in to LangSmith and choose **Deployments** in the sidebar.
2. Click **+ New Deployment**.
3. Link your GitHub account if this is your first time or the repo is private.
4. Pick the repository and click **Submit**. It can take about **15 minutes**; check status in **Deployment details**.

Then call it. The assistant id is the **graph name from `langgraph.json`** (for example `agent`):

```bash
curl -s --request POST \
  --url <DEPLOYMENT_URL>/runs/stream \
  --header 'Content-Type: application/json' \
  --header 'X-Api-Key: <LANGSMITH_API_KEY>' \
  --data '{"assistant_id": "agent", "input": {"messages": [{"role": "user", "content": "Hi"}]}}'
```

Other options exist beyond Cloud: **hybrid**, **standalone servers** and **self-hosted with a control plane**. A deployment provisions a checkpointer for you, so conversations persist without your own database.

:::note Note on the middleware overview
The overview page says middleware "is not a separate runtime": hooks run inside the compiled LangGraph that `create_agent` returns, so the whole agent (middleware included) can be a node in a larger graph. That is also why `langgraph.json` can point at it directly.
:::

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Committing `.env` | Leaked API key | Keep it out of git |
| `graphs` path wrong in `langgraph.json` | Dev server cannot find the agent | Use `./path/file.py:variable` |
| Safari with Studio | Cannot connect | `langgraph dev --tunnel` |
| Sensitive data in tags or metadata | Readable by project members | Opaque ids only |
| Tracing everything in production | Cost and noise | `tracing_context` for selected calls |
| Wrong assistant id when calling | 404 | Use the graph name from `langgraph.json` |

## Hands-on lab

1. Install the CLI, write `langgraph.json` and run `langgraph dev` on a tiny agent.
2. Open Studio, run a prompt and inspect the tool call.
3. Change the system prompt, watch hot-reload, and re-run from a step.
4. Turn on tracing with the three environment variables and find your run.
5. Add tags and metadata and filter by them in LangSmith.
6. Trace one call only with `tracing_context`.
7. Push to GitHub and walk through **+ New Deployment** (or read the steps if you have no account).

## Interview corner

:::pitch
Locally I debug with LangSmith Studio through `langgraph dev`, which needs a `langgraph.json` pointing at my compiled agent. In every environment I trace with LangSmith using environment variables, tag and annotate runs with opaque metadata, and trace selectively in production. To ship, I push a repo with `langgraph.json` and dependencies and create a LangSmith Deployment, then call it by assistant id with an API key.
:::

### Basics

:::qa What is LangSmith Studio?
A free visual interface that connects to your locally running agent to show prompts, tool calls, results and state, and lets you re-run from any step.
:::

:::qa What does `langgraph.json` do?
It tells the CLI and deployment where your graph is (`graphs`), what to install (`dependencies`) and where the environment file is (`env`).
:::

:::qa How do you enable tracing?
Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY`. Agents built with `create_agent` are traced with no code changes.
:::

### Intermediate

:::qa How do you trace only some calls?
Wrap them in `langsmith.tracing_context(enabled=True)`, optionally with a project name, tags and metadata.
:::

:::qa How does a deployed agent get its assistant id?
From the key under `graphs` in `langgraph.json`.
:::

### Tricky

:::qa Why can `create_agent` output be used directly in `langgraph.json`?
It returns a compiled LangGraph graph, which is what the `graphs` entry expects.
:::

:::qa What should never go in trace metadata?
Sensitive data such as emails, keys or passwords. Anyone with project access can read it, so use opaque ids and consider the anonymizer.
:::

## Quick revision

- [ ] I can set up Studio with `langgraph.json` and `langgraph dev`
- [ ] I know Studio's local API address and the Safari tunnel fix
- [ ] I can enable tracing and trace selectively
- [ ] I can tag runs safely
- [ ] I can describe the deployment steps and how to call the result

## Sources and further reading

- [LangSmith Studio (LangChain docs)](https://docs.langchain.com/oss/python/langchain/studio)
- [LangSmith Observability (LangChain docs)](https://docs.langchain.com/oss/python/langchain/observability)
- [Deployment (LangChain docs)](https://docs.langchain.com/oss/python/langchain/deploy)
- [Custom middleware: tracing (LangChain docs)](https://docs.langchain.com/oss/python/langchain/middleware/custom)
