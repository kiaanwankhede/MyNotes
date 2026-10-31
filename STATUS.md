# Coverage status

Updated 2026-10-31 by `build/status.py`. This file is regenerated after every prompt.

**How to read it, in plain words.** For each file I use one of three levels:

- **Read properly**: I read it from start to finish and the notes use its details.
- **Looked through (skimmed)**: I opened it and read parts of it, or turned it into text and scanned it. The notes use its main points, not every line. Typical for notebooks, PDFs, big folders of similar files and code.
- **Not opened**: I have not looked at it.

*Opened at all* = read properly + looked through. Percentages count files or pages, not how much you know. A file counts as *looked through* even if I only used one idea from it, so treat *Read properly* as the number that matters.

## 1. Course repo files (368, excluding 95 lock, log and config files)

| Area | Files | Read properly | Opened at all | Not opened |
|---|---:|---:|---:|---:|
| Repo root, scripts, workflows | 26 | 10 (38%) | 100% | 0 |
| Complete MCP (TimeTrack, servers, clients) | 60 | 15 (25%) | 100% | 0 |
| Weekend 00 (induction) | 1 | 1 (100%) | 100% | 0 |
| Weekends 01-02 (Python, Project 0) | 49 | 0 (0%) | 100% | 0 |
| Weekends 03-07 | 50 | 19 (38%) | 100% | 0 |
| Weekends 08-11 | 45 | 9 (20%) | 100% | 0 |
| Weekends 12-15 (MCP, multi-agent, Meridian) | 112 | 11 (10%) | 100% | 0 |
| Class write-ups (00-22) | 25 | 24 (96%) | 100% | 0 |
| **Total** | **368** | **89 (24%)** | **100%** | **0** |

279 files (76%) are cited by at least one chapter.

## 2. Everything outside the repo

| Source | What is measured | Done | Share | Notes |
|---|---|---:|---:|---|
| LangChain docs | Pages in scope | 41 of 41 | 100% | 23 read earlier plus the 18 that were blocked, all read in full on 31 Oct 2026 through the desktop browser. Out of scope by your request: frontend pages, Agent Chat UI, Deep Agents from scratch, four multi-agent tutorials. |
| Pydantic docs | Pages read | 19 of 19 | 100% | All 19 pages read (the settings page about 96%, the rest in full; the last 7 on 31 Oct 2026): get started, models, fields, validators, serialization, strict mode, types, JSON schema, settings, error handling, the LLM article, the Pydantic AI example, unions, alias, configuration, dataclasses, TypeAdapter, performance, and FastAPI (5 tutorial pages: body, response model, extra models, body updates, query parameter models; other FastAPI pages not read). A few tabbed code examples did not come through in the text, noted in the chapters. |
| Instructor sites | Sites read in full | 15 of 15 | 100% | All 15 read in full: 3 MCP sites, Pydantic, all 7 series guides, AI terms, Python agents, the context-window simulator (all 4 tabs and its script), Meridian slides (7 of 7 modules). |
| Meridian slides | Modules read in full | 7 of 7 | 100% | All 7 modules read in full (about 500 slides). Caveat: the text I extracted leaves out the code boxes, so exact command lines come from the repo files (deploy.yml, DEPLOY.md), not from the slides. |
| Craft page | Index pages read | 14 of 14 | 100% | All index pages read. |
| Craft page | Attachments opened | 31 of 40 | 78% | Of 40 items: 17 PDFs (text extracted; counts approximate for the earlier ones), 4 notebooks (from the repo) and all 10 Colabs opened. Colabs: 2 read in full (Custom Middleware, MCP adapter); the other 8 were compared by title, headings and opening cells with repo notebooks that were read earlier, not re-read cell by cell. Not opened: the .excalidraw file (its PDF export was read) and 5 class videos. Skipped on purpose: the AI Industry Handbook (not for redistribution) and 2 job-ad PDFs (not course content). Keys found in Colabs were not copied. |
| Meridian learner repo | Repo reviewed | 1 of 1 | 100% | README, code and a frontend digest read; not every file individually. |
| agent-flow repo | Repo reviewed | 0 of 1 | 0% | README and folder layout only, source not read. |
| Code run | Automated checks (count, not coverage) | 73 of 73 | 100% | Pydantic claims 47 of 47 (build/pydantic_claims_test.py), key-free Foundations and RAG checks 9 of 9 (build/rag_foundations_test.py), Meridian's own backend tests 17 of 17; TimeTrack lab run earlier. 100% here means every check written passes, not that every chapter's code was run. |

## 3. Skipped on purpose

- Frontend material (you asked to drop it)
- LangGraph (lectures not started; no book yet)
- AI Industry Handbook (marked not for redistribution)
- Search-excerpt content (removed after you objected)
- API keys found in a notebook and a Colab (flagged in the notes, never reproduced)

## 4. Structural gaps

- RAG book is built only from Meridian; no course RAG classes exist yet
- LangChain chapter order reviewed on 31 Oct 2026: sound, with 8 findings waiting for your decision (see REVIEW_langchain_chapter_order.md); nothing reordered
- Not run: provider SDK calls that need paid keys (Pydantic ch 11, Foundations, RAG with Gemini), Vertex AI Vector Search and Cloud Run, the thirteen RAG variants on real answers, and the notebook cells

## 5. Change log (newest first)

- 2026-10-31: Self-review: 2 more Pydantic checks (wrap-validator order, settings priority; now 47 of 47), review finding 8 corrected, new pages render-checked
- 2026-10-31: Glossaries and cheat sheets added to Foundations, Pydantic and RAG; Pydantic claims (45), key-free RAG/Foundations checks (9) and Meridian tests (17) run and passing; LangChain chapter order reviewed (REVIEW file, nothing reordered)
- 2026-10-31: Craft attachments: 3 MCP PDFs not in the repo and all 10 Colabs opened (now 31 of 40); mini-contra checked; keys in Colab flagged
- 2026-10-31: Context-window simulator site read in full (all 4 tabs and script); instructor sites now 15 of 15
- 2026-10-31: Read the 7 unread Pydantic docs pages (unions, alias, config, dataclasses, TypeAdapter, performance, FastAPI x5); now 19 of 19
- 2026-10-31: Coverage wording made plainer: Read properly, Looked through, Not opened
- 2026-10-31: Meridian module 7 (Docker and Google Cloud) read in full, now 7 of 7 modules; costs added to RAG r5
- 2026-10-31: Meridian module 6 (service and screen) read in full, now 6 of 7 modules
- 2026-10-31: Meridian module 4 (RAG) read in full, now 5 of 7 modules; RAG chapters expanded
- 2026-10-31: Meridian module 5 (the audit team) read in full, now 4 of 7 modules
- 2026-10-31: Meridian modules 1 and 3 read in full (now 3 of 7); STATUS.md and CLAUDE.md added
- 2026-10-31: Read the 18 blocked LangChain docs pages (now 41 of 41), Meridian module 2, AI terms and Python-agents sites, class 1-2 write-ups and the last unread repo files
