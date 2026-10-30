# From the Craft notes
> lead: What the instructor's Craft page contains: the course expectations, a date-by-date map of every shared resource (Colab notebooks, PDFs, interactive sites, videos), and the AI newsletter project. Use it as an index into the course material.

meta: Craft page "Agentic 3.0" | read 30 Oct 2026 | 10 min read

:::note What this page is
The Craft page is an **index of links and files**, not written lessons. I opened the home page and all 13 class and project sub-pages. The PDFs, notebooks and linked websites are **not read** here: this page lists them so you can find them. Items unrelated to learning (job posts, Udemy coupons, a referral link) and a local Inspector link that carries an access token are left out on purpose.
:::

## The instructor's own guidance ("Best Practice")

The page opens with "First 20 minutes (quick points)". The parts that matter for study:

| Topic | What it says |
| --- | --- |
| Mindset | Learn one concept at a time, understand before remembering, build first and memorisation follows. Learn concepts, patterns and architecture, not framework names: frameworks change, fundamentals do not |
| Class rhythm | Weekend classes 8:00 to 11:00 AM IST, taught with Excalidraw and live coding, in a 15 to 20 minute teach, doubt, continue rhythm, with a doubt session after each class and recordings within 24 hours |
| Asking questions | Try for 10 to 15 minutes first, then ask. Debugging is a core skill |
| Tools | Free tiers and trials first; paid tools only when truly necessary |
| What the course is | Production-focused: build, deploy, monitor and improve AI systems, with cloud as a deployment platform |
| Final thought | "Leave saying I can build production AI systems" |

:::tip Doubt helper
The page links a custom GPT, **Mayank Doubt Solver - Agents**, for asking common doubts in simple language, and the main course repository `github.com/mayank953/Live-Class-2026`.
:::

## Resource map by class

How each Craft entry lines up with this book. Links are to the instructor's resources.

| Craft entry | What is attached | Where it fits here (my mapping) |
| --- | --- | --- |
| **Class 1: Python** | Setup links (VS Code, Python, `uv`, Windows Terminal, Git for Windows), the commands `uv venv --python 3.12` and `source .venv/bin/activate`, a video, and a 6.1 MB PDF (`Class-1---PythonAI.pdf`) | Skipped as a chapter; see the primer |
| **Class 2: Windows, Python refresher, Pydantic** | A video, a GeeksforGeeks page on Python arrays, a Colab notebook, a PDF (`Agentic-3-0.pdf`) | Primer |
| **Classes 3 and 4: Pydantic, AI and agentic AI basics** | Interactive sites for Pydantic (`pydantic-with-mayank.netlify.app`), common AI terms (`ai-terms-with-mayank.netlify.app`) and a context-window and memory simulator (`context-with-mayank.netlify.app`); the OpenAI tokenizer; a Colab; a Claude usage tracker extension; PDF `Class-3-4.pdf` | Primer, and Chapter 3 for tokens and context |
| **11 July: Python and agents** | One Colab notebook | Primer |
| **12 July: Agents, Python and LangChain** | Site "Agents, with just Python" (`python-agents-with-mayank.netlify.app`), a Colab, the setup `uv init`, `uv add langchain langchain-openai langchain-anthropic`, `uv sync`, two PDFs (`Agentic-Python.pdf` and `Untitled-scene (3).pdf`) | Primer and Chapter 1 |
| **18 to 19 July: LangChain** | A Colab, a 22 MB `Langchain.pdf`, and a GitHub repo of collected system prompts of AI tools (`x1xhlol/system-prompts-and-models-of-ai-tools`) | Chapters 1 to 3 |
| **25 to 26 July: LangChain continued** | Colab, a video, `Langchain-2.pdf` and `Langchain.pdf`, the `Revision_Parts_1-4.ipynb` notebook | Chapters 3 to 5 |
| **1 Aug** | Assignment, interview questions and a revision notebook on GitHub (the folder for the structured output and tools class), a Colab and `Langchain-2 (2).pdf` | Chapters 4 and 5 |
| **8 to 9 Aug** | The page is empty apart from the title ("Preview of the page will be displayed here") | Nothing to add |
| **16 Aug** | `Assignment_2_Agents_and_Prebuilt_Middleware.ipynb`, `Assignment_LangChain_Fundamentals_SOLUTIONS.ipynb`, a "Custom Middleware" Colab | Chapters 6 to 9 |
| **22 Aug: Runtime and HITL** | A Colab, the `Runtime-HITL.excalidraw` diagram, `Runtime-HITL.pdf`, `Runtime_and_HITL.ipynb` | Chapter 10 |
| **MCP starts** | A seven-part interactive series "Claude and AI, properly explained" (`ai-automation-with-mayank.netlify.app`) | Chapters 11 to 17 |

## MCP material on the page

| Resource | What the page says about it |
| --- | --- |
| MCP Lifecycle conversation simulator (`mcp-lifecycle-simulator.netlify.app`) | A simulator of the conversation. The card notes that **roots, sampling and logging are being deprecated** in the newest spec revision (SEP-2577) |
| MCP Lifecycle complete guide (`mcp-lifecycle.netlify.app`) | "Every MCP connection moves through exactly three stages, in exactly this order" (Chapter 12) |
| MCP: What is actually changing (`mcp-legacy-vs-modern.netlify.app`) | Legacy versus modern MCP and how gradually servers adopt it (Chapter 17) |
| PDFs | `MCP-Lifecycle.pdf` (two versions), `Complete-MCP.pdf`, `MCP-Primitives.pdf`, `MCP-Server.pdf`, `MCP-Client.pdf`, `AI-Updater-Project.pdf` |
| LangChain MCP Colab | One notebook (Chapter 18) |
| `github.com/patoles/agent-flow` | An extra repo the instructor linked |
| Inspector command | `CLIENT_PORT=9999 npx @modelcontextprotocol/inspector python3 recipebox_fastmcp.py`, which is how the class opened a local server in Inspector (Chapter 14) |

:::key A point worth connecting
The Craft card says sampling is being deprecated. That matches Chapter 17, where `ctx.sample()` is removed from the current FastMCP and the TimeTrack server calls the model provider directly instead.
:::

## The Meridian project

The page points to **one place for all project content for 3 to 31 October**: the site `meridian-ai-course.netlify.app` and the repo `github.com/mayank953/meridian-ai-learner`, which holds the approach, code and slides. Chapter 20 is a tour of the same project.

## Project: the AI newsletter

The page has an **AI newsletter project** with two parts: a request, then the long prompt that came out of it.

**The request** (a prompt given to a Claude chat): build an AI newsletter and updater that searches **recursively** using Tavily, goes **in depth** on each story, and splits news by industry (tech, business and so on). Then create an **HTML draft in Gmail**, an **8 AM Google Calendar event** to read it, and two **Apple Notes** (a LinkedIn post and a Markdown article for Substack), using apps already connected through connectors and MCP.

**The workflow the prompt defines** (the visible part of the page; the rest of the prompt is clipped on the page):

| Step | Action |
| --- | --- |
| 0 | Check Google Calendar for a recurring "Read Today's Update" event (8:00 to 8:15 AM, daily). Create it only if it does not exist, so no duplicates |
| 1 | **Broad search** with Tavily, one search per category (AI, Tech, Business, Finance and markets) for the last 24 hours, shortlisting 2 to 4 significant stories each |
| 2 | **Recursive deep dive**: a follow-up Tavily search on each shortlisted story for context, numbers, reactions and why it matters, done independently per story (the branching search) |
| 3 | **Synthesise** into four sections, 2 to 4 sentences per story (what happened, why it matters, source), dropping thin or unverified items |
| 4 | **Create a Gmail draft** (do not send): subject "Daily Update - date", clean HTML with one section per category and source links, no sign-off or contact details |
| 5 | **Create two Apple Notes**: a LinkedIn post about the single most interesting story, and a Markdown article |

:::trap Why this prompt is built this way
Two good habits are visible. It checks before creating (the calendar event), so a daily run never makes duplicates, and it drafts instead of sending (the Gmail step), so a human reviews it first. Both are the same safety ideas as human-in-the-loop in Chapter 10.
:::

## Not read

- The PDFs, Colab notebooks and Excalidraw files attached on the page.
- The linked interactive websites and the Meridian repo and site (Chapter 20 covers the Meridian code from the course repo instead).
- The clipped tail of the newsletter prompt.

## Sources

- [Craft page: Agentic 3.0](https://bugs-sleep-6uj.craft.me/agentic3)
- [Course repository](https://github.com/mayank953/Live-Class-2026)
- [Meridian learner repository](https://github.com/mayank953/meridian-ai-learner)
