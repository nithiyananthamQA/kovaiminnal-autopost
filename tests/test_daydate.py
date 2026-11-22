"""owner 22 Nov (viewer comment): never நாளை alone - the date goes with it, in the voice, headline, screen lines and caption."""
import datetime
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "research_free"))
import daydate as D      # noqa: E402

T = datetime.date(2026, 11, 22)


class DayDate(unittest.TestCase):
    def test_voice_gets_the_date(self):
        self.assertEqual(D.spoken("பொள்ளாச்சியில் நாளை காலை 9 மணி முதல் மின்தடை.", T),
                         "பொள்ளாச்சியில் நாளை, நவம்பர் 23ஆம் தேதி, காலை 9 மணி முதல் மின்தடை.")

    def test_no_comma_before_full_stop(self):
        self.assertEqual(D.spoken("மின்தடை நாளை.", T), "மின்தடை நாளை, நவம்பர் 23ஆம் தேதி.")

    def test_day_after_tomorrow(self):
        self.assertEqual(D.written("நாளை மறுநாள் விடுமுறை", T), "நாளை மறுநாள் (நவம்பர் 24) விடுமுறை")

    def test_month_end(self):
        self.assertEqual(D.written("நாளை கூட்டம்", datetime.date(2026, 11, 30)), "நாளை (டிசம்பர் 1) கூட்டம்")

    def test_already_dated_left_alone(self):
        for s in ["நாளை (நவம்பர் 23) மின்தடை", "நாளை 23ஆம் தேதி கூட்டம்", "நாளை (23.11.2026) மின்தடை", "நவ.23 நாளை மின்தடை"]:
            self.assertEqual(D.written(s, T), s)
            self.assertEqual(D.spoken(s, T), s)

    def test_clock_time_is_not_a_date(self):
        self.assertIn("(நவம்பர் 23)", D.written("நாளை காலை 10 மணி", T))

    def test_other_words_untouched(self):
        for s in ["நாளைய வானிலை", "நாளைக்கு விடுமுறை", "இன்று மின்தடை"]:
            self.assertEqual(D.written(s, T), s)

    def test_screen_line_keeps_its_limit(self):
        self.assertEqual(D.screen("சூலூரில் நாளை மின்தடை", T, 40), "சூலூரில் நாளை (நவ.23) மின்தடை")
        s = D.screen("நாளை மறுநாள் பள்ளிகளுக்கு விடுமுறை.", T, 40)
        self.assertEqual(s, "நவ.24 பள்ளிகளுக்கு விடுமுறை.")
        self.assertLessEqual(len(D.screen("ஆனைமலை, வால்பாறை பகுதிகளில் நாளை மின்தடை அறிவிப்பு", T, 40)), 60)

    def test_whole_draft(self):
        d = {"reel_script": "நாளை காலை 9 மணி முதல் மின்தடை.", "tamil_headline": "சூலூரில் நாளை மின்தடை", "caption": "⚡ சூலூரில் நாளை மின்தடை",
             "slides_spec": {"hl1": "சூலூர்: நாளை மின்தடை", "hl2": "காலை 9 - மாலை 5", "slides": [{"title": "நாளை", "lines": ["நாளை காலை 9 மணி"]}]}}
        D.add_dates(d, T)
        self.assertIn("நவம்பர் 23ஆம் தேதி", d["reel_script"])
        self.assertIn("(நவம்பர் 23)", d["tamil_headline"])
        self.assertIn("(நவம்பர் 23)", d["caption"])
        self.assertIn("நவ.23", d["slides_spec"]["hl1"])
        self.assertIn("நவ.23", d["slides_spec"]["slides"][0]["lines"][0])
        self.assertLessEqual(len(d["slides_spec"]["hl1"]), 40)

    def test_writer_adds_the_dates(self):
        src = (Path(__file__).resolve().parent.parent / "research_free" / "run.py").read_text(encoding="utf-8")
        self.assertIn("daydate.add_dates(d)", src)


if __name__ == "__main__":
    unittest.main()
