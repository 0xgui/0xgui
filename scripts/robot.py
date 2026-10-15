#!/usr/bin/env python3
"""Rewrite the robot block in README.md based on public commits from the last 7 days.

The block is only rewritten when the mood or the count changes. Its date is the
day of the last change, so the workflow does not commit every day just for a date.
"""

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

MOODS = ("sleeping", "idle", "busy", "ascending", "fell-over")
LABELS = {"sleeping": "Sleeping", "idle": "Idle", "busy": "Busy", "ascending": "Ascending", "fell-over": "Fell over"}
ALTS = {m: f"Robot is {m}" for m in MOODS} | {"fell-over": "Robot fell over"}
WORKFLOW_URL = f"https://github.com/{USER}/{USER}/actions/workflows/robot.yml"
DATE_PREFIX = "Last changed "


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
        return "fell-over"
    if count == 0:
        return "sleeping"
    if count <= 5:
        return "idle"
    if count <= 20:
        return "busy"
    return "ascending"


def render(mood, count, day):
    commits = "commit" if count == 1 else "commits"
    return "\n".join([
        START,
        '<p align="center">',
        f'  <img src="assets/{mood}.svg" alt="{ALTS[mood]}" width="220"><br>',
        f"  <b>{LABELS[mood]}</b>: {count} {commits} in the last 7 days<br>",
        f"  <sub>This robot updates itself every day from my public GitHub activity. "
        f'<a href="{WORKFLOW_URL}">See how</a>. {DATE_PREFIX}{day.isoformat()}.</sub>',
        "</p>",
        END,
    ])


def without_date(block):
    """The block with its date removed, so a new day alone is not a change."""
    i = block.find(DATE_PREFIX)
    return block if i == -1 else block[:i] + block[i + len(DATE_PREFIX) + 10:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", default=os.path.join(os.path.dirname(__file__), "..", "README.md"))
    parser.add_argument("--mood", choices=MOODS)
    parser.add_argument("--count", type=int)
    parser.add_argument("--print", action="store_true", help="print the block instead of writing")
    args = parser.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    count = args.count if args.count is not None else count_commits(now)
    mood = args.mood or mood_for(count, now.date())
    block = render(mood, count, now.date())

    if args.print:
        print(block)
        return 0

    with open(args.readme, encoding="utf-8", newline="") as f:
        text = f.read()
    start, end = text.find(START), text.find(END)
    if start == -1 or end == -1 or end < start:
        sys.exit(f"robot markers not found in {args.readme}")
    current = text[start:end + len(END)]
    if without_date(current) == without_date(block):
        print(f"unchanged: {mood}, {count} commits")
        return 0
    with open(args.readme, "w", encoding="utf-8", newline="") as f:
        f.write(text[:start] + block + text[end + len(END):])
    print(f"updated: {mood}, {count} commits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
