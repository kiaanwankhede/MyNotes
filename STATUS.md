# Coverage status

Updated 2026-10-31 by `build/status.py`. This file is regenerated after every prompt.

**How to read it.** Percentages are shares of items (files or pages), not of knowledge. *Full read* means read start to finish. *Touched* means read plus skimmed (scanned, text-extracted or parsed).

## 1. Course repo files (368, excluding 95 lock, log and config files)

| Area | Files | Full read | Touched | Not read |
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
| Pydantic docs | Pages read | 12 of 19 | 63% | Read: get started, models, fields, validators, serialization, strict mode, types, JSON schema, settings (about 96%), error handling, the LLM article, the Pydantic AI example. Not read: unions, alias, configuration, dataclasses, TypeAdapter, performance, FastAPI docs. |
| Instructor sites | Sites read in full | 13 of 15 | 87% | Full: 3 MCP sites, Pydantic, all 7 series guides, AI terms, Python agents. Partial: the context-window site (widgets only) and the Meridian slides (see below). |
| Meridian slides | Modules read in full | 4 of 7 | 57% | Modules 1, 2, 3 and 5 read in full (223 slides). Modules 4, 6 and 7 are digests from the "In short" lines (module 4 chapter 21 was read in full). Remaining about 370K characters. |
| Craft page | Index pages read | 14 of 14 | 100% | All index pages read. |
| Craft page | Attachments opened | 20 of 40 | 50% | 15 PDFs text-extracted and 5 Colabs opened (counts approximate). Not opened: Excalidraw files, videos, the other Colab links (same notebooks as in the repo), tail of the newsletter prompt, the AI Industry Handbook (not for redistribution). |
| Meridian learner repo | Repo reviewed | 1 of 1 | 100% | README, code and a frontend digest read; not every file individually. |
| agent-flow repo | Repo reviewed | 0 of 1 | 0% | README and folder layout only, source not read. |

## 3. Skipped on purpose

- Frontend material (you asked to drop it)
- LangGraph (lectures not started; no book yet)
- AI Industry Handbook (marked not for redistribution)
- Search-excerpt content (removed after you objected)
- API keys found in a notebook and a Colab (flagged in the notes, never reproduced)

## 4. Structural gaps

- Foundations, Pydantic and RAG books have no glossary or cheat sheet
- RAG book is built only from Meridian; no course RAG classes exist yet
- Chapter order inside the LangChain book has not been reviewed
- Only the TimeTrack lab was run; SDK snippets in the Pydantic book were not run

## 5. Change log (newest first)

- 2026-10-31: Meridian module 5 (the audit team) read in full, now 4 of 7 modules
- 2026-10-31: Meridian modules 1 and 3 read in full (now 3 of 7); STATUS.md and CLAUDE.md added
- 2026-10-31: Read the 18 blocked LangChain docs pages (now 41 of 41), Meridian module 2, AI terms and Python-agents sites, class 1-2 write-ups and the last unread repo files
