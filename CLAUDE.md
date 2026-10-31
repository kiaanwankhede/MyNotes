# Standing instructions for this repo

These come from the owner (Hitesh) and apply to every session.

1. **Do only what was asked.** Do not make decisions on your own; ask when a choice is the owner's to make.
2. **Use only fully read sources.** Never use search-result excerpts as a source. Fetch the whole page or file first, and say honestly what was not read.
3. **Name sources in every chapter** (a "Sources and further reading" list, plus a line in any section built from docs).
4. **One topic per book.** Craft pages, instructor sites and project ideas go into the chapter they support, in study order, never in a separate chapter at the end. LangGraph is not started; do not create it ahead of time. Frontend material is dropped.
5. **Never reproduce secrets.** If a key appears in a notebook or Colab, flag it and do not copy it.
6. **After every prompt, update the coverage table.** Run these, in order, before replying:
   - `python3 -I build/sources.py snapshot <book> /path/to/Live-Class-2026` for each book, if any repo file's review level changed (edit `books/*/review_levels.json` first);
   - edit `coverage_external.json` if any outside source (docs, sites, slides, Craft) was read or skipped;
   - regenerate the Excel master (`MASTER_COVERAGE.xlsx`): `python3 -I build/master_analyze.py /path/to/Live-Class-2026 /path/to/docsrc`, then `python3 -I build/master_xlsx.py`, then recalc it; manual changes go in `build/master_overrides.json`;
   - `python3 -I build/status.py --log "one line of what changed"` to regenerate `STATUS.md` and add the change-log line;
   - rebuild with `python3 -I build/build.py .`, then commit `STATUS.md` with the rest.
   Tell the owner in the reply what moved in the table.
7. **Commit trailers** are required on every commit and push goes to `main` of `kiaanwankhede/MyNotes`.
