#!/usr/bin/env python3
"""Update the profile robot: README stats line and the composed assets/robot.svg.

Inputs, all from public GitHub data for USER:
- mood: commits in the last 7 days, from public push events (each commit counted once).
- power level: inside the ascending mood, also from the 7-day count.
- streak: consecutive UTC days, ending today or yesterday, with at least one public commit.
- evolution: public commits in the last 365 days unlock gear.
Streak and evolution come from the commit search API (public repos only, default branches).

The README block is only rewritten when its text changes. Its date is the day of the
last change, so the workflow does not commit every day just for a date.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_robots  # noqa: E402

USER = "0xgui"
API = "https://api.github.com"
START = "<!-- robot:start -->"
END = "<!-- robot:end -->"
ZERO_SHA = "0" * 40
EASTER_EGG_PERCENT = 2

MOODS = ("sleeping", "idle", "busy", "ascending", "fell-over")
LABELS = {"sleeping": "Sleeping", "idle": "Idle", "busy": "Busy", "ascending": "Ascending", "fell-over": "Fell over"}
ALTS = {m: f"Robot is {m}" for m in MOODS} | {"fell-over": "Robot fell over"}
# Power levels inside the ascending mood (21+ commits in 7 days): (minimum commits, level)
POWER_LEVELS = ((50, 3), (35, 2), (21, 1))
# Evolution gear by public commits in the last 365 days: (minimum commits, tier). Names in draw_robots.GEAR.
EVOLUTION = ((300, 4), (150, 3), (75, 2), (25, 1), (0, 0))
SEARCH_PAGES = 10  # the search API returns at most 1000 results
WORKFLOW_URL = f"https://github.com/{USER}/{USER}/actions/workflows/robot.yml"
DATE_PREFIX = "Last changed "
HERE = os.path.dirname(__file__)


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
        url = next_link(link)
    return len(shas)


def next_link(link):
    return next((p.split(";")[0].strip(" <>") for p in link.split(",") if 'rel="next"' in p), None)


def commit_history(today):
    """Public commits in the last 365 days: (total, set of UTC days with a commit).

    Pages through newest first only while the streak could still reach further back.
    """
    since = today - dt.timedelta(days=364)
    q = urllib.parse.quote(f"author:{USER} is:public author-date:>={since.isoformat()}")
    shas, days, total = set(), set(), 0
    for page in range(1, SEARCH_PAGES + 1):
        data, _ = get_json(f"{API}/search/commits?q={q}&sort=author-date&order=desc&per_page=100&page={page}")
        total = data["total_count"]
        items = data.get("items", [])
        for item in items:
            if item["sha"] in shas:
                continue
            shas.add(item["sha"])
            when = dt.datetime.fromisoformat(item["commit"]["author"]["date"].replace("Z", "+00:00"))
            days.add(when.astimezone(dt.timezone.utc).date())
        oldest = min(days) if days else today
        if len(items) < 100 or streak(days, today) < (today - oldest).days:
            break
    return total, days


def streak(days, today):
    """Consecutive days with a commit, ending today, or yesterday if today has none yet."""
    day = today if today in days else today - dt.timedelta(days=1)
    n = 0
    while day in days:
        n += 1
        day -= dt.timedelta(days=1)
    return n


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


def power_level(count):
    return next((level for minimum, level in POWER_LEVELS if count >= minimum), 1)


def evolution_tier(year_total):
    return next(tier for minimum, tier in EVOLUTION if year_total >= minimum)


def render(mood, count, day, level=1, days_in_row=0, year_total=0, tier=0):
    commits = "commit" if count == 1 else "commits"
    label = LABELS[mood] + (f", power level {level}" if mood == "ascending" else "")
    alt = ALTS[mood] + (f" at power level {level}" if mood == "ascending" else "")
    gear = draw_robots.GEAR[tier]
    run = f"{days_in_row}-day streak" if days_in_row else "No streak right now"
    year = "commit" if year_total == 1 else "commits"
    return "\n".join([
        START,
        '<p align="center">',
        f'  <img src="assets/robot.svg" alt="{alt}, evolution {gear}, {run.lower()}" width="220"><br>',
        f"  <b>{label}</b>: {count} {commits} in the last 7 days. {run}. "
        f"Evolution: {gear} ({year_total} {year} in the last year).<br>",
        f"  <sub>This robot updates itself every day from my public GitHub activity. "
        f'<a href="{WORKFLOW_URL}">See how</a>. {DATE_PREFIX}{day.isoformat()}.</sub>',
        "</p>",
        END,
    ])


def without_date(block):
    """The block with its date removed, so a new day alone is not a change."""
    i = block.find(DATE_PREFIX)
    return block if i == -1 else block[:i] + block[i + len(DATE_PREFIX) + 10:]


def write_if_changed(path, data):
    old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
    if old != data:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(data)
    return old != data


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--readme", default=os.path.join(HERE, "..", "README.md"))
    parser.add_argument("--svg", default=os.path.join(HERE, "..", "assets", "robot.svg"))
    parser.add_argument("--mood", choices=MOODS)
    parser.add_argument("--count", type=int, help="commits in the last 7 days")
    parser.add_argument("--streak", type=int, help="streak in days")
    parser.add_argument("--year", type=int, help="public commits in the last 365 days")
    parser.add_argument("--print", action="store_true", help="print the block instead of writing")
    args = parser.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    count = args.count if args.count is not None else count_commits(now)
    if args.streak is None or args.year is None:
        year_total, days = commit_history(today)
    days_in_row = args.streak if args.streak is not None else streak(days, today)
    year_total = args.year if args.year is not None else year_total
    mood = args.mood or mood_for(count, today)
    level, tier = power_level(count), evolution_tier(year_total)
    block = render(mood, count, today, level, days_in_row, year_total, tier)
    art = draw_robots.compose(mood, level, tier, days_in_row)
    summary = f"{mood}, level {level}, {count} commits, {days_in_row}-day streak, {year_total} this year, {draw_robots.GEAR[tier]}"

    if args.print:
        print(block)
        return 0

    with open(args.readme, encoding="utf-8", newline="") as f:
        text = f.read()
    start, end = text.find(START), text.find(END)
    if start == -1 or end == -1 or end < start:
        sys.exit(f"robot markers not found in {args.readme}")
    svg_changed = write_if_changed(args.svg, art)
    current = text[start:end + len(END)]
    if without_date(current) == without_date(block):
        print(f"{'svg updated' if svg_changed else 'unchanged'}: {summary}")
        return 0
    with open(args.readme, "w", encoding="utf-8", newline="") as f:
        f.write(text[:start] + block + text[end + len(END):])
    print(f"updated: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
