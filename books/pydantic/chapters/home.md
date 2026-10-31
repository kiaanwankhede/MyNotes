# Pydantic
> lead: How to make Python check data at the door: models, constraints, validators, settings, FastAPI, and validating what an LLM sends back, ending with a small ticket-triage project.
meta: Book 2 of the library | 9 chapters | Read after Foundations

## Why a whole book on one library

Pydantic is the validation layer under LangChain's structured output, tool schemas, FastAPI and most agent frameworks. If you understand it here, chapter 4 of the LangChain book (structured output) is mostly review.

| Chapter | Topic |
| --- | --- |
| 1 | Why validation exists, and type hints |
| 2 | Your first model, coercion, dumping |
| 3 | Constraints and custom validators |
| 4 | Computed fields and controlling output |
| 5 | Nested models |
| 6 | Settings and secrets |
| 7 | Pydantic with FastAPI |
| 8 | Validating LLM output (the AI bridge) |
| 9 | Where Pydantic goes next, and the final project |

:::key Source
Built from the instructor's Pydantic reference site and the class 03 and 04 material in the course repo (`8_Pydantic/`). The code samples here are my own short versions of the ideas, not copies of the site.
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

