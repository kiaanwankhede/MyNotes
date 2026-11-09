# Projects

Notes built from the Live Class 2026 course and other sources. Chapters are in study order.

## Using these projects as a Gen AI portfolio (*added by Claude*)

| Showcase | Proves | Best for roles |
|---|---|---|
| **Meridian** (Ch 3) | RAG, agents, cloud deploy, evaluation | Gen AI / ML engineer |
| **TimeTrack MCP** (Ch 2) | protocol knowledge, tool safety, testing | agent platform, integration |
| **CineBot** (Ch 1) | agent control: gating, approval, idempotency | applied AI, product engineering |

**What a reviewer looks for in the GitHub README, in this order:**
1. One-line problem and a 60-second demo GIF
2. Architecture diagram (Mermaid renders on GitHub)
3. **An eval table with real numbers** (pass rate, hit rate, cost per query)
4. How to run it in three commands (`uv sync`, `cp .env.example .env`, `uv run ...`)
5. Design decisions and known limits, stated honestly

- Pin one project at the top of your GitHub profile; quality of one beats quantity of five
- Never commit keys; add a `.env.example` and a CI job that runs the offline tests
