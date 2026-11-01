# Chapter 1: Course roadmap and prerequisites

**After this chapter you can:**

- Say where the course sits and what each stage covers
- Name the four golden rules for judging an agent in production
- Find every topic in these notes from the course phases
- Finish the one-time setup and run the first class folder

The map before the road trip: where the course sits, what comes in what order, the mentor's rules of thumb, and the setup you need before class 01.

## 1.1 Where the course sits

Krish Naik Academy places each learner on one of three paths:

| Path | For whom |
|---|---|
| Traditional | Data science, then GenAI, then agentic AI |
| Modern | Some experience, faster ramp-up |
| Advanced | Highly experienced, quick implementation |

- Agentic AI 3.0 sits **between Modern and Advanced**
- Built for people who want fundamentals to specialisation without starting from zero
- A separate no-code agentic AI batch exists for managers who want to skip coding

*Source: Live-Class-2026, `classes_summary/00` and `classes_transcription_summary/00`.*

## 1.2 Agentic 2.0 versus 3.0

| | Agentic 2.0 | Agentic 3.0 |
|---|---|---|
| Focus | Understanding agents | Using and deploying agents |
| Frameworks | Older LangChain and LangGraph | Latest LangChain, MCP, A2A, Claude Agent SDK |
| Tools | Basic | Claude Code, OpenClaude, Hermes/Nemo agents |
| Projects | Simpler builds | Production-grade, multi-agent, CI/CD-driven |
| New roles | None | Harness Engineering, Forward-Deployed Engineer (FDE) |

- 2.0 comes free with 3.0 enrolment but is **not a prerequisite**
- New hot topics are added as the field changes (example: n8n, added in 2.0)
- Azure and Microsoft AI Foundry, Bedrock and Vertex AI each get dedicated sessions
- **A2A** is the agent-to-agent protocol the roadmap places beside MCP and LangGraph
- **AgentOps**, the deployment and monitoring side, comes after fundamentals and frameworks, about 1.5 to 2 months in

*Source: `classes_transcription_summary/00`, `classes_summary/00`, the Q&A in `classes_transcription_summary/02`.*

## 1.3 The curriculum arc

The induction session gives seven stages:

1. **Foundations:** LLMs and model providers (OpenAI, Anthropic, others)
2. **Core frameworks and protocols:** LangChain, LangGraph, MCP, A2A, RAG, context engineering
3. **Mini-projects:** each concept applied by hand
4. **Interim projects:** deployed on cloud and a VPS
5. **Coding agent ecosystem:** Claude Code, OpenClaude, Hermes/Nemo agents
6. **Extended frameworks:** ADK, the Claude Agent SDK and more
7. **Production capstones:** about nine portfolio-grade builds

The repo describes five phases. These notes follow them:

| Phase | Content | Where in these notes |
|---|---|---|
| 0 Foundations | Python, Pydantic, AI vocabulary | [Python](../python/01-setup-and-api-basics.md), [Pydantic](../pydantic/01-why-pydantic-and-basemodel.md), [LLM Ch 3](03-inside-the-model.md) |
| 1 Agents in pure Python | Brain, memory, tools, the loop | [Python Ch 3](../python/03-anatomy-of-an-agent.md), [LLM Ch 2](02-the-agentic-loop-in-pure-python.md) |
| 2 LangChain in depth | Models, structured output, tools, agents, middleware, runtime | [Langchain book](../langchain/01-introduction-to-langchain.md) (Ch 1 to 15) |
| 3 LangGraph and beyond | State, checkpointing, MCP, RAG | [MCP book](../mcp/01-why-mcp-exists.md) (Ch 1 to 8). Checkpointing is in Langchain Ch 6. RAG is shown in [Projects Ch 3](../projects/03-meridian-ai-learner.md). No book yet for LangGraph itself |
| 4 Production capstones | Deployed on cloud and VPS | [Projects book](../projects/01-cinebot.md) (Ch 1 to 4) |

- The repo README says it covers classes 00 to 18. Its transcript folder goes to class 23 (MCP in LangChain), so the README is out of date there

*Source: `classes_summary/00`, `classes_transcription_summary/00`, root `README.md`.*

## 1.4 The four golden rules

The mentor's rules for judging a system **in production**, repeated all course:

1. **Cost**, including token use
2. **Failure rate**, trending toward zero
3. **Latency**, the speed of the response
4. **Quality**: is the output useful?

His line: **"Simple is scalable."** Philosophy from the Q&A:

- Minimise calls to outside services, APIs and LLMs. Every hop costs time and money
- Prefer the simplest system that solves the problem. Do not build for scale that never arrives
- Use several LLMs only when needed, such as failover. Calling models in parallel by default doubles cost

*Source: `classes_summary/00`, `classes_transcription_summary/00`.*

## 1.5 How the hands-on learning works

- Each concept gets a mini-project in class
- The mentor then walks through a full project and shares the package: code, diagrams, explanations
- Short of time: run the given code with its explanation
- With time: customise and extend it
- Built for working professionals. You are never forced to write everything from scratch

*Source: `classes_transcription_summary/00`.*

## 1.6 Recurring projects and tooling

| Project | First appears | What it is |
|---|---|---|
| Project Zero | Class 04 | Hand-built raw-Python agent: model, tools, memory, Streamlit UI |
| CineBot | Class 09 | Movie-ticket agent, the vehicle for structured output and tools |
| TripMate | Class 11 | Travel planner with real weather, search and SQLite storage |

- CineBot is gathered in [Projects Ch 1](../projects/01-cinebot.md)
- Python 3.10 or newer, managed with **UV**. Every code folder has its own `pyproject.toml`
- Free LLM access: Groq and OpenRouter. Paid: OpenAI and Anthropic
- Keys go in `.env`, never committed. Each project ships a `.env.example`
- Google Colab for line-by-line learning. VS Code for real multi-file projects
- Excalidraw for the diagrams drawn live

*Source: root `README.md`.*

## 1.7 Prerequisites and first-time setup

Do this once, before class 01. Why UV and VS Code: [Python Ch 1](../python/01-setup-and-api-basics.md).

1. **Python 3.10 or newer.** Check with `python3 --version`
   - Projects pin 3.13. Each folder pins its exact version in `.python-version`, which UV reads
2. **UV.** Mac or Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`. Windows: Git Bash or Windows Terminal and the UV docs
3. **VS Code.** The course uses `.py` scripts, a real terminal and debugging, not only notebooks
4. **One free LLM API key.** Every class folder needs one provider key:

| Provider | Cost | Where |
|---|---|---|
| Groq | Free, fast, quickest to sign up | console.groq.com/keys |
| OpenRouter | Free tier. `model="openrouter/free"` routes to a free model so it does not go stale | openrouter.ai/keys |
| OpenAI | Paid | platform.openai.com/api-keys |
| Anthropic | Paid | console.anthropic.com |

5. **The `.env` workflow**, the same in every folder. Never edit `.env.example`. Copy it:

```bash
cd "Weekend 01 - 27-28 Jun/01 - 27 Jun - Python Setup & API Basics"
uv sync
cp .env.example .env
# open .env and paste in at least one real key, e.g. GROQ_API_KEY=...
uv run main.py
```

- `.env` is git-ignored at the repo root. Only `.env.example` ships, with placeholders
- The code files also fall back to a stand-in when no key is set ([Python Ch 3](../python/03-anatomy-of-an-agent.md), 3.4)

**If `git clone` or `git pull` fails** (the repo's own table):

| Symptom | Fix |
|---|---|
| `invalid path '...'` or `unable to checkout working tree` | A bad filename slipped in. Report the path, then `git restore --source=HEAD :/` and `git pull` after it is fixed |
| `Filename too long` (Windows) | `git config --global core.longpaths true`; clone to a short path such as `C:\src\` |
| `Your local changes would be overwritten by merge` | `git stash -u`, `git pull`, `git stash pop` |
| A folder never shows on GitHub | It has its own `.git` (created by `uv init`). Delete `<folder>/.git`, or use `uv init --no-vcs` |

**Checklist before class 01:**

- Python 3.10+ and UV installed (`uv --version` runs)
- VS Code installed
- One free API key in hand
- Saturday and Sunday, 8 to 11 AM IST, blocked on your calendar

*Source: `PREREQUISITES.md`, `classes_summary/00`.*

## 1.8 Further reading

From the course repo:

- Running notes, class links, Colab links, doubt-solving chatbot: bugs-sleep-6uj.craft.me/agentic3
- Course code: github.com/mayank953/Live-Class-2026
- Topic sites: Mastering Pydantic (pydantic-with-mayank.netlify.app), AI Terms (ai-terms-with-mayank.netlify.app), Agents with Pure Python (python-agents-with-mayank.netlify.app), Claude and AI (ai-automation-with-mayank.netlify.app), AI Memory Lab (context-with-mayank.netlify.app)
- MCP: lifecycle guide (mcp-lifecycle.netlify.app) and conversation simulator (mcp-lifecycle-simulator.netlify.app)
- Transformer Explainer: poloclub.github.io/transformer-explainer

*Source: transcription folder `Readme.md` and root `README.md`. These links were not opened.*

**The AI Industry Handbook**

- A PDF in the repo: the *Industry-Ready AI Handbook* (2026 edition), a business companion to an ET Masterclass
- 22 pages: ten industries (manufacturing, healthcare, banking, retail, hospitality, FMCG, real estate, media and marketing, IT and consulting, energy) plus a fashion bonus
- Also: India's AI market, AI uses by job role, a tool list, a 30-day starter plan
- It may be the industry handbook the class 01 Q&A promised. That is not confirmed
- It is marked "Not for redistribution", so these notes carry none of its figures or company claims. Open the PDF itself

*Source: `Weekend 01 - 27-28 Jun/AI_Industry_Handbook_2026.pdf`, read in full.*

## 1.9 Interview corner

**Q1. How do you judge an agent system in production?**
- Cost, failure rate, latency, quality. Watch all four, not one

**Q2. "Simple is scalable." What does it mean here?**
- Fewer calls and fewer moving parts. Each extra LLM or API hop adds cost and failure points

**Q3. When do you use more than one LLM?**
- When the problem needs it, such as failover. Not in parallel by default, which doubles cost

**Q4. What is AgentOps?**
- The deployment and monitoring side of agents in production

**Q5. Why teach the raw-Python loop before LangChain?**
- So the framework is a convenience, not a mystery ([Chapter 2](02-the-agentic-loop-in-pure-python.md))

**Q6. Why keep keys in `.env` and ship `.env.example`?**
- A real key must never be committed. The example shows which variables to set

**Q7. Why UV and a `pyproject.toml`?**
- One tool for versions, environments and dependencies, and a file that rebuilds the same setup elsewhere

**Q8. Colab or VS Code?**
- Colab to learn line by line without setup. VS Code for real multi-file projects

## 1.10 Added by Claude, not from the sources

- **Map the rules to tools.** Cost, latency and failures show up in a trace: LangSmith records each step's time and token cost ([Langchain Ch 2](../langchain/02-langchain-family-and-harness-engineering.md)). Quality needs your own test questions
- **A key check before you push:** run `git status` and confirm `.env` is not listed; `git check-ignore .env` prints the path when it is ignored
- **Rotate a leaked key.** If a key ever lands in a commit, revoke it at the provider, not only in the repo. Several keys in this course's source files should be revoked by their owner (see [Langchain Ch 12](../langchain/12-mcp-in-langchain.md), 12.11)
- **Read the dates.** The README, transcripts and notes were written at different times. The class count (18 versus 23) is one example of drift
- **FDE in general use** usually means an engineer who works with a customer to build and deploy a solution on site. The course names the role but the sources here do not define it, so check the course material before relying on this reading

## Recap

- Three paths. 3.0 sits between Modern and Advanced
- Seven stages in class; five phases in the repo; all mapped to these books
- Four golden rules: cost, failure rate, latency, quality. "Simple is scalable"
- Setup: Python 3.10+, UV, VS Code, one free key, the `.env` copy workflow
- Fix git problems with the table. Keep keys out of Git

## Practice

1. Place yourself on the three paths and say why 3.0 fits (or does not)
2. Name the four golden rules and give one example of each from a system you know
3. Finish the setup checklist and run `uv run main.py` in the class 01 folder
4. Open the phase table and note which book you will study first

## How this chapter was checked

- **Rewritten** from the earlier version of this chapter, which was built from the induction summaries, `PREREQUISITES.md`, the root README, the transcription `Readme.md` and the handbook PDF (read in full at that time). I did not re-open those files in this pass
- **Checked in the repo:** every link to a chapter in the phase table points to a file that exists
- **Not run:** `uv`, the setup steps, the git fixes, any link in 1.8
- The phase table reflects the books as they stand now. Earlier versions of this chapter listed several as "not written yet"

## Sources and further reading

- Live-Class-2026, `classes_summary/00 - 21 Jun - Course Induction & Roadmap.md`
- Live-Class-2026, `classes_transcription_summary/00 - 21 June - Course Induction & Roadmap.md`
- Live-Class-2026, `PREREQUISITES.md`, root `README.md` and `classes_transcription_summary/Readme.md`

Next: [Chapter 2, The agentic loop in pure Python](02-the-agentic-loop-in-pure-python.md)
