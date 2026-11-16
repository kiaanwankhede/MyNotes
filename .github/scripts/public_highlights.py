#!/usr/bin/env python3
"""Copy your highlights and chapter notes into the site, for browsers without a token (view only).

Reads highlights.json from the private highlights repo with the HIGHLIGHTS_TOKEN secret (a read-only token),
keeps only the fields the reader needs (each highlight, and the text of each chapter note), and writes
highlights-public.json next to index.html. Everything in it is public, as agreed. Writes changed=true or changed=false to $GITHUB_OUTPUT by comparing with the copy that is live now.
If the private repo cannot be read, the live copy is kept, so the office view never goes blank by accident.
"""
import base64, datetime, json, os, sys, urllib.error, urllib.request

API = os.environ.get("HL_API_URL", "https://api.github.com/repos/kiaanwankhede/MyNotes-highlights/contents/highlights.json")
LIVE = os.environ.get("HL_LIVE_URL", "https://kiaanwankhede.github.io/MyNotes/highlights-public.json")
OUT = os.environ.get("HL_OUT", "highlights-public.json")
KEEP = ("id", "book", "ch", "text", "pre", "post", "kind", "u")   # what the reader needs to place a highlight


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def private_data(token):
    data = get_json(API, {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                          "X-GitHub-Api-Version": "2022-11-28"})
    raw = base64.b64decode(data["content"]).decode("utf-8") if data.get("content") else "{}"
    data = json.loads(raw)
    items = {k: {f: v[f] for f in KEEP if f in v} for k, v in data.get("items", {}).items()
             if isinstance(v, dict) and not v.get("del") and v.get("text")}
    notes = {k: {"text": v["text"], "u": v.get("u", 0)} for k, v in data.get("notes", {}).items()
             if isinstance(v, dict) and not v.get("del") and v.get("text")}
    return items, notes


def live_copy():
    try:
        return get_json(LIVE)
    except (urllib.error.URLError, ValueError, OSError):
        return None


def say(changed):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write("changed=%s\n" % ("true" if changed else "false"))
    print("changed:", changed)


def main():
    live = live_copy()
    token = os.environ.get("HIGHLIGHTS_TOKEN", "").strip()
    try:
        if not token:
            raise RuntimeError("the HIGHLIGHTS_TOKEN secret is not set")
        items, notes = private_data(token)
    except Exception as e:                          # keep what is live, never publish an empty copy by accident
        print("::warning::Could not read your highlights (%s). Keeping the copy that is live now." % e)
        if live:
            with open(OUT, "w") as f:
                json.dump(live, f)
        say(False)
        return 0
    copy = {"v": 1, "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": items, "notes": notes}
    with open(OUT, "w") as f:
        json.dump(copy, f)   # keep \u escapes: a highlight's context can hold half an emoji
    print("highlights copied:", len(items), "| chapter notes copied:", len(notes))
    say(not live or live.get("items") != items or live.get("notes", {}) != notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
