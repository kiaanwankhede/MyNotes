#!/usr/bin/env python3
"""Builds one self-contained reader (index.html) from every book listed in library.json.

Usage:  python3 -I build/build.py <repo_root>

Repo layout:
  library.json                     {"books": ["agentic-ai", "sap-btp"]}
  books/<id>/book.json             title, source links, chapter list (file null = "soon")
  books/<id>/chapters/*.md         one markdown file per chapter

Markdown extras:
  :::key Title ... :::             callouts: key tip trap analogy note repo beyond pitch
  :::qa Question ... :::           tap-to-reveal interview question
  ```mermaid ... ```               diagram, drawn to SVG at build time (needs mmdc)
  ==highlight==                    highlighted phrase
  - [ ] item                       tickable checklist
  {{src:path/in/source/repo}}      link to a file in the book's source repo
  {{tree:path/in/source/repo}}     link to a folder in the book's source repo
"""
import hashlib
import html as H
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")

LABELS = {
    "key": "Key idea", "tip": "Pro tip", "trap": "Common trap", "analogy": "Analogy",
    "note": "Note", "repo": "Repo note", "pitch": "Say it in 30 seconds",
    "beyond": "Beyond the class",
}


# ---------- diagrams ----------
def draw_mermaid(src):
    """Return inline SVG for a mermaid source, or None if the CLI is unavailable."""
    key = hashlib.sha1(src.encode("utf-8")).hexdigest()[:10]
    os.makedirs(CACHE, exist_ok=True)
    cached = os.path.join(CACHE, key + ".svg")
    if not os.path.exists(cached):
        if not shutil.which("mmdc"):
            return None
        tmp = tempfile.mkdtemp()
        try:
            inp, out = os.path.join(tmp, "d.mmd"), os.path.join(tmp, "d.svg")
            open(inp, "w", encoding="utf-8").write(src)
            r = subprocess.run(["mmdc", "-i", inp, "-o", out, "-b", "transparent", "-t", "neutral"],
                               capture_output=True, text=True, timeout=120)
            if r.returncode != 0 or not os.path.exists(out):
                sys.stderr.write("mmdc failed: %s\n" % r.stderr[-300:])
                return None
            shutil.copy(out, cached)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    svg = open(cached, encoding="utf-8").read()
    svg = svg.replace("my-svg", "d" + key)          # unique ids so inline SVGs do not collide
    svg = re.sub(r"^<\?xml.*?\?>\s*", "", svg)
    return svg


# ---------- markdown ----------
def md_render(text):
    m = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    return m.convert(text)


def highlight_marks(htm):
    parts = re.split(r"(<pre.*?</pre>|<code>.*?</code>|<svg.*?</svg>)", htm, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"==(.+?)==", r"<mark>\1</mark>", parts[i])
    return "".join(parts)


def render(text, book):
    stash = {}

    def keep(htm):
        k = "@@STASH%d@@" % len(stash)
        stash[k] = htm
        return "\n\n" + k + "\n\n"

    def src_link(m):
        kind, path = m.group(1), m.group(2).strip()
        base = book.get("source_base" if kind == "src" else "tree_base", "")
        return base + urllib.parse.quote(path)
    text = re.sub(r"\{\{(src|tree):(.+?)\}\}", src_link, text)

    def mer(m):
        src = m.group(1).strip("\n")
        svg = draw_mermaid(src)
        if svg:
            return keep('<div class="diagram" role="img" aria-label="Diagram">%s</div>' % svg)
        return keep('<details class="diagram-src"><summary>Diagram (source)</summary><pre><code>%s</code></pre></details>' % H.escape(src))
    text = re.sub(r"```mermaid\n(.*?)\n```", mer, text, flags=re.S)

    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        d = re.match(r"^:::(\w+)\s*(.*)$", ln)
        if d and d.group(1) in list(LABELS) + ["qa"]:
            kind, title = d.group(1), d.group(2).strip()
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                body.append(lines[i])
                i += 1
            inner = render("\n".join(body), book)
            if kind == "qa":
                out.append(keep('<details class="qa"><summary>%s</summary><div class="ans">%s</div></details>'
                                % (re.sub(r"`([^`]+)`", r"<code>\1</code>", H.escape(title)), inner)))
            else:
                t = '<div class="ct">%s%s</div>' % (LABELS[kind], ("<em>%s</em>" % H.escape(title)) if title else "")
                out.append(keep('<aside class="callout %s">%s%s</aside>' % (kind, t, inner)))
        else:
            out.append(ln)
        i += 1
    htm = md_render("\n".join(out))
    htm = highlight_marks(htm)
    htm = htm.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
    htm = re.sub(r"<li>\[ \] (.*?)</li>", r'<li class="task"><label><input type="checkbox"><span>\1</span></label></li>', htm, flags=re.S)
    htm = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', htm)
    for k, v in stash.items():
        htm = htm.replace("<p>%s</p>" % k, v).replace(k, v)
    return htm


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48]


def article(book, ch, body_md, prev, nxt):
    bid, cid = book["id"], ch["id"]
    title, lead, meta = ch["title"], "", []
    lines = body_md.split("\n")
    start = 0
    for idx, ln in enumerate(lines):
        if ln.startswith("# "):
            title = ln[2:].strip()
        elif ln.startswith("> lead:"):
            lead = ln[len("> lead:"):].strip()
        elif ln.startswith("meta:"):
            meta = [x.strip() for x in ln[5:].split("|") if x.strip()]
        elif ln.strip() == "":
            continue
        else:
            start = idx
            break
    body = render("\n".join(lines[start:]), book)
    seen = {}

    def hid(m):
        lvl, inner = m.group(1), m.group(2)
        s = bid + "-" + cid + "-" + slug(re.sub(r"<.*?>", "", inner))
        n = seen.get(s, 0)
        seen[s] = n + 1
        return '<h%s id="%s">%s</h%s>' % (lvl, s + ("-%d" % n if n else ""), inner, lvl)
    body = re.sub(r"<h([23])[^>]*>(.*?)</h\1>", hid, body, flags=re.S)
    num, part = ch.get("num", ""), ch["part"]
    if num and num != "A":
        crumb = "%s &middot; Chapter %s" % (H.escape(part), num)
    elif num == "A":
        crumb = "Part A &middot; Foundations"
    else:
        crumb = H.escape(part)
    chips = "".join('<span class="chip%s">%s</span>' % ("" if i == 0 else " plain", H.escape(x)) for i, x in enumerate(meta))
    lead_html = re.sub(r"`([^`]+)`", r"<code>\1</code>", H.escape(lead)) if lead else ""
    jump = '<details class="jump"><summary>Jump to a section</summary><nav class="jl"></nav></details>'
    pager = '<div class="pager">'
    pager += ('<button data-id="%s-%s"><small>Previous</small><b>%s</b></button>' % (bid, prev["id"], H.escape(prev["title"]))) if prev else "<span style='flex:1'></span>"
    pager += ('<button class="next" data-id="%s-%s"><small>Next</small><b>%s</b></button>' % (bid, nxt["id"], H.escape(nxt["title"]))) if nxt else ""
    pager += "</div>"
    read = '<button class="readbtn" data-id="%s-%s">Mark this chapter as read</button>' % (bid, cid) if cid != "home" else ""
    return ('<article id="ch-%s-%s" hidden><p class="crumb">%s</p><h1>%s</h1>%s%s%s%s%s%s</article>'
            % (bid, cid, crumb, H.escape(title), ('<p class="lead">%s</p>' % lead_html) if lead_html else "",
               ('<div class="meta">%s</div>' % chips) if chips else "", jump, body, read, pager))


def quiz_article(book, prev, nxt):
    bid = book["id"]
    return ('<article id="ch-%s-quiz" hidden><p class="crumb">Welcome</p><h1>Quiz me</h1>'
            '<p class="lead">Interview questions from every ready chapter, one at a time. Answer out loud, then check.</p>'
            '<div class="quizroot" data-book="%s"></div></article>' % (bid, bid))


def make_bank(bdir, chapters):
    """Collect every :::qa block from the written chapters into one searchable page."""
    skip = {"home", "quiz", "bank", "glossary", "cheat", "projects", "craft"}
    out, total = [], 0
    for c in chapters:
        if c["id"] in skip or not c.get("file") or c["file"].startswith("@"):
            continue
        text = open(os.path.join(bdir, "chapters", c["file"]), encoding="utf-8").read()
        qas = re.findall(r"^:::qa (.*?)\n(.*?)\n:::[ \t]*$", text, flags=re.S | re.M)
        if not qas:
            continue
        label = ("Chapter %s: " % c["num"]) if c.get("num") and c["num"] != "A" else ("Primer: " if c.get("num") == "A" else "")
        out.append("## %s%s\n" % (label, c["title"]))
        for q, a in qas:
            out.append(":::qa %s\n%s\n:::\n" % (q.strip(), a.strip()))
            total += 1
    head = ("# Interview question bank\n> lead: Every interview question from every chapter in one place, in chapter order. "
            "Tap a question to reveal the answer.\nmeta: %d questions | Rebuilt automatically from the chapters\n\n" % total)
    return head + "\n".join(out)


def build_book(root, bid):
    bdir = os.path.join(root, "books", bid)
    book = json.load(open(os.path.join(bdir, "book.json"), encoding="utf-8"))
    chapters = []
    for c in book["chapters"]:
        chapters.append(c)
        if c["id"] == "home":          # Quiz me sits right after the start page
            chapters.append({"id": "quiz", "num": "", "title": "Quiz me", "part": "Welcome", "file": "@quiz"})
    ready = [c for c in chapters if c.get("file")]
    arts = []
    for i, c in enumerate(ready):
        prev = ready[i - 1] if i > 0 else None
        nxt = ready[i + 1] if i + 1 < len(ready) else None
        if c["file"] == "@quiz":
            arts.append(quiz_article(book, prev, nxt))
        elif c["file"] == "@bank":
            arts.append(article(book, c, make_bank(bdir, chapters), prev, nxt))
        else:
            md = open(os.path.join(bdir, "chapters", c["file"]), encoding="utf-8").read()
            arts.append(article(book, c, md, prev, nxt))
    meta = {"id": book["id"], "title": book["title"], "short": book.get("short", book["title"]),
            "chapters": [{"id": c["id"], "num": c.get("num", ""), "title": c["title"], "part": c["part"],
                          "ready": bool(c.get("file"))} for c in chapters]}
    return meta, arts


def main():
    root = os.path.abspath(sys.argv[1])
    lib = json.load(open(os.path.join(root, "library.json"), encoding="utf-8"))
    metas, arts = [], []
    for bid in lib["books"]:
        m, a = build_book(root, bid)
        metas.append(m)
        arts.extend(a)
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
    js = open(os.path.join(HERE, "app.js"), encoding="utf-8").read()
    page = (tpl.replace("/*CSS*/", css).replace("/*JS*/", js)
            .replace("<!--ARTICLES-->", "\n".join(arts))
            .replace("/*BOOKS*/", "window.__BOOKS__ = " + json.dumps(metas) + ";"))
    out = os.path.join(root, "index.html")
    open(out, "w", encoding="utf-8").write(page)
    print("built", out, len(page) // 1024, "KB;", len(metas), "book(s),", len(arts), "pages")


if __name__ == "__main__":
    main()
