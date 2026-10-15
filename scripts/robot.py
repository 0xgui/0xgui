#!/usr/bin/env python3
"""Rewrite the robot block in README.md based on public commits from the last 7 days."""

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

USER = "0xgui"
API = "https://api.github.com"
START = "<!-- robot:start -->"
END = "<!-- robot:end -->"
ZERO_SHA = "0" * 40
EASTER_EGG_PERCENT = 2

ROBOTS = {
    "sleeping": r"""
   .---.
  [ -_- ]  z z Z
  /|___|\
   d   b
""",
    "idle": r"""
   .---.
  [ o_o ]
  /|___|\
   d   b
""",
    "busy": r"""
   .---.
  [ ^_^ ]/  *clack*
  /|___|   *clack*
   d   b
""",
    "overheating": r"""
    ~ ~ ~
   .---.
  [ @_@ ]  !!
  /|###|\
   d   b
""",
    "fell over": r"""
  *thunk*
   _____ .---.
  d|___|[ x_x ]
  b      '---'
""",
}

CAPTIONS = {
    "sleeping": "Robot status: sleeping ({count} commits this week)",
    "idle": "Robot status: idle ({count} commits this week)",
    "busy": "Robot status: busy ({count} commits this week)",
    "overheating": "Robot status: overheating ({count} commits this week)",
    "fell over": "Robot status: fell over, standing back up ({count} commits this week)",
}


def get_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-profile-robot"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        return json.load(resp), resp.headers.get("Link", "")


def push_commit_shas(event):
    payload = event.get("payload", {})
    if payload.get("commits"):
        return [c["sha"] for c in payload["commits"] if c.get("distinct", True)]
    before, head = payload.get("before"), payload.get("head")
    if not head:
        return []
    if not before or before == ZERO_SHA:
        return [head]
    try:
        data, _ = get_json(f"{API}/repos/{event['repo']['name']}/compare/{before}...{head}")
    except urllib.error.HTTPError:
        return [head]
    return [c["sha"] for c in data.get("commits", [])] or [head]


def count_commits(now):
    since = now - dt.timedelta(days=7)
    shas = set()
    url = f"{API}/users/{USER}/events/public?per_page=100"
    while url:
        events, link = get_json(url)
        for event in events:
            created = dt.datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            if event["type"] == "PushEvent" and created >= since:
                shas.update(push_commit_shas(event))
        url = next(
            (p.split(";")[0].strip(" <>") for p in link.split(",") if 'rel="next"' in p),
            None,
        )
    return len(shas)


def mood_for(count, day):
    roll = int(hashlib.sha256(day.isoformat().encode()).hexdigest(), 16) % 100
    if roll < EASTER_EGG_PERCENT:
        return "fell over"
    if count == 0:
        return "sleeping"
    if count <= 5:
        return "idle"
    if count <= 20:
        return "busy"
    return "overheating"


def render(mood, count):
    art = ROBOTS[mood].strip("\n")
    return f"{START}\n```\n{art}\n```\n{CAPTIONS[mood].format(count=count)}\n{END}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", default=os.path.join(os.path.dirname(__file__), "..", "README.md"))
    parser.add_argument("--mood", choices=sorted(ROBOTS))
    parser.add_argument("--count", type=int)
    parser.add_argument("--print", action="store_true", help="print the block instead of writing")
    args = parser.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    count = args.count if args.count is not None else count_commits(now)
    mood = args.mood or mood_for(count, now.date())
    block = render(mood, count)

    if args.print:
        print(block)
        return 0

    with open(args.readme, encoding="utf-8", newline="") as f:
        text = f.read()
    start, end = text.find(START), text.find(END)
    if start == -1 or end == -1 or end < start:
        sys.exit(f"robot markers not found in {args.readme}")
    updated = text[:start] + block + text[end + len(END):]
    if updated == text:
        print(f"unchanged: {mood}, {count} commits")
        return 0
    with open(args.readme, "w", encoding="utf-8", newline="") as f:
        f.write(updated)
    print(f"updated: {mood}, {count} commits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
