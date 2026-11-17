"""owner 18 Nov: the Cloudflare Worker "test" (workers/timer) starts every page's GitHub jobs at their own cron times, once, and replaces
keeper.yml. Its schedule.json must match the workflows (tools/make_timer.py) and its day simulation must pass (workers/timer/test.mjs)."""
import json, shutil, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


class TimerWorker(unittest.TestCase):
    def test_schedule_matches_the_workflows(self):
        import make_timer
        saved = json.loads((ROOT / "workers" / "timer" / "src" / "schedule.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["repos"][make_timer.KOVAI], make_timer.jobs(ROOT), "run python3 tools/make_timer.py and deploy")

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_a_simulated_day(self):
        r = subprocess.run(["node", str(ROOT / "workers" / "timer" / "test.mjs")], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        self.assertIn("timer test OK", r.stdout)

    def test_plain_name(self):      # owner 18 Nov: "no kovai minnal or bot like thing" in Cloudflare
        w = (ROOT / "workers" / "timer" / "wrangler.toml").read_text(encoding="utf-8")
        self.assertIn('name = "test"', w)


if __name__ == "__main__":
    unittest.main()
