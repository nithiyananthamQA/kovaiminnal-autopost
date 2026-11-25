"""owner 25 Nov (reference autofix 24 Nov): a news HELD by the fact-check is written again from its article with the problems told to the
writer; only a clean version is saved (poster/fixed/<story>.json) and the posting job posts that corrected text. Today's and yesterday's
news only, 2 tries per news, busy AI writers do not use up a try, nothing here can stop a round."""
import datetime, json, sys, tempfile, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
for d in ("poster", "research_free"):
    sys.path.insert(0, str(ROOT / d))
import autofix      # noqa: E402
import post      # noqa: E402

IST = autofix.IST
NOW = datetime.datetime(2026, 11, 25, 13, 0, tzinfo=IST)
HELD = "DRAFT (x) - NOT CLEAN, held from posting - problems: fact-check: the draft says 65 வயது but the article says 60 வயது"


def row(sid, day=25, **kw):
    r = {"story_id": sid, "source": f"https://www.dinamalar.com/news/{sid}", "published": f"2026-11-{day}T09:00:00+05:30",
         "headline_ta": "பழைய தலைப்பு", "reel_script": "பழைய", "caption": "பழைய", "slides_spec": "{}", "location": "உக்கடம், கோவை மாவட்டம்",
         "verification": HELD, "post_to": "Kovai Minnal", "review": ""}
    r.update(kw)
    return r


def hold(r):
    return "held: fact-check problems - x" if "NOT CLEAN" in str(r.get("verification")) else str(r.get("_hold", ""))


GOOD = {"headline_ta": "புதிய தலைப்பு", "headline_en": "new", "caption": "புதிய", "reel_script": "புதிய", "slides_spec": "{}",
        "location": "உக்கடம், கோவை மாவட்டம்", "verification": "DRAFT (x) - fact-check: no problems found"}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.p = [mock.patch.object(autofix, "FIX", self.tmp), mock.patch.object(autofix, "TRIES", self.tmp / "_tries.json"),
                  mock.patch.object(post, "news_hold", side_effect=hold), mock.patch.object(post, "_skip_reason_base", return_value=""),
                  mock.patch.object(post, "page_done", return_value=False), mock.patch.object(post, "pages_of", return_value=["coimbatore"])]
        for x in self.p:
            x.start()

    def tearDown(self):
        for x in self.p:
            x.stop()


class Candidates(Base):
    def test_only_fact_check_holds_of_today_and_yesterday(self):
        rows = [row("RN-1"), row("RN-2", day=24), row("RN-3", day=22),      # today, yesterday, too old
                row("RN-4", verification="DRAFT (x) - fact-check: no problems found"),      # not held
                row("RN-5", verification="clean", _hold="held: location is only the district - x"),      # another hold
                row("RN-6", review="Hold")]      # the owner's own Hold
        got = [r["story_id"] for r in autofix.candidates(rows, NOW)]
        self.assertEqual(got, ["RN-1", "RN-2"])

    def test_already_fixed_or_would_not_post_anyway_is_not_rewritten(self):
        (self.tmp / "RN-1.json").write_text("{}", encoding="utf-8")
        with mock.patch.object(post, "_skip_reason_base", side_effect=lambda r: "stale: x" if r["story_id"] == "RN-2" else ""):
            got = [r["story_id"] for r in autofix.candidates([row("RN-1"), row("RN-2"), row("RN-3")], NOW)]
        self.assertEqual(got, ["RN-3"])


class Main(Base):
    def run_main(self, rows, rewrite):
        with mock.patch.object(post, "bridge_get", return_value={"rows": rows}), mock.patch.object(autofix, "rewrite", side_effect=rewrite):
            autofix.main(NOW)
        return json.loads((self.tmp / "_tries.json").read_text(encoding="utf-8"))

    def test_a_clean_rewrite_is_saved_for_the_posting_job(self):
        tries = self.run_main([row("RN-1")], lambda r, n: (dict(GOOD), ""))
        d = json.loads((self.tmp / "RN-1.json").read_text(encoding="utf-8"))
        self.assertEqual(d["headline_ta"], "புதிய தலைப்பு")
        self.assertEqual(d["source"], row("RN-1")["source"])
        self.assertTrue(d["verification"].startswith("AUTO-FIXED"))
        self.assertEqual(tries, {"RN-1": 1})

    def test_still_wrong_uses_a_try_and_saves_nothing(self):
        tries = self.run_main([row("RN-1")], lambda r, n: (None, "still held: held: fact-check problems - x"))
        self.assertFalse((self.tmp / "RN-1.json").exists())
        self.assertEqual(tries, {"RN-1": 1})

    def test_busy_writers_do_not_use_up_a_try_and_stop_the_run(self):
        seen = []
        tries = self.run_main([row("RN-1"), row("RN-2")], lambda r, n: (seen.append(r["story_id"]), (None, "all free models failed: 429"))[1])
        self.assertEqual(seen, ["RN-1"])      # stopped after the first: the writers are busy for every news
        self.assertEqual(tries.get("RN-1", 0), 0)

    def test_two_tries_per_news_then_left_alone(self):
        (self.tmp / "_tries.json").write_text(json.dumps({"RN-1": 2}), encoding="utf-8")
        seen = []
        self.run_main([row("RN-1")], lambda r, n: (seen.append(1), (None, "x"))[1])
        self.assertEqual(seen, [])

    def test_queue_not_readable_never_raises(self):
        with mock.patch.object(post, "bridge_get", side_effect=RuntimeError("bridge down")):
            autofix.main(NOW)
        self.assertEqual(list(self.tmp.glob("RN-*.json")), [])

    def test_dry_run_saves_nothing(self):
        with mock.patch.object(autofix, "DRY", True):
            with mock.patch.object(post, "bridge_get", return_value={"rows": [row("RN-1")]}), \
                    mock.patch.object(autofix, "rewrite", return_value=(dict(GOOD), "")):
                autofix.main(NOW)
        self.assertEqual(list(self.tmp.glob("*.json")), [])      # not even the try counts


class ApplyFixes(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.p = mock.patch.object(post, "FIXED_DIR", self.tmp)
        self.p.start()

    def tearDown(self):
        self.p.stop()

    def test_the_corrected_text_replaces_the_sheet_text(self):
        (self.tmp / "RN-1.json").write_text(json.dumps(dict(GOOD, source=row("RN-1")["source"], story_id="RN-1")), encoding="utf-8")
        rows = post.apply_fixes([row("RN-1"), row("RN-2")])
        self.assertEqual(rows[0]["headline_ta"], "புதிய தலைப்பு")
        self.assertEqual(post.news_hold(rows[0]), "")      # the hold is gone: it posts
        self.assertEqual(rows[1]["headline_ta"], "பழைய தலைப்பு")

    def test_a_file_for_another_link_is_ignored(self):
        (self.tmp / "RN-1.json").write_text(json.dumps(dict(GOOD, source="https://other/x")), encoding="utf-8")
        self.assertEqual(post.apply_fixes([row("RN-1")])[0]["headline_ta"], "பழைய தலைப்பு")

    def test_a_broken_file_never_stops_posting(self):
        (self.tmp / "RN-1.json").write_text("{not json", encoding="utf-8")
        self.assertEqual(post.apply_fixes([row("RN-1")])[0]["headline_ta"], "பழைய தலைப்பு")


if __name__ == "__main__":
    unittest.main()
