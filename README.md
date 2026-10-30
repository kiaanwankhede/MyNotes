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

## Keep the notes in step with the course repo

Each book records which course files it used, and how deeply they were reviewed:

- `books/<book>/sources.json`: every course file with its content fingerprint, review status and the chapters that cite it.
- `books/<book>/review_levels.json`: how deeply each file or folder was reviewed (`read`, `skimmed`, `not_read`).
- `books/<book>/COVERAGE.md`: a readable report of the above, including the files still to read.

When the course repo changes, pull it and run:

```bash
python3 -I build/sources.py check agentic-ai /path/to/Live-Class-2026     # new, changed and removed files
python3 -I build/sources.py snapshot agentic-ai /path/to/Live-Class-2026  # refresh the ledger afterwards
```

The check names the chapters that cite any changed file, so you know exactly what to update.

## Add a new subject (for example SAP BTP or SAP AI)

1. Create `books/sap-btp/book.json` (copy the one from `agentic-ai` and change the id, titles, source links and chapter list).
2. Put one Markdown file per chapter in `books/sap-btp/chapters/`.
3. Add `"sap-btp"` to `library.json`.
4. Rebuild. A book switcher appears at the top of the reader. The link and repo stay the same.

Chapter files support callouts (`:::key`, `:::tip`, `:::trap`, `:::analogy`, `:::beyond`, `:::pitch`), tap-to-reveal questions (`:::qa`), diagrams (` ```mermaid `), highlights (`==text==`) and checklists (`- [ ]`).

## Publish as a website

Repository Settings, then Pages, then deploy from branch `main` and folder `/ (root)`.
The site appears at `https://kiaanwankhede.github.io/MyNotes/`.
