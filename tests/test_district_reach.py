"""owner 14 Nov (Instagram's own best practices for the district pages, Chennai first): a place tag on every post from the page's own
verified ids (districts/locations.json), and Kovai's comment-reply flow (owner chooses, the district bridge posts). No network."""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
ENV = {k: v for k, v in os.environ.items() if not k.startswith(("BRIDGE_", "DISTRICT_", "FB_", "GH_", "GITHUB_", "DRY_RUN", "POWERCUT_"))}
DENV = dict(ENV, DISTRICT_BRIDGE_URL="https://example.invalid/districts", DISTRICT_BRIDGE_KEY="test", BRIDGE_URL="https://example.invalid/kovai")
HEAD = "import sys, json; sys.path.insert(0, 'districts'); import pipeline as PL\n"


def run(code, env=DENV, args=()):
    r = subprocess.run([PY, "-c", code, *args], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stdout[-1500:] + r.stderr[-3000:])
    return r.stdout


# a test mapping with filled ids (the shipped file has none until the owner checks them)
FAKE_MAP = """
import tempfile, pathlib
_dir = pathlib.Path(tempfile.mkdtemp())
PL.LOCATIONS = _dir / "locations.json"
PL.LOCATIONS.write_text(json.dumps({"chennai": {"city": {"place": "Chennai, Tamil Nadu", "id": "1001"},
    "areas": [{"place": "Tambaram", "match": ["தாம்பர", "tambaram"], "id": "2002"},
              {"place": "Velachery", "match": ["வேளச்சேரி", "velachery"], "id": "3003"},
              {"place": "Guindy", "match": ["கிண்டி"], "id": ""}]}}, ensure_ascii=False), encoding="utf-8")
_real_page = PL.page
def _page(k):
    d = _real_page(k); d["state"] = _dir / "state" / k; return d
PL.page = _page
PL.use_bridge(); d = PL.apply("chennai")
import post as P
def row(head, cat="விபத்து", en="", loc=""):
    return {"headline_ta": head, "headline_en": en, "category": cat, "location": loc}
"""


class LocationTag(unittest.TestCase):
    def test_shipped_mapping_is_well_formed(self):
        m = json.loads((ROOT / "districts" / "locations.json").read_text(encoding="utf-8"))
        keys = json.loads((ROOT / "districts" / "districts.json").read_text(encoding="utf-8"))["districts"]
        self.assertIn("chennai", m)
        for k, v in m.items():
            if k == "note":
                continue
            self.assertIn(k, keys)
            self.assertTrue(v["city"]["place"])
            for a in [v["city"]] + v["areas"]:
                self.assertTrue(a["id"] == "" or a["id"].isdigit(), a)      # empty (TODO owner) or a real numeric id - never a guess in words
            for a in v["areas"]:
                self.assertTrue(a["match"] and a["place"], a)
                for w in a["match"]:      # the city name is the "default", never a match word (it would beat every area)
                    self.assertNotIn(w.lower(), {keys[k]["ta"], keys[k]["en"].lower(), "default"})

    def test_no_filled_id_no_tag_as_before(self):
        """the shipped file (ids still to be filled by the owner) and a district without an entry: no tag, exactly as before"""
        out = run(HEAD + """
import tempfile, pathlib
PL.LOCATIONS = pathlib.Path(tempfile.mkdtemp()) / "locations.json"
PL.LOCATIONS.write_text(json.dumps({"chennai": {"city": {"place": "Chennai", "id": ""}, "areas": [{"place": "T", "match": ["தாம்பர"], "id": ""}]}}))
PL.use_bridge(); d = PL.apply(sys.argv[1])
import post as P
print(P.CONFIG["location_tags"], P.CONFIG["locations"], repr(P.pick_location({"headline_ta": "தாம்பரத்தில் விபத்து"}, {})))""", args=("chennai",))
        self.assertEqual(out.strip().splitlines()[-1], "False {} ''")
        out = run(HEAD + "PL.use_bridge(); d = PL.apply('salem')\nimport post as P\nprint(P.CONFIG['location_tags'], P.CONFIG['locations'])")
        self.assertEqual(out.strip().splitlines()[-1], "False {}")

    def test_area_first_then_city(self):
        out = run(HEAD + FAKE_MAP + """
print(json.dumps({
  "area_inflected": P.pick_location(row("தாம்பரத்தில் கார் மோதி இருவர் காயம்"), {}),
  "first_named_wins": P.pick_location(row("வேளச்சேரி அருகே தாம்பரம் பேருந்து விபத்து"), {}),
  "english_headline": P.pick_location(row("சென்னையில் விபத்து", en="Bus accident near Velachery"), {}),
  "reel_place_line": P.pick_location(row("சென்னையில் விபத்து"), {"loc": "தாம்பரம், சென்னை"}),
  "city_fallback": P.pick_location(row("சென்னையில் மழை எச்சரிக்கை"), {}),
  "empty_id_area_city": P.pick_location(row("கிண்டியில் விபத்து"), {}),
  "power_cut_city": P.pick_location(row("தாம்பரம், வேளச்சேரியில் நாளை மின் தடை", cat="மின் தடை"), {}),
  "tags_on": P.CONFIG["location_tags"],
}))""")
        o = json.loads(out.strip().splitlines()[-1])
        self.assertEqual(o["area_inflected"], "2002")         # தாம்பரத்தில் -> Tambaram (Tamil stem)
        self.assertEqual(o["first_named_wins"], "3003")       # the place named first in the headline
        self.assertEqual(o["english_headline"], "3003")
        self.assertEqual(o["reel_place_line"], "2002")
        self.assertEqual(o["city_fallback"], "1001")          # no known area -> "Chennai, Tamil Nadu"
        self.assertEqual(o["empty_id_area_city"], "1001")     # an area without an id -> the city
        self.assertEqual(o["power_cut_city"], "1001")         # a power cut covers many areas -> always the city
        self.assertTrue(o["tags_on"])
        self.assertIn("location tag: Tambaram (2002)", out)

    def test_refused_id_remembered_other_errors_not(self):
        out = run(HEAD + FAKE_MAP + """
calls = []
def fake(method, path, token, **kw):
    calls.append((method, path, kw.get("location_id")))
    if kw.get("location_id") == "2002":
        raise RuntimeError("Instagram 1/media: {'message': 'Param location_id is not a valid location page ID', 'code': 100}")
    if kw.get("video_url") == "bad":
        raise RuntimeError("Instagram 1/media: {'message': 'The video could not be downloaded', 'code': 9004}")
    return {"id": "c1"}
import types
# the guard apply() put around P.ig, here around a fake Instagram (no network)
P.ig = PL.location_guard(types.SimpleNamespace(ig=fake), d, {"2002": "Tambaram", "1001": "Chennai, Tamil Nadu"})
P.LOC_ID = "2002"
cid, collab_ok, why = P.create_with_collab("1", "t", {"media_type": "REELS", "video_url": "ok"}, False)
print("posted without the tag:", cid, [c[2] for c in calls])
print("refused file:", sorted(PL.refused_places(d)))
print("next pick:", P.pick_location(row("தாம்பரத்தில் விபத்து"), {}))
P.LOC_ID = "3003"
try:
    P.create_with_collab("1", "t", {"media_type": "REELS", "video_url": "bad"}, False)
except RuntimeError:
    pass
print("other error keeps the id:", sorted(PL.refused_places(d)))""")
        self.assertIn("posted without the tag: c1 ['2002', None]", out)      # the post goes on without the place (post.create_with_collab)
        self.assertIn("refused file: ['2002']", out)
        self.assertIn("next pick: 1001", out)                                # never tried again -> the city
        self.assertIn("other error keeps the id: ['2002']", out)            # a video problem never blacklists a place id
        self.assertIn("LOCATION ID REFUSED by Instagram: Tambaram (2002)", out)

    def test_kovai_location_code_unchanged(self):
        """Kovai keeps its own picker, ig-probe check and config.json "locations" (the district file is never read for Kovai)"""
        out = run("import sys; sys.path[:0] = ['poster']\nimport post as P\n"
                  "print(P.pick_location.__module__, P.ig.__module__, P.verified_locations.__module__, 'pipeline' in sys.modules)", env=ENV)
        self.assertEqual(out.strip(), "post post post False")

    def test_post_resets_the_place_between_stories(self):
        src = (ROOT / "districts" / "main.py").read_text(encoding="utf-8")
        body = src.split("def cmd_post")[1].split("\ndef ")[0]
        self.assertLess(body.index('P.LOC_ID = ""'), body.index("P.main()"))


class CommentReplies(unittest.TestCase):
    def test_switch(self):
        cfg = json.loads((ROOT / "poster" / "config.json").read_text(encoding="utf-8"))["district_powercut"]
        self.assertIn("chennai", cfg["comments_live"])
        out = run(HEAD + """
PL.settings = lambda: {"enabled": True, "live": ["chennai"], "comments_live": ["chennai", "salem"]}
print(PL.comments_on("chennai"), PL.comments_on("salem"))
PL.settings = lambda: {"enabled": True, "live": ["chennai"]}
print(PL.comments_on("chennai"))
PL.settings = lambda: {"enabled": False, "live": ["chennai"], "comments_live": ["chennai"]}
print(PL.comments_on("chennai"))
print(sorted(m for m in sys.modules if m in ('post', 'comments', 'collect')))""")
        self.assertEqual(out.split("\n")[:4], ["True False", "False", "False", "[]"])      # salem is not live; read without imports
        r = subprocess.run([PY, "districts/main.py", "comments", "salem"], cwd=ROOT, env=DENV, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("comment replies are off", r.stdout)

    def test_kovai_bridge_refused(self):
        env = dict(DENV, DISTRICT_BRIDGE_URL="https://example.invalid/kovai")
        r = subprocess.run([PY, "districts/main.py", "_comments", "chennai"], cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Kovai Minnal's bridge", r.stdout + r.stderr)

    def test_chennai_flow(self):
        """the district Sheet only, Chennai's token and Instagram account only, the page's own username (from Instagram) skipped,
        nothing posted on Instagram, no comment text or username in the public log"""
        out = run(HEAD + """
import datetime as dt, io, contextlib
PL.use_bridge(); d = PL.apply("chennai")
import post as P
sys.path.insert(0, "districts"); import main as M
import comments as CM
now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")
uid = d["instagram"]["user_id"]
gets, sent, calls = [], [], []
def bget(action, **kw):
    gets.append((action, kw))
    return {"token": "EAA-chennai"} if action == "token" else {"ids": ["c2"]}
P.bridge_get = bget
P.bridge_post = lambda a, payload: sent.append((a, payload)) or {"ok": True, "added": len(payload["items"])}
def ig(m, path, tok, **kw):
    calls.append((m, path, tok))
    if path == uid:
        return {"id": uid, "username": "chennai_minnal"}
    if path.endswith("/media"):
        return {"data": [{"id": "m1", "caption": "தாம்பரத்தில் விபத்து\\nவிவரம்", "timestamp": now, "permalink": "https://instagram.com/p/m1", "comments_count": 4}]}
    return {"data": [{"id": "c1", "text": "SECRET-TEXT இது எப்போது?", "username": "viewer_one", "timestamp": now},
                     {"id": "c2", "text": "seen before", "username": "viewer_two", "timestamp": now},
                     {"id": "c3", "text": "நன்றி", "username": "chennai_minnal", "timestamp": now},
                     {"id": "c4", "text": "answered in the app", "username": "viewer_three", "timestamp": now,
                      "replies": {"data": [{"username": "chennai_minnal"}]}}]}
P.ig = ig
CM.options_for = lambda cap, text: ("question", ["a", "b", "c"])
CM.DRY = False
print("rc", M._comments_one("chennai"))
print(json.dumps({"bridge": P.BRIDGE_URL, "gets": gets, "sent_action": sent[0][0], "sent_page": sent[0][1]["page"],
                  "ids": [x["comment_id"] for x in sent[0][1]["items"]], "methods": sorted({c[0] for c in calls}),
                  "paths": sorted({c[1] for c in calls}), "tokens": sorted({c[2] for c in calls})}, ensure_ascii=False))""")
        lines = out.strip().splitlines()
        o = json.loads(lines[-1])
        self.assertEqual(o["bridge"], "https://example.invalid/districts")      # the district Sheet, never Kovai's
        self.assertEqual(o["gets"], [["token", {"page": "chennai"}], ["commentsSeen", {}]])      # Chennai's token only
        self.assertEqual((o["sent_action"], o["sent_page"], o["ids"]), ("commentNew", "chennai", ["c1"]))      # c2 seen, c3 own, c4 answered
        self.assertEqual(o["methods"], ["GET"])      # the job only reads Instagram - the owner's choice is posted by the bridge
        self.assertEqual(o["paths"], ["17841452418440882", "17841452418440882/media", "m1/comments"])
        self.assertEqual(o["tokens"], ["EAA-chennai"])
        log = "\n".join(lines[:-1])
        self.assertIn("rc 0", log)
        self.assertNotIn("SECRET-TEXT", log)
        self.assertNotIn("viewer_one", log)

    def test_workflow_job(self):
        y = yaml.safe_load((ROOT / ".github" / "workflows" / "district_powercut.yml").read_text(encoding="utf-8"))
        job = y["jobs"]["comments"]
        self.assertNotIn("needs", job)      # every run of the job, not only when something new was found
        txt = json.dumps(job)
        self.assertIn("districts/main.py comments", txt)
        for secret in ("secrets.BRIDGE_URL", "secrets.BRIDGE_KEY", "FB_TOKEN", "FB_PAGE_ID", "IG_TOKEN"):
            self.assertNotIn(secret, txt)      # never Kovai's bridge, never a page token in the job
        self.assertIn("DRY_RUN", job["env"])
        kovai = (ROOT / ".github" / "workflows" / "comments.yml").read_text(encoding="utf-8")
        self.assertIn("python poster/comments.py coimbatore", kovai)      # Kovai's own comments job unchanged


if __name__ == "__main__":
    unittest.main()
