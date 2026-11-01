# Chapter 3: Meridian AI learner

**After this chapter you can:**

- Explain what Meridian does and name every technology in it
- Trace a document question and a purchase audit through the system
- Say why the code is split into packages, and what depends on what
- Run the audit locally and check the document answers against the sample PDFs
- Deploy it to Google Cloud, know what costs money, and switch it off
- Answer interview questions on RAG, agents and deployment

**Builds on:** [LangChain Ch4](../langchain/04-structured-output.md) (structured output), [LangChain Ch5](../langchain/05-tools.md) (tools), [LangChain Ch6](../langchain/06-agents-and-memory.md) (agents). Pydantic is used for request shapes.

> **Status of these notes.** Built from the README, `DEPLOY.md` and the four sample PDFs. The backend and frontend **code was not read**, and **nothing was deployed or run**. Code-level notes will be added when the code batch is done.

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

```python
# the idea, not the repo's code (not read)
q_vec  = embed(question)
chunks = vector_search(q_vec, k=3)
answer = llm(f"Answer only from this:\n{chunks}\n\nQ: {question}")
```

## 3.5 Purchase audit (agents)

- Input: a request, for example 200 PLC controllers from Japan, 480,000 EUR
- **Three agents** each read it and choose their own tools (the README lists **five tools**; one example is the exchange-rate check)
  - Risk, tax and control
- A final step reads the three reports and writes **one memo** with a decision
  - Approved, conditional hold, or rejected
- Output is four texts: three reports and the memo. Wording changes; layout stays the same
- Takes up to a minute or more, because several model calls run in turn

## 3.6 Why many files

- **One file, one job.** Names tell you where to look; a change stays in its own file; parts can be tested alone
- Layout (from the README):
  - `api/` : `main.py`, `endpoints.py`, `schemas.py` (the request and reply shapes)
  - `rag/` : `llm.py`, `embeddings.py`, `vector_store.py`, `data_ingestion.py`, `retrieval.py`
  - `agent/` : `tools.py`, `prompts.py`, `agents.py`
  - `config/settings.py`, `logger/custom_logger.py`, `tests/`
- **Prompts live in their own file.** You can edit instructions without touching logic
- **Settings come from `.env`**, never from code, and `.env` is never committed

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

**Q8. The audit says "approved". Should you trust it?**
- No. The checks come from general model knowledge. Treat it as a demo

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
- **Compare answers to the PDFs, not to your expectations.** A good RAG test set has questions whose answers you can find on a page
- **Add a "not in the documents" question** every time. It is the test that catches made-up answers
- **Retrieval count (3) is a trade-off.** Too few misses facts, too many adds noise
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

- Read fully: `README.md`, `DEPLOY.md`, four sample PDFs
- Computed in Python: the figures in 3.12
- **Not read:** all backend and frontend code, the Dockerfile, `deploy.yml`
- **Not run:** the app, tests, the deploy, any Google service. The price figure in `DEPLOY.md` is third-party, as the guide says

## Sources and further reading

- Live-Class-2026, `Weekend 14 - Oct 3 & Oct 4/meridian-ai-learner-main/README.md`, `DEPLOY.md`, `sample_docs/*.pdf`
- Google pricing: https://cloud.google.com/vertex-ai/pricing

Previous: [Chapter 2, Time Tracker (MCP)](02-time-tracker-mcp.md) · Next: [Chapter 4, AI Updater](04-ai-updater.md)
