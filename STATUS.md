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
| LangChain docs | Pages in scope | 41 of 41 | 100% | The LangChain section of the docs has 68 pages. Out of scope by your request: 20 frontend pages, Agent Chat UI, Deep Agents from scratch and 4 multi-agent tutorials, leaving about 42; I recorded 41 as read in full. Gaps: only 23 docs pages are linked as sources in the book, so the rest are not traceable page by page; about 12 related pages outside that folder were not read (concepts: memory, context, human-in-the-loop, products, providers-and-models; migration guides; v1 release notes; common errors; versioning). The wider Python docs have 234 build pages (LangGraph, Deep Agents and Managed Deep Agents are out of scope for now). |
| Pydantic docs | Teaching pages read (of 54; API reference not counted) | 17 of 54 | 31% | Corrected 31 Oct: the earlier '19 of 19' counted a list I made, not the site. The docs have 91 pages: Get started 8, Concepts 19, Internals 2, Examples 8, Errors 4, Integrations 13 (54 teaching pages) plus 36 API-reference pages and 1 people page. Read: 14 of 19 Concepts (not read: Conversion Table, Experimental Features, Forward Annotations, JSON, Validation Decorator), the Get started page, Error Handling (1 of 4), the Pydantic AI example (1 of 8), nothing from Internals or Integrations. Outside the 91: the Pydantic LLM article and 5 FastAPI tutorial pages, read in full. |
| Instructor sites | Sites read in full | 15 of 15 | 100% | All 15 read in full: 3 MCP sites, Pydantic, all 7 series guides, AI terms, Python agents, the context-window simulator (all 4 tabs and its script), Meridian slides (7 of 7 modules). |
| Meridian slides | Modules read in full | 7 of 7 | 100% | All 7 modules read in full (about 500 slides). Caveat: the text I extracted leaves out the code boxes, so exact command lines come from the repo files (deploy.yml, DEPLOY.md), not from the slides. |
| Craft page | Index pages read | 14 of 14 | 100% | All index pages read. |
| Craft page | Attachments opened | 33 of 42 | 79% | Recounted 31 Oct from the full list (COVERAGE_INVENTORY.md section 5a): 22 PDFs, 4 notebooks, 1 .excalidraw, 10 Colabs, 5 videos = 42. Opened: 19 PDFs, 4 notebooks, 10 Colabs. Not opened: the .excalidraw file (its PDF export was read) and 5 videos. Skipped on purpose: the AI Industry Handbook and 2 job-ad PDFs. Three LangChain PDF variants share names with repo copies; byte-for-byte equality was not checked. Only 2 Colabs were read cell by cell; 8 were compared by title and headings with repo notebooks. |
| Meridian learner repo | Repo reviewed | 1 of 1 | 100% | README, code and a frontend digest read; not every file individually. |
| agent-flow repo | Repo reviewed | 0 of 1 | 0% | README and folder layout only, source not read. |
| Code run | Automated checks (count, not coverage) | 73 of 73 | 100% | Pydantic claims 47 of 47 (build/pydantic_claims_test.py), key-free Foundations and RAG checks 9 of 9 (build/rag_foundations_test.py), Meridian's own backend tests 17 of 17; TimeTrack lab run earlier. 100% here means every check written passes, not that every chapter's code was run. |
| MCP official docs (2026-07-28) | Docs pages read | 1 of 26 | 4% | Only the intro page has been read. Not yet read: Learn 4, Develop 6, SDKs 1, Security tutorials 3, Inspector and debugging 11. Planned for the MCP book once you approve. |
| MCP official docs (2026-07-28) | Specification pages read | 0 of 31 | 0% | Not read yet. Plus 9 extension pages and 33 community pages, which I would skip unless you want them. |

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
- New upstream file not yet read: classes_transcription_summary/23 - 27 Sep - MCP In LangChain.md (the course repo moved from dd4bfe3 to 579c38a)

## 5. Change log (newest first)

- 2026-10-31: Full inventory written (COVERAGE_INVENTORY.md): every repo file and every LangChain, MCP and Pydantic docs page with status; found 1 new upstream class file; Craft attachments recounted as 33 of 42
- 2026-10-31: Coverage corrected: Pydantic docs are 17 of 54 teaching pages (not 19 of 19); LangChain docs gaps stated; MCP official docs added (1 of 26 docs, 0 of 31 spec). No book content changed
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
