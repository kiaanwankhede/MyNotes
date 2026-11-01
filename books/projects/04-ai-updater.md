# Chapter 4: AI Updater

**After this chapter you can:**

- Describe a no-code MCP project built from connectors
- Explain "brain decides, tools act"
- Avoid the headline-count mistake from the live run

**Builds on:** [MCP Ch3](../mcp/03-lifecycle-json-rpc-and-capability-negotiation.md), 3.11.

## 4.1 What it is

- Aim: learn MCP **without writing code**, using Claude Desktop **connectors** (MCP servers)
- Output: a daily AI-news email draft, a calendar reminder, and a LinkedIn post

## 4.2 Flow

1. Ask for an AI update
2. Several searches run (Tavily)
3. Results are combined into a readable letter
4. Save as a **Gmail draft**, create a **recurring Calendar** reminder, save a post to **Apple Notes**
5. Repeat on a schedule

## 4.3 Connectors used

- Gmail, Google Calendar, Tavily, Apple Notes

## 4.4 Lessons

- **Brain decides, tools act.** The model picks tools and arguments; data moves only through tool calls
- **Say how much you want.** With no count per category, the model quietly dropped real stories
- **Test the output** against the sources

## 4.5 Interview corner

**Q1. What is a connector?**
- An MCP server a host can use

**Q2. Why does the search tool not write the story?**
- Tools return data; the model assembles it

## 4.6 Added by Claude, not from the sources

- The whiteboard did not label every step. Detail beyond the live run is not in the sources
- Mailing yourself drafts is safer than auto-sending

## Recap

- Four connectors, one system prompt, three outputs
- Be explicit about quantities

## Practice

1. Rebuild the flow with your connectors
2. Add a headline count per category and compare

## How this chapter was checked

- Notes from the class summary and whiteboard. Nothing run

## Sources and further reading

- Live-Class-2026, class 18 summary; MCP Ch3, 3.11

Previous: [Chapter 3, Meridian AI learner](03-meridian-ai-learner.md)
