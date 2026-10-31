# Chapter 1: Course roadmap and prerequisites

This chapter is the map before the road trip: where the course sits, what it covers in what order, the rules of thumb the mentor repeats, and the one-time setup you need before the first coding class.

## 1.1 Where the course sits

Krish Naik Academy places every learner on one of three paths:

| Path | For whom |
|---|---|
| Traditional | Data science, then GenAI, then agentic AI |
| Modern | Some experience, faster ramp-up |
| Advanced | Highly experienced, quick implementation |

Agentic AI 3.0 sits between the Modern and Advanced paths. It is built for people who want to go from fundamentals to specialisation without starting from zero. The induction session also mentions a separate no-code agentic AI batch for managers who want to skip coding.

*Source: Live-Class-2026, `classes_summary/00` and `classes_transcription_summary/00`.*

## 1.2 Agentic 2.0 versus 3.0

| | Agentic 2.0 | Agentic 3.0 |
|---|---|---|
| Focus | Understanding agents | Using and deploying agents |
| Frameworks | Older LangChain and LangGraph | Latest LangChain, MCP, A2A, Claude Agent SDK |
| Tools | Basic | Claude Code, OpenClaude, Hermes/Nemo agents |
| Projects | Simpler builds | Production-grade, multi-agent, CI/CD-driven |
| New roles covered | None | Harness Engineering, Forward-Deployed Engineer (FDE) |

Notes from the session:

- 2.0 comes free with 3.0 enrolment but is not a prerequisite.
- New hot topics are added as the field changes (the session's example is n8n, which was added in 2.0).
- The session says Azure and Microsoft AI Foundry, Bedrock and Vertex AI each get dedicated sessions.
- A2A is the agent-to-agent protocol that the roadmap places beside MCP and LangGraph for connecting separate agentic systems.
- AgentOps, the production deployment-and-monitoring side that the course pairs with agent building, comes after the fundamentals and framework phases, roughly one and a half to two months in.

*Source: `classes_transcription_summary/00`, `classes_summary/00`, and the Q&A in `classes_transcription_summary/02`.*

## 1.3 The curriculum arc

The induction session lays out seven stages:

1. **Foundations:** LLMs and model providers (OpenAI, Anthropic and others).
2. **Core frameworks and protocols:** LangChain, LangGraph, MCP, A2A, RAG, context engineering.
3. **Mini-projects:** applying each concept by hand.
4. **Interim projects:** deployed on cloud and a VPS.
5. **Coding agent ecosystem:** Claude Code, OpenClaude, Hermes/Nemo agents.
6. **Extended frameworks:** ADK, the Claude Agent SDK and more.
7. **Production capstones:** about nine real-world, portfolio-grade builds.

The course repo describes the same journey in five phases, and these notes follow it:

| Phase | Content | Where in these notes |
|---|---|---|
| 0 Foundations | Python, Pydantic, AI vocabulary | Python and Pydantic books, LLM chapter 3 |
| 1 Agents in pure Python | Brain, memory, tools, the agentic loop | Python chapter 3, LLM chapter 2 |
| 2 LangChain in depth | Models, structured output, tools, agents, middleware | Langchain book (chapters 1 to 5 written; 6 to 12 not yet) |
| 3 LangGraph and beyond | State, checkpointing, MCP, RAG | MCP book for the MCP part (not written yet). No book is planned yet for LangGraph or RAG |
| 4 Production capstones | Deployed on cloud and VPS | Projects book (not written yet) |

The repo's own README says it covers classes 00 to 18. Its transcript folder goes further, to class 23 (MCP in LangChain), so the README is out of date on that point.

*Source: `classes_summary/00`, `classes_transcription_summary/00`, root `README.md`.*

## 1.4 The four golden rules

The mentor's rules for judging a system after it is in production, repeated all through the course:

1. **Cost**, including token usage.
2. **Failure rate**, which should trend toward zero.
3. **Latency**, the speed of the response.
4. **Quality**: is the output actually useful?

His summary line: "Simple is scalable". The engineering philosophy from the Q&A:

- Minimise calls to outside services, APIs and LLMs. Every hop costs time and money.
- Prefer the simplest system that solves the problem. Do not over-engineer for a scale that never arrives.
- Use several LLMs only when the problem demands it, for example failover. Calling models in parallel by default just doubles the cost.

*Source: `classes_summary/00`, `classes_transcription_summary/00`.*

## 1.5 How the hands-on learning works

Each concept is taught with a mini-project in class. The mentor then walks through a full project build and shares the complete package: code, diagrams and explanations. If you are short of time, run the given code with its explanation. If you have time, customise and extend it yourself. The course is built for working professionals, so you are never forced to write everything from scratch.

*Source: `classes_transcription_summary/00`.*

## 1.6 Recurring projects and tooling

Three projects come back through the course:

| Project | First appears | What it is |
|---|---|---|
| Project Zero | Class 04 | The hand-built raw-Python agent: model, tools, memory and a Streamlit UI |
| CineBot | Class 09 | A movie-ticket booking agent, the vehicle for structured output and tools |
| TripMate | Class 11 | A travel-planning agent with real weather, search and SQLite storage |

Tooling used throughout:

- Python 3.10 or newer, managed with UV. Every code folder has its own `pyproject.toml`.
- Free LLM access through Groq and OpenRouter, paid access through OpenAI and Anthropic. Keys always go in `.env` and are never committed. A `.env.example` ships in each project.
- Google Colab for line-by-line learning and VS Code for real multi-file projects.
- Excalidraw for the diagrams drawn live in class.

*Source: root `README.md`.*

## 1.7 Prerequisites and first-time setup

Do this once, before class 01. Python, UV and VS Code are explained in the Python book, Chapter 1, so this section lists the steps and links there for the reasons.

1. **Python 3.10 or newer.** Check with `python3 --version`. The course projects pin 3.13, and each project folder pins its exact version in `.python-version`, which UV reads automatically.
2. **UV.** On Mac or Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`. On Windows use Git Bash or Windows Terminal and follow the UV install docs. See [Python Chapter 1](../python/01-setup-and-api-basics.md) for why UV and what it creates.
3. **VS Code.** The course leans on `.py` scripts, a real terminal and debugging, not only notebooks.
4. **At least one free LLM API key.** Every class folder needs one provider key to run its live calls, and you need only one to start:

| Provider | Cost | Where to get a key |
|---|---|---|
| Groq | Free, fast (the quickest to sign up for) | console.groq.com/keys |
| OpenRouter | Free tier. `model="openrouter/free"` routes to a free model so it does not go stale | openrouter.ai/keys |
| OpenAI | Paid | platform.openai.com/api-keys |
| Anthropic | Paid | console.anthropic.com |

5. **The `.env` workflow, the same in every project folder.** Never edit `.env.example`. Copy it:

```bash
cd "Weekend 01 - 27-28 Jun/01 - 27 Jun - Python Setup & API Basics"
uv sync
cp .env.example .env
# open .env and paste in at least one real key, e.g. GROQ_API_KEY=...
uv run main.py
```

`.env` is git-ignored at the repo root, so a real key is never committed by accident. Only `.env.example` ships, with placeholder values. The code files also fall back to a built-in stand-in when no key is set (see [Python Chapter 3](../python/03-anatomy-of-an-agent.md), section 3.4).

**If `git clone` or `git pull` fails** (from the repo's own troubleshooting table):

| Symptom | Fix |
|---|---|
| `error: invalid path '...'` or `unable to checkout working tree` | A bad filename slipped into the repo. Report the exact path to the mentor, then run `git restore --source=HEAD :/` and `git pull` after it is fixed |
| `Filename too long` (Windows) | Run `git config --global core.longpaths true` and clone somewhere short such as `C:\src\` |
| `Your local changes would be overwritten by merge` | Save your work with `git stash -u`, run `git pull`, then `git stash pop` |
| A folder you created never shows up on GitHub | It probably has its own hidden `.git` folder, which `uv init` creates. Delete `<folder>/.git`, or create projects with `uv init --no-vcs` |

**Checklist before class 01:** Python 3.10+ and UV installed (`uv --version` runs), VS Code installed, one free API key in hand, and Saturday and Sunday 8 to 11 AM IST blocked on your calendar.

*Source: `PREREQUISITES.md`, `classes_summary/00`.*

## 1.8 Further reading

The mentor's own notes and tools, from the course repo:

- Running notes, class links, Colab links and the doubt-solving chatbot: bugs-sleep-6uj.craft.me/agentic3
- The course code: github.com/mayank953/Live-Class-2026
- Topic sites: Mastering Pydantic (pydantic-with-mayank.netlify.app), AI Terms (ai-terms-with-mayank.netlify.app), Agents with Pure Python (python-agents-with-mayank.netlify.app), Claude and AI (ai-automation-with-mayank.netlify.app), AI Memory Lab (context-with-mayank.netlify.app)
- MCP: MCP Lifecycle guide (mcp-lifecycle.netlify.app) and the conversation simulator (mcp-lifecycle-simulator.netlify.app)
- Transformer Explainer: poloclub.github.io/transformer-explainer

*Source: transcription folder `Readme.md` and root `README.md`. I did not open these links.*

**The AI Industry Handbook.** The repo also holds a PDF, the *Industry-Ready AI Handbook* (2026 edition), a business-oriented companion to an ET Masterclass. It is a 22-page guide that walks through ten industries (manufacturing, healthcare, banking, retail, hospitality, FMCG, real estate, media and marketing, IT and consulting, energy) plus a fashion bonus, giving example companies for each and a closing question for the reader. It also has a section on India's AI market, a list of AI uses by job role, a tool list, and a 30-day plan for getting started. It may be the handbook of AI opportunities across industries that the class 01 Q&A promised, but I could not confirm that. The PDF is marked "Not for redistribution", so these notes contain none of its figures or company claims. Open the PDF itself if you need them.

*Source: `Weekend 01 - 27-28 Jun/AI_Industry_Handbook_2026.pdf`, read in full.*

## Practice

1. Place yourself on the three paths and say why 3.0 fits (or does not).
2. Name the four golden rules and give one example of each from a system you know.
3. Finish the setup checklist and run `uv run main.py` in the class 01 folder.

## Sources and further reading

- Live-Class-2026, `classes_summary/00 - 21 Jun - Course Induction & Roadmap.md`
- Live-Class-2026, `classes_transcription_summary/00 - 21 June - Course Induction & Roadmap.md`
- Live-Class-2026, `PREREQUISITES.md`, root `README.md` and `classes_transcription_summary/Readme.md`

Next: [Chapter 2, The agentic loop in pure Python](02-the-agentic-loop-in-pure-python.md) (not written yet)
