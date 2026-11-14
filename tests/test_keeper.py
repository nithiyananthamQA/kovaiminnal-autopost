"""owner 14 Nov: GitHub's own timer almost never starts our scheduled workflows - keeper.yml (tools/keeper.py) starts each one at its
OWN cron times, once per time, only when switched on, with the inputs of a normal scheduled run. No network: gh is faked."""
import datetime as dt
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import keeper as K      # noqa: E402

K.log = lambda *a: None

UTC = dt.timezone.utc
DAY = dt.datetime(2026, 11, 15, tzinfo=UTC)


def ist(hhmm, day=DAY):
    h, m = map(int, hhmm.split(":"))
    return day + dt.timedelta(hours=h, minutes=m) - dt.timedelta(hours=5, minutes=30)


class FakeGh:
    """the GitHub API keeper uses: workflow states, runs created since a time, workflow_dispatch"""
    def __init__(self, off=(), ran=None):
        self.off, self.ran, self.started, self.calls = set(off), dict(ran or {}), [], 0
        self.now = DAY

    def __call__(self, *args):
        self.calls += 1
        if args[:2] == ("api", "repos/{owner}/{repo}/actions/workflows?per_page=100"):
            return json.dumps({"workflows": [{"path": ".github/workflows/" + w, "state": "disabled_manually" if w in self.off else "active"}
                                             for w in list(K.scheduled()) + [K.SELF]]})
        m = re.match(r"repos/\{owner\}/\{repo\}/actions/workflows/([^/]+)/runs\?per_page=1&created=%3E%3D(\S+)$", args[1]) if args[0] == "api" else None
        if m:
            since = dt.datetime.strptime(m.group(2), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            return str(sum(1 for t in self.ran.get(m.group(1), []) if t >= since))
        if args[:2] == ("workflow", "run"):
            wf = args[2]
            assert args[3:5] == ("--ref", "main"), args
            ins = dict(a.split("=", 1) for a in args[6::2])
            self.started.append((wf, self.now, ins))
            self.ran.setdefault(wf, []).append(self.now)
            return ""
        raise AssertionError(f"unexpected gh call {args}")


def run_day(gh, start=DAY, minutes=1440):
    done, cache = {}, {}
    for i in range(minutes):
        gh.now = start + dt.timedelta(minutes=i, seconds=5)
        K.check(gh.now, done, cache, run=gh)
    return gh


class Keeper(unittest.TestCase):
    def test_times_are_exactly_the_workflows_own_cron_lines(self):
        jobs = K.scheduled()
        self.assertNotIn("keeper.yml", jobs)
        self.assertEqual(set(jobs), set(K.LIVE_INPUTS))      # a new scheduled workflow needs its live inputs here
        for wf, lines in jobs.items():
            y = (ROOT / ".github" / "workflows" / wf).read_text(encoding="utf-8")
            self.assertEqual(lines, re.findall(r'cron: "([^"]+)"', y), wf)

    def test_inputs_exist_and_mean_a_live_run(self):
        for wf, ins in K.LIVE_INPUTS.items():
            y = (ROOT / ".github" / "workflows" / wf).read_text(encoding="utf-8")
            d = y[y.index("workflow_dispatch:"):]
            for k in list(ins) + (["top"] if wf == "pick.yml" else []):
                self.assertRegex(d, rf"\n      {k}:\n", f"{wf} has no input {k}")
            for k, v in ins.items():
                if k in ("dry", "dry_run", "prebuild", "repost", "post_only"):
                    self.assertIn(v, ("0", "false"), (wf, k))
        self.assertEqual(K.LIVE_INPUTS["post.yml"]["timer"], "true")      # post.yml: counts as scheduled (LIVE file, no commit every 5 min)
        self.assertIn("github.event.schedule == '" + K.PICK_8 + "' && '8'", (ROOT / ".github/workflows/pick.yml").read_text(encoding="utf-8"))

    def test_a_whole_day_starts_each_time_once(self):
        gh = run_day(FakeGh())
        n = {}
        for wf, _, _ in gh.started:
            n[wf] = n.get(wf, 0) + 1
        self.assertEqual(n, {"post.yml": 288, "powercut.yml": 34, "comments.yml": 36, "district_powercut.yml": 34,
                             "pick.yml": 3, "rasipalan.yml": 4, "insights.yml": 1})
        picks = [(t.astimezone(K.IST).strftime("%H:%M"), i["top"]) for wf, t, i in gh.started if wf == "pick.yml"]
        self.assertEqual(picks, [("06:00", "8"), ("10:00", "6"), ("19:00", "6")])      # 8 + 6 + 6, as scheduled
        first = {wf: t.astimezone(K.IST).strftime("%H:%M") for wf, t, _ in reversed(gh.started)}
        self.assertEqual(first["powercut.yml"], "05:50")
        self.assertEqual(first["district_powercut.yml"], "05:35")
        self.assertEqual(first["insights.yml"], "02:10")
        self.assertEqual(first["rasipalan.yml"], "07:00")
        self.assertLess(gh.calls, 2500)      # GITHUB_TOKEN: 1000 API calls an hour for the whole repository

    def test_switched_off_never_started_and_an_earlier_run_counts(self):
        gh = FakeGh(off={"post.yml", "pick.yml"}, ran={"powercut.yml": [ist("05:52")]})      # e.g. GitHub's own timer ran 05:50
        run_day(gh, start=ist("05:30"), minutes=60)
        started = [(wf, t.astimezone(K.IST).strftime("%H:%M")) for wf, t, _ in gh.started]
        self.assertNotIn("post.yml", [w for w, _ in started])
        self.assertNotIn("pick.yml", [w for w, _ in started])
        self.assertEqual([t for w, t in started if w == "powercut.yml"], ["06:20"])      # 05:50 already ran

    def test_switched_on_late_starts_the_missed_time_within_an_hour(self):
        gh = FakeGh(off={"pick.yml"})
        done, cache = {}, {}
        gh.now = ist("06:10")
        K.check(gh.now, done, cache, run=gh)
        gh.off.clear()
        for hhmm in ("06:20", "06:21", "06:22"):
            gh.now = ist(hhmm)
            K.check(gh.now, done, cache, run=gh)
        self.assertEqual([wf for wf, _, _ in gh.started if wf == "pick.yml"], ["pick.yml"])
        gh2 = FakeGh()
        gh2.now = ist("07:05")      # 65 minutes after 06:00: too late, left (GitHub's own timer is not that late either)
        K.check(gh2.now, {}, {}, run=gh2)
        self.assertNotIn("pick.yml", [wf for wf, _, _ in gh2.started])

    def test_a_failed_start_is_tried_again_next_minute(self):
        gh = FakeGh()
        real = gh.__call__

        def flaky(*a):
            if a[:3] == ("workflow", "run", "pick.yml") and not getattr(flaky, "failed", False):
                flaky.failed = True
                raise RuntimeError("HTTP 500")
            return real(*a)
        done, cache = {}, {}
        for hhmm in ("06:00", "06:01"):
            gh.now = ist(hhmm)
            K.check(gh.now, done, cache, run=flaky)
        self.assertEqual([t.astimezone(K.IST).strftime("%H:%M") for wf, t, _ in gh.started if wf == "pick.yml"], ["06:01"])

    def test_cron_fields(self):
        self.assertTrue(K.matches("43 1-23/2 * * *", dt.datetime(2026, 11, 15, 3, 43, tzinfo=UTC)))
        self.assertFalse(K.matches("43 1-23/2 * * *", dt.datetime(2026, 11, 15, 4, 43, tzinfo=UTC)))
        self.assertTrue(K.matches("13 */2 * * *", dt.datetime(2026, 11, 15, 22, 13, tzinfo=UTC)))
        self.assertTrue(K.matches("0 9 * * 0", dt.datetime(2026, 11, 15, 9, 0, tzinfo=UTC)))      # 15 Nov 2026 is a Sunday
        self.assertFalse(K.matches("0 9 * * 1-5", dt.datetime(2026, 11, 15, 9, 0, tzinfo=UTC)))

    def test_keeper_workflow(self):
        y = (ROOT / ".github" / "workflows" / "keeper.yml").read_text(encoding="utf-8")
        for s in ("workflow_dispatch:", "group: keeper", "cancel-in-progress: false", "actions: write", "contents: read",
                  "python3 -u tools/keeper.py", "if: ${{ !cancelled() }}", "run: gh workflow run keeper.yml --ref main",
                  'KEEPER_MINUTES: "340"', "timeout-minutes: 350"):
            self.assertIn(s, y)
        self.assertGreaterEqual(len(K.crons(y)), 2)      # backup restarts of the chain
        try:
            import yaml
        except ImportError:
            return
        for p in (ROOT / ".github" / "workflows").glob("*.yml"):
            yaml.safe_load(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
