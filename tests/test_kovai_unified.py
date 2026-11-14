"""14 Nov: Kovai Minnal can post to Instagram through Meta's Unified (system-user) login, switched by configuration only:
poster/config.json "instagram": {"api": "unified", "user_id": ""}. Empty user_id = the Instagram login exactly as before
(graph.instagram.com + "me"); filled = graph.facebook.com/v24.0 + that account id, and "me" is never asked on that host.
Every job that calls Instagram for Kovai (post.py and all that use post.ig, rasipalan) follows the same rule; a district page never
inherits Kovai's setting; the bridge never tries to refresh a system-user token (EAA...)."""
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
ENV = {k: v for k, v in os.environ.items() if not k.startswith(("BRIDGE_", "DISTRICT_", "FB_", "GH_", "GITHUB_", "IG_"))}
DENV = dict(ENV, DISTRICT_BRIDGE_URL="https://example.invalid/districts", DISTRICT_BRIDGE_KEY="test", BRIDGE_URL="https://example.invalid/kovai")
UID = "17841400000000077"
sys.path.insert(0, str(ROOT / "poster"))
import ig_api      # noqa: E402


def run(code, cwd=ROOT, env=ENV):
    r = subprocess.run([PY, "-c", code], cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise AssertionError(r.stdout[-1500:] + r.stderr[-3000:])
    return r.stdout.strip()


def tree(user_id, api="unified"):
    """a copy of poster/post.py + ig_api.py + rasipalan/rasi_daily.py with config.json's instagram block set - the real
    config.json is never touched"""
    tmp = Path(tempfile.mkdtemp())
    atexit.register(shutil.rmtree, tmp, True)
    (tmp / "poster").mkdir()
    (tmp / "rasipalan").mkdir()
    for f in ("post.py", "ig_api.py"):
        shutil.copy(ROOT / "poster" / f, tmp / "poster" / f)
    shutil.copy(ROOT / "rasipalan" / "rasi_daily.py", tmp / "rasipalan" / "rasi_daily.py")
    cfg = json.loads((ROOT / "poster" / "config.json").read_text(encoding="utf-8"))
    cfg["instagram"] = {"api": api, "user_id": user_id}
    (tmp / "poster" / "config.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    return tmp


# post.py with ig() recording the paths it is asked for (no network)
POST = """
import sys; sys.path.insert(0, 'poster'); import post as P
calls = []
P.ig = lambda m, path, token, **kw: calls.append(path) or {'user_id': '1', 'id': path, 'username': 'kovaiminnal'}
"""


class Settings(unittest.TestCase):
    def test_rule(self):
        login, fb = ig_api.LOGIN_HOST, ig_api.UNIFIED_HOST
        self.assertEqual(ig_api.settings({}, env={}), (login, "", ""))
        self.assertEqual(ig_api.settings({"instagram": {"api": "unified", "user_id": ""}}, env={}), (login, "", ""))
        self.assertEqual(ig_api.settings({"instagram": {"api": "unified", "user_id": " " + UID + " "}}, env={}), (fb, "v24.0", UID))
        self.assertEqual(ig_api.settings({"instagram": {"api": "instagram", "user_id": UID}}, env={}), (login, "", ""))
        self.assertEqual(ig_api.settings({"instagram": {"api": "unified", "user_id": UID}}, env={"IG_API_VERSION": "v25.0"}), (fb, "v25.0", UID))
        self.assertTrue(ig_api.me_allowed(login))
        self.assertFalse(ig_api.me_allowed(fb))

    def test_shipped_config_is_read_at_import(self):
        """post.py takes host / version / id from config.json's instagram block (empty or filled - this test passes either way,
        so filling the id never turns the tests red)"""
        cfg = json.loads((ROOT / "poster" / "config.json").read_text(encoding="utf-8"))
        ig = cfg["instagram"]
        self.assertEqual(ig["api"], "unified")
        self.assertRegex(str(ig["user_id"]), r"^(\d{10,20})?$")      # empty, or the Instagram account id (digits only - never a token)
        out = run(POST + "print(P.IG_HOST, P.IG_VER, P.IG_USER_ID, sep='|')")
        self.assertEqual(out, "|".join(ig_api.settings(cfg, env={})))


class KovaiPost(unittest.TestCase):
    def test_filled_uses_graph_facebook_and_the_account_id(self):
        tmp = tree(UID)
        out = run(POST + "print(P.IG_HOST, P.IG_VER, P.IG_USER_ID, P.ig_account('t'), calls, P.ig_url(P.IG_USER_ID + '/media'))", cwd=tmp)
        self.assertEqual(out, f"https://graph.facebook.com v24.0 {UID} ('{UID}', 'kovaiminnal') ['{UID}'] https://graph.facebook.com/v24.0/{UID}/media")

    def test_empty_id_with_unified_api_is_the_old_path(self):
        out = run(POST + "print(P.IG_HOST, repr(P.IG_USER_ID), P.ig_account('t'), calls)", cwd=tree(""))
        self.assertEqual(out, "https://graph.instagram.com '' ('1', 'kovaiminnal') ['me']")

    def test_never_me_on_the_unified_host(self):
        """'me' there is the system user, never the page: refused before any request is sent"""
        out = run("""
import sys; sys.path.insert(0, 'poster'); import post as P
sent = []
P.requests.request = lambda *a, **k: sent.append(a) or (_ for _ in ()).throw(AssertionError('network'))
P.IG_USER_ID = ''      # the account id missing on the Unified host
for f in (lambda: P.ig('GET', 'me', 't', fields='user_id'), lambda: P.ig_account('t')):
    try:
        f(); print('NOT REFUSED')
    except RuntimeError as e:
        print('refused')
print(P.IG_HOST, sent)""", cwd=tree(UID))
        self.assertEqual(out.split("\n"), ["refused", "refused", "https://graph.facebook.com []"])

    def test_every_kovai_instagram_job_goes_through_post_ig(self):
        """comments, insights, ig_comments, ig_probe, collect's recent-post check: no own Instagram host or 'me' call"""
        for f in ("poster/comments.py", "poster/insights.py", "poster/ig_comments.py", "poster/ig_probe.py", "research_free/collect.py",
                  "research_free/pick.py", "research_free/powercut.py", "research_free/run.py", "poster/facebook.py", "tools/repost.py"):
            t = (ROOT / f).read_text(encoding="utf-8")
            self.assertNotIn("graph.instagram.com", t, f)
            self.assertNotIn('"me"', t, f)
        post = (ROOT / "poster" / "post.py").read_text(encoding="utf-8")
        self.assertNotIn('IG_HOST = "https://graph.instagram.com"', post)      # host comes from ig_api.settings(CONFIG) only


class Rasipalan(unittest.TestCase):
    STUBS = """
import sys, types
for m in ('rasi_panchang', 'rasi_festivals', 'rasi_sources', 'rasi_writer', 'rasi_render'):
    sys.modules[m] = types.ModuleType(m)
sys.path.insert(0, 'rasipalan'); import rasi_daily as R
calls = []
R.requests.request = lambda m, url, **k: calls.append(url) or (_ for _ in ()).throw(AssertionError('network'))
"""

    def test_filled(self):
        out = run(self.STUBS + "print(R.IG, R.IG_VER, R.account_id('t'), calls)", cwd=tree(UID), env=dict(ENV, PAGE="coimbatore"))
        self.assertEqual(out, f"https://graph.facebook.com v24.0 {UID} []")

    def test_empty_uses_me_on_the_instagram_host(self):
        out = run(self.STUBS + """
class Resp:
    status_code = 200
    def json(self): return {'user_id': '1'}
R.requests.request = lambda m, url, **k: calls.append(url) or Resp()
print(R.IG, repr(R.IG_VER), R.account_id('t'), calls)""", cwd=tree(""), env=dict(ENV, PAGE="coimbatore"))
        self.assertEqual(out, "https://graph.instagram.com '' 1 ['https://graph.instagram.com/me']")

    def test_other_page_never_uses_kovai_setting(self):
        out = run(self.STUBS + "print(R.IG, repr(R.IG_USER_ID))", cwd=tree(UID), env=dict(ENV, PAGE="rasipuram"))
        self.assertEqual(out, "https://graph.instagram.com ''")


class Districts(unittest.TestCase):
    def test_plain_district_never_inherits_kovai_unified(self):
        """Kovai filled (Unified) + a district on the Instagram login: the district keeps graph.instagram.com and its own 'me'"""
        out = run(f"""
import sys; sys.path.insert(0, 'districts'); import pipeline as PL
import post as P
P.IG_HOST, P.IG_VER, P.IG_USER_ID = P.ig_api.UNIFIED_HOST, 'v24.0', '{UID}'      # as if Kovai's config.json had its id
real = PL.districts()
x = dict(real); x['salem'] = {{k: v for k, v in real['salem'].items() if k != 'instagram'}}
PL.districts = lambda: x
PL.use_bridge(); PL.apply('salem')
calls = []
P.ig = lambda m, path, token, **kw: calls.append(path) or {{'user_id': '2', 'username': 'salemminnal'}}
print(P.IG_HOST, repr(P.IG_VER), repr(P.IG_USER_ID), P.ig_account('t'), calls)""", env=DENV)
        self.assertEqual(out.splitlines()[-1], "https://graph.instagram.com '' '' ('2', 'salemminnal') ['me']")


class Bridge(unittest.TestCase):
    def test_system_user_token_never_refreshed(self):
        for f in ("Code.gs", "Code.districts.gs"):
            gs = (ROOT / "apps_script" / f).read_text(encoding="utf-8")
            body = gs[gs.index("function refreshTokens()"):]
            body = body[:body.index("\n}\n")]
            self.assertLess(body.index("if (systemUserToken_(t)) return;"), body.index("refresh_access_token"), f)
            self.assertIn("return /^EAA/.test(String(t || ''));", gs)
            self.assertNotIn("UrlFetchApp.fetch(IG_REPLY_HOST +", gs, f)      # comment reply / hide: host chosen by the token
            self.assertIn("return systemUserToken_(tok) ? IG_REPLY_HOST_UNIFIED : IG_REPLY_HOST;", gs)

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_bridges_are_valid_javascript(self):
        """Apps Script refuses to save a file with a syntax error (14 Nov: a plain Python string put line breaks inside JS strings)"""
        for f in ("Code.gs", "Code.districts.gs"):
            tmp = Path(tempfile.mkdtemp()) / (f + ".js")
            shutil.copy(ROOT / "apps_script" / f, tmp)
            r = subprocess.run(["node", "--check", str(tmp)], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, f + ": " + r.stderr[-800:])


if __name__ == "__main__":
    unittest.main()
