"""owner 17 Nov ("like his setup - if he pushes, all pages follow"): tools/sync_pages.py gives every page Kovai's code and never touches
a page's own live data. Every file a workflow commits (its bots' data) must be in sync_pages.PROTECT, or one push would wipe it."""
import re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import sync_pages      # noqa: E402

# whole-folder adds that only ever carry protected files: flow_switch.yml (ENABLED / START_AT), powercut.yml's "$f" loop
# (archive / results), the district engine (Kovai only - not in page copies)
BROAD = {"research_free", "$f", "districts/state", "districts/state/$KEY"}


class Protect(unittest.TestCase):
    def test_every_file_a_bot_commits_is_protected(self):
        prot = [p.strip("/").rstrip("*") for p in sync_pages.PROTECT]
        missing = []
        for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
            for line in re.findall(r"git add ([^;&|\n]+)", wf.read_text(encoding="utf-8")):
                for a in line.split():
                    a = a.strip('"\'')
                    if a.startswith("-") or a in ("2>/dev/null", "||", "true") or a in BROAD or a.startswith("2>"):
                        continue
                    if not any(a == p or a.startswith(p.rstrip("/") + "/") or a.startswith(p) for p in prot):
                        missing.append(f"{wf.name}: {a}")
        self.assertEqual(missing, [])

    def test_code_is_never_protected(self):
        for p in sync_pages.PROTECT:
            self.assertFalse(p.endswith(".py") or p.startswith(("/poster/post", "/reel/", "/research_free/collect")), p)

    def test_page_copies_do_not_get_the_sync_tool(self):
        import make_page
        self.assertTrue(make_page.SKIP.match("tools/sync_pages.py"))
        self.assertTrue(make_page.SKIP.match("tests/test_sync_pages.py"))


if __name__ == "__main__":
    unittest.main()


class PowerCutPage19Nov(unittest.TestCase):
    """owner 19 Nov: Salem = power cuts only, its own Apps Script + Meta app, the reference's own Salem lists"""
    def test_timer_starts_only_the_power_cut_jobs(self):
        import make_timer, make_page
        got = {j["file"] for j in make_timer.jobs(ROOT, make_page.PAGE["salem"]["jobs"])}
        self.assertEqual(got, {"powercut.yml", "post.yml", "comments.yml", "insights.yml", "cloudclean.yml"})
        self.assertNotIn("pick.yml", got)

    def test_own_token_and_reference_lists(self):
        import json, make_page
        sys.path.insert(0, str(ROOT / "districts"))
        d, PL = make_page.page_values("salem")
        cfg = make_page.config_values(json.loads((ROOT / "poster" / "config.json").read_text(encoding="utf-8")), d, PL)
        self.assertEqual(cfg["instagram"]["shared_token_page"], "")      # never the Minnal bridge's shared token
        ref = make_page.ref_lists("salem")
        self.assertIn("news360-tn/salem360-autopost", ref["from"])
        self.assertIn("மேட்டூர்", ref["allnews"]["TOWNS"])
        self.assertIn("district-news-salem", ref["powercut"]["DISTRICT_URL"])
        src = make_page.allnews_values((ROOT / "research_free" / "allnews.py").read_text(encoding="utf-8"), d, PL)
        self.assertNotIn("SALEM_WORDS", src)      # his name for the list is ours (COIMBATORE_WORDS)
        self.assertIn("ஆத்தூர்", src)


class NotLivePage20Nov(unittest.TestCase):
    """owner 20 Nov: Tiruvallur = full news like Chennai, set up but "dont live as of now" - no job of it ever starts"""
    def test_timer_never_starts_a_page_that_is_not_live(self):
        import tempfile, make_timer, make_page
        from unittest import mock
        with tempfile.TemporaryDirectory() as home:
            (Path(home) / "tiruvallurminnal-autopost" / ".github" / "workflows").mkdir(parents=True)
            with mock.patch.object(Path, "home", return_value=Path(home)):
                repos = make_timer.build()["repos"]
        self.assertNotIn("nithiyananthamQA/tiruvallurminnal-autopost", repos)
        self.assertIs(make_page.PAGE["tiruvallur"]["live"], False)

    def test_sync_switches_every_job_off_until_live(self):
        import json, make_page
        from unittest import mock
        calls = []

        def run(cmd, cwd, check=True):
            calls.append(cmd)
            out = json.dumps([{"path": ".github/workflows/pick.yml", "state": "active"},
                              {"path": ".github/workflows/post.yml", "state": "disabled_manually"}]) if "list" in cmd else ""
            return mock.Mock(returncode=0, stdout=out, stderr="")
        with mock.patch.object(sync_pages, "run", run):
            sync_pages.only_jobs("tiruvallur")
        self.assertIn(["gh", "workflow", "disable", "pick.yml", "-R", "nithiyananthamQA/tiruvallurminnal-autopost"], calls)
        self.assertEqual(sum("disable" in c for c in calls), 1)

    def test_full_news_page_values(self):
        import json, make_page
        sys.path.insert(0, str(ROOT / "districts"))
        d, PL = make_page.page_values("tiruvallur")
        self.assertIsNone(d.get("jobs"))      # every job, like Chennai
        cfg = make_page.config_values(json.loads((ROOT / "poster" / "config.json").read_text(encoding="utf-8")), d, PL)
        self.assertEqual(cfg["instagram"]["shared_token_page"], "")      # its own Meta app token
        src = make_page.allnews_values((ROOT / "research_free" / "allnews.py").read_text(encoding="utf-8"), d, PL)
        self.assertIn("சென்னையை அடுத்த", src)      # CITY_ROADS: "near Chennai" is taken out before the other-district check
        self.assertEqual(make_page.ref_lists("tiruvallur"), {})
