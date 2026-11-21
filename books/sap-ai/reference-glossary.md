# Reference: Glossary

*The acronyms and terms used in this book, in one line each, with the chapter that explains them.*

> [!NOTE]
> **📍 At a glance**
> - **Use it for:** looking up a term while you read; the chapter number links to the full explanation
> - **What it is:** a summary of what the book already says; no new sources
> - **Level:** reference
> - **Last checked:** 21 Nov 2026

## 59.1 Acronyms

| Term | Meaning | Chapter |
|---|---|---|
| **C_JSD** | SAP certification for developing with Joule Studio | [2](sap-ai-careers-certifications.md) |
| **HITL / HOTL / HIC** | Human in the loop, on the loop, in command: three levels of human oversight of AI | [6](responsible-ai-ethics-governance.md) |
| **JWT** | JSON Web Token: the signed token a service returns after sign-in; some APIs need a user-specific one | [10](tutorial-translation-hub-python.md) |
| **LLM** | Large language model | [4](llm-prompt-to-answer.md) |
| **RAG** | Retrieval-augmented generation: look up documents, then let the model answer from them | [5](prompt-engineering.md), [SAP Joule 1](../sap-joule/joule-for-consultants.md) |

## 59.2 Terms

| Term | Meaning | Chapter |
|---|---|---|
| **AI Core** | SAP's BTP service for running AI workloads; its generative AI hub serves LLMs through deployments | [7](sap-ai-core-launchpad.md), [8](tutorial-genai-hub-python.md) |
| **AI Launchpad** | The web UI for SAP AI Core: chat, prompt editor, grounding management, orchestration | [7](sap-ai-core-launchpad.md), [11](tutorial-rag-grounding-genai-hub.md) |
| **Deployment (AI Core)** | One running instance of a model in SAP AI Core, with its own ID | [8](tutorial-genai-hub-python.md) |
| **Document AI** | SAP service that extracts fields from business documents; its API was called Document Information Extraction | [9](tutorial-document-ai-python.md) |
| **Generative AI hub** | The part of SAP AI Core that gives access to LLMs from several providers with one service key (extended plan) | [7](sap-ai-core-launchpad.md), [8](tutorial-genai-hub-python.md) |
| **Orchestration (generative AI hub)** | One API call that runs grounding, templating, masking, filtering and the model as a pipeline | [11](tutorial-rag-grounding-genai-hub.md) |
| **Resource group** | A partition of an SAP AI Core tenant that holds deployments; the course uses `default` | [7](sap-ai-core-launchpad.md), [8](tutorial-genai-hub-python.md) |
| **Token (LLM)** | The piece of text a language model reads and writes; also the unit of cost | [4](llm-prompt-to-answer.md) |
| **Translation Hub** | SAP service for translating application texts and documents by API | [10](tutorial-translation-hub-python.md) |
| **Vector engine** | SAP HANA Cloud's store for embeddings; finds the chunks nearest to a question | [11](tutorial-rag-grounding-genai-hub.md) |
| **Prompt template** | A saved, versioned prompt (system, user, assistant parts and variables) in AI Launchpad's prompt management | [7](sap-ai-core-launchpad.md) |
| **Quota (rate limit)** | The most requests a resource group may send to a model per minute or hour; set and approved in AI Launchpad administration | [7](sap-ai-core-launchpad.md) |
| **Workspace (AI Launchpad)** | One connection from AI Launchpad to one SAP AI Core instance, made by uploading its service key | [7](sap-ai-core-launchpad.md) |

## How this page was built

- Compiled on 21 Nov 2026 from the book's chapters: every term with two or more uses was considered, and meaningful ones were kept.
- No new sources; definitions follow the linked chapters.
- Split on 21 Nov 2026 from the single glossary/facts page of the former combined course book: this page keeps the rows whose main chapter is in this book. Links to the other SAP books name the book.

## Sources

- The chapters linked in each row.

Previous: [Tutorial: Setup SAP AI Core Basic Trial](tutorial-teched2026-aicore-basic-trial.md) · Next: [Reference: Current facts to re-check](reference-current-facts.md)
