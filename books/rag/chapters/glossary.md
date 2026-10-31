# Glossary
> lead: The RAG terms from this book in one line each, grouped by theme, with the chapter where each is explained. Use the search box to jump to a term.
meta: About 50 terms | Links go to the chapter

## The idea

| Term | One line | Chapter |
| --- | --- | --- |
| **RAG** | Look up relevant text first, then answer from it: an open-book exam | [1](#rag-r1) |
| **Closed book vs open book** | A plain model answers from memory; RAG hands it the pages first | [1](#rag-r1) |
| **Indexing (once)** | Read, chunk, embed and store the documents | [1](#rag-r1) |
| **Query time (every question)** | Embed the question, find the closest chunks, build the prompt, answer | [1](#rag-r1) |
| **Hallucination guard** | The prompt rule "if you do not know based on the context, say so" | [3](#rag-r3) |
| **The eight parts** | Parse, chunk, embed, store, retrieve, rerank, generate, evaluate | [1](#rag-r1) |
| **Do you even need RAG?** | If the whole knowledge base fits in the context window, you can paste it in instead | [1](#rag-r1) |
| **Before / during / after / beyond** | Where to improve basic RAG: change the question, the search, the results, or go past it | [1](#rag-r1) |

## Ingestion and storage

| Term | One line | Chapter |
| --- | --- | --- |
| **Chunk** | A piece of a document sized for search (about 1,000 characters in Meridian) | [2](#rag-r2) |
| **Chunk overlap** | Neighbouring chunks share text (100 characters) so sentences are not cut off | [2](#rag-r2) |
| **`RecursiveCharacterTextSplitter`** | The splitter that cuts text at natural breaks to a size limit | [2](#rag-r2) |
| **Embedding** | A list of numbers for meaning (768 in this project) | [2](#rag-r2) |
| **Dimensions** | Length of the number list; the embedding model must match the index | [2](#rag-r2), [5](#rag-r5) |
| **Same model rule** | One embedding model must index and search; numbers from two models cannot be compared | [1](#rag-r1), [2](#rag-r2) |
| **Vector store / vector database** | Stores vectors with text and source and answers "what is nearest" | [1](#rag-r1), [2](#rag-r2) |
| **Chroma** | The local vector store, a folder on disk (`.meridian/chroma`) | [2](#rag-r2) |
| **Vertex AI Vector Search** | The managed cloud vector store; bills by the hour while deployed | [2](#rag-r2), [5](#rag-r5) |
| **Chunk id (`sha1`)** | A hash of source, page and position, so indexing a file twice replaces, not duplicates | [2](#rag-r2) |
| **Keep the originals** | Store the source files; a new model, chunk size or bug fix means re-indexing | [2](#rag-r2) |
| **`APP_MODE`** | The one setting that switches local and cloud storage behind the same code | [2](#rag-r2) |
| **Strategy pattern** | Same interface, swappable implementation (local or cloud store) | [2](#rag-r2) |
| **Metadata `source`** | Which file a chunk came from, so an answer can be traced | [2](#rag-r2) |

## Retrieval and answering

| Term | One line | Chapter |
| --- | --- | --- |
| **Retriever** | Anything that turns a question into a list of documents | [3](#rag-r3) |
| **Similarity search** | The `k` chunks closest in meaning (default 3) | [3](#rag-r3) |
| **Multi-query** | The model rewrites the question several ways and merges the results | [3](#rag-r3) |
| **Contextual compression** | Fetch 10 chunks, then the model trims each to the relevant part | [3](#rag-r3) |
| **MMR** | Maximal marginal relevance: relevant and different, so no near-duplicates | [3](#rag-r3), [4](#rag-r4) |
| **LCEL** | LangChain's pipe syntax for chains: each step's output feeds the next, joined with the pipe symbol | [3](#rag-r3) |
| **`RunnablePassthrough`** | Passes the question through unchanged alongside the retrieved context | [3](#rag-r3) |
| **`langchain-classic`** | The package holding the older chains and retrievers after LangChain v1 | [3](#rag-r3) |
| **Expected answer first** | Write the answer you expect before testing; otherwise it is only a demo | [3](#rag-r3), [5](#rag-r5) |

## Advanced variants

| Term | One line | Chapter |
| --- | --- | --- |
| **HyDE** | Search with an imagined answer instead of the question | [4](#rag-r4) |
| **Hybrid search** | Keyword ranking plus meaning ranking, merged | [4](#rag-r4) |
| **Reciprocal rank fusion** | Score each item by the sum of `1/(60 + position)` across rankings | [4](#rag-r4) |
| **Reranking** | Over-fetch, then have the model score each candidate and keep the best | [4](#rag-r4) |
| **Parent pages** | Search small pieces but hand over the whole page | [4](#rag-r4) |
| **Decomposition** | Split a many-part question into simple ones, search each, merge | [4](#rag-r4) |
| **Follow-up rewrite** | Turn "And for moderate risk?" into a question that stands alone | [4](#rag-r4) |
| **Contextual retrieval** | The model writes a short note onto each chunk before embedding it | [4](#rag-r4) |
| **BM25** | A standard keyword-ranking method; the lab's keyword side is a simpler home-made version | [4](#rag-r4) |

## Cost and operations

| Term | One line | Chapter |
| --- | --- | --- |
| **Deployed index** | An index running on machines at an endpoint; billed by the hour even when idle | [5](#rag-r5) |
| **Budget alert** | Emails you as spending grows; it never stops anything | [5](#rag-r5) |
| **Searchable delay** | New data takes about a minute to become searchable | [5](#rag-r5) |
| **Key-free tests** | Tests that replace the model with a stand-in, so they run without keys or accounts | [5](#rag-r5) |
