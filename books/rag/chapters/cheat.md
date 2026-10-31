# Cheat sheet
> lead: The RAG pipeline, the retrieval choices and the cost traps on one page. Every item links back to its chapter.
meta: Quick reference | Code is condensed. See the chapters for the full versions

## The pipeline ([Ch 1](#rag-r1), [Ch 2](#rag-r2), [Ch 3](#rag-r3))

```text
Once:      PDF -> pages -> chunks (~1000 chars, 100 overlap) -> embeddings -> vector store
Each ask:  question -> SAME embedding model -> nearest chunks -> prompt -> LLM -> answer
```

```python
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | ANSWER_PROMPT | llm | StrOutputParser()
)
answer = chain.invoke("When do we pay servo motor suppliers?")
```

The prompt must say: use the context, and **if you do not know based on the context, say so**.

## Which retrieval? ([Ch 3](#rag-r3), [Ch 4](#rag-r4))

| Choice | Extra cost | Typical reason |
| --- | --- | --- |
| Similarity (k=3) | none | start here |
| Multi-query | 1 model call | the user's words differ from the document's |
| Contextual compression | 1 call + 1 per chunk | prompts are too long or noisy |
| MMR | none | results are near-duplicates |
| HyDE | 1 call | the question looks nothing like the answer |
| Hybrid (RRF) | none extra | exact terms matter (names, codes) |
| Rerank | 1 call | the right chunk is found but not first |
| Parent pages | bigger prompt | a chunk needs its surrounding page |
| Decomposition | 1 call | the question has several parts |
| Follow-up rewrite | 1 call | chat questions like "and for moderate risk?" |

The last column is my short summary of each idea, not a rule from the slides. Reciprocal rank fusion: `score = sum over rankings of 1 / (60 + position)`. No variant wins everywhere; add one at a time and **measure on your own questions with known answers**.

## Rules that save hours

- **One embedding model** must index and search; dimensions must match the index (768 here). Switching models means re-indexing, so **keep the originals**.
- Chunk ids from a hash of source, page and position make re-indexing replace, not duplicate.
- Local mode uses Chroma (a folder); cloud mode uses Vertex AI Vector Search. One setting, `APP_MODE`, switches them; the two stores are separate, so re-upload after switching.
- New data takes about a minute to become searchable.
- Write the **expected answer first**; a test without one is a demo.
- Tests replace the model with a stand-in, so they need no key.

## Costs ([Ch 5](#rag-r5))

| If this exists | It costs |
| --- | --- |
| An index deployed to an endpoint | **By the hour, even with no users**: the main bill |
| A Cloud Run service | Only while it handles requests |
| Buckets, images, secrets | Small storage charges |
| Only a project with billing linked | Nothing |

A budget alert **only emails**. Switch things off: undeploy the index, then delete the endpoint and the index. For small data, Postgres with pgvector or local Chroma is cheaper.

## Errors ([Ch 5](#rag-r5))

| You see | Do this |
| --- | --- |
| Nothing found right after upload | Wait about a minute |
| `DefaultCredentialsError` | `gcloud auth application-default login` |
| 503 listing missing settings | `APP_MODE=cloud` with an empty index id: fill the settings |
| Errors after switching models | Dimensions must match the index (768) |
| "Index ... is not deployed to endpoint" | Check `deployedIndexes` on the endpoint before uploading |
