# Pydantic
> lead: How to make Python check data at the door: models, constraints, validators, settings, FastAPI, and validating what an LLM sends back, ending with a small ticket-triage project.
meta: Book 2 of the library | 12 chapters | Read after Foundations

## Why a whole book on one library

Pydantic is the validation layer under LangChain's structured output, tool schemas, FastAPI and most agent frameworks. If you understand it here, chapter 4 of the LangChain book (structured output) is mostly review.

| Chapter | Topic |
| --- | --- |
| 1 | Why validation exists, and type hints |
| 2 | Your first model |
| 3 | Fields and constraints |
| 4 | Validators |
| 5 | Computed fields and serialization |
| 6 | Nested models |
| 7 | Strict mode and JSON Schema |
| 8 | Settings and secrets |
| 9 | Reading validation errors |
| 10 | Pydantic with FastAPI |
| 11 | Validating what an LLM gives you back |
| 12 | Where Pydantic goes next, and the final project |

:::key Sources
Each chapter names its sources at the end. In short, the book is built from: the official Pydantic documentation (models, fields, validators, serialization, strict mode, types, JSON schema, settings, error handling, and the get-started page), the class 03 write-up, the `Pydantic_From_Scratch` notebook in the course repo, Pydantic's article on LLMs, and the instructor's Pydantic site. The analogies come from the instructor's site, the repo notes flag problems in the notebook, and code samples are short examples of my own.
:::

:::beyond Not read
The settings docs page was read up to about 100,000 of its roughly 103,900 characters. The docs pages on unions, dataclasses, type adapters, performance and the Pydantic AI framework itself were not read. The FastAPI chapter comes from the instructor's site only.
:::

Try the idea straight away. Edit the JSON, break a rule, and read the error:

:::widget pydantic-playground
Interactive demo: edit JSON and validate it against a small Pydantic-style model.
:::

<!-- res -->
## Course resources

| Craft entry | What is attached |
| --- | --- |
| **Classes 3 and 4: Pydantic, AI and agentic AI basics** | Interactive sites for Pydantic (`pydantic-with-mayank.netlify.app`), common AI terms (`ai-terms-with-mayank.netlify.app`) and a context-window and memory simulator (`context-with-mayank.netlify.app`); the OpenAI tokenizer; a Colab; a Claude usage tracker extension; PDF `Class-3-4.pdf` |

The class 3 and 4 Colab "Pydantic From Scratch" is the same notebook as `Pydantic_From_Scratch.ipynb` in the repo: it shows why unchecked types let `age = 10000` produce a birth year of -7974.
<!-- /res -->

