#!/usr/bin/env python3
"""Copy your highlights (never your private chapter notes) into the site, for browsers without a token.

Reads highlights.json from the private highlights repo with the HIGHLIGHTS_TOKEN secret (a read-only token),
keeps only the fields the reader needs to show each highlight, and writes highlights-public.json next to
index.html. Writes changed=true or changed=false to $GITHUB_OUTPUT by comparing with the copy that is live now.
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


def private_items(token):
    data = get_json(API, {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                          "X-GitHub-Api-Version": "2022-11-28"})
    raw = base64.b64decode(data["content"]).decode("utf-8") if data.get("content") else "{}"
    items = json.loads(raw).get("items", {})        # the "notes" part (private chapter notes) is never read
    return {k: {f: v[f] for f in KEEP if f in v} for k, v in items.items()
            if isinstance(v, dict) and not v.get("del") and v.get("text")}


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
        items = private_items(token)
    except Exception as e:                          # keep what is live, never publish an empty copy by accident
        print("::warning::Could not read your highlights (%s). Keeping the copy that is live now." % e)
        if live:
            with open(OUT, "w") as f:
                json.dump(live, f, ensure_ascii=False)
        say(False)
        return 0
    copy = {"v": 1, "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": items}
    with open(OUT, "w") as f:
        json.dump(copy, f, ensure_ascii=False)
    print("highlights copied:", len(items))
    say(not live or live.get("items") != items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
