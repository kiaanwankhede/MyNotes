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
The settings docs page was read up to about 100,000 of its roughly 103,900 characters. The pages on unions, alias, configuration, dataclasses, type adapters and performance were read in full on 31 Oct 2026, together with five FastAPI tutorial pages (body, response model, extra models, body updates, query parameter models). Some tabbed code examples did not come through in the text; the chapters say which. The Pydantic AI framework itself and other FastAPI pages were not read.
:::

Try the idea straight away. Edit the JSON, break a rule, and read the error:

:::widget pydantic-playground
Interactive demo: edit JSON and validate it against a small Pydantic-style model.
:::

<!-- res -->
<!-- verified -->
## What was run, and what was not

On 31 Oct 2026 I ran this book's code and checked its claims against a real install (Pydantic 2.14.2, pydantic-settings 2.16.2, FastAPI 0.162.0, Python 3.13).

- All 13 code blocks in the chapters run. Three needed small additions first (chapter 3's comparison was a fragment; chapter 7's and chapter 9's examples lacked imports or the model they use), and I added them.
- A test script (`build/pydantic_claims_test.py`) checks **55 behaviours** the chapters state, from coercion and extra keys to validator order, unions, aliases, configuration, dataclasses, `TypeAdapter`, settings, JSON Schema, error structure and the FastAPI patterns. **All 55 pass.** The docs' "about 2.5 times faster" claim for `TypedDict` over nested models measured 2.2 to 2.8 times on my machine.
- **Not run:** the OpenAI and Anthropic SDK calls in chapter 11 (they need paid keys), and the notebook's own cells.
- The test is mine, written from the chapters' statements. A pass means the statement is true for that version, not that the chapter covers everything.
<!-- /verified -->

## Course resources

| Craft entry | What is attached |
| --- | --- |
| **Classes 3 and 4: Pydantic, AI and agentic AI basics** | Interactive sites for Pydantic (`pydantic-with-mayank.netlify.app`), common AI terms (`ai-terms-with-mayank.netlify.app`) and a context-window and memory simulator (`context-with-mayank.netlify.app`); the OpenAI tokenizer; a Colab; a Claude usage tracker extension; PDF `Class-3-4.pdf` |

The class 3 and 4 Colab "Pydantic From Scratch" is the same notebook as `Pydantic_From_Scratch.ipynb` in the repo: it shows why unchecked types let `age = 10000` produce a birth year of -7974.
<!-- /res -->

