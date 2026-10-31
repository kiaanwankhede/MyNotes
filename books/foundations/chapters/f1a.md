# APIs, JSON and HTTP in plain words
> lead: Every AI call is an API call. This chapter explains requests, JSON, endpoints, the five HTTP verbs, headers, authentication and status codes with a restaurant analogy, using real Tavily, Apify and Claude requests as examples.
meta: Foundations | Class 01 and the instructor's guide "APIs, Properly Explained" | 15 min read

## Why it matters

Class 01 of the course is "Python setup and API basics" for a reason: an LLM, a search tool and a connector are all reached the same way. If you can read a request and a status code, most integration failures stop being mysterious.

## Core ideas

### An API is a waiter

You do not cook in the restaurant kitchen. You tell a waiter what you want, the waiter takes it to the kitchen, and food comes back. Ask, do the work, hand back the result: that round trip is every API, including the ones behind ChatGPT and Claude. Your app sends a message to Claude's API, Claude's servers do the thinking, and text comes back; your app never touches a GPU.

Claude's **connectors** are the same trip. When you ask what is on your calendar, Claude sends a real request to the Calendar API using a token you approved, gets JSON back, and turns it into a sentence. It never sees your Google password.

### JSON is a labeled box

Almost every request and response is JSON: curly braces, labels, values. Text goes in quotes; numbers and `true`/`false` do not.

```json
{ "dish": "Pizza", "size": "Large", "extraCheese": true }
```

When your code sends `role: "user", content: "Hi!"` to Claude, that one labeled box is the whole message.

### Endpoints and query parameters

An **endpoint** is a fixed URL that always means the same thing (Tavily search is always `api.tavily.com/search`). **Parameters** customise a call without a new endpoint: after a `?` in a URL, or in a request body (`max_results`, `search_depth`). Same endpoint, same shape; only the parameters move.

### The five HTTP verbs

| Verb | Meaning | Restaurant version |
| --- | --- | --- |
| GET | Read | Check on your order |
| POST | Create | Place a new order |
| PUT | Replace the whole thing | Swap the whole order |
| PATCH | Change one detail | Tweak one detail |
| DELETE | Remove | Cancel it |

With Apify you POST to start a scraper run, GET its status, and DELETE a schedule you no longer need.

### Body versus headers

The **body** is the order itself (the JSON). **Headers** ride alongside: the format you send (`Content-Type: application/json`), who you are (`Authorization: Bearer ...`). A GET has no body. Calls to Claude carry a content-type header and an `x-api-key`; leave one out and the call fails before Claude sees your message.

:::tip Header habits
Never put a key in the URL (URLs get logged and pasted). Always set `Content-Type` when sending a body. Keep keys in environment variables, and use a separate key per project so one leak does not mean rotating everything.
:::

### Authentication ladder

From weaker to stronger: no auth, an API key, a bearer token, OAuth 2.0. API keys and bearer tokens are what modern AI tools use. OAuth is the "sign in once, get a token" flow behind connectors. Others you may meet: Basic and Digest auth, OAuth 1.0, custom or query-string auth (avoid the last).

### Testing a call

**Postman** is a visual form for building a request, a friendly first stop before putting a call into n8n or code, and it can show the equivalent cURL command. **cURL** makes the same request from a terminal, like phoning the kitchen directly. The three real shapes in the guide (Tavily, Apify, Claude) all follow the same pattern: bearer token, content-type header, JSON body, JSON response.

### Status codes

Only the first digit matters at first: **2xx** good news, **4xx** you slipped up, **5xx** they did.

| Code | Meaning |
| --- | --- |
| 200 / 201 / 204 | OK / created / done, nothing to return |
| 400 | Bad request (malformed) |
| 401 | Unauthorized (missing or wrong key) |
| 403 | Forbidden (known, but not allowed) |
| 404 | Not found |
| 405 | Method not allowed |
| 429 | Too many requests (slow down) |
| 500 / 502 / 503 / 504 | Server error / bad gateway / unavailable / gateway timeout |

Whose fault it is tells you what to do: fix your request (4xx) or wait and retry (5xx). A 401 from Tavily means a wrong or expired key; a 429 means add a delay.

### When it gets real

Rate limiting (a cap on how fast you may ask), pagination (big answers one page at a time), webhooks (the kitchen calls you), and error handling. The guide names these without detail. **Docs and versioning:** read the provider's docs first, and pin a version; Claude requires an `anthropic-version` header so integrations keep working as new features arrive.

## Common mistakes

| Mistake | Symptom | Fix |
| --- | --- | --- |
| Key in the URL | Key in logs and chat | Put it in a header |
| Forgetting `Content-Type` | Valid JSON read as garbage | Set `application/json` |
| Hammering an API | 429 | Add a delay or backoff |
| Treating every error alike | Retrying a 401 forever | 4xx: fix the request; 5xx: retry later |

## Interview corner

:::qa What is the difference between a header and the body?
The body is the data you are sending (the order). Headers are metadata about it: the format, who you are, how to handle it.
:::

:::qa What do 401, 403 and 429 mean?
401: not authenticated (missing or wrong key). 403: authenticated but not allowed. 429: you are sending requests faster than the limit.
:::

:::qa How does a Claude connector work?
Claude makes a normal API request to the service (for example Gmail) with a token you approved via OAuth, receives JSON, and summarises it. It never sees your password.
:::

## Quick revision

- [ ] I can name the five verbs and what each does
- [ ] I can say what goes in a header and what goes in a body
- [ ] I can read a status code by its first digit
- [ ] I know why a key never goes in a URL

## Sources and further reading

- Instructor's guide: [Claude and AI, properly explained](https://ai-automation-with-mayank.netlify.app/) (part 1, APIs). The guide's text was read in full from its 13 sections.
- [Class 01 notes]({{src:classes_transcription_summary/01 - 27 June - Python Setup & API Basics.md}})
