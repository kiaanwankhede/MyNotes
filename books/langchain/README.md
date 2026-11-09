# Langchain

Notes built from the Live Class 2026 course and other sources. Chapters are in study order.

## Study path for a Gen AI developer

| Goal | Read | Then build |
|---|---|---|
| Ship a first tool-calling agent | Ch 1 → 3 → 5 | a two-tool agent with streaming and a `recursion_limit` |
| Reliable, typed outputs | Ch 4 | an extraction agent with a `Literal` + optional-field schema |
| Memory that survives | Ch 6 | per-user store + per-conversation `thread_id` |
| Control the loop | Ch 7 → 8 → 9 → 10 | summarisation, retries/fallback, PII masking, one custom middleware |
| Safe actions | Ch 11 | human approval on every write/send/pay tool |
| External tools | Ch 12 | connect one MCP server; handle auth per user |
| Several agents | Ch 13 → 14 | supervisor + 2 subagents; then compare with a router |
| Prove it works | Ch 15 | a 20-case eval set run before every prompt change |
| Interview prep | Ch 17, plus each chapter's Interview corner and Cheat sheet | |

- **Fast revision:** read only the 🏭 *In production* boxes, the Interview corners and the Cheat sheets
- Sections marked *added by Claude* are industry practice beyond the class; the ✅ marks show what was run

## Live Colab notebooks

The notebooks the mentor shared and ran live, by class. Links are from the course repo's `COLAB_NOTEBOOKS.md` and were **not opened**. If one asks you to sign in, tell the mentor.

| Class | Notebook | Covers | Chapter |
|---|---|---|---|
| 07–08 | [Live session notebook](https://colab.research.google.com/drive/16yT0w6ha6eWK2dOHsOrj7qW8oZiIvGxc?usp=sharing) | Models, streaming, tools, structured output, messages | Ch 3, 4, 5 |
| 07–08 | [Revision Notebook — Parts 1-4](https://colab.research.google.com/drive/1v15iHbt8lsIRsPYw0UgSOCogaenBo4_W?usp=sharing) | Consolidated revision: Landscape → Environment Setup → Models & Messag | Ch 3, 4, 5 |
| 09 | [CineBot — Movie Ticket Booking Assistant](https://colab.research.google.com/drive/1BfYVnjabM0BYL0Wr6zqabdFCn6-Waz-T?usp=sharing) | Structured output, Union multi-intent, error recovery | Ch 4 |
| 10 | [Student Reference — Structured Output and Tools](https://colab.research.google.com/drive/1KlOpWf5-KIwsA0UaqWH98eISyZZQphXD?usp=sharing) | Chapter-by-chapter reference/Assignment & Questions/Student_Reference_ | Ch 5 |
| 11–12 | [Middleware notebook](https://colab.research.google.com/drive/1Qt9uU2HhDvtFTWwbbFBYxK86jJypv1w_?usp=sharing) | All nine built-in middlewares, worked live | Ch 7, 8, 9 |
| 14 | [Custom middleware notebook](https://colab.research.google.com/drive/1CpnGhWhGG4r8NCIoh0WEmcPEVb6KJ2TH?usp=sharing) | Shell tools, the six middleware hooks, decorator vs. class middleware | Ch 10 |
| 15 | [Runtime & HITL notebook](https://colab.research.google.com/drive/1dFuLlELzyS2NDIBgeVOowrqGJGFPERSL?usp=sharing) | Runtime's five components, ToolRuntime, Human-in-the-Loop in depth | Ch 11 |

- Classes without a row had no separate live Colab, or the code in the repo is the notebook
