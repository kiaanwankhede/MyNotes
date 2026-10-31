# RAG
> lead: How to make a model answer from your own documents: the two stages, ingestion, retrieval, advanced variants, and the cost traps, taught through the Meridian project.
meta: Book 4 of the library | 5 chapters | Read after Agentic AI with LangChain

## What this book covers

| Chapter | You will be able to |
| --- | --- |
| 1. RAG explained | Draw the two stages and name the eight parts of a RAG system |
| 2. Embeddings, storage, ingestion | Explain chunking, overlap, embeddings and the local versus cloud store |
| 3. Retrieval and the answer chain | Write the chain as one pipeline and compare three retrievers |
| 4. Advanced RAG | Choose between MMR, HyDE, hybrid, rerank, parent pages and decomposition |
| 5. Costs, errors, tests | Avoid the surprise bill and debug the common errors |

:::key Prerequisites
**Foundations** chapter 2 (embeddings and the context window) and **Agentic AI with LangChain** chapters 1 to 5 (chains, tools, structured output). The agent and deployment half of Meridian is the last chapter of the LangChain book.
:::

:::beyond Where this came from
The content comes from the Meridian course slides and the Meridian learner repo. No class write-up exists for it. When the course's own RAG classes arrive, this book is where they will be added.
:::

## Project idea: guideline Q&A with RAG

**Goal:** upload a handful of public guideline PDFs and answer questions using **only** their content.

- Chunk with overlap, embed, store, retrieve the top three, answer from them.
- The prompt must say "I do not know" when the answer is not in the documents. Test it with a question that is not covered.
- **Stretch:** compare `similarity`, `multiquery` and `contextual` retrieval on the same ten questions and record which wins.
- **Interview story:** how you stopped the model making things up, and what the retrieval comparison showed.

:::note Real data
Never use real patient or personal data with any model or tool. Use synthetic or fully de-identified examples.
:::
