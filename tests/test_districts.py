"""owner 11 Nov: district power-cut pages (districts/). Off by default; each power cut only on its own district's page; no Kovai Minnal
word on a district page; Kovai Minnal itself unchanged. Every district runs in its own process (as districts/main.py does)."""
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
ENV = {k: v for k, v in os.environ.items() if not k.startswith(("BRIDGE_", "DISTRICT_", "FB_", "GH_", "GITHUB_"))}
DENV = dict(ENV, DISTRICT_BRIDGE_URL="https://example.invalid/districts", DISTRICT_BRIDGE_KEY="test", BRIDGE_URL="https://example.invalid/kovai")


def run(code, env=DENV, args=()):
    r = subprocess.run([PY, "-c", code, *args], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise AssertionError(r.stdout[-1500:] + r.stderr[-3000:])
    return r.stdout


HEAD = "import sys, json; sys.path.insert(0, 'districts'); import pipeline as PL\n"


class Switch(unittest.TestCase):
    def test_only_live_pages_run(self):
        cfg = json.loads((ROOT / "poster" / "config.json").read_text(encoding="utf-8"))["district_powercut"]
        self.assertEqual(run(HEAD + "print(PL.enabled_keys())").strip(), str(cfg["live"] if cfg["enabled"] is True else []))
        self.assertNotIn("salem", cfg.get("live") or [])      # salem is not live: every command for it does nothing
        for cmd in (["write", "salem"], ["post", "salem"], ["verify", "salem"]):
            r = subprocess.run([PY, "districts/main.py", *cmd], cwd=ROOT, env=dict(DENV, POWERCUT_DRY=""), capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("switched off", r.stdout)
        out = run(HEAD + "PL.enabled_keys(); print(sorted(m for m in sys.modules if m in ('post','collect','powercut','allnews')))")
        self.assertEqual(out.strip(), "[]")      # the switch is read without importing any pipeline module

    def test_switch_lists(self):
        out = run(HEAD + """
PL.settings = lambda: {"enabled": True, "disabled": ["salem"]}
k = PL.enabled_keys(); print(len(k), "salem" in k, "erode" in k)
PL.settings = lambda: {"enabled": "yes"}
print(PL.enabled_keys())
PL.settings = lambda: {"enabled": True, "disabled": [], "live": ["chennai", "salem"]}
print(PL.enabled_keys())
PL.settings = lambda: {"enabled": False, "live": ["chennai"]}
print(PL.enabled_keys())""")
        self.assertEqual(out.split("\n")[:4], ["36 False True", "[]", "['chennai', 'salem']", "[]"])      # only a real true switches it on


class OwnSheet(unittest.TestCase):
    def test_kovai_bridge_refused(self):
        env = dict(DENV, DISTRICT_BRIDGE_URL="https://example.invalid/kovai")
        r = subprocess.run([PY, "-c", HEAD + "PL.use_bridge()"], cwd=ROOT, env=env, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Kovai Minnal's bridge", r.stderr + r.stdout)

    def test_missing_bridge_stops(self):
        r = subprocess.run([PY, "-c", HEAD + "PL.use_bridge()"], cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(r.returncode, 0)

    def test_rows_of_other_districts_dropped(self):
        out = run(HEAD + """
d = PL.page("salem")
r = PL._own_rows(d, {"ok": True, "rows": [{"story_id": "RN-1", "post_to": "Salem Minnal"}, {"story_id": "RN-2", "post_to": "Erode Minnal"},
                                         {"story_id": "RN-3", "post_to": "Kovai Minnal"}, {"story_id": "RN-4"}]})
print([x["story_id"] for x in r["rows"]])""")
        self.assertEqual(out.strip(), "['RN-1']")


    def test_district_bridge_up_to_date(self):
        """apps_script/Code.districts.gs is made from Kovai's Code.gs (python districts/make_bridge.py) - never edited by hand"""
        r = subprocess.run([PY, "districts/make_bridge.py", "--check"], cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        gs = (ROOT / "apps_script" / "Code.districts.gs").read_text(encoding="utf-8")
        self.assertNotIn("KOVAIMINNAL", gs)      # same Gmail as Kovai's bridge: never read Kovai's e-mails
        self.assertIn("salem: 'சேலம் மின்னல்'", gs)
        self.assertIn('"Salem Minnal": "salem"', gs)


class EveryDistrict(unittest.TestCase):
    def test_no_kovai_word_and_own_values(self):
        """all 37: the writer rules, example, fact-check, proofread, picture and fact-gate prompts carry the district's own page"""
        keys = json.loads((ROOT / "districts" / "districts.json").read_text(encoding="utf-8"))["districts"]
        code = HEAD + """
key = sys.argv[1]
PL.use_bridge(); d = PL.apply(key)
import run as RN, collect as C, post as P, validate as V, factgate as G, tamilcheck as T, powercut as PC, facebook as FB
for name, txt in (("rules", RN.SYSTEM), ("example", json.dumps(RN.EX, ensure_ascii=False)), ("check", RN.CHECK), ("proof", RN.PROOF),
                  ("brief", C.BRIEF_SYSTEM), ("gate", G.CONFIRM)):
    assert not PL.LEAK.search(txt), (key, name)
assert d["follow_spoken"] in RN.SYSTEM and d["name_en"] in RN.SYSTEM and len(RN.EX) == 1
assert V.PAGE == C.PAGE_NAME == P.PAGE_EN == d["name_en"] and V.LAST == T.LAST == P.FOLLOW_LINE == d["follow_spoken"]
assert P.PAGES == (key,) and P.pages_of({}) == [key] and P.LABEL == {key: d["name_ta"]} and P.PAGE_TAGS[key] == d["tag"]
assert P.PAGE_LOGOS[key].exists() and str(P.OUT).endswith("out/districts/" + key) and "districts/state/" + key in str(PC.STATE)
assert "districts/state/" + key in str(FB.STATE) and "districts/state/" + key in str(C.ARCHIVE)
assert C.BRIDGE_URL == P.BRIDGE_URL == "https://example.invalid/districts"
assert C.trigger_workflow("post.yml") is False and C.trigger_posting() is None
print("ok", key)
"""
        for k in keys:
            with self.subTest(district=k):
                self.assertIn("ok " + k, run(code, args=(k,)))


class Routing(unittest.TestCase):
    CODE = HEAD + """
PL.use_bridge(); d = PL.apply(sys.argv[1])
import post as P, allnews as A, freshness as F
def row(head, src, loc=""):
    return {"story_id": "RN-1", "headline_ta": head, "headline_en": "", "location": loc, "caption": head, "source": src, "post_to": d["name_en"]}
out = {
 "own_town": P.not_coimbatore(row("ஆத்தூரில் நாளை மின்தடை", "https://www.dinamalar.com/news/tamil-nadu-district-news-salem/attur-power-shutdown/4373999")),
 "own_name": P.not_coimbatore(row("சேலத்தில் நாளை மின்தடை", "https://www.dinamani.com/tamilnadu/2026/nov/11/x")),
 "kovai_page": P.not_coimbatore(row("ஆத்தூரில் நாளை மின்தடை", "https://www.dinamalar.com/news/tamil-nadu-district-news-coimbatore/x/4373998")),
 "erode_head": P.not_coimbatore(row("ஈரோட்டில் நாளை மின்தடை", "https://www.dinamani.com/tamilnadu/2026/nov/11/y")),
 "two_areas_same_day": F.same_power_cut("சேலம் ஆத்தூரில் நாளை மின்தடை", "2026-11-11", "சேலம் ஓமலூரில் நாளை மின்தடை", "2026-11-11"),
 "same_area": F.same_power_cut("சேலம் ஆத்தூரில் நாளை மின்தடை", "2026-11-11", "ஆத்தூர் பகுதியில் நாளை மின்தடை", "2026-11-11"),
}
cap = P.final_caption(dict(row("ஆத்தூரில் நாளை மின்தடை", "https://www.dinamalar.com/news/tamil-nadu-district-news-salem/x/4373999", "Attur, Salem district"),
                           category="மின் தடை", caption="⚡ ஆத்தூரில் நாளை மின்தடை\\n\\nவிவரம்\\n\\n📍 ஆத்தூர், சேலம் | 12 நவம்பர் 2026\\n\\n" + d["follow_caption"] + "\\n\\n#KovaiMinnal #Coimbatore"))
out["caption_leak"] = bool(PL.LEAK.search(cap)); out["caption_tag"] = d["tag"] in cap; out["caption_follow"] = d["follow_caption"] in cap
print(json.dumps(out, ensure_ascii=False))
"""

    def test_salem_cut_only_salem(self):
        o = json.loads(run(self.CODE, args=("salem",)).strip().split("\n")[-1])
        self.assertEqual(o["own_town"], "")            # a Salem town on Salem's own Dinamalar page
        self.assertEqual(o["own_name"], "")            # the district named in the headline
        self.assertNotEqual(o["kovai_page"], "")       # a notice filed under Coimbatore never goes to Salem
        self.assertNotEqual(o["erode_head"], "")       # another district's notice never goes to Salem
        self.assertFalse(o["two_areas_same_day"])      # two Salem areas on one day are two posts (the district name is no shared place)
        self.assertTrue(o["same_area"])
        self.assertFalse(o["caption_leak"])
        self.assertTrue(o["caption_tag"] and o["caption_follow"])


class SharedSearch(unittest.TestCase):
    def test_links_routed_by_where_the_paper_filed_them(self):
        out = run(HEAD + """
import tempfile, pathlib
PL.use_bridge(); d = PL.apply(sys.argv[1])
PL.SHARED = pathlib.Path(tempfile.mkdtemp()) / "search.json"
PL.SHARED.write_text(json.dumps([
 {"url": "https://www.dinamani.com/all-editions/edition-trichy/tanjore/2026/Nov/10/a", "title": "பாபநாசம் பகுதியில் நாளை மின்தடை"},
 {"url": "https://www.dinamani.com/all-editions/edition-thirunelveli/tuticorin/2026/Nov/10/b", "title": "கோவில்பட்டியில் இன்று மின்நிறுத்தம்"},
 {"url": "https://www.dinamalar.com/news/tamil-nadu-district-news-namakkal/c/4373001", "title": "நாளை மின்தடை"},
 {"url": "https://www.dinamani.com/thanjavur/2026/Nov/10/d", "title": "நாளை மின்தடை"},
 {"url": "https://www.dinamani.com/tamilnadu/2026/Nov/10/e", "title": "தஞ்சாவூரில் நாளை மின்தடை"},
 {"url": "https://www.dinamani.com/tamilnadu/2026/Nov/10/f", "title": "திருச்சியில் நாளை மின்தடை"}], ensure_ascii=False))
import allnews as A
A.from_dinamalar_list = lambda: []
print(json.dumps(sorted(x["url"][-1] for x in PL.district_links(d))))""", args=("thanjavur",))
        self.assertEqual(json.loads(out.strip().split("\n")[-1]), ["a", "d", "e"])


class KovaiUnchanged(unittest.TestCase):
    def test_kovai_values(self):
        out = run("""
import sys; sys.path[:0] = ['poster', 'research_free', 'reel']
import post as P, collect as C, validate as V, powercut as PC
print(P.PAGE, P.PAGES, P.TAG, P.PAGE_TAGS, P.PAGE_LOGOS, P.DEFAULT_LOC, P.PAGE_EN, C.PAGE_NAME, C.IG_PAGES, V.PAGE, PC.PAGE_KEY)
""", env=ENV)
        self.assertEqual(out.strip(), "coimbatore ('coimbatore',) #KovaiMinnal {'coimbatore': '#KovaiMinnal'} {} கோவை Kovai Minnal Kovai Minnal "
                                      "('coimbatore',) Kovai Minnal coimbatore")

    @unittest.skipUnless(importlib.util.find_spec("playwright"), "the reel needs playwright (not installed in the test job)")
    def test_reel_pages(self):
        out = run("""
import sys; sys.path[:0] = ['reel']
import reel5 as R5
k, s = R5.R.PAGES['coimbatore'], R5.R.PAGES['salem']
print(k['name'], 'district' in k, k['logo'], s['name'], s['handle'], s['district'], s['logo'].endswith('districts/salem/logo.png'),
      s['footer_wide'].endswith('districts/salem/footer.png'))
""", env=ENV)
        self.assertEqual(out.strip(), "கோவை மின்னல் False logo_coimbatore.png சேலம் மின்னல் salemminnal True True True")


class FirstRun(unittest.TestCase):
    def test_seed_skips_old_links_but_opens_power_ones(self):
        out = run(HEAD + """
import tempfile, pathlib
PL.use_bridge(); d = PL.apply("salem")
import powercut as PC
PC.STATE = pathlib.Path(tempfile.mkdtemp()) / "s.json"
PL._LINKS["salem"] = [
  {"url": "https://www.dinamalar.com/news/tamil-nadu-district-news-salem/4-people-arrested/1", "title": "", "via": "dinamalar-list", "_slug": "4-people-arrested"},
  {"url": "https://www.dinamalar.com/news/tamil-nadu-district-news-salem/power-shutdown-tomorrow/2", "title": "", "via": "dinamalar-list", "_slug": "power-shutdown-tomorrow"},
  {"url": "https://www.dinamalar.com/news/tamil-nadu-district-news-salem/x/3", "title": "சேலம் நாளை மின்தடை", "via": "dinamalar-list", "_slug": "x"}]
print(PL.seed_first_run(d), PL.seed_first_run(d), sorted(json.loads(PC.STATE.read_text())["seen"]))""")
        n1, n2, rest = out.strip().split(" ", 2)
        self.assertEqual((n1, n2), ("1", "0"))      # only the untitled non-power link; the second call does nothing (state exists)
        self.assertIn("4-people-arrested", rest)
        self.assertNotIn("power-shutdown", rest)

    def test_dinamalar_titles_read_from_page_data(self):
        out = run(HEAD + """
import sources as S
page = ('<a href="/news/tamil-nadu-district-news-salem/power-shutdown-tomorrow/4373471">x</a>'
        '{"newsid":4373471,"newstitle":"\\\\u0b9a\\\\u0bc7\\\\u0bb2\\\\u0bae\\\\u0bcd \\\\u0bae\\\\u0bbf\\\\u0ba9\\\\u0bcd\\\\u0ba4\\\\u0b9f\\\\u0bc8","x":1}'
        '"/news/tamil-nadu-district-news-erode/other/4373472"')
S._get = lambda u: page
r = PL.dinamalar_list(PL.page("salem"))
print(json.dumps([(x["url"].rsplit("/", 1)[1], x["title"], x["via"]) for x in r], ensure_ascii=False))""")
        self.assertEqual(json.loads(out.strip()), [["4373471", "சேலம் மின்தடை", "dinamalar-list"]])


class UnifiedLogin(unittest.TestCase):
    """13 Nov: a page on Meta's Unified login (app Minnal Pages) posts on graph.facebook.com with its Instagram account id;
    Kovai Minnal keeps graph.instagram.com and "me"."""
    PATCH = """
real = PL.districts()
x = dict(real); x["salem"] = dict(real["salem"], instagram=INSTA)
PL.districts = lambda: x
"""

    def test_unified_page_switches_host_and_account(self):
        out = run(HEAD + "INSTA = {'api': 'unified', 'user_id': '17841400000000001'}" + self.PATCH + """
PL.use_bridge(); d = PL.apply("salem")
import post as P
calls = []
P.ig = lambda m, path, token, **kw: calls.append((m, path, kw.get("fields"))) or {"id": path, "username": "salemminnal"}
print(P.IG_HOST, P.IG_VER, P.ig_account("t"), calls)""")
        self.assertEqual(out.strip(), "https://graph.facebook.com v24.0 ('17841400000000001', 'salemminnal') [('GET', '17841400000000001', 'id,username')]")

    def test_unified_page_without_account_id_only_stops_posting(self):
        out = run(HEAD + "INSTA = {'api': 'unified', 'user_id': ''}" + self.PATCH + """
PL.use_bridge(); d = PL.apply("salem")
import post as P
print("posting blocked:", P.missing_setup())""")
        self.assertIn("salem: Instagram account id missing", out)
        self.assertIn("posting blocked: True", out)

    def test_kovai_unchanged(self):
        out = run("import sys; sys.path.insert(0, 'poster'); import post as P\n"
                  "calls = []\n"
                  "P.ig = lambda m, path, token, **kw: calls.append(path) or {'user_id': '1', 'username': 'kovaiminnal'}\n"
                  "print(P.IG_HOST, repr(P.IG_USER_ID), P.ig_account('t'), calls)", env=ENV)
        self.assertEqual(out.strip(), "https://graph.instagram.com '' ('1', 'kovaiminnal') ['me']")


class LocalNews(unittest.TestCase):
    """owner 13 Nov: Chennai posts its other local news too - highest points first, capped, no flood on the first run, never the
    power-cut follow line; off unless the page is in news_live"""
    FAKE = """
import datetime, tempfile, pathlib
d = PL.page("chennai"); d["state"] = pathlib.Path(tempfile.mkdtemp()); d["out"] = pathlib.Path(tempfile.mkdtemp())
now = datetime.datetime.now(PL.IST)
iso = lambda h: (now - datetime.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%S+05:30")
L = [("https://x/chennai/student-hit/1", "சென்னையில் கார் மோதி மாணவி பலத்த காயம்", 1),
     ("https://x/chennai/metro/2", "திருமங்கலத்தில் மெட்ரோ ரயில் பணிகள்", 2),
     ("https://x/chennai/egg/3", "நாமக்கல் முட்டை விலை நிலவரம்", 1),
     ("https://x/chennai/old/4", "சென்னையில் பழைய செய்தி விபத்து", 9),
     ("https://x/chennai/cut/5", "சென்னையில் நாளை மின் தடை", 1)]
PL.dinamalar_list = lambda d_: [{"url": u, "title": t} for u, t, h in L]
PL.dinamalar_meta = lambda d_: {u.rsplit("/", 1)[-1]: {"published": iso(h), "snippet": ""} for u, t, h in L}
PL.settings = lambda: {"enabled": True, "news_live": ["chennai"], "news_per_run": 1, "news_per_day": 2, "news_max_age_hours": 6}
"""

    def test_first_run_no_flood_then_best_first_and_capped(self):
        out = run(HEAD + "PL.use_bridge(); PL.apply('chennai')\n" + self.FAKE + """
print("first:", PL.find_news(d, log=lambda *a: None))
L.append(("https://x/chennai/new-a/6", "சென்னையில் பேருந்து விபத்து 5 பேர் காயம்", 1))
L.append(("https://x/chennai/new-b/7", "சென்னையில் புதிய பூங்கா திறப்பு", 1))
L.append(("https://x/chennai/new-c/8", "சென்னையில் லாரி மோதி இருவர் பலி", 1))
r1 = PL.find_news(d, log=lambda *a: None); r2 = PL.find_news(d, log=lambda *a: None); r3 = PL.find_news(d, log=lambda *a: None)
print("runs:", len(r1), len(r2), len(r3), "| same twice:", bool(set(r1) & set(r2)))""")
        self.assertIn("first: []", out)                   # the first run only remembers what is on the page
        self.assertIn("runs: 1 1 0 | same twice: False", out)      # one per check, at most news_per_day (2) a day, never twice

    def test_news_mode_uses_news_follow_line(self):
        out = run(HEAD + """
PL.use_bridge(); d = PL.apply("chennai", mode="news")
import validate as V, run as RN
print("power" if "பவர்கட்" in V.LAST else "news", "|", "செய்திகளை" in V.LAST, "|", "LOCAL NEWS PAGE" in RN.SYSTEM, "|",
      any((e.get("output") or {}).get("category") != "மின் தடை" for e in RN.EX))""")
        self.assertEqual(out.strip(), "news | True | True | True")      # not only the power-cut writer example

    def test_writenews_off_unless_news_live(self):
        code = (HEAD + "import runpy\nPL.settings = lambda: {'enabled': True, 'live': ['chennai'], 'news_live': []}\n"
                "sys.argv = ['districts/main.py', 'writenews', 'chennai']\n"
                "try:\n    runpy.run_path('districts/main.py', run_name='__main__')\nexcept SystemExit as e:\n    print('exit', e.code)")
        out = run(code)
        self.assertIn("local news is off", out)
        self.assertIn("exit 0", out)

    def test_news_only_in_rounds(self):
        out = run(HEAD + "PL.use_bridge(); PL.apply('chennai')\n" + self.FAKE + """
import datetime as _dt
class _D(_dt.datetime):
    T = None
    @classmethod
    def now(cls, tz=None):
        return cls.T
PL.datetime.datetime = _D
PL.settings = lambda: {"enabled": True, "news_live": ["chennai"], "news_per_day": 10, "news_max_age_hours": 12, "news_rounds": {"06": 4, "10": 3, "19": 3}}
PL.dinamalar_meta = lambda d_: {u.rsplit("/", 1)[-1]: {"published": (_D.T - _dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%S+05:30"), "snippet": ""} for u, t, h in L}
_D.T = _D(2026, 11, 14, 6, 5, tzinfo=PL.IST); print("first:", PL.find_news(d, log=lambda *a: None))
L[:] = [(u.replace("/x/", "/y/"), t, h) for u, t, h in L]
_D.T = _D(2026, 11, 14, 8, 5, tzinfo=PL.IST); print("08:05:", len(PL.find_news(d, log=lambda *a: None)))
_D.T = _D(2026, 11, 14, 10, 5, tzinfo=PL.IST); print("10:05:", len(PL.find_news(d, log=lambda *a: None)))""")
        self.assertIn("08:05: 0", out)      # not a news round: power cuts only
        self.assertIn("10:05: 3", out)      # a news round: 3 (student 1 h, metro 2 h, old 9 h; egg = other district, cut = power cut)


if __name__ == "__main__":
    unittest.main()
