# Glossary
> lead: The terms from Python and Agent Foundations in one line each, grouped by theme, with the chapter where each is explained. Use the search box to jump to a term.
meta: About 60 terms | Links go to the chapter

## Setup and Python

| Term | One line | Chapter |
| --- | --- | --- |
| **`uv`** | The package and project manager used all course long; `uv sync` rebuilds an exact environment from `pyproject.toml` and `uv.lock` | [1](#foundations-f1) |
| **`pyproject.toml` / `uv.lock`** | The project's dependency list and the exact versions that were resolved | [1](#foundations-f1) |
| **`.python-version`** | A file that pins the Python version for a project (the course pins 3.13) | [1](#foundations-f1) |
| **`.env`** | A local file of real keys, git-ignored so a key cannot be committed by accident | [1](#foundations-f1) |
| **`.env.example`** | The safe template you copy to make `.env`; it is committed, the real file is not | [1](#foundations-f1) |
| **API key** | A long secret that proves a request comes from you; treat it like a password | [1](#foundations-f1), [1A](#foundations-f1a) |
| **Groq / OpenRouter** | Free LLM providers for the course; OpenRouter's `openrouter/free` model auto-routes to a free model | [1](#foundations-f1) |
| **Git Bash / Windows Terminal** | The shells to use on Windows, instead of plain CMD or PowerShell | [1](#foundations-f1) |
| **`@dataclass`** | A class with an auto-written `__init__`; it stores values but does not validate them | [1](#foundations-f1), [Pydantic 2](#pydantic-p2) |
| **Decorator** | A function that wraps another function to add behaviour, written with `@` | [1](#foundations-f1) |
| **Type hint** | A note about what type a value should be; documentation, not enforcement | [Pydantic 1](#pydantic-p1) |
| **Compromised key** | Any key that was committed or shared; revoke it and use `.env` or Colab Secrets | [1](#foundations-f1), [4](#foundations-f4) |

## APIs, JSON and HTTP

| Term | One line | Chapter |
| --- | --- | --- |
| **API** | A waiter between you and a kitchen: you ask, work is done elsewhere, the result comes back | [1A](#foundations-f1a) |
| **JSON** | A labeled box of text: braces, labels and values; almost every request and response | [1A](#foundations-f1a) |
| **Endpoint** | A fixed URL that always means the same thing | [1A](#foundations-f1a) |
| **Query parameter** | An option added after `?` in a URL (or in a body) to customise a call | [1A](#foundations-f1a) |
| **GET / POST / PUT / PATCH / DELETE** | Read / create / replace everything / change one detail / remove | [1A](#foundations-f1a) |
| **Request body** | The order itself (the JSON); a GET has none | [1A](#foundations-f1a) |
| **Header** | Information that rides alongside a request: format, who you are | [1A](#foundations-f1a) |
| **`Content-Type`** | The header that says what format the body is in (`application/json`) | [1A](#foundations-f1a) |
| **Bearer token** | A credential sent in the `Authorization` header | [1A](#foundations-f1a) |
| **OAuth 2.0** | "Sign in once, get a token"; the flow behind connectors | [1A](#foundations-f1a) |
| **Connector** | Claude calling another app's API with a token you approved; it never sees your password | [1A](#foundations-f1a) |
| **Postman / cURL** | A visual request builder / the same request from a terminal | [1A](#foundations-f1a) |
| **2xx / 4xx / 5xx** | Success / your mistake / their mistake; 429 means slow down, 401 means wrong key | [1A](#foundations-f1a) |
| **Rate limiting** | A cap on how fast you may call an API | [1A](#foundations-f1a) |
| **Pagination / webhook** | Big answers one page at a time / the server calls you | [1A](#foundations-f1a) |

## LLM basics

| Term | One line | Chapter |
| --- | --- | --- |
| **LLM** | A next-word predictor; it predicts the next token, not the next word | [2](#foundations-f2) |
| **Token** | A piece of text (a "Lego brick"); the unit of billing and of limits | [2](#foundations-f2) |
| **Stateless** | Each call remembers nothing; "memory" is the history you resend | [2](#foundations-f2), [3](#foundations-f3) |
| **Context window** | The fixed amount of text a model considers at once; older text falls out when it is full | [2](#foundations-f2) |
| **Embedding / vector** | A list of numbers for meaning; similar meanings sit close together | [2](#foundations-f2), [RAG 2](#rag-r2) |
| **Parameters** | The model's billions of learned numbers; size is only a rough proxy for ability | [2](#foundations-f2) |
| **Attention** | Each word weighs which other words matter, for every word at once | [2](#foundations-f2) |
| **Transformer** | The architecture the LLM runs on | [2](#foundations-f2) |
| **Training / fine-tuning / RLHF** | Learn from text / specialise afterwards / humans pick better answers | [2](#foundations-f2) |
| **Zero-shot / few-shot** | A bare instruction / an instruction with worked examples | [2](#foundations-f2) |
| **Temperature** | A dial from safe to adventurous; low for facts and code | [2](#foundations-f2) |
| **Hallucination** | A confident guess presented as fact; worse when important context was forgotten | [2](#foundations-f2) |
| **RAG** | Fetch relevant documents first, then answer (open book) | [2](#foundations-f2), [RAG 1](#rag-r1) |
| **Context engineering** | Deciding what is on the table before the model speaks | [2](#foundations-f2) |
| **MCP** | One universal plug between models and tools | [2](#foundations-f2) |
| **Multimodal / reasoning model / small language model** | More than text / thinks step by step first / a smaller, cheaper model | [2](#foundations-f2) |
| **Open-weight model** | A model whose trained numbers you can download and run | [2](#foundations-f2) |
| **Subscription vs API** | A flat monthly plan in an app vs pay-per-token calls from your code | [2](#foundations-f2) |

## Agents

| Term | One line | Chapter |
| --- | --- | --- |
| **Agent** | A brain (LLM), memory (the message list) and tools, deciding its next step | [3](#foundations-f3) |
| **Chatbot vs agent** | A chatbot has history; an agent also has tools and decides what to do next | [3](#foundations-f3) |
| **Tool** | A function the model may ask for; the model never runs it, your code does | [3](#foundations-f3), [4](#foundations-f4) |
| **Tool schema** | Name, description and parameters shown to the model; the description decides when it is used | [3](#foundations-f3) |
| **Tool call** | The model's request: a tool name and arguments; several can come in one reply | [3](#foundations-f3) |
| **Agentic loop** | Model decides, code runs the tool, result goes back, repeat until plain text | [3](#foundations-f3) |
| **`max_turns`** | A cap on loop passes so a confused model cannot loop forever | [3](#foundations-f3), [4](#foundations-f4) |
| **`tool_call_id`** | Links a tool result message to the request it answers | [3](#foundations-f3) |
| **Structured output** | Forcing the model's reply into a fixed shape that code can read | [3](#foundations-f3), [Pydantic 11](#pydantic-p11) |
| **Provider picker** | A small function that chooses a free or paid provider from your keys | [4](#foundations-f4) |
| **Project 0** | The agent built in seven plain-Python files, no framework | [4](#foundations-f4) |
