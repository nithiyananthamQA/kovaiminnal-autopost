"""District power-cut pages: their OWN Apps Script bridge (own Sheet, own Instagram tokens), made from Kovai Minnal's bridge
apps_script/Code.gs so every fix there reaches the districts too.

    python districts/make_bridge.py          -> apps_script/Code.districts.gs   (tests/test_districts.py checks it is up to date)

Differences from Kovai's bridge (every one checked - a change in Code.gs that breaks one stops this script):
  - 37 pages: PAGE_LABEL / PAGE_COL, post_to "<District> Minnal" -> page key, weekly token refresh of IG_TOKEN_<KEY> for each page
  - 'recent' rows carry post_to (each district job reads only its own rows)
  - e-mail subjects use DISTRICTMINNAL instead of KOVAIMINNAL: both bridges run in the same Gmail and must never read each other's mails
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "apps_script" / "Code.gs"
DST = ROOT / "apps_script" / "Code.districts.gs"


def build():
    ds = json.loads((ROOT / "districts" / "districts.json").read_text(encoding="utf-8"))["districts"]
    t = SRC.read_text(encoding="utf-8")
    labels = ", ".join(f"{k}: '{d['name_ta']}'" for k, d in ds.items())
    cols = ", ".join(f"{k}: C.coimbatore_link" for k in ds)
    by_name = json.dumps({d["name_en"]: k for k, d in ds.items()}, ensure_ascii=False)
    keys_up = json.dumps([k.upper() for k in ds])
    names_re = "|".join(re.escape(d["name_en"]) for d in ds.values())

    def rep(old, new, n=1):
        nonlocal t
        c = t.count(old)
        if c != n:
            raise SystemExit(f"make_bridge: expected {n} x {old[:70]!r} in Code.gs, found {c} - update districts/make_bridge.py")
        t = t.replace(old, new)

    rep(" * Kovai Minnal bridge (Coimbatore district page கோவை மின்னல்) – copied from the Namakkal News360 bridge.",
        " * DISTRICT POWER-CUT PAGES bridge (37 pages '<District> Minnal') - MADE BY districts/make_bridge.py FROM Code.gs, do not edit.\n"
        " * Own Sheet + own Apps Script project + own Instagram tokens (IG_TOKEN_<KEY>); Kovai Minnal's bridge is a different project.")
    rep("var PAGE_LABEL = { coimbatore: 'கோவை மின்னல்' };", "var PAGE_LABEL = { " + labels + " };")
    rep("var PAGE_COL = { coimbatore: C.coimbatore_link };", "var PAGE_COL = { " + cols + " };")
    rep("function targets_(postTo) {\n  return ['coimbatore'];\n}",
        "var PAGE_OF = " + by_name + ";\n"
        "function targets_(postTo) {\n  var k = PAGE_OF[String(postTo || '').trim()];\n  return k ? [k] : [];\n}")
    rep("  ['COIMBATORE'].forEach(function (p) {", "  " + keys_up + ".forEach(function (p) {")
    rep("images: r.images, reel_link: r.reel_link, coimbatore_link: r.coimbatore_link, spare_link: r.spare_link });",
        "images: r.images, reel_link: r.reel_link, coimbatore_link: r.coimbatore_link, spare_link: r.spare_link, post_to: r.post_to });")
    rep("""  if (!/^Kovai Minnal\\s*$/.test(st.post_to)) p.push("post_to must be 'Kovai Minnal' (the only page; Coimbatore-district news only)");""",
        "  if (!/^(" + names_re + ")\\s*$/.test(st.post_to)) p.push(\"post_to must be one district page name, e.g. 'Salem Minnal'\");")
    rep("var MANUAL_LAST = 'மேலும் செய்திகளுக்கு கோவை மின்னல் பக்கத்தை பின்தொடருங்கள்.';", "var MANUAL_LAST = '';      // each district has its own closing line (written by the writer)")
    n = t.count("KOVAIMINNAL")
    if n < 10:
        raise SystemExit(f"make_bridge: only {n} KOVAIMINNAL e-mail tags found in Code.gs - check the e-mail subjects")
    t = t.replace("KOVAIMINNAL", "DISTRICTMINNAL")
    t = t.replace('"Kovai Minnal Log" Sheet', '"Minnal Power Cut Pages Log" Sheet').replace('Drive folder "Kovai Minnal"', 'Drive folder "Minnal Power Cut Pages"')
    return t


if __name__ == "__main__":
    out = build()
    if "--check" in sys.argv:
        sys.exit(0 if DST.exists() and DST.read_text(encoding="utf-8") == out else "apps_script/Code.districts.gs is out of date: python districts/make_bridge.py")
    DST.write_text(out, encoding="utf-8")
    print("written", DST.relative_to(ROOT))
