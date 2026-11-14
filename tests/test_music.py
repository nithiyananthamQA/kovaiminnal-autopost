"""owner 14 Nov: our own news music under the reels - mood by news type, ducked under the voice, up again in every pause."""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "reel"), str(ROOT / "poster")]
import reel3 as V3  # noqa: E402
import post  # noqa: E402


class Mood(unittest.TestCase):
    def test_power_cut_is_alert(self):
        self.assertEqual("alert", post.music_mood({"headline_ta": "சிங்காநல்லூரில் நாளை மின்தடை"}, {}))
        self.assertEqual("alert", post.music_mood({"category": "Power cut"}, {}))

    def test_crime_and_accident_are_serious(self):
        self.assertEqual("serious", post.music_mood({"category": "Crime & Safety"}, {"hl2": "3 பேர் கைது"}))
        self.assertEqual("serious", post.music_mood({"headline_ta": "உக்கடத்தில் பஸ் மோதி விபத்து"}, {}))

    def test_rest_is_calm(self):
        self.assertEqual("calm", post.music_mood({"headline_ta": "கோவையில் வேலைவாய்ப்பு முகாம்"}, {}))


class Ducking(unittest.TestCase):
    def test_down_under_voice_up_in_pauses_and_at_the_end(self):
        hop = 0.01
        lv = [-120] * 10 + [-20] * 300 + [-120] * 16 + [-20] * 300 + [-120] * 200
        env = V3.duck_envelope(lv, len(lv) * hop)
        self.assertAlmostEqual(-14.0, env[150], places=1)                 # voice speaking
        self.assertGreater(max(env[310:326]), -6)                          # the 0.16 s pause: music comes back up
        self.assertAlmostEqual(0.0, env[650], places=1)                    # after the voice (end card, before the last 1.5 s fade)
        self.assertLess(env[-1], -20)                                      # faded out at the very end

    def test_switch(self):
        with mock.patch.dict(os.environ, {"REEL_MUSIC": "0"}):
            self.assertFalse(V3.music_on())
        with mock.patch.dict(os.environ, {"REEL_MUSIC": "1"}):
            self.assertTrue(V3.music_on())

    def test_our_own_tracks_exist(self):
        for m in ("serious", "alert", "calm"):
            self.assertTrue((V3.MUSIC_DIR / f"{m}.wav").exists(), m)


if __name__ == "__main__":
    unittest.main()
