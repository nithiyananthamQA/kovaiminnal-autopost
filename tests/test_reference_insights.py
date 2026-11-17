"""owner 17 Nov (ours): "we need to consider his and ours - main is ours, in the meantime his one also helps us".
learned.json = our page's numbers wherever we have enough reels, the reference page's live insights for the rest."""
import json, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research_free"))
sys.path.insert(0, str(ROOT / "poster"))
import learned, reference_insights as R      # noqa: E402

HIS = {"updated": "2026-11-17T10:46+05:30", "posts_measured": 350,
       "topic_weight": {"power_cut": 1.33, "crime": 0.19, "education": -0.5, "politics": -0.5, "sports_culture": -0.03},
       "topic_n": {"power_cut": 23, "crime": 58, "education": 41, "politics": 17, "sports_culture": 3, "jobs": 2},
       "best_hours_ist": [0, 4, 10, 11], "top_openings": ["⚡ his opening"], "avg_watch_s": 7.8}


class Blend(unittest.TestCase):
    def test_without_our_numbers_his_fill_everything(self):
        out = R.blend({"updated": "x", "posts_measured": 0}, HIS, learned.TRUST_N, 12)
        self.assertEqual(out["topic_weight"]["power_cut"], 1.33)
        self.assertEqual(out["topic_source"]["crime"], "reference")
        self.assertEqual(out["avg_watch_s"], 7.8)
        self.assertEqual(out["posts_measured"], 0)      # our own count stays ours
        self.assertEqual(learned.reach_weight("கொலை வழக்கில் கைது", out)[0], 0.19)

    def test_ours_wins_once_we_have_enough_reels_of_the_topic(self):
        ours = {"posts_measured": 40, "topic_weight": {"crime": 0.9, "education": 0.4}, "topic_n": {"crime": 6, "education": 3},
                "avg_watch_s": 9.1, "best_hours_ist": [19]}
        out = R.blend(ours, HIS, learned.TRUST_N, 12)
        self.assertEqual((out["topic_weight"]["crime"], out["topic_source"]["crime"]), (0.9, "ours"))      # 6 of ours >= 5
        self.assertEqual((out["topic_weight"]["education"], out["topic_n"]["education"]), (-0.5, 41))      # 3 of ours: his helps
        self.assertEqual(out["avg_watch_s"], 9.1)
        self.assertEqual(out["best_hours_ist"], [19])
        self.assertEqual(out["top_openings"], ["⚡ his opening"])      # we have none yet

    def test_a_topic_neither_page_trusts_keeps_ours(self):
        out = R.blend({"posts_measured": 20, "topic_weight": {"sports_culture": 0.5}, "topic_n": {"sports_culture": 3}}, HIS, 5, 12)
        self.assertEqual(out["topic_weight"]["sports_culture"], 0.5)

    def test_no_reference_is_ours_alone(self):
        ours = {"posts_measured": 0}
        self.assertEqual(R.blend(ours, {}, 5, 12), ours)


class Fetch(unittest.TestCase):
    def test_a_failed_download_keeps_the_last_copy(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(R, "CACHE", str(Path(d) / "ref.json")):
            ok = mock.Mock(json=lambda: HIS, raise_for_status=lambda: None)
            self.assertEqual(R.fetch(lambda: ok)["posts_measured"], 350)

            def down():
                raise OSError("network")
            self.assertEqual(R.fetch(down)["posts_measured"], 350)
            bad = mock.Mock(json=lambda: {"updated": "x"}, raise_for_status=lambda: None)      # no weights: never replaces the copy
            self.assertEqual(R.fetch(lambda: bad)["posts_measured"], 350)
            self.assertEqual(json.loads((Path(d) / "ref.json").read_text(encoding="utf-8"))["posts_measured"], 350)

    def test_nothing_ever_read(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(R, "CACHE", str(Path(d) / "none.json")):
            self.assertEqual(R.fetch(lambda: (_ for _ in ()).throw(OSError("x"))), {})


class OurHistoryOnly(unittest.TestCase):
    def test_his_frozen_rows_are_not_in_our_history(self):
        h = json.loads((ROOT / "poster" / "insights" / "history.json").read_text(encoding="utf-8"))
        self.assertTrue(all(v["t"] >= "2026-11-14" for v in h.values()))      # our page's first reel: 14 Nov


if __name__ == "__main__":
    unittest.main()
