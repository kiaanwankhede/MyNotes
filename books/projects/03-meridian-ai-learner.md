# Chapter 3: Meridian AI learner

**After this chapter you can:**

- Explain what Meridian does and name every technology in it
- Trace a document question and a purchase audit through the system
- Say why the code is split into packages, and what depends on what
- Run the audit locally and check the document answers against the sample PDFs
- Deploy it to Google Cloud, know what costs money, and switch it off
- Answer interview questions on RAG, agents and deployment

**Builds on:** [LangChain Ch4](../langchain/04-structured-output.md) (structured output), [LangChain Ch5](../langchain/05-tools.md) (tools), [LangChain Ch6](../langchain/06-agents-and-memory.md) (agents). Pydantic is used for request shapes.

> **Status of these notes.** Built from the README, `DEPLOY.md`, the four sample PDFs and, for settings, logging and document Q&A, the backend code (3.4, 3.5, 3.6, 3.8), which was run with stand-ins for Google's services. The **web code** is not read yet. The **frontend is left out** at your request. **Nothing was deployed.**

## 3.1 What it is

- A small web app that does **two jobs** with AI:
  - **Document Q&A (RAG):** upload PDFs, ask in plain English, answer comes only from the documents
  - **Purchase audit:** paste a purchase request, three specialist agents review it, a "CFO" step writes a memo
- Built to **learn from**. *Aldermoor Industries* and all sample data are **fictional**
- The README says the audit checks come from the model's general knowledge. Only the exchange-rate check uses live data
  - So this is a demo of the *build*, **not** a compliance tool

## 3.2 The technologies

| Technology | Role | Course link |
|---|---|---|
| React + TypeScript | The web page | Frontend only |
| FastAPI | Receives requests, returns answers | Web layer |
| Pydantic | Checks request and reply shapes | Pydantic book |
| LangChain | Joins the AI steps | LangChain book |
| Gemini | Chat model that writes answers | LLM book |
| Embeddings | Text to numbers that capture meaning | 3.4 |
| Vertex AI Vector Search | Finds stored text closest in meaning | 3.4 |
| Cloud Storage | Keeps uploaded files | Cloud |
| Docker + Cloud Run | Packs the app, runs it on the internet | 3.9 |
| Secret Manager | Stores keys | 3.9 |
| GitHub Actions | Builds and deploys automatically | 3.9 |
| structlog | JSON log lines | 3.8 |

## 3.3 How it fits together

```
Browser (React) -> FastAPI backend
                    |- Document Q&A:  PDF -> pieces -> embeddings -> Vector Search -> Gemini
                    '- Purchase audit: Risk / Tax / Control agents (with tools) -> CFO memo
```

- **Frontend** talks to the backend through one file only (`src/lib/api.ts`)
- **Backend** is FastAPI. It has two feature areas: `rag/` and `agent/`
- Layers depend downward only: `api -> rag, agent -> config, logger`
  - The web layer does not know how AI works. The AI code does not know what a web address is

## 3.4 Document Q&A (RAG)

**RAG = retrieve first, then answer.** An open-book exam.

- **Ingest (once per file):**
  - Cut the PDF into small pieces
  - Turn each piece into an **embedding** (a list of numbers for its meaning)
  - Store them in Vector Search
- **Ask (every question):**
  1. Embed the question
  2. Vector Search returns the **three** closest pieces
  3. Gemini is told: answer using only these pieces
  4. The answer goes back to the page
- If the answer is not in the documents, it should say it does not know. **Test this** (3.7)
- Why not paste the whole PDF into the prompt? Cost, limits, and noise. Retrieval sends only what matters

**The code, file by file** (`backend/rag/`):

| File | Job |
|---|---|
| `data_ingestion.py` | PDF to pages to chunks to Vector Search |
| `embeddings.py` | Text to a 768-number vector (Vertex AI `text-embedding-005`) |
| `vector_store.py` | Connect to Vertex AI Vector Search |
| `llm.py` | The Gemini chat model, plus `extract_text` |
| `retrieval.py` | Find chunks, build the prompt, call the model |

**Ingest** (`data_ingestion.py`):

```python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100      # neighbouring chunks share up to 100 characters

def ingest_pdf(local_path, source):
    pages = PyPDFLoader(local_path).load()
    for page in pages: page.metadata["source"] = source
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(pages)
    get_vector_store().add_documents(chunks)       # embeds, then stores
    return {"pages": len(pages), "chunks": len(chunks)}
```

- `source` is written into every chunk so an answer can be traced to a file
- `ingest_data_from_gcs()` does the same for every `.pdf` under the bucket and prefix: download to a temp folder, ingest, delete the folder
- Two ways in: the upload endpoint calls `ingest_pdf`; the bulk route calls the GCS version

**Ask** (`retrieval.py`): three retrievers, chosen by `retriever_type`:

| Type | What it does | Model calls per question |
|---|---|---|
| `similarity` (default) | the 3 closest chunks | 1 (the answer) |
| `multiquery` | the model rewrites the question several ways, results merged | 2 |
| `contextual` | fetch 10 chunks, the model trims each to the relevant part | one **per chunk fetched**, plus the answer |

- An unknown type logs a warning and falls back to `similarity`
- The system prompt says: answer from the context, otherwise say you don't know, keep it concise
- It uses `create_stuff_documents_chain` and `create_retrieval_chain` from `langchain_classic`, the older chain helpers
- `get_llm()`, `get_embeddings()` and `get_vector_store()` are cached with `lru_cache` and connect on **first use**, so `/api/health` works before Google is configured

**Two ways to sign in to Google** (the file says this on purpose):

- Gemini chat: an **API key** (`GOOGLE_API_KEY`)
- Embeddings and Vector Search: **Google Cloud credentials**
- The index is built with **768 dimensions**. The same embedding model must be used to index and to search

## 3.5 Purchase audit (agents)

- Input: a request, for example 200 PLC controllers from Japan, 480,000 EUR
- Output is four texts: three specialist reports and one CFO memo. Wording changes; layout stays the same
- Takes up to a minute or more, because the model is called many times, **one after another**

**Shape** (`agent/agents.py`):

```
request -> Risk agent -> Tax agent -> Control agent -> CFO prompt -> memo
```

- The README diagram draws the three agents side by side. The code runs them **in sequence**: `run_audit` calls `risk`, then `tax`, then `control`. No agent sees another's report
- Each specialist is one line of LangChain: `create_agent(model=get_llm(), tools=[...], system_prompt=...)`
- The CFO step is **not an agent**. It is one plain model call with a prompt that has the three reports pasted in
- The result is a dict: `risk_result`, `tax_result`, `control_result`, `cfo_memo`

**The agents and their tools** (`agent/tools.py`, five tools):

| Agent | Tools | What the tool does |
|---|---|---|
| Risk & Compliance | `check_sanctions_list(vendor_name)` | asks the **model** to screen from its training knowledge; answers `RED ALERT:` or `CLEARED:` |
| | `get_vendor_credit_score(vendor_name)` | asks the model for JSON `{score, risk_level, reasoning}`; formats it |
| Tax & Treasury | `calculate_cross_border_tax(amount, origin, destination)` | asks the model for rates and amounts as JSON |
| | `validate_fx_hedge(currency_pair, rate_used)` | gets a live rate from the Frankfurter API, else asks the model; flags a gap above 5% |
| Financial Control | `categorize_expense(amount, item_description)` | asks the model for CapEx or OpEx, with flags |

- **Four of the five "tools" are the model answering a prompt.** Only the exchange rate comes from outside. The README says so ("done by the AI from its general knowledge")
- A tool's name, argument names and docstring become what the agent sees. The docstring is the description
- The agents have **no document search tool**. The audit never reads the PDFs from Document Q&A. The rules it applies (19% VAT, EUR 250,000 and 1,000,000 thresholds) are **typed into the prompts**

**The prompt recipe** (`agent/prompts.py`, stated in the file's comments):

1. **Role**: who the agent is, with the fictional company's background
2. **Responsibilities**: what it owns
3. **Decision framework**: which tool first, how to read each result, thresholds
4. **Output format**: an exact structure, so the next step can rely on it

- Risk: sanctions first ("a hard blocker"), then credit score. 75 or more is low risk, 50-74 needs a deposit or letter of credit, below 50 escalates to the Head of Procurement and CFO
- Tax: German VAT 19%, intra-EU B2B reverse charge 0%, third-country import VAT plus customs duty; then the FX check
- Control: CapEx versus OpEx per IFRS; EUR 250,000 means Department Head, EUR 1,000,000 means CFO and Board; GL account ranges `0xxx`, `4xxx`, `5xxx`, `6xxx`
- **The CFO prompt holds the decision rule:**
  - any `RED ALERT` means REJECTED
  - any `FX ALERT` or `HOLD FOR TREASURY AUDIT` means CONDITIONAL HOLD
  - all approved means APPROVED TO PAY
- The file warns that these literal strings come from the tools and prompts. **Rename one and the rule silently stops matching**

**Run with stand-ins** (a scripted agent model and a scripted tool model, pinned `langchain` 1.2.11):

- The order was: risk calls both tools, then tax, then control, then the CFO call. Each report was built from its tool results
- With a sanctions `RED ALERT`, the **tax and control agents still ran** and the alert text reached the CFO prompt
- So "REJECTED" depends on the model following the prompt. **No line of code enforces it.** What the real model does was not run

**The five tools, tested one by one** (model replaced by a fake):

| Tool | What happened |
|---|---|
| Sanctions | `CLEARED` passes through. A model error gives `SYSTEM WARNING ... Manual review required` |
| Credit score | Plain JSON and JSON wrapped in a code fence are parsed into `CREDIT SCORE: 82/100 | RISK: LOW | ...`. Plain text passes through. Missing keys give `N/A/100`. **JSON that is a list crashes** with `AttributeError` |
| Tax | Good JSON passes. **Unparseable text becomes a flat 15% rate** (480,000 gives 72,000) with a note. A missing `tax_rate` also defaults to 15%. A model error returns an `error` dict |
| FX | Live rate used when the API answers. 4.9% off passes, 6% off gives `FX ALERT`, exactly 5% passes (the check is strictly greater than 5%) |
| Expense | If the model is down, a heuristic runs (below) |

**FX tool surprises** (all run):

- The Frankfurter call failed from my sandbox, so the fallback was exercised
- If the API fails and the **model guesses** the rate, the text still says "**live market** rate". Only a pair with no separator (such as `EURJPY`) says "estimated"
- The model replying with text (`about 163.5 JPY`) gives an `FX WARNING`. The model replying `0` **crashes** with `ZeroDivisionError`
- The prompts talk about Aldermoor's **hedged rate**. The tool compares to the **market** rate

**Fallback heuristic in `categorize_expense`** (model down): anything over 50,000, or a description containing `server`, `machine`, `vehicle`, `building`, `equipment` or `hardware`, becomes CapEx over 3 years.

- 120,000 CNC machine: CapEx (right)
- 60,000 lubricants and consumables: CapEx (wrong, it is OpEx)
- 10,000 cloud server **subscription**: CapEx (wrong)
- 500 "hardware store screws": CapEx (wrong)

**`generate_json.py`** belongs to the deploy:

- It writes `init_embeddings.json`: one record, id `init_0001`, with **768 random numbers** (about 15.9 KB)
- `deploy.yml` runs it and copies the file to the bucket before creating the index. A new index needs starting data, and the dimension must be 768
- The workflow's index settings include 768 dimensions and `DOT_PRODUCT_DISTANCE`. The rest of `deploy.yml` is not covered here

## 3.6 Why many files

- **One file, one job.** Names tell you where to look; a change stays in its own file; parts can be tested alone
- Layout (from the README):
  - `api/` : `main.py`, `endpoints.py`, `schemas.py` (the request and reply shapes)
  - `rag/` : `llm.py`, `embeddings.py`, `vector_store.py`, `data_ingestion.py`, `retrieval.py`
  - `agent/` : `tools.py`, `prompts.py`, `agents.py`
  - `config/settings.py`, `logger/custom_logger.py`, `tests/`
- **Prompts live in their own file.** You can edit instructions without touching logic
- **Settings come from `.env`**, never from code, and `.env` is never committed
  - `config/settings.py` is a `pydantic-settings` class. Each field maps an environment name to a Python name, for example `GCP_PROJECT_ID` becomes `settings.GCP_PROJECT`
  - It reads `.env` from the **current folder**, which is why you start the app from the main folder
  - Defaults: temperature `0.0`, embedding model `text-embedding-005`, chat model `gemini-3.8-flash` (the repo's own default; model names get retired, so check it)
  - Unknown variables are ignored (`extra="ignore"`)
  - If `GCP_SERVICE_ACCOUNT_PATH` points to an existing file, the module sets `GOOGLE_APPLICATION_CREDENTIALS` for you. A missing file is **silently ignored**; the log lines for it are commented out
  - `.env.example` lists every variable. `VECTOR_SEARCH_INDEX_ID` and the endpoint ID stay empty until the deploy prints them

## 3.7 Run it

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env                  # set GOOGLE_API_KEY
uvicorn api.main:app --app-dir backend --reload --port 8080
```

- Open `http://localhost:8080/docs` (FastAPI's automatic page). Try `GET /api/health`, then `POST /api/agent/audit`
- The audit needs only a **Gemini key**. No Google Cloud
- Document Q&A needs the cloud (the vector database exists only there)
- `pytest backend/tests` is expected to give **9 passed**, with no accounts or internet
- Run commands from the **main folder**. Wrong folder gives `No module named 'api'` or empty settings

**Check the document answers.** The four sample PDFs give answers you can verify (all fictional):

| Ask | Expected |
|---|---|
| FY2024 total revenue | about EUR 2.84 billion |
| Payment terms for servo motor suppliers | Net-45 |
| Customs duty on PLC controllers from Japan | 2.2 % |
| Depreciation of filling line equipment | 10 years |
| Something not in the documents | "I don't know" |

- The sample PDFs are the accounting policy (IFRS), the FY2024 annual report, the procurement policy and an EU tariff excerpt
- These facts were read from the PDFs. They were **not** produced by running the app

## 3.8 Logs and tests

- The app writes **one JSON line per event** (structlog). When something fails, read the last lines
- `logger/custom_logger.py`:
  - Importing `logger` creates one shared logger, a `logs/` folder in the current directory, and a timestamped file
  - Lines go to the console **and** the file as JSON, with `timestamp`, `level`, `event` and any extra fields (`log.info("Embedding chunks", source="a.pdf", chunks=3)`)
  - A small step copies the level into `severity`, which Cloud Logging uses to colour and filter entries
  - On exit, the file is uploaded to `gs://<bucket>/logs/<timestamp>.log`. With no bucket set it prints a skip message; with a bucket but no credentials it prints the error and moves on
- **Gap:** `log.error("...", exc_info=True)` writes `"exc_info": true`, **not** the traceback, because no step turns it into text
- Tests need no accounts. They run the parts that do not call the cloud
- A rule worth copying: **a project's tests should run with no internet and no keys**

## 3.9 Deploying to Google Cloud

**Plan:** Google Cloud project, a service account, three GitHub secrets, run the workflow.

| Secret | Holds |
|---|---|
| `GCP_PROJECT_ID` | Project ID, not the name |
| `GCP_CREDENTIALS_JSON` | The whole key file of the service account |
| `GOOGLE_API_KEY` | Gemini key |

- The workflow (`deploy.yml`) does it all: enable services, create the bucket, create the vector index and endpoint, store the key in Secret Manager, build the Docker image, deploy to Cloud Run
- **The first run waits 30-45 minutes** for the vector database
- Re-running after a failure is safe (per `DEPLOY.md`)
- Get the index and endpoint IDs with `gcloud ai indexes list` and `gcloud ai index-endpoints list`
- The service URL appears in the *Deploy to Cloud Run* log step

**A snag the guide itself flags (untested there):** the image name uses `gcr.io`. Google's old Container Registry is closed, so you may need an Artifact Registry repository.

## 3.10 Money and safety

- **The vector database is billed by the hour while it runs, even if nobody uses it.** This is the main cost
- New Google Cloud customers get **$300 credit for 90 days**. A card is needed. No automatic charge at the end
- **Set a budget alert first.** It emails you. It does **not** stop spending
- **Do all cloud work in one sitting, then switch it off.** Recreating takes 30-45 minutes
- **Public URL has no login.** Anyone with it can use your Gemini quota and upload files
  - Do not upload private documents. The guide caps the service at 3 copies to limit damage
- The service-account key is a **password**. Never commit it. Delete it after use
- The guide gives the robot broad roles for simplicity. A real company would give the least needed

**Switch off:**

```bash
gcloud ai index-endpoints undeploy-index ENDPOINT_ID --deployed-index-id=deployed_financial_docs --region=us-central1
gcloud ai index-endpoints delete ENDPOINT_ID --region=us-central1
gcloud ai indexes delete INDEX_ID --region=us-central1
gcloud run services delete meridian-ai-cloud-run --region=us-central1
gcloud projects delete YOUR_PROJECT_ID     # removes everything
```

## 3.11 Interview corner

**Q1. What is RAG and why use it?**
- Retrieve relevant text first, then let the model answer from it
- It grounds answers in your documents, avoids retraining, and allows "I don't know"

**Q2. What is an embedding?**
- A vector that captures meaning. Similar meaning gives nearby vectors
- Search by meaning, not by keyword

**Q3. Why split the PDF into pieces?**
- The unit you retrieve must be small and focused. A whole PDF is too big and too noisy

**Q4. Why separate `api`, `rag` and `agent`?**
- One job per package, testable alone, dependencies run one way

**Q5. Why run several agents instead of one prompt?**
- Each has a focused instruction and tools. A final step combines them
- Cost: more model calls, more time

**Q6. What does a service account do in CI?**
- It lets a program (GitHub Actions) act in your cloud without a person's login
- Give it the minimum permissions and rotate or delete its key

**Q7. What is the cost trap in this project?**
- A vector index endpoint bills hourly while deployed, idle or not

**Q8. Why use `lru_cache` on the model and store getters?**
- They connect on first use and are reused. The API can start and answer `/health` before Google is set up

**Q9. Why overlap chunks?**
- A sentence cut at a boundary still appears whole in one of the two neighbours. Cost: some repeated text

**Q10. The audit says "approved". Should you trust it?**
- No. The checks come from general model knowledge. Treat it as a demo

**Q11. How would you make the three specialists run in parallel?**
- They do not depend on each other, so run them together (threads or async) and join the results before the CFO call. Total time becomes the slowest agent, not the sum

**Q12. Where does the "RED ALERT means reject" rule live, and is that safe?**
- In the CFO prompt text. Safe only if the model always obeys. For a hard rule, check the result in code

**Q13. Why is a model-backed sanctions check weak?**
- The model answers from training knowledge, which can be stale or wrong. A real check calls an official list

## 3.12 Added by Claude, not from the sources

- **Worked example (my arithmetic, not app output).** Using the figures from the README example and the sample tariff and procurement documents:
  - Order: EUR 480,000 of PLC controllers from Japan to Germany
  - Duty at 2.2 % = **EUR 10,560**
  - VAT base = 480,000 + 10,560 = **EUR 490,560**
  - German import VAT at 19 % = **EUR 93,206.40**
  - Landed cost including VAT = **EUR 583,766.40**
  - Approval: above EUR 250,000 needs **Department Head**; below EUR 1,000,000 so **no CFO and Board**
  - Quoted yen amount at 1 EUR = 163.5 JPY = **JPY 78,480,000**
  - Whether the app reaches the same numbers is **not tested**. Use these to judge its output
- **The audit will not use the 2.2% in the tariff PDF.** The tax tool asks the model for a "general merchandise" duty rate, and no tool reads documents. Expect a different duty from the worked example above
- **Compare answers to the PDFs, not to your expectations.** A good RAG test set has questions whose answers you can find on a page
- **Add a "not in the documents" question** every time. It is the test that catches made-up answers
- **The sample set is too small to prove retrieval.** Each of the four PDFs is one page and **one chunk** (644 to 949 characters, under the 1,000 limit). So the whole store holds 4 chunks and "the 3 closest" returns 3 of 4. A right answer proves the pipeline is wired, not that retrieval is good. The "not in the documents" question is the stronger test
- **Retrieval count (3) is a trade-off.** Too few misses facts, too many adds noise
- **`contextual` gets expensive:** one model call per chunk fetched (10) plus the answer
- **A bulk GCS run stops at the first bad PDF.** There is no per-file `try`, so files after it are skipped. With 3 files and the 2nd corrupt, only 1 was stored. Wrap each file if you want the rest to continue
- **Make the safety rule code, not prose.** If a sanctions check returns `RED ALERT`, stop the run in Python and reject. Today the other agents still run and the model is trusted to apply the rule
- **Labels should tell the truth.** An FX result guessed by the model should never say "live market"
- **Validate model JSON.** Check it is a dict, check ranges (a rate between 0 and 1, a score between 0 and 100), and fail loudly instead of defaulting to 15%
- **Use the structured-output tools** from [LangChain Ch4](../langchain/04-structured-output.md) instead of asking for "strict JSON" and parsing text
- **`exc_info` is not rendered** (see 3.8). Add structlog's exception formatter if you want tracebacks in the logs
- **Pin model names in config.** The README warns that model names are retired; the default shown there is its own and was not checked

## Recap

- Two jobs: RAG over your PDFs, and a three-agent purchase audit with a CFO memo
- RAG: chunk, embed, store, retrieve three, answer only from them
- One file, one job. Layers depend downward only
- Audit needs only a Gemini key. Document Q&A needs Google Cloud
- Deploy is a service account, three secrets and one workflow run (30-45 min wait)
- The vector database costs by the hour. Set a budget alert. Switch off after

## Practice

1. Run the audit locally with the README example. Compare to the worked example in 3.12
2. Run `pytest backend/tests`. Confirm 9 passed
3. Ask each of the four sample questions, then one not in the documents
4. Change the retrieval count and watch answers change
5. Add a fourth specialist agent (for example, legal) and see where it must be registered
6. Draw the layer diagram and mark what may call what
7. Write the shutdown commands in order for your own project IDs

## How this chapter was checked

- Read fully: `README.md`, `DEPLOY.md`, four sample PDFs, `.env.example`, the settings, logger and five `rag/` files, and the `agent/` files plus `generate_json.py`
- Computed in Python: the figures in 3.12
- **Run** with the pinned packages from `requirements.txt` (`langchain` 1.2.11, `pydantic` 2.12.5, `structlog` 26.1.0, `pypdf` 6.7.5):
  - settings: defaults, environment override, `.env` file, a bad temperature (a clear validation error), the credentials path
  - logger: JSON fields, console and file output, the GCS skip and failure messages
  - ingestion: the 4 sample PDFs (4 chunks), a 7,689-character page (9 chunks, neighbours share 91 to 97 characters), a fake GCS bucket, a corrupt PDF
  - tools: all five, with the model replaced by a fake (every case in 3.5), and the FX tool with a faked API
  - agents: the whole `ProcurementSupervisor` flow with a scripted agent model and a scripted tool model, including the `RED ALERT` case
  - retrieval: all three retrievers plus an unknown type, with a **stand-in embedding** (word counts) and a **stand-in chat model**. This checks the wiring and the call counts. It says **nothing** about Vertex or Gemini answer quality
- **Not read:** the API code, the tests, the Dockerfile, and `deploy.yml` beyond the lines around `generate_json.py`. The frontend is left out at your request
- **Not run:** the real app, Vertex AI, Gemini, Cloud Storage, the deploy. The price figure in `DEPLOY.md` is third-party, as the guide says

## Sources and further reading

- Live-Class-2026, `Weekend 14 - Oct 3 & Oct 4/meridian-ai-learner-main/README.md`, `DEPLOY.md`, `sample_docs/*.pdf`
- Google pricing: https://cloud.google.com/vertex-ai/pricing

Previous: [Chapter 2, Time Tracker (MCP)](02-time-tracker-mcp.md) · Next: [Chapter 4, AI Updater](04-ai-updater.md)
