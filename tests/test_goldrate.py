"""owner 14 Nov: daily gold & silver rate post - real data only (2 pages must agree), compared with yesterday"""
import sys, unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "goldrate"))
import gold_sources as S      # noqa: E402
import gold_daily as G      # noqa: E402

GR = ("Gold Price on 14 November 2026 - Goodreturns Today's gold price in Chennai stands at ₹13,900 per gram for 24 karat gold "
      "(99.9% purity), ₹12,745 per gram for 22 karat gold (91.6% purity)")


class Parse(unittest.TestCase):
    def test_goodreturns_and_groww(self):
        self.assertEqual(S.parse_gold(GR), (12745, 13900))
        self.assertEqual(S.parse_gold(GR.replace("₹13,900", "₹13,900.00").replace("₹12,745", "₹12,745.00")), (12745, 13900))

    def test_bankbazaar(self):
        self.assertEqual(S.parse_gold("09 Nov 2026 UPDATED DAILY Gold Rate, Chennai ₹ 13,255/ 1 gram (22K) ₹ 95")[0], 13255)

    def test_silver(self):
        self.assertEqual(S.parse_silver("Today's silver price in Chennai stands at ₹195 per gram and ₹1,95,000 per kg"), 195)

    def test_only_todays_page_counts(self):
        self.assertTrue(S.has_today(GR, date(2026, 11, 14)))
        self.assertFalse(S.has_today(GR, date(2026, 11, 15)))

    def test_24k_read_from_wrong_place_is_dropped(self):
        self.assertEqual(S.parse_gold(GR.replace("₹13,900", "₹19,900"))[1], None)

    def test_two_pages_must_agree(self):
        self.assertEqual(S.agree([12745, 12745, 12800]), (12745, 2))
        self.assertEqual(S.agree([12745, 12800])[0], None)


class Compare(unittest.TestCase):
    def test_yesterday_and_week(self):
        hist = [{"date": "2026-11-07", "g22": 13160}, {"date": "2026-11-13", "g22": 12695, "g24": 13849}]
        r = G.rates_for_slides(hist, date(2026, 11, 14), {"g22": 12745, "g24": 13900, "sources": []}, None)
        self.assertEqual((r["g22_prev"], r["g24_prev"], r["vs"]), (12695, 13849, "நேற்றைய விலையைவிட"))
        self.assertEqual(len(r["week22"]), 7)
        self.assertEqual(r["week22"][0], ("8 நவ", 13160))      # a day with no rate keeps the day before's rate
        self.assertNotIn("silver", r)      # silver not confirmed -> gold slide only

    def test_older_last_day_is_not_called_yesterday(self):
        r = G.rates_for_slides([{"date": "2026-11-11", "g22": 13015, "g24": 14200}], date(2026, 11, 14),
                               {"g22": 12745, "g24": 13900, "sources": []}, None)
        self.assertEqual(r["vs"], "முந்தைய விலையைவிட")

    def test_caption(self):
        r = G.rates_for_slides([{"date": "2026-11-13", "g22": 12695, "g24": 13849, "silver": 195}], date(2026, 11, 14),
                               {"g22": 12745, "g24": 13900, "sources": []}, {"silver": 195, "sources": []})
        cap = G.caption(dict(G.PAGES["namakkal"]), date(2026, 11, 14), r)
        self.assertIn("இன்றைய தங்கம், வெள்ளி விலை | 14 நவம்பர் 2026", cap)
        self.assertIn("₹50 உயர்வு", cap)
        self.assertIn("மாற்றமில்லை", cap)


if __name__ == "__main__":
    unittest.main()


class MinnalDesign(unittest.TestCase):
    """owner 17 Nov: our own slide design with better data - every number is the confirmed rate or plain arithmetic on it"""
    def test_numbers_are_arithmetic_on_the_rates(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "goldrate"))
        import minnal_render as M, gold_daily as G
        p = dict(G.PAGES["coimbatore"], logo="x.png")
        self.assertEqual(p["design"], "minnal")
        r = {"date": "17 நவம்பர் 2026", "g22": 12470, "g22_prev": 12695, "g24": 13604, "g24_prev": 13849, "vs": "நேற்றைய விலையைவிட",
             "week22": [("16 நவ", 12695), ("17 நவ", 12470)], "silver": 190, "silver_prev": 195, "weeksilver": [("17 நவ", 190)]}
        gold, silver = M.page(p, r, "gold"), M.page(p, r, "silver")
        self.assertIn("₹99,760", gold)          # 1 சவரன் = 8 g of 22K
        self.assertIn("₹1,800", gold)           # its change = 8 x 225
        self.assertIn("₹1,02,753", gold)        # + 3% GST
        self.assertIn("₹1,36,040", gold)        # 24K 10 g
        self.assertIn("₹1,90,000", silver)      # 1 kg
        self.assertNotIn("360", gold + silver)
        self.assertIn("@kovai_minnal", gold)
        cap = G.caption(p, G.date.fromisoformat("2026-11-17"), r)
        self.assertIn("1 சவரன் (8 கிராம்): ₹99,760", cap)


class OwnCity(unittest.TestCase):
    """owner 17 Nov: "keep chennai and kovai separate" - Kovai reads the Coimbatore rate pages and says Kovai, never Chennai"""
    def test_kovai_reads_coimbatore_pages(self):
        g, s = S.pages_for(G.PAGES["coimbatore"]["city"])
        self.assertEqual(len(g), 4)
        self.assertEqual(len(s), 4)
        self.assertTrue(all("coimbatore" in u and "chennai" not in u for _, u in g + s))
        self.assertEqual(S.pages_for()[0], S.GOLD_PAGES)      # the reference's pages = Chennai

    def test_caption_names_the_page_city(self):
        p = dict(G.PAGES["coimbatore"], logo="x.png")
        r = {"g22": 12470, "g22_prev": 12470, "g24": 13604, "g24_prev": 13604}
        cap = G.caption(p, date(2026, 11, 17), r)
        self.assertIn("கோவை விலை நிலவரம்", cap)
        self.assertNotIn("சென்னை", cap)
        self.assertIn("சென்னை சந்தை விலை", G.caption(dict(G.PAGES["namakkal"]), date(2026, 11, 17), r))      # reference pages as before


class RateReel(unittest.TestCase):
    """owner 17 Nov (ours): the rate also as a reel with our music + sound effects; carousel and reel are tracked apart"""
    def test_reel_caption_never_counts_as_the_carousel(self):
        p = dict(G.PAGES["coimbatore"], logo="x.png")
        r = {"g22": 12470, "g22_prev": 12695, "g24": 13604, "g24_prev": 13849}
        day = date(2026, 11, 17)
        post_mark = f"இன்றைய தங்கம், வெள்ளி விலை | {G.date_ta(day)}"
        self.assertIn(post_mark, G.caption(p, day, r))
        self.assertNotIn(post_mark, G.reel_caption(p, day, r))
        self.assertTrue(G.reel_caption(p, day, r).startswith(G.REEL_HEAD))
        self.assertNotEqual(G.state_path("coimbatore"), G.state_path("coimbatore", "reel"))
        self.assertTrue(G.PAGES["coimbatore"].get("reel"))
        self.assertFalse(G.PAGES["namakkal"].get("reel"))      # the reference's pages: carousel only, as he does

    def test_sound_effects_land_on_their_cues(self):
        import numpy as np
        import gold_reel as R
        fx = R.effects([{"t": 1.0, "kind": "tick"}, {"t": 2.5, "kind": "riser"}, {"t": 0.5, "kind": "nope"}], 3.0)
        self.assertEqual(len(fx), 3 * R.SR)
        sec = lambda a, b: np.abs(fx[int(a * R.SR):int(b * R.SR)]).max()      # noqa: E731
        self.assertLess(sec(0, 0.99), 1e-6)            # an unknown kind makes no sound
        self.assertGreater(sec(1.0, 1.06), 0.3)        # the tick at 1.0 s
        self.assertGreater(sec(2.2, 2.5), 0.2)         # the riser builds up BEFORE its cue ...
        self.assertLess(sec(2.5, 3.0), 1e-6)           # ... and ends on it
        for k, f in R.SFX.items():
            x = f()
            self.assertTrue(0 < len(x) and np.abs(x).max() <= 1.0001, k)
