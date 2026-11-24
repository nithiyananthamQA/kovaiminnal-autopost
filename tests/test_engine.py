"""owner 24 Nov ("an Instagram monster ... post the reels our users loved to see ... it's an engine", "separate insights for each
district"): each page learns from its OWN final reels which topics, areas and headline words its viewers watch, and the pick orders
each round by that. Order only - nothing dropped, power cuts first, any problem = the old order."""
import datetime, sys, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research_free"))
import learned      # noqa: E402
import pick         # noqa: E402

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def reel(head, views, day=1, hour=10, watch=5000):
    t = datetime.datetime(2026, 11, day, hour, 0, tzinfo=IST).astimezone(datetime.timezone.utc).isoformat()
    return {"caption": head + "\n📰 முழு விவரம்", "t": t, "views": views, "ig_reels_avg_watch_time": watch, "final": True}


def page():
    rows = []
    for d in range(1, 11):
        rows += [reel("வடவள்ளியில் நகை திருட்டு: இருவர் கைது", 3000, d, watch=9000),
                 reel("பொள்ளாச்சியில் கபடி போட்டி", 300, d, watch=3000),
                 reel("அன்னூரில் குடிநீர் குழாய் கசிவு: பொதுமக்கள் அவதி", 2000, d, watch=8000),
                 reel("கல்லூரியில் ஆண்டு விழா", 500, d, watch=4000)]
    return rows


class Learn(unittest.TestCase):
    def test_learns_what_people_watch(self):
        e = learned.learn(page())
        self.assertTrue(e["ready"])
        self.assertGreater(e["topic"]["crime"][0], 0)
        self.assertLess(e["topic"]["sports_culture"][0], 0)
        d = {"engine": e}
        good, _ = learned.engine_score("சாய்பாபா காலனியில் நகை திருட்டு", d)
        poor, _ = learned.engine_score("பொள்ளாச்சியில் கபடி போட்டி", d)
        self.assertGreater(good, poor)

    def test_a_good_day_is_not_credited_to_the_news(self):
        # the same news type on a day when every reel did 10x: no better than on a normal day
        rows = page() + [reel("கல்லூரியில் ஆண்டு விழா", 5000, 11), reel("பொள்ளாச்சியில் கபடி போட்டி", 3000, 11),
                         reel("வடவள்ளியில் நகை திருட்டு: இருவர் கைது", 30000, 11), reel("அன்னூரில் குடிநீர் குழாய் கசிவு: பொதுமக்கள் அவதி", 20000, 11)]
        a, b = learned.learn(page()), learned.learn(rows)
        self.assertAlmostEqual(a["topic"]["education"][0], b["topic"]["education"][0], delta=0.05)

    def test_one_lucky_reel_moves_little(self):
        rows = page() + [reel("மேட்டுப்பாளையத்தில் யானை", 100000, 5)]
        e = learned.learn(rows)
        self.assertNotIn("மேட்டுப்பாளையம்", e.get("area", {}))      # one reel: no area effect at all

    def test_too_few_reels_not_ready(self):
        e = learned.learn(page()[:10])
        self.assertFalse(e["ready"])
        self.assertEqual(learned.engine_score("x", {"engine": e})[0], None)


class PickOrder(unittest.TestCase):
    def setUp(self):
        self.d = {"engine": learned.learn(page())}

    def test_engine_leads_the_order(self):
        at = datetime.datetime(2026, 11, 24, 17, 0, tzinfo=IST)
        items = [{"id": "a", "title": "கல்லூரியில் ஆண்டு விழா", "score": 8},
                 {"id": "b", "title": "உக்கடத்தில் நகை திருட்டு", "score": 4},
                 {"id": "c", "title": "நாளை மின்தடை", "score": 3, "power_cut": True}]
        with mock.patch.object(learned, "load", return_value=self.d):
            got, sc = pick.reach_rank(items, at)
        self.assertEqual([x["id"] for x in got], ["c", "b", "a"])      # power cut first, then what people watch
        self.assertTrue(sc["b"][3].startswith("engine:"))

    def test_engine_not_ready_keeps_the_old_order(self):
        at = datetime.datetime(2026, 11, 24, 17, 0, tzinfo=IST)
        items = [{"id": "a", "title": "கல்லூரியில் ஆண்டு விழா", "score": 8}, {"id": "b", "title": "உக்கடத்தில் நகை திருட்டு", "score": 4}]
        with mock.patch.object(learned, "load", return_value={}):
            got, sc = pick.reach_rank(items, at)
        self.assertEqual([x["id"] for x in got], ["a", "b"])
        self.assertFalse(str(sc["a"][3]).startswith("engine:"))

    def test_engine_error_keeps_the_old_order(self):
        at = datetime.datetime(2026, 11, 24, 17, 0, tzinfo=IST)
        items = [{"id": "a", "title": "கல்லூரியில் ஆண்டு விழா", "score": 8}, {"id": "b", "title": "உக்கடத்தில் நகை திருட்டு", "score": 4}]
        with mock.patch.object(learned, "engine_score", side_effect=RuntimeError("boom")), mock.patch.object(learned, "load", return_value={}):
            got, _ = pick.reach_rank(items, at)
        self.assertEqual([x["id"] for x in got], ["a", "b"])


class Openings(unittest.TestCase):
    def test_most_watched_and_never_sensitive(self):
        rows = page() + [reel("சூலூரில் மாணவனிடம் சீண்டல்: போக்சோவில் கைது", 90000, 3),
                         reel("பேரூரில் எச்சில் துப்பியதால் தகராறு: மன்னிப்பு கேட்டும் தாக்கிய இருவர் கைது", 40000, 4)]
        got = learned.best_openings(rows)
        self.assertEqual(got[0], "பேரூரில் எச்சில் துப்பியதால் தகராறு: மன்னிப்பு கேட்டும் தாக்கிய இருவர் கைது")
        self.assertFalse(any("போக்சோ" in g for g in got))


class Topics(unittest.TestCase):
    def test_complaint_project_and_feature_are_told_apart(self):
        self.assertEqual(learned.topic("பத்திரப்பதிவுக்கு நாள் முழுக்க காத்திருப்பு: பொதுமக்கள் அதிருப்தி"), "civic")
        self.assertEqual(learned.topic("சிங்காநல்லூரில் மேம்பாலம் கட்டுவது எப்போது"), "infra")
        self.assertEqual(learned.topic("மிஸ்டர் ஏஐ.. நீங்க நல்லவரா, கெட்டவரா..?"), "feature")
        self.assertNotEqual(learned.topic("மத்திய சிறை மைதானத்தில் ஒலிம்பிக் அகாடமி வருகிறது"), "crime")
        self.assertEqual(learned.topic("நாளை 9 பகுதிகளில் மின் தடை: சாலை பணிகள்"), "power_cut")


if __name__ == "__main__":
    unittest.main()
