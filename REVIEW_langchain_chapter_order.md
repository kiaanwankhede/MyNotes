# Review: chapter order of the LangChain book

Written 31 Oct 2026. **Nothing was reordered or edited.** Changing the order is your decision (standing instruction 1); this file lists what I found and the options.

**How I checked.** I read all chapter titles, leads and section headings, and traced every "Chapter N" mention in the text (outside code) to see which chapters lean on later ones. I spot-read ch1, ch5, ch6 and ch10 where the overlaps are. I did not re-read every chapter in full.

## Verdict

The order is sound. It follows the class order (Part A classes 06–10, B 11–14, C 15, D 16–22, E weekends 13–14), and almost every cross-reference points **back** to an earlier chapter or says "Chapter N covers this in depth". No chapter needs a later chapter to make its core code run. The issues below are overlaps and a few soft forward dependencies, not a broken order.

## Findings, most useful first

| # | Finding | Where | Options (your call) |
| --- | --- | --- | --- |
| 1 | **Memory is taught three times.** Ch1 has a "Memory: why the agent forgets" section with checkpointer code that I added to fix the repo example; ch6 teaches the same checkpointer and `thread_id` properly (class 11); ch5 teaches the long-term **store** before ch6 introduces short-term memory. | ch1 §Memory, ch5 §8–8b, ch6 §8–9 | (a) Keep ch1 as a short teaser that points to ch6. (b) Move ch5 §8–8b (store) to after ch6. (c) Leave as is. |
| 2 | **`ToolRuntime` comes before Runtime.** Ch5 §7–8b uses `runtime.state`, `context` and `store`; ch10 explains the five components of runtime, `context_schema` and "who gets what", then repeats the `ToolRuntime` example. | ch5 §7–8b, ch10 §3–6 | (a) Add a one-line pointer in ch5 to ch10 (smallest change). (b) Move ch5 §7–8b into ch10 and keep ch5 to plain tools. |
| 3 | **Setup is written twice** in this book (ch1 "Setting up a project", ch2 "Setting up the environment"), and a third time in the Foundations book (chapter 1). | ch1, ch2, Foundations f1 | Make one the full version and have the others point to it. |
| 4 | **Middleware is spread over four chapters** plus HITL in two: ch6 (idea, VIP demo), ch7 (six built-ins), ch8 (rest of the catalogue), ch9 (custom), HITL in ch7 and again in ch10. It reads fine in order but is hard to find later. | ch6–ch10 | Add one "where is each middleware" table (in ch7 or the cheat sheet). No move needed. |
| 5 | **The capstone points forward to another book.** Ch20 sends RAG details to the RAG book (`#rag-r2` to `#rag-r5`), which comes after this book. This is the "option C" split you approved, so it is by design. | ch20 | None, but ch20's first lines could say "RAG half is in book 4". |
| 6 | **Two chapters are very long.** Ch20 is about 83 KB (it now holds the module-by-module Meridian digests) and ch16 about 56 KB; the next longest is 36 KB. | ch20, ch16 | Split ch20 into "the tour" and "slide-by-slide detail", or collapse the digests. Needs your decision on where the detail goes. |
| 7 | **Streaming is split.** Model streaming is in ch3, agent streaming in ch10A (docs only, labelled "10A", between HITL and MCP). | ch3, ch10A | Fine; maybe number it 11 and shift the rest, or leave as is. |
| 8 | **MCP is seven chapters (ch11–17)** and ch17 (the July 2026 spec change) comes after chapters that teach the older design. That is the right order for learning, but ch11–16 should say early that ch17 changes some details. | ch11, ch17 | Add a one-line note at the top of ch11. |

## Checked and fine

- Ch3 (model) before ch4 (structured output) before ch5 (tools): each builds on the last.
- Ch7 uses a checkpointer introduced in ch6, and says HITL is deepened in ch10.
- Ch18 (MCP inside LangChain) comes after the MCP part and after HITL and elicitation, which it uses.
- Ch19 (multi-agent) comes after tools, middleware and runtime, which the patterns need.
- Part labels in the home page match the actual chapters.

## If you want the smallest set of changes

Findings 2, 3 and 8 are one-line pointers each. Findings 1 and 6 are the only ones that would move content.
