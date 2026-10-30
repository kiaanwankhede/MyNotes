# MyNotes

Study notes and interview prep, one "book" per subject, all in one reader.

- `index.html` is the reader. Open it in a browser, or publish the repo with GitHub Pages.
- `books/<subject>/` holds each subject: a `book.json` and a `chapters/` folder of Markdown files.
- `library.json` lists which books appear and in what order.
- `build/` holds the script that turns every book into `index.html`.

## Books

| Book | Folder |
| --- | --- |
| Agentic AI 3.0 | `books/agentic-ai/` |

## Rebuild the reader

```bash
python3 build/build.py .
```

Diagrams are drawn at build time with the Mermaid CLI (`mmdc`). If it is not installed, diagrams show as collapsed source instead.

## Add a new subject (for example SAP BTP or SAP AI)

1. Create `books/sap-btp/book.json` (copy the one from `agentic-ai` and change the id, titles, source links and chapter list).
2. Put one Markdown file per chapter in `books/sap-btp/chapters/`.
3. Add `"sap-btp"` to `library.json`.
4. Rebuild. A book switcher appears at the top of the reader. The link and repo stay the same.

Chapter files support callouts (`:::key`, `:::tip`, `:::trap`, `:::analogy`, `:::beyond`, `:::pitch`), tap-to-reveal questions (`:::qa`), diagrams (` ```mermaid `), highlights (`==text==`) and checklists (`- [ ]`).

## Publish as a website

Repository Settings, then Pages, then deploy from branch `main` and folder `/ (root)`.
The site appears at `https://kiaanwankhede.github.io/MyNotes/`.
