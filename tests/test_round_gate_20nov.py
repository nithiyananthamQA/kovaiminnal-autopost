"""ours 20 Nov (owner: "chennai why 45 post"): a late GitHub schedule run never starts a second pick round (poster/round_gate.py)"""
import datetime as d
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "poster"))
import round_gate as G      # noqa: E402

UTC = d.timezone.utc


def at(day, h, m=0):
    return d.datetime(2026, 11, day, h, m, tzinfo=UTC)


def run(i, created, event="workflow_dispatch", conclusion="success"):
    return {"id": i, "event": event, "conclusion": conclusion, "created_at": created.strftime("%Y-%m-%dT%H:%M:%SZ")}


class FireTime(unittest.TestCase):
    def test_same_day(self):
        self.assertEqual(G.fire_time("0 3 * * *", at(20, 4, 6)), at(20, 3, 0))      # 08:30 IST round, GitHub 66 min late

    def test_22_30_round_fired_after_midnight_utc(self):
        self.assertEqual(G.fire_time("30 22 * * *", at(21, 0, 40)), at(20, 22, 30))      # 04:00 IST round, run starts 00:40 UTC
        self.assertEqual(G.fire_time("30 22 * * *", at(20, 22, 45)), at(20, 22, 30))

    def test_hour_list(self):
        self.assertEqual(G.fire_time("30 23,3 * * *", at(20, 1, 24)), at(19, 23, 30))
        self.assertEqual(G.fire_time("30 23,3 * * *", at(20, 4, 6)), at(20, 3, 30))

    def test_bad_cron_is_none(self):
        self.assertIsNone(G.fire_time("*/5 * * * *", at(20, 4)))
        self.assertEqual(G.decide("*/5 * * * *", at(20, 4), [run(1, at(20, 4))]), "go")


class Decide(unittest.TestCase):
    def test_worker_ran_the_round_late_github_stops(self):      # 20 Nov: Worker 03:30 UTC, GitHub 04:06 UTC
        self.assertEqual(G.decide("0 3 * * *", at(20, 4, 6), [run(1, at(20, 3, 0))], self_id=9), "skip")
        self.assertEqual(G.decide("0 3 * * *", at(20, 3, 50), [run(1, at(20, 2, 59))], self_id=9), "skip")      # a minute early counts

    def test_worker_missed_github_is_the_round(self):
        self.assertEqual(G.decide("0 3 * * *", at(20, 4, 6), [], self_id=9), "go")
        self.assertEqual(G.decide("0 3 * * *", at(20, 4, 6), [run(1, at(20, 2, 40))], self_id=9), "go")      # the earlier round's run

    def test_cancelled_or_schedule_or_self_do_not_count(self):
        self.assertEqual(G.decide("0 3 * * *", at(20, 4, 6), [run(1, at(20, 3, 0), conclusion="cancelled")], self_id=9), "go")
        self.assertEqual(G.decide("0 3 * * *", at(20, 4, 6), [run(1, at(20, 3, 0), event="schedule")], self_id=9), "go")
        self.assertEqual(G.decide("0 3 * * *", at(20, 4, 6), [run(9, at(20, 4, 6))], self_id=9), "go")

    def test_running_round_counts(self):      # the Worker's round is still running (no conclusion yet)
        self.assertEqual(G.decide("30 7 * * *", at(20, 9, 0), [run(1, at(20, 7, 30), conclusion=None)], self_id=9), "skip")

    def test_after_midnight_round(self):      # 04:00 IST round: Worker 22:30 UTC, GitHub 00:40 UTC next day
        self.assertEqual(G.decide("30 22 * * *", at(21, 0, 40), [run(1, at(20, 22, 30))], self_id=9), "skip")


class Workflow(unittest.TestCase):
    def test_pick_runs_only_when_the_gate_says_go_and_gate_failure_runs_it(self):
        wf = (ROOT / ".github" / "workflows" / "pick.yml").read_text(encoding="utf-8")
        self.assertIn("run: python3 poster/round_gate.py", wf)
        self.assertIn("CRON: ${{ github.event.schedule }}", wf)
        self.assertIn("needs: gate", wf)
        self.assertIn("if: ${{ !cancelled() && needs.gate.outputs.go != '0' }}", wf)      # never `== '1'`: a failed gate = round runs
        self.assertIsNone(re.search(r"(?m)^concurrency:", wf))      # on the pick job, so a stopped run never queues / replaces one
        self.assertIn("    concurrency:      # on the job", wf)


if __name__ == "__main__":
    unittest.main()
