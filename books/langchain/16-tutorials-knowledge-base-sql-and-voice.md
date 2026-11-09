# Chapter 16: Build-along tutorials: knowledge base, SQL agent, voice agent

> [!NOTE]
> **📍 At a glance**
> - **You will build:** a semantic search engine, a SQL agent with approval, and a voice pipeline
> - **Level:** intermediate to advanced · **Time:** about 20 minutes
> - **Builds on:** [Chapter 5](05-tools.md) (tools), [Chapter 6](06-agents-and-memory.md) (agents, streaming), [Chapter 11](11-runtime-and-human-in-the-loop.md) (human-in-the-loop).

**After this chapter you can:**

- Build a semantic search over documents: `Document`, splitter, embeddings, vector store, retriever
- Build a SQL agent with three tools, a safe prompt and human approval before each query
- Explain the voice-agent "sandwich" and chain its three stages as async generators
- Read `stream_events(version="v3")` with `interleave`, `interrupted` and `interrupts`

## 16.1 Knowledge base: semantic search over a PDF

```mermaid
flowchart LR
    subgraph Index["Index once"]
        PDF[PDF] --> L[Load pages] --> SP[Split chunks] --> EM[Embed] --> VS[(Vector store)]
    end
    subgraph Query["Every question"]
        Q([Question]) --> QE[Embed query] --> VS
        VS --> K[Top-k chunks] --> LLM[Model answers with context]
    end
```

- *Source: LangChain docs, `knowledge-base.mdx`.*
- The pipeline: **load, split, embed, store, search, wrap as retriever**
- `Document` has `page_content`, `metadata` (a dict) and an optional `id`
```python
from langchain_core.documents import Document
Document(page_content="Cats are independent.", metadata={"source": "pets"})
```
- **Load a PDF** page by page (the page's own helper uses `pypdf`; `PyPDFLoader` is the packaged option):
```python
import pypdf
def load_pdf_pages(fp):
    return [Document(page_content=p.extract_text() or "", metadata={"source": fp, "page": i})
            for i, p in enumerate(pypdf.PdfReader(fp).pages)]
```
- **Split** so a passage is not drowned by its page:
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
splits = splitter.split_documents(docs)   # each chunk keeps a start_index
```
- **Embed:** `embeddings.embed_query(text)` gives a vector; every vector has the same length
- **Store and search:**
```python
ids = vector_store.add_documents(splits)
vector_store.similarity_search("When was Nike incorporated?")          # list of Documents
vector_store.similarity_search_with_score("...")                       # (Document, score)
vector_store.similarity_search_by_vector(embeddings.embed_query("..."))
await vector_store.asimilarity_search("...")                           # async
```
  - Scores differ by provider. In the page's example the score is a distance, so lower means closer
  - MMR search balances similarity with variety
- **Retrievers are Runnables, vector stores are not.** Get one with `vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 1})`, then `.invoke`, `.batch`
  - `search_type`: `"similarity"` (default), `"mmr"`, `"similarity_score_threshold"`
  - Or wrap any function with `@chain` to make a retriever
- ✅ *Verified (details in "How this chapter was checked").*

> [!IMPORTANT]
> **🏭 In production**
> - Retrieval quality decides answer quality: build a small set of real questions with known answer passages and measure hit rate before tuning prompts
> - Hybrid search (keywords + vectors) and a re-ranker often beat a bigger model
> - Store source and page metadata so every answer can cite where it came from
> - *Added by Claude.*

## 16.2 SQL agent

- *Source: LangChain docs, `sql-agent.mdx` and its code snippets (`sql-agent-*.mdx`).*
- The agent: list tables, pick relevant ones, read their schemas, write a query, check it, run it, fix errors, answer
- **Warning on the page:** you run model-written SQL. Use read-only credentials and narrow permissions. The tools are demo wrappers, not production safe
- **Three tools**, built with `@tool` on `sqlite3`:
  - `sql_db_list_tables()`: names of tables (skips `sqlite_` internals)
  - `sql_db_schema(table_names)`: `CREATE TABLE` text plus 3 sample rows per table; unknown names return an error string
  - `sql_db_query(query)`: runs SQL, returns rows as text, **errors as text** so the model can retry
- **System prompt** (key lines): create a correct `{dialect}` query; limit to `{top_k}` rows unless told otherwise; never select all columns; **double check before running**; **no INSERT, UPDATE, DELETE, DROP**; always look at the tables first
```python
agent = create_agent(model, tools, system_prompt=system_prompt)
```
- **Human approval before each query:**
```python
agent = create_agent(
    model, tools, system_prompt=system_prompt,
    middleware=[HumanInTheLoopMiddleware(
        interrupt_on={"sql_db_query": True},
        description_prefix="Tool execution pending approval")],
    checkpointer=InMemorySaver(),
)
```
- Run with `agent.stream_events(input, config, version="v3")`, read with `stream.interleave("messages", "tool_calls")`
  - A paused run has `stream.interrupted == True` and `stream.interrupts[0].value["action_requests"]` (each has a `description`)
  - Resume with `Command(resume={"decisions": [{"type": "approve"}]})` on the same `thread_id`
- ✅ *Verified (details in "How this chapter was checked").*

> [!IMPORTANT]
> **🏭 In production**
> - Connect the SQL agent with a read-only database user and a row limit in code; prompts are not permissions
> - Log every generated query with the user and question for audit
> - *Added by Claude.*

## 16.3 Voice agent: the sandwich

- *Source: LangChain docs, `voice-agent.mdx`.*
- Every voice agent must **listen, think, speak**
- **Sandwich (STT, agent, TTS):** three parts you can swap
  - Good: control of each part, newest text models, clear boundaries
  - Bad: more services to run; speech to text loses tone and emotion
- **Speech to speech:** one multimodal model takes audio and returns audio
  - Good: simpler, often lower delay, keeps tone
  - Bad: fewer models, more lock-in, less control
- The page builds the sandwich: browser microphone over a **WebSocket**, then Python: AssemblyAI (speech to text), a LangChain agent, Cartesia (text to speech)
- Each stage is an **async generator** that passes upstream events through and adds its own, so work overlaps
- **Speech to text events:** `stt_chunk` (partial) and `stt_output` (final, triggers the agent). Audio is sent while transcripts arrive (producer-consumer)
- **Agent stage:** on `stt_output`, stream the reply with `astream_events(..., version="v3")` and yield each token from `stream.messages`
  - One `thread_id` per call, plus a checkpointer, gives memory across turns
  - The prompt says: no emojis, special characters or markdown, because a speech engine reads the text
- **Text to speech stage:** merge two concurrent streams (events going to the TTS service, audio coming back)
- **Chain them:**
```python
pipeline = (RunnableGenerator(stt_stream)
            | RunnableGenerator(agent_stream)
            | RunnableGenerator(tts_stream))
async for event in pipeline.atransform(audio_stream): ...
```
- ✅ *Verified (details in "How this chapter was checked").*

## 16.4 Questions from the class

- None in the class material for this chapter. It comes from the LangChain docs only

## 16.5 Interview corner

**What interviewers listen for:** you can draw the **index vs query** pipeline, you know retrieval quality must be measured, and you lock down the database rather than trusting the prompt.

### 🟢 Basic

<details class="qa"><summary>1. What is the difference between a vector store and a retriever?</summary>

- A vector store adds and searches documents; a retriever is a Runnable that takes a query and returns documents
- *Stronger answer:* a retriever can wrap anything, even an API; `as_retriever` wraps a vector store

</details>

<details class="qa"><summary>2. Why split documents before indexing?</summary>

- A page is too coarse; small chunks with overlap keep a passage from being diluted by its surroundings
- *Stronger answer:* `add_start_index` keeps the position so you can find the source text

</details>

### 🟡 Intermediate

<details class="qa"><summary>3. How do you make a SQL agent safer?</summary>

- Read-only credentials, a prompt that forbids writes, a check before running, and human approval on `sql_db_query`
- *Stronger answer:* the prompt is not enforcement; the database permission is

</details>

<details class="qa"><summary>4. Why return SQL errors as text?</summary>

- The model reads the error and rewrites the query, which is the repair loop

</details>

### 🔴 Senior

<details class="qa"><summary>5. Sandwich or speech to speech?</summary>

- Sandwich for control and newest models; speech to speech for simplicity and tone, at the cost of lock-in

</details>

<details class="qa"><summary>6. Your RAG answers are wrong although the documents contain the answer. Where do you look?</summary>

- Retrieval first: is the right chunk in the top-k? Check chunk size, overlap, embeddings and filters
- *Stronger answer:* measure hit rate on a labelled set, add hybrid search or re-ranking, then fix the prompt; only then try a bigger model

</details>

> [!TIP]
> **🧩 Design question to practise:** *"Build a policy Q&A bot over 2,000 internal PDFs that must cite sources."* Cover loading, chunking, metadata, the vector store, evaluation of retrieval, and keeping the index fresh.

## 16.6 Added by Claude, not from the sources

- **Limit rows in code, not only in the prompt.** Add `LIMIT` or a row cap inside `sql_db_query`
- **Open the database read-only.** `sqlite3.connect("file:Chinook.db?mode=ro", uri=True)` stops writes however the model behaves
- **Do not judge retrieval with fake embeddings.** Use a real model and a few known question and answer pairs
- **Keep chunk size a tested choice.** Try two sizes on your own questions
- **A voice reply should be short.** Long text means long audio; say so in the prompt

## Cheat sheet

```python
splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200,
                                        add_start_index=True).split_documents(docs)
store = InMemoryVectorStore(embeddings); store.add_documents(splits)
retriever = store.as_retriever(search_type="mmr", search_kwargs={"k": 4})
retriever.invoke("question")
```

## Recap

- Semantic search = split, embed, store, search; the retriever is the Runnable
- SQL agent = three tools plus a strict prompt plus approval on the query tool
- Voice sandwich = speech to text, agent, text to speech, each an async generator
- `stream_events(version="v3")`: `interleave`, `interrupted`, `interrupts`
- Fake components prove wiring, not quality

## Practice

1. Build a small store with a fake embedding. Run all four search calls and the retriever
2. Set `score_threshold` to 5 and read the error. Fix it
3. Make a two-table SQLite file, run the three tools, then add approval and approve and reject a query
4. Chain two `RunnableGenerator`s of your own and feed them a few numbers
5. Make the SQL tool read-only with a `mode=ro` connection and try an `INSERT`

## How this chapter was checked

- Run offline: the knowledge-base pipeline with fake embeddings, the docs' SQL tools on my own SQLite file with a scripted agent and approval, the voice agent stage with a fake transcript stream, and `RunnableGenerator` chaining
- **Not run:** real embeddings, the Nike PDF, the Chinook database, any real model, AssemblyAI, Cartesia, WebSockets, Studio
- The `mode=ro` tip in 16.6 was run: a read worked and an `INSERT` raised `OperationalError`
- **Details by section** (moved here from the ✅ markers):
  - *16.1 Knowledge base: semantic search over a PDF:* Checked (langchain-core 1.7.3, `DeterministicFakeEmbedding`, `InMemoryVectorStore`):
    - A blank one-page PDF loaded with the helper (1 page); a repeated text split into 9 chunks with `start_index` in the metadata
    - `similarity_search` returned 4 Documents by default; `similarity_search_with_score` gave a float; search by vector and async search worked
    - `@chain` and `as_retriever(...)` both batched to one result each; the store has no `invoke`, the retriever has
    - `"mmr"` worked; `similarity_score_threshold` needs `score_threshold` as a float **between 0 and 1** or it raises a `ValidationError`
    - **Fake embeddings test the plumbing only, not relevance.** The Nike PDF examples were not run (no download)
  - *16.2 SQL agent:* Checked (scripted model, own 2-table SQLite file, the docs' tool code run as written):
    - List tables, schema with an unknown name (error text), a query, and a bad column (`Error: no such column: bad`) all behaved as described
    - Without approval the run ended `human, ai, tool, ai, tool, ai`; with approval it paused at `sql_db_query` after the list-tables call (`interrupted` was `True`), the description began `Tool execution pending approval`, and after resume `sql_db_query` ran and `interrupted` was `False`
    - **Docs mismatch:** the sample output lists a fourth tool, `sql_db_query_checker`, but the page's code defines only three tools
    - Not run: the Chinook download (blocked), a real model, Studio
  - *16.3 Voice agent: the sandwich:* Checked (scripted model, fake speech-to-text stream, no audio):
    - The agent stage turned two `stt_output` events into `agent_chunk` events, and the model saw 2, 4, 6 messages over the run, so memory held across turns
    - `RunnableGenerator(a) | RunnableGenerator(b)` with `atransform` chained two async generators correctly
    - Not run: AssemblyAI, Cartesia, WebSocket, any real audio, the reference app in `voice-sandwich-demo`
- The 2026 review added the diagrams, 🏭 In production boxes, graded interview layout, extra senior and design questions and the cheat sheet. These are Added by Claude: standard engineering practice. Cheat-sheet APIs were checked against the installed `langchain` 1.4.7 signatures
- **Cheat sheet:** ran the splitter, `InMemoryVectorStore` with a fake embedding and an MMR retriever; `start_index` metadata was present; real embeddings were not used. Ran on `langchain` 1.4.7 with a scripted fake chat model (no API keys, no network), so no real model call was made.

## Sources and further reading

- LangChain docs, `src/oss/langchain/knowledge-base.mdx`, `sql-agent.mdx`, `voice-agent.mdx` and `src/snippets/code-samples/sql-agent-*.mdx` (github.com/langchain-ai/docs, MIT, commit 433a92c)
- Reference app: github.com/langchain-ai/voice-sandwich-demo

Previous: [Chapter 15, Testing agents and tracing](15-testing-agents-and-tracing.md) · Next: [Chapter 17, Interview questions](17-interview-questions.md)
