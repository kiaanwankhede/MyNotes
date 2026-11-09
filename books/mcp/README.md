# MCP

Notes built from the Live Class 2026 course and other sources. Chapters are in study order.

## Study path for a Gen AI developer

| Goal | Read | Then build |
|---|---|---|
| Know when MCP is worth it | Ch 1 → 2 | decide: `@tool`, MCP or A2A for one of your use cases |
| Understand what goes over the wire | Ch 3 → 4 | watch a real handshake and a tool call in the wiretap |
| Build a server properly | Ch 5 | a FastMCP server with `ToolError`, annotations and an in-memory pytest suite |
| Ship it | Ch 6 | an HTTP server with `/health`, in a container, behind auth |
| Keep up with the spec | Ch 7 | a client that works with the current library |
| Use it from LangChain | [Langchain Ch 12](../langchain/12-mcp-in-langchain.md) | an agent over two servers with prefixed tool names |
| Interview prep | Ch 8 (incl. the debugging round) | |

- **Fast revision:** the 🏭 *In production* and 🔒 *Security* boxes, Interview corners and Cheat sheets
- Sections marked *added by Claude* go beyond the class; ✅ marks show what was run and on which version
