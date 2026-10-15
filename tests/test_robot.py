"""Offline checks for the robot's thresholds, streak and SVG output. Run: python3 -m unittest discover tests"""

import datetime as dt
import os
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import draw_robots  # noqa: E402
import robot  # noqa: E402

TODAY = dt.date(2026, 10, 15)


def days(*offsets):
    return {TODAY - dt.timedelta(days=o) for o in offsets}


class Streak(unittest.TestCase):
    def test_no_commits(self):
        self.assertEqual(robot.streak(set(), TODAY), 0)

    def test_today_only(self):
        self.assertEqual(robot.streak(days(0), TODAY), 1)

    def test_run_ending_today(self):
        self.assertEqual(robot.streak(days(0, 1, 2, 3), TODAY), 4)

    def test_nothing_today_but_yesterday(self):
        self.assertEqual(robot.streak(days(1, 2, 3), TODAY), 3)

    def test_gap_stops_the_run(self):
        self.assertEqual(robot.streak(days(0, 1, 3, 4, 5), TODAY), 2)

    def test_last_commit_two_days_ago_is_broken(self):
        self.assertEqual(robot.streak(days(2, 3, 4), TODAY), 0)

    def test_month_boundary(self):
        run = {dt.date(2026, 10, 1) - dt.timedelta(days=i) for i in range(5)}
        self.assertEqual(robot.streak(run, dt.date(2026, 10, 1)), 5)


class History(unittest.TestCase):
    """commit_history with a fake search API: dedupes shas, uses UTC days, pages only while needed."""

    def setUp(self):
        self.real = robot.get_json

    def tearDown(self):
        robot.get_json = self.real

    def fake(self, pages):
        calls = []

        def get_json(url):
            calls.append(url)
            page = int(url.rsplit("page=", 1)[1])
            items = pages[page - 1] if page <= len(pages) else []
            return {"total_count": sum(map(len, pages)), "items": items}, ""
        return get_json, calls

    @staticmethod
    def item(sha, when):
        return {"sha": sha, "commit": {"author": {"date": when}}}

    def test_dedupe_and_utc(self):
        # 23:30 at -02:00 is already the next day in UTC
        page = [self.item("a", "2026-10-14T23:30:00-02:00"), self.item("a", "2026-10-14T23:30:00-02:00"),
                self.item("b", "2026-10-14T10:00:00+01:00")]
        robot.get_json, calls = self.fake([page])
        total, got = robot.commit_history(TODAY)
        self.assertEqual(got, {dt.date(2026, 10, 15), dt.date(2026, 10, 14)})
        self.assertEqual(len(calls), 1)
        self.assertIn("is%3Apublic", calls[0])

    def test_pages_only_while_streak_continues(self):
        full = [self.item(f"s{i}", f"{TODAY - dt.timedelta(days=i % 2)}T12:00:00Z") for i in range(100)]
        older = [self.item(f"o{i}", f"{TODAY - dt.timedelta(days=2 + i % 3)}T12:00:00Z") for i in range(100)]
        last = [self.item("z", f"{TODAY - dt.timedelta(days=9)}T12:00:00Z")]
        robot.get_json, calls = self.fake([full, older, last])
        total, got = robot.commit_history(TODAY)
        self.assertEqual(len(calls), 3)  # page 2 still ended inside the streak, page 3 is short
        self.assertEqual(robot.streak(got, TODAY), 5)
        self.assertEqual(total, 201)


class Thresholds(unittest.TestCase):
    def test_moods_unchanged(self):
        day = TODAY  # not a fell-over day
        self.assertNotEqual(robot.mood_for(5, day), "fell-over")
        got = [robot.mood_for(c, day) for c in (0, 1, 5, 6, 20, 21, 500)]
        self.assertEqual(got, ["sleeping", "idle", "idle", "busy", "busy", "ascending", "ascending"])

    def test_fell_over_is_rare(self):
        hits = sum(robot.mood_for(30, TODAY + dt.timedelta(days=i)) == "fell-over" for i in range(2000))
        self.assertTrue(10 < hits < 80, hits)

    def test_power_levels(self):
        got = {c: robot.power_level(c) for c in (21, 34, 35, 49, 50, 200)}
        self.assertEqual(got, {21: 1, 34: 1, 35: 2, 49: 2, 50: 3, 200: 3})

    def test_evolution(self):
        got = [robot.evolution_tier(c) for c in (0, 24, 25, 74, 75, 149, 150, 299, 300, 5000)]
        self.assertEqual(got, [0, 0, 1, 1, 2, 2, 3, 3, 4, 4])
        self.assertEqual(len(draw_robots.GEAR), 5)


class Output(unittest.TestCase):
    def test_every_combination_is_valid_and_small(self):
        for mood in robot.MOODS:
            for level in (1, 2, 3):
                for tier in range(5):
                    for streak in (0, 1, 365):
                        svg = draw_robots.compose(mood, level, tier, streak)
                        ET.fromstring(svg)
                        self.assertLess(len(svg.encode()), 12.5 * 1024, (mood, level, tier))

    def test_block_text(self):
        block = robot.render("ascending", 41, TODAY, 2, 12, 480, 3)
        self.assertIn("<b>Ascending, power level 2</b>: 41 commits in the last 7 days. 12-day streak. "
                      "Evolution: Jetpack (480 commits in the last year).", block)
        self.assertIn('src="assets/robot.svg"', block)
        self.assertIn("updates itself every day", block)
        quiet = robot.render("sleeping", 0, TODAY, 1, 0, 1, 0)
        self.assertIn("<b>Sleeping</b>: 0 commits in the last 7 days. No streak right now. Evolution: Bare (1 commit", quiet)

    def test_date_only_change_is_not_a_change(self):
        a = robot.render("busy", 9, TODAY, 1, 3, 80, 2)
        b = robot.render("busy", 9, TODAY + dt.timedelta(days=1), 1, 3, 80, 2)
        self.assertEqual(robot.without_date(a), robot.without_date(b))


if __name__ == "__main__":
    unittest.main()
