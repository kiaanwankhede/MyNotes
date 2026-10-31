#!/usr/bin/env python3
"""Rebuilds STATUS.md, the coverage table for the whole library.

Usage:
  python3 -I build/status.py                    # regenerate STATUS.md
  python3 -I build/status.py --log "what changed"   # add a dated line to the change log first

Repo numbers come from books/*/sources.json (run build/sources.py snapshot first).
Everything else comes from coverage_external.json, which is edited by hand when a
source is read.
"""
import collections
import datetime
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pct(a, b):
    return "%d%%" % round(100 * a / b) if b else "n/a"


def main():
    ext_path = os.path.join(ROOT, "coverage_external.json")
    ext = json.load(open(ext_path, encoding="utf-8"))
    if "--log" in sys.argv:
        msg = sys.argv[sys.argv.index("--log") + 1]
        ext["log"].insert(0, "%s: %s" % (datetime.date.today().isoformat(), msg))
        ext["log"] = ext["log"][:40]
        json.dump(ext, open(ext_path, "w", encoding="utf-8"), indent=1)

    files = {}
    for b in sorted(os.listdir(os.path.join(ROOT, "books"))):
        p = os.path.join(ROOT, "books", b, "sources.json")
        if not os.path.exists(p):
            continue
        for k, v in json.load(open(p, encoding="utf-8"))["files"].items():
            f = files.setdefault(k, {"status": v["status"], "cited": False})
            if v.get("cited_in"):
                f["cited"] = True

    def grp(k):
        if k.startswith("Complete MCP"):
            return "Complete MCP (TimeTrack, servers, clients)"
        m = re.match(r"Weekend (\d+)", k)
        if m:
            n = int(m.group(1))
            if n == 0:
                return "Weekend 00 (induction)"
            if n <= 2:
                return "Weekends 01-02 (Python, Project 0)"
            if n <= 7:
                return "Weekends 03-07"
            if n <= 11:
                return "Weekends 08-11"
            return "Weekends 12-15 (MCP, multi-agent, Meridian)"
        if k.startswith("classes_transcription_summary"):
            return "Class write-ups (00-22)"
        return "Repo root, scripts, workflows"

    agg = collections.OrderedDict()
    tot = collections.Counter()
    for k, v in sorted(files.items()):
        if v["status"] == "ignored":
            continue
        g = agg.setdefault(grp(k), collections.Counter())
        g[v["status"]] += 1
        g["total"] += 1
        g["cited"] += int(v["cited"])
        tot[v["status"]] += 1
        tot["total"] += 1
        tot["cited"] += int(v["cited"])

    L = []
    L.append("# Coverage status\n")
    L.append("Updated %s by `build/status.py`. This file is regenerated after every prompt.\n" % datetime.date.today().isoformat())
    L.append("**How to read it, in plain words.** For each file I use one of three levels:\n")
    L.append("- **Read properly**: I read it from start to finish and the notes use its details.")
    L.append("- **Looked through (skimmed)**: I opened it and read parts of it, or turned it into text and scanned it. The notes use its main points, not every line. Typical for notebooks, PDFs, big folders of similar files and code.")
    L.append("- **Not opened**: I have not looked at it.\n")
    L.append("*Opened at all* = read properly + looked through. Percentages count files or pages, not how much you know. A file counts as *looked through* even if I only used one idea from it, so treat *Read properly* as the number that matters.\n")
    L.append("## 1. Course repo files (%d, excluding %d lock, log and config files)\n" % (tot["total"], sum(1 for v in files.values() if v["status"] == "ignored")))
    L.append("| Area | Files | Read properly | Opened at all | Not opened |\n|---|---:|---:|---:|---:|")
    for g, c in agg.items():
        L.append("| %s | %d | %d (%s) | %s | %d |" % (g, c["total"], c["read"], pct(c["read"], c["total"]), pct(c["read"] + c["skimmed"], c["total"]), c["not_read"]))
    L.append("| **Total** | **%d** | **%d (%s)** | **%s** | **%d** |\n" % (tot["total"], tot["read"], pct(tot["read"], tot["total"]), pct(tot["read"] + tot["skimmed"], tot["total"]), tot["not_read"]))
    L.append("%d files (%s) are cited by at least one chapter.\n" % (tot["cited"], pct(tot["cited"], tot["total"])))
    L.append("## 2. Everything outside the repo\n")
    L.append("| Source | What is measured | Done | Share | Notes |\n|---|---|---:|---:|---|")
    for it in ext["items"]:
        L.append("| %s | %s | %d of %d | %s | %s |" % (it["group"], it["name"], it["done"], it["total"], pct(it["done"], it["total"]), it["note"]))
    L.append("\n## 3. Skipped on purpose\n")
    L += ["- " + s for s in ext["skipped_on_purpose"]]
    L.append("\n## 4. Structural gaps\n")
    L += ["- " + s for s in ext["structure_gaps"]]
    L.append("\n## 5. Change log (newest first)\n")
    L += ["- " + s for s in ext["log"]] or ["- (empty)"]
    open(os.path.join(ROOT, "STATUS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("wrote STATUS.md")


if __name__ == "__main__":
    main()
