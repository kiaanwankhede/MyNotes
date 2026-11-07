# Chapter style guide (reader v2)

Every chapter in every book follows this. The reader (`index.html`) and GitHub both render it.

## Building blocks

| Block | Markdown | Renders as |
|---|---|---|
| At a glance | `> [!NOTE]` + first line `> **📍 At a glance**` | Blue box |
| Tip | `> [!TIP]` | 💡 green box |
| In production | `> [!IMPORTANT]` + first line `> **🏭 In production**` | Purple box |
| Pitfall | `> [!WARNING]` | ⚠️ amber box |
| Security | `> [!CAUTION]` | 🔒 red box |
| Diagram | a ` ```mermaid ` code block (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`) | Drawn diagram |
| Interview answer | `<details class="qa"><summary>Question</summary>` + blank line + bullets + blank line + `</details>` | Click to reveal |
| Verified | `✅ *Verified: what was run (details at the end).*` | One short line |

- A bold first line inside a callout becomes its title.
- Leave a blank line after `<summary>…</summary>` and before `</details>`, or the bullets will not render.

## Chapter shape

1. Title, then a one-line italic subtitle
2. **📍 At a glance** box: you will learn, you will build, level, time, builds on
3. **After this chapter you can** bullets
4. Numbered concept sections (`## N.1 …`):
   - bullets, with no paragraph longer than two lines
   - a short runnable snippet per concept
   - at least **one Mermaid diagram per chapter** (a loop, a flow, a sequence or a state machine)
   - comparison **tables** where they help (options, trade-offs, "pick X when")
   - ⚠️ pitfalls, 🔒 security and 🏭 in-production boxes where they apply
   - ✅ one-line verified marker instead of long "Checked" text
5. **Added by Claude, not from the sources** section (labelled; also end every 🏭 box with *Added by Claude*)
6. **Interview corner:**
   - a "What interviewers listen for" line
   - questions graded 🟢 Basic, 🟡 Intermediate and 🔴 Senior, as collapsible `qa` blocks
   - each answer is 2 to 4 bullets plus one *Stronger answer*
   - one 🧩 design question in a TIP box
7. **Cheat sheet**: one code block or a small table
8. **Recap**, **Practice**, **How this chapter was checked** (full test details live here), **Sources and further reading** (web sources for any industry claim), Previous/Next links

## Rules

- Keep section numbers stable where possible. If they change, update the master's "Where covered" in the same batch.
- Class-specific sections ("Questions from the class" and the like) stay where they are, polished. They are not removed.
- Any current-state claim (versions, companies, framework landscape) is web-checked and sourced.
- Emojis only as block markers and level badges, not sprinkled in text.

## Highlights (reader feature, nothing to do per chapter)
- Readers highlight by selecting text and tapping Highlight. Highlights live in the private repo `MyNotes-highlights` (`highlights.json`), not in chapter files.
- A highlight is found again by its exact text plus 40 characters either side, so adding sections or editing nearby lines keeps it.
- **Rewriting a sentence that may be highlighted:** keep the key phrase if the meaning is unchanged. A fully rewritten line moves to "Needs attention" on that page, so mention it in the batch summary.
- Chapter file names are part of the key: renaming a chapter file orphans its highlights, so avoid renames.
- Headings, bullets, table rows and callouts are all highlightable. "★ Marked only" shows just the highlighted lines under their headings.
- **My highlights page** (`#highlights`, also in the chapter menu and the ⚙ panel): every highlight across all books, grouped by book and chapter, with search, book filter, Open in chapter, Remove and Copy all. Chapter titles come from `SUMMARY.md`, so keep titles and file names there accurate.

## Project chapters (Projects book)
Project chapters use a write-up shape instead of the lesson shape:
- Title, italic one-line subtitle, then a `> [!NOTE]` **📍 Project card**: Problem, Stack, You practise, Status (honest: class example / run locally / deployed), Level and time to rebuild, Builds on
- A `> [!WARNING]` **Short write-up** box when the material is thin
- An **Architecture** Mermaid diagram right after "What it is"
- The numbered body sections (keep their numbers: the master cites them)
- Unnumbered **From demo to production** table (area · in the project · needed for production)
- Unnumbered **Talking about this project** with a `> [!TIP]` **🎤 60-second pitch** (problem, what I built, key decisions, how I verified it, next or honest limits)
- Interview corner (graded `qa` blocks, senior questions, 🧩 design question), Added by Claude, Cheat sheet (files, commands or design choices), Recap, Practice, How checked, Sources

## Registering a new book (reader)
- Add one entry to `books.json`: `slug` (folder name under `books/`), `title`, `shelf` (Foundations, GenAI & Agents, Projects or SAP; add a new shelf name to `shelves` if needed) and a one-line `blurb`.
- The book needs `books/<slug>/SUMMARY.md` and `README.md`. No change to `index.html` is needed; the library page and the "Book ▾" picker read `books.json`.
- Empty shelves are hidden, so the SAP shelf appears when its first book is registered.
