#!/usr/bin/env python3
"""Builds one self-contained reader page from markdown chapters.
Usage: python3 -I build.py <content_dir> <out_file>
Directives in markdown:
  :::key Title / :::tip / :::trap / :::analogy / :::note / :::repo / :::pitch  ...  :::
  :::qa Question text ...answer...  :::
  ```mermaid ... ```
  ==highlight==
  - [ ] checklist item
"""
import html as H
import json
import os
import re
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))

# id, number label, title, part, source file (None = not written yet)
CHAPTERS = [
    ("home", "", "Start here", "Welcome", "home.md"),
    ("primer", "A", "Primer: what an agent is", "Part A  Foundations", "primer.md"),
    ("ch1", "1", "Introduction to LangChain", "Part B  LangChain core", "ch1.md"),
    ("ch2", "2", "The LangChain family and harness engineering", "Part B  LangChain core", None),
    ("ch3", "3", "Inside the model", "Part B  LangChain core", None),
    ("ch4", "4", "Structured output", "Part B  LangChain core", None),
    ("ch5", "5", "Tools deep dive", "Part B  LangChain core", None),
    ("ch6", "6", "Agents, memory and middleware", "Part C  Agents and middleware", None),
    ("ch7", "7", "Mastering middleware", "Part C  Agents and middleware", None),
    ("ch8", "8", "Guardrails, todo lists, resilience", "Part C  Agents and middleware", None),
    ("ch9", "9", "Shell tools and custom middleware", "Part C  Agents and middleware", None),
    ("ch10", "10", "Runtime and human-in-the-loop", "Part D  Runtime", None),
    ("ch11", "11", "Why MCP exists", "Part E  MCP", None),
    ("ch12", "12", "MCP primitives, lifecycle, JSON-RPC", "Part E  MCP", None),
    ("ch13", "13", "Capability negotiation", "Part E  MCP", None),
    ("ch14", "14", "Shutdown and transports", "Part E  MCP", None),
    ("ch15", "15", "Time Tracker project", "Part E  MCP", None),
    ("ch16", "16", "Deploying MCP servers", "Part E  MCP", None),
    ("ch17", "17", "Legacy vs modern MCP", "Part E  MCP", None),
    ("ch18", "18", "MCP inside LangChain", "Part F  Advanced", None),
    ("ch19", "19", "Multi-agent patterns", "Part F  Advanced", None),
    ("ch20", "20", "Meridian project overview", "Part F  Advanced", None),
    ("glossary", "", "Glossary", "Back matter", None),
    ("bank", "", "Interview question bank", "Back matter", None),
    ("cheat", "", "Cheat sheet", "Back matter", None),
    ("projects", "", "Mini-project ideas", "Back matter", None),
    ("craft", "", "From the Craft notes", "Back matter", None),
]

LABELS = {
    "key": "Key idea", "tip": "Pro tip", "trap": "Common trap", "analogy": "Analogy",
    "note": "Note", "repo": "Repo note", "pitch": "Say it in 30 seconds",
}


def md_render(text):
    m = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    return m.convert(text)


def highlight_marks(htm):
    parts = re.split(r"(<pre.*?</pre>|<code>.*?</code>)", htm, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r"==(.+?)==", r"<mark>\1</mark>", parts[i])
    return "".join(parts)


def render(text):
    stash = {}

    def keep(htm):
        k = "@@STASH%d@@" % len(stash)
        stash[k] = htm
        return "\n\n" + k + "\n\n"

    # mermaid
    def mer(m):
        return keep('<div class="diagram"><pre class="mermaid">%s</pre></div>' % H.escape(m.group(1).strip("\n")))
    text = re.sub(r"```mermaid\n(.*?)\n```", mer, text, flags=re.S)

    # directive blocks (no nesting)
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
            inner = render("\n".join(body))
            if kind == "qa":
                out.append(keep('<details class="qa"><summary>%s</summary><div class="ans">%s</div></details>' % (H.escape(title), inner)))
            else:
                t = '<div class="ct">%s%s</div>' % (LABELS[kind], ("<em>%s</em>" % H.escape(title)) if title else "")
                out.append(keep('<aside class="callout %s">%s%s</aside>' % (kind, t, inner)))
        else:
            out.append(ln)
        i += 1
    htm = md_render("\n".join(out))
    htm = highlight_marks(htm)
    htm = re.sub(r"<table>", '<div class="tablewrap"><table>', htm)
    htm = re.sub(r"</table>", "</table></div>", htm)
    htm = re.sub(r"<li>\[ \] (.*?)</li>", r'<li class="task"><label><input type="checkbox"><span>\1</span></label></li>', htm, flags=re.S)
    for k, v in stash.items():
        htm = htm.replace("<p>%s</p>" % k, v).replace(k, v)
    return htm


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48]


def article(cid, num, title, part, src, content_dir, prev, nxt):
    raw = open(os.path.join(content_dir, src), encoding="utf-8").read()
    # front matter: first line "# Title", then optional "> lead", then "meta: a | b"
    lead, meta = "", []
    lines = raw.split("\n")
    body_start = 0
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
            body_start = idx
            break
    body = render("\n".join(lines[body_start:]))
    # unique heading ids
    seen = {}

    def hid(m):
        lvl, inner = m.group(1), m.group(2)
        s = cid + "-" + slug(re.sub(r"<.*?>", "", inner))
        n = seen.get(s, 0)
        seen[s] = n + 1
        if n:
            s += "-%d" % n
        return '<h%s id="%s">%s</h%s>' % (lvl, s, inner, lvl)
    body = re.sub(r"<h([23])[^>]*>(.*?)</h\1>", hid, body, flags=re.S)
    crumb = ("%s &middot; Chapter %s" % (H.escape(part), num)) if num and num != "A" else H.escape(part)
    if num == "A":
        crumb = "Part A &middot; Foundations"
    chips = "".join('<span class="chip%s">%s</span>' % ("" if i == 0 else " plain", H.escape(x)) for i, x in enumerate(meta))
    pager = '<div class="pager">'
    pager += ('<button data-id="%s"><small>Previous</small><b>%s</b></button>' % (prev[0], H.escape(prev[2]))) if prev else "<span style='flex:1'></span>"
    pager += ('<button class="next" data-id="%s"><small>Next</small><b>%s</b></button>' % (nxt[0], H.escape(nxt[2]))) if nxt else ""
    pager += "</div>"
    read = '<button class="readbtn" data-id="%s">Mark this chapter as read</button>' % cid if cid != "home" else ""
    return (
        '<article id="ch-%s" hidden><p class="crumb">%s</p><h1>%s</h1>%s%s%s%s%s</article>'
        % (cid, crumb, H.escape(title), ('<p class="lead">%s</p>' % re.sub(r"`([^`]+)`", r"<code>\1</code>", H.escape(lead))) if lead else "",
           ('<div class="meta">%s</div>' % chips) if chips else "", body, read, pager)
    )


def main():
    content_dir, out_file = sys.argv[1], sys.argv[2]
    ready = [c for c in CHAPTERS if c[4]]
    arts = []
    for i, c in enumerate(ready):
        prev = ready[i - 1] if i > 0 else None
        nxt = ready[i + 1] if i + 1 < len(ready) else None
        arts.append(article(c[0], c[1], c[2], c[3], c[4], content_dir, prev, nxt))
    nav = [dict(id=c[0], num=c[1], title=c[2], part=c[3], ready=bool(c[4])) for c in CHAPTERS]
    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    css = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()
    js = open(os.path.join(HERE, "app.js"), encoding="utf-8").read()
    page = (tpl.replace("/*CSS*/", css).replace("/*JS*/", js)
            .replace("<!--ARTICLES-->", "\n".join(arts))
            .replace("/*CHAPTERS*/", "window.__CHAPTERS__ = " + json.dumps(nav) + ";"))
    open(out_file, "w", encoding="utf-8").write(page)
    print("built", out_file, len(page) // 1024, "KB,", len(arts), "chapters")


if __name__ == "__main__":
    main()
