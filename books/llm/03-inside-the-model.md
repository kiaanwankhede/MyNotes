# Chapter 3: Inside the model

This chapter starts with the five terms you need before building an agent, and how a chat with an LLM really works. Later classes on the model layer will add to it.

## 3.1 Five terms to know cold

*Source: Live-Class-2026, `classes_transcription_summary/03` and `classes_summary/03`.*

| Term | One-line mental model |
|---|---|
| **LLM** | Predicts the next *token*, not the next word. It completes patterns rather than understanding |
| **Token** | The billing currency. About three quarters of a word. Output tokens cost more than input |
| **Vector embedding** | A word turned into coordinates. Similar meanings sit close together |
| **Context window** | A whiteboard of fixed size. The oldest content is erased when it fills up |
| **Parameters** | Billions of fixed weights set during training. Not the same thing as tokens |

### LLM

An LLM is trained on a huge amount of text and learns which word usually comes next. It then generates text one token at a time by probability. The class analogy: a friend who has read every book ever published but was never told what any of it means. They have simply seen "thank you for" followed by "your business" millions of times. ChatGPT, Claude and Gemini are LLMs; OpenAI, Anthropic and Google are LLM providers. The class slide's line: ChatGPT is to AI what Google is to the internet, a household name for the whole field. It draws the LLM as a box with an input on one side and, on the other, an output that is a next-token prediction.

### Tokens

The model sees only tokens, never raw words. A token is more like a Lego brick than a word, so "unbelievable" can split into three pieces. You are billed per token on both input and output, like a prepaid phone plan billed per minute. Output costs more because the model has to generate it, not just receive it. Input tokens are charged too, because every token must be processed. An uploaded PDF costs tokens like any other input.

The slide's token example: a short input measured as 5 tokens. The output can be anything, but it too is counted in tokens. Output tokens always cost more than input tokens. The slide's price card shows a model labelled "5.5" at $5 for input and $30 for output (the card does not state the unit), and writes "output pricing is 6 times the input". Prices change, so check the current ones before relying on the ratio. The slide's one-line summary: tokens are the currency of AI. It also compares tokens to a phone plan charged by the minute, where more words mean more minutes and words are the currency of talking.

*Source: `Class-3-4.pdf`.*

### Vector embeddings

An embedding turns a word into a list of numbers, a point in a high-dimensional space. "Puppy" lands close to "dog" and "happy" far from both. The class showed a 10,000-word, 200-dimension space where searching "guitar" surfaced music-related neighbours. The number of dimensions is a design choice you make: more dimensions separate meaning better but need more hardware. Dimensions are not hand-labelled categories.

Embeddings come from classic natural language processing, not just modern AI. The LLM and the embedding model are different, specialised models, and no embedding model is best for every use. Closeness between two vectors is measured with **cosine similarity**. In this context "vector" and "embedding" are used interchangeably.

### Context window

The window is a whiteboard of fixed size. Once it is full, the oldest content is erased to make room. The mentor's analogy: your context window as a student is about three hours, so teaching you for six makes you forget hour one. A "400K" model holds about 400,000 tokens before older content drops. The context window is **not memory**. Memory is a separate, lasting mechanism covered in a later class.

### Parameters

Parameters are billions of tiny internal values set during training, like a mixing console with billions of sliders. No single one means anything alone; the capability comes from the combination. They are fixed once training ends and change only when a new model version is released. They are not tokens: parameters are what the model *is*, tokens are what flows in and out when you use it. More parameters usually mean more potential, but never a guarantee of a better answer to one question.

## 3.2 Calls are stateless, so the history is resent

*Source: `classes_transcription_summary/04`, `classes_summary/04`.*

An LLM keeps no state between calls. A chat only seems to remember because the app sends the whole history again with every message, so message 2 carries message 1 and reply 1 as well. That is why each extra turn costs more tokens.

The context window explains why a model gets forgetful in a long chat. In a class demo with a toy 40-token window, earlier messages visibly greyed out as new ones pushed them out. Once a message falls out, the model has no idea it existed. Starting a new chat resets the cost.

## 3.3 Web app versus API

The chat web apps are like an all-you-can-eat buffet: a flat subscription and no visible per-token cost. The API is à la carte: you pay exactly per token and see full usage. When you build software you need the API. The slide labels the web app a "controlled buffet" and the API "à la carte", and notes that through the API you can have lots and lots of models. A student question captured on the slide, with no answer written on it, asks what happens to the context window if you switch between two models in the same chat.

*Source: `Class-3-4.pdf`.*

**OpenRouter** gives one API key for models from many providers (OpenAI, Anthropic, Google, Mistral and others). The class created a key, called a free model, and checked the exact input and output token counts in the dashboard.

## Practice

1. Explain the five terms to someone else without notes.
2. Explain the whiteboard analogy for the context window in your own words.
3. Create a free OpenRouter key and call a model outside the web UI.

## Sources and further reading

- Live-Class-2026, `classes_summary/03 - 4 Jul - Pydantic Deep Dive.md` (vocabulary table)
- Live-Class-2026, `classes_transcription_summary/03 - 4 Jul - Pydantic Deep Dive.md`
- Live-Class-2026, `classes_transcription_summary/04 - 5 Jul - Anatomy of an Agent.md`
- Live-Class-2026, whiteboard `Class-3-4.pdf` in the class 02-03 folder

Previous: [Chapter 2](02-the-agentic-loop-in-pure-python.md) · Next: [Chapter 4, Glossary](04-glossary.md)

*Class 08 (Inside the Model: parameters, streaming, tools, structured output) is written up in the Langchain book, [Chapters 3 to 5](../langchain/03-models-messages-and-parameters.md), because all of its code uses LangChain.*
