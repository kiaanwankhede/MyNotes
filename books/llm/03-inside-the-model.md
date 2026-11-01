# Chapter 3: Inside the model

**After this chapter you can:**

- Define LLM, token, embedding, context window and parameters in one line each
- Explain why a chat model is stateless and why every turn costs more
- Say the difference between a chat web app and the API
- Use OpenRouter to call a model and read its token counts

**Builds on:** [Chapter 1](01-course-roadmap-and-prerequisites.md) (setup and API keys). **Used by:** [Chapter 2](02-the-agentic-loop-in-pure-python.md), [Python Ch 3](../python/03-anatomy-of-an-agent.md).

## 3.1 Five terms to know cold

| Term | One-line mental model |
|---|---|
| **LLM** | Predicts the next *token*, not the next word. Completes patterns |
| **Token** | The billing unit. About three quarters of a word |
| **Vector embedding** | A word as coordinates. Similar meanings sit close together |
| **Context window** | A whiteboard of fixed size. Oldest content is erased first |
| **Parameters** | Billions of fixed weights set in training. Not tokens |

*Source: Live-Class-2026, `classes_summary/03` and `classes_transcription_summary/03`.*

### LLM

- Trained on a huge amount of text. Learns which token usually comes next
- Generates one token at a time, by probability
- Class analogy: a friend who has read every book but was never told what any of it means
  - They have seen "thank you for" followed by "your business" millions of times
- ChatGPT, Claude and Gemini are LLMs. OpenAI, Anthropic and Google are LLM providers
- The slide draws the LLM as a box: input on one side, a next-token prediction on the other

### Tokens

- The model sees tokens, never raw words. A token is more like a Lego brick: "unbelievable" can split into three
- You are billed per token, on **input and output**, like a phone plan billed per minute
- **Output costs more** than input, because the model has to generate it
- Input is charged too: every token must be processed, so an uploaded PDF costs tokens
- Slide example: a short input measured as 5 tokens
- Slide price card: a model labelled "5.5" at $5 input and $30 output. The card does not state the unit
  - It also writes "output pricing is 6 times the input"
  - Prices change. Check current ones before relying on the ratio
- Slide's summary: tokens are the currency of AI

*Source: `Class-3-4.pdf`.*

### Vector embeddings

- A word becomes a list of numbers: a point in a high-dimensional space
- "Puppy" lands near "dog". "Happy" lands far from both
- The class showed a 10,000-word, 200-dimension space. Searching "guitar" surfaced music neighbours
- The number of dimensions is **your design choice**. More separate meaning better but need more hardware
- Dimensions are not hand-labelled categories
- Embeddings come from classic NLP, not only modern AI
- The LLM and the embedding model are **different** models. No embedding model is best for everything
- Closeness is measured with **cosine similarity**
- "Vector" and "embedding" are used interchangeably here

### Context window

- A whiteboard of fixed size. When full, the oldest content is erased
- Mentor's analogy: your window as a student is about three hours, so six hours of teaching erases hour one
- A "400K" model holds about 400,000 tokens before older content drops
- It is **not memory**. Memory is a separate, lasting mechanism (a later class)

### Parameters

- Billions of tiny values set during training. Like a mixing console with billions of sliders
- No single one means anything alone. The capability comes from the combination
- Fixed once training ends. They change only with a new model version
- **Not tokens.** Parameters are what the model *is*. Tokens are what flows in and out
- More parameters usually means more potential, never a guarantee for one question

## 3.2 Calls are stateless, so the history is resent

- An LLM keeps **no state** between calls
- A chat seems to remember because the app sends the **whole history** each time
- Message 2 carries message 1 and reply 1. So **each turn costs more**
- Class demo with a toy 40-token window: earlier messages greyed out as new ones pushed them out
- Once a message falls out, the model has no idea it existed
- A new chat resets the cost

```python
history.append({"role": "user", "content": question})
reply = client.chat.completions.create(model=model, messages=history)   # the whole list, every time
history.append({"role": "assistant", "content": reply.choices[0].message.content})
```

*Source: `classes_transcription_summary/04`, `classes_summary/04`.*

## 3.3 Web app versus API

| | Chat web app | API |
|---|---|---|
| Pricing | Flat subscription ("controlled buffet") | Per token ("à la carte") |
| Usage visible | No | Yes, in full |
| Models | The app's own | Many, through one account |
| For building software | No | **Yes** |

- A student question on the slide, with no written answer: what happens to the context window if you switch between two models in the same chat?

*Source: `Class-3-4.pdf`.*

**OpenRouter**

- One API key for models from many providers (OpenAI, Anthropic, Google, Mistral and others)
- The class made a key, called a free model, and read the exact input and output token counts in the dashboard

## 3.4 Interview corner

**Q1. Why is an LLM called stateless? How does a chatbot still remember you?**
- Each call is independent. The app resends the full history with every message

**Q2. What is a token, and why does output cost more than input?**
- A piece of a word, about three quarters of one. Output must be generated, input only processed

**Q3. Difference between parameters and tokens?**
- Parameters are fixed weights learned in training. Tokens are the text units you send and receive

**Q4. What is the context window? Is it memory?**
- The most tokens a model can consider in one call. No: memory is a separate, lasting mechanism

**Q5. What is an embedding, and what is cosine similarity for?**
- A vector for meaning. Cosine similarity compares the angle between two vectors to score closeness

**Q6. Why would a company use the API and not the web app?**
- Per-token billing and visibility, many models, and it can be called from code

**Q7. A long chat gets slow and costly. Why? What do you do?**
- The whole history is resent. Start a new chat, or summarise older turns

## 3.5 Added by Claude, not from the sources

Each item marked *checked* was calculated or run.

- **Cost grows with the length of the chat.** *Checked:* five requests to a local stand-in server carried 1, 3, 5, 7 and 9 messages
  - With 100 tokens per message, 10 turns bill **10,000** input tokens, not 1,000. The growth is roughly quadratic
- **Example price calculation.** If the card meant dollars per million tokens (the slide does not say): 1,000 in and 500 out costs 1,000 × 5/1,000,000 + 500 × 30/1,000,000 = **$0.02**. *Checked* by arithmetic
- **Cosine similarity, small example.** *Checked:* `dog = [0.9, 0.1]`, `puppy = [0.85, 0.2]`, `happy = [0.05, 0.95]` give cosine **0.993** for dog and puppy and **0.163** for dog and happy
  - Cosine ignores vector length: `[1, 0]` and `[2, 0]` score 1.0 while their dot product is 2
- **Embedding models are a separate choice.** A vector search index must use the **same** embedding model to index and to query (see [Projects Ch 3](../projects/03-meridian-ai-learner.md))
- **Token counts differ by model.** The same text gives different counts under different tokenisers. Use the provider's usage figures for billing, not a word count
- **Bigger window is not free.** A larger context costs more per call and can still lose detail in the middle. Send only what the task needs

## Recap

- LLM: predicts the next token. Token: the billing unit. Embedding: meaning as coordinates
- Context window: fixed whiteboard, oldest content erased first. Parameters: fixed weights
- Calls are stateless. The history is resent, so each turn costs more
- API: pay per token, many models, usable from code. Web app: flat fee, no visible token cost
- OpenRouter: one key, many providers, exact token counts

## Practice

1. Explain the five terms to someone else without notes
2. Explain the whiteboard analogy for the context window in your own words
3. Create a free OpenRouter key and call a model outside the web UI. Read the token counts
4. Make a chat of 5 turns against any model and count the messages in each request
5. Compute the cosine similarity of two vectors you choose

## How this chapter was checked

- **Run:** five-turn history growth against a local stand-in API with the real OpenAI client; the token and price arithmetic; the cosine examples
- **Not run:** a real model, OpenRouter, any provider dashboard
- The slide price card and the "400K" figure are as the class showed them. Prices were not looked up
- The class summaries and slides were not re-opened in this rewrite; the text comes from the earlier version of the chapter

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md` (vocabulary table)
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/04 - 5 Jul - Anatomy of an Agent.md`
- Live-Class-2026, whiteboard `Class-3-4.pdf` in the class 02-03 folder

Class 08 (parameters, streaming, tools, structured output) is in the Langchain book, [Chapters 3 to 5](../langchain/03-models-messages-and-parameters.md), because its code uses LangChain.

Previous: [Chapter 2](02-the-agentic-loop-in-pure-python.md) · Next: [Chapter 4, Glossary](04-glossary.md)
