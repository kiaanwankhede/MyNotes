# Agentic AI 3.0 Study Notes
> lead: A chapter-by-chapter reader built from the live class code, notebooks, PDFs and class summaries, written so you can learn each topic and defend it in an interview.
meta: Draft for review | Primer and Chapter 1 ready

## How to read this book

:::key Read in order
Each chapter builds on the one before it. Chapter 1 explains `create_agent()`, Chapter 6 adds memory and middleware, and Chapter 10 adds human approval. If you skip ahead, the later chapters will assume terms you have not seen.
:::

Every chapter has the same shape, so you always know where to look:

| Section | What it gives you |
| --- | --- |
| **Why it matters** | The problem the topic solves, in a few lines |
| **Core ideas** | The concepts, with diagrams and analogies |
| **Code** | The key patterns, trimmed and explained line by line |
| **Under the hood** | What actually happens, so you can answer follow-up questions |
| **Common mistakes** | Mistake, symptom and fix in one table |
| **Hands-on lab** | A small exercise to make the idea stick |
| **Interview corner** | A 30-second pitch, then questions with model answers (tap to reveal), including tricky ones |
| **Quick revision** | A tickable checklist; your ticks are remembered on this device |
| **Sources** | Links to the exact class notes and code files in the course repository |

:::tip How to use the interview corner
Cover the answer, say yours out loud, then open it and compare. Aim to match the structure of the model answer, not the exact words.
:::

:::beyond How to read the labels
A box marked **Beyond the class** means the content comes from a different class than the chapter's own, or is my explanation added to fill a gap. Everything else comes from the class itself. Boxes marked **Repo note** point out problems or details in the course code.
:::

:::key Quiz me
The **Quiz me** page in the sidebar pulls every interview question from the chapters that are written. It shows one at a time with the answer hidden. Mark the ones you knew and they stop appearing.
:::

## The course at a glance

```mermaid
flowchart LR
    A["Part A<br/>Primer<br/>model, tools, loop"] --> B["Part B<br/>LangChain core<br/>models, output, tools"]
    B --> C["Part C<br/>Agents and middleware<br/>memory, guardrails"]
    C --> D["Part D<br/>Runtime<br/>state, human approval"]
    D --> E["Part E<br/>MCP<br/>protocol to deployment"]
    E --> F["Part F<br/>Advanced<br/>multi-agent, full project"]
```

| Part | Classes | You will be able to |
| --- | --- | --- |
| A. Primer | 01 to 05 | Explain what an agent is and write the tool-calling loop from memory |
| B. LangChain core | 06 to 10 | Build agents with `create_agent`, control models, get structured output, write good tools |
| C. Agents and middleware | 11 to 14 | Add memory, guardrails, retries, todo lists and shell tools; write custom middleware |
| D. Runtime | 15 | Use runtime context and state, and pause for human approval |
| E. MCP | 16 to 22 | Explain why MCP exists, its lifecycle and primitives, then build, deploy and compare versions |
| F. Advanced | Weekends 13 to 14 | Use MCP inside LangChain, choose a multi-agent pattern, tour a full-stack project |

## What is in this draft

:::note Review status
This draft contains the **Primer** and **Chapter 1** only. Other chapters appear greyed out in the sidebar and will be added once the format is approved. Material from the Craft notes page will be added in the last section when the export is shared.
:::

:::repo Gaps in the source repository
Classes 13 to 15 have written summaries but no shared code. There is no Weekend 12 folder. The Oct 10 to 11 folder contains only two links, so there is no class content for that weekend yet.
:::
