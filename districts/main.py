"""District power-cut pages (owner 11 Nov) - one command per step, one district per process (districts/pipeline.py).

The whole feature is switched in poster/config.json:
    "district_powercut": {"enabled": false, "disabled": []}
enabled false -> every command here stops at once (nothing imported, nothing fetched) and Kovai Minnal runs exactly as before.
"disabled" lists district keys that stay off while the others run.

    python districts/main.py list                 the switch + every district page and what it still needs
    python districts/main.py find [key ...]       new power-cut notices of every switched-on district (one process each)
                                                  -> out/districts/found.json + GitHub matrix of the districts that have one
    python districts/main.py write <key>          write the district's new notices into the district Sheet (reference collect.py)
    python districts/main.py post <key>           make the reels and post them on that district's page (reference post.py)
    python districts/main.py verify <key>         exit 3 while a notice written in the last 12 h is not on Instagram

POWERCUT_DRY=1 (find): only shows what would be written; nothing is saved (works with the switch off, for a free test).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline as PL      # noqa: E402  (imports nothing of the pipeline until apply())

DRY = os.environ.get("POWERCUT_DRY", "") == "1"


def switched_on(key=None):
    keys = PL.enabled_keys()
    if not keys and not (DRY and sys.argv[1:2] in (["find"], ["_find"])):
        print("district power-cut pages are switched off (poster/config.json district_powercut.enabled) - nothing done")
        return False
    if key and key not in PL.districts():
        raise SystemExit(f"unknown district '{key}' (districts/districts.json)")
    if key and keys and key not in keys:
        print(f"{key} is switched off (district_powercut.disabled) - nothing done")
        return False
    return True


def cmd_list():
    s = PL.settings()
    keys = PL.enabled_keys()
    print("switch:", "ON" if s.get("enabled") is True else "OFF", "| disabled:", ", ".join(s.get("disabled") or []) or "-")
    for k, d in PL.districts().items():
        fb = "FB ok" if os.environ.get(f"FB_PAGE_ID_{k.upper()}") or os.environ.get("FB_PAGE_ID") else "FB -"
        logo = "logo ok" if (HERE / k / "logo.png").exists() and (HERE / k / "footer.png").exists() else "LOGO MISSING"
        print(f"  {'on ' if k in keys else 'off'} {k:15} {d['name_en']:24} @{d['handle']:22} {logo:12} {fb}")
    return 0


def cmd_find(keys):
    """one news search for all districts, then one process per district (6 at a time): a district's values never leak into the next"""
    import concurrent.futures as cf
    keys = keys or PL.enabled_keys() or (list(PL.districts()) if DRY else [])
    if os.environ.get("POST_ONLY") == "1":      # owner 14 Nov: post the waiting stories now - no search, nothing new written
        found = [{"key": k, "secret": k.upper(), "urls": "", "news": ""} for k in keys]
        print(f"post only: {', '.join(keys) or '-'} (the stories already waiting in the Sheet)")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as fh:
                fh.write(f"n={len(found)}\n")
                fh.write("matrix=" + json.dumps({"include": found}, ensure_ascii=False) + "\n")
        return 0
    try:
        PL.shared_search(PL.log)
    except Exception as e:
        PL.log("shared search failed (each district still reads its own Dinamalar page):", str(e)[:150])
        PL.SHARED.unlink(missing_ok=True)

    def one(k):
        try:
            r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "_find", k], timeout=900, capture_output=True, text=True)
            return k, r.returncode, r.stdout + r.stderr[-3000:]
        except subprocess.TimeoutExpired:
            return k, 9, "timed out after 15 minutes"
    found, bad = [], []
    with cf.ThreadPoolExecutor(6) as ex:
        for k, rc, log in ex.map(one, keys):
            print(f"== {k}\n{log.rstrip()}", flush=True)
            if rc != 0:
                bad.append(k)
                continue
            f = PL.OUT_ROOT / k / "powercut_urls.txt"
            urls = [u for u in (f.read_text(encoding="utf-8").split() if f.exists() else []) if u.startswith("http")]
            g = PL.OUT_ROOT / k / "news_urls.txt"
            news = [u for u in (g.read_text(encoding="utf-8").split() if g.exists() else []) if u.startswith("http")]
            if urls or news:
                found.append({"key": k, "secret": k.upper(), "urls": " ".join(urls), "news": " ".join(news)})
    PL.OUT_ROOT.mkdir(parents=True, exist_ok=True)
    (PL.OUT_ROOT / "found.json").write_text(json.dumps(found, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"new power cuts: {sum(len(x['urls'].split()) for x in found)} | new news: {sum(len(x['news'].split()) for x in found)} | "
          f"{len(found)} district(s)" + (f" | finder failed: {', '.join(bad)}" if bad else ""))
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"n={len(found)}\n")
            fh.write("matrix=" + json.dumps({"include": found}, ensure_ascii=False) + "\n")
    return 1 if bad and len(bad) == len(keys) else 0


def _find_one(key):
    PL.use_bridge() if not DRY or os.environ.get("DISTRICT_BRIDGE_URL") else None
    if DRY and not os.environ.get("DISTRICT_BRIDGE_URL"):
        os.environ["BRIDGE_URL"], os.environ["BRIDGE_KEY"] = "", ""      # dry test without the district Sheet: duplicate check is this run only
    d = PL.apply(key)
    PL.make_dirs(d) if not DRY else d["out"].mkdir(parents=True, exist_ok=True)      # a dry run saves nothing
    import powercut as PC
    if DRY:
        PC.STATE = d["out"] / "powercut_state.dry.json"      # a dry run never touches the saved state
        PC.STATE.unlink(missing_ok=True)
    n = PL.seed_first_run(d)
    if n:
        PL.log(f"first run for {key}: {n} old links remembered unopened")
    rc = PC.cmd_find()
    if PL.news_on(key) or (DRY and os.environ.get("NEWS_DRY") == "1"):      # owner 13 Nov: the page's other local news too
        try:
            PL.find_news(d, dry=DRY, log=PL.log)
        except Exception as e:
            PL.log("news finder failed (power cuts unaffected):", str(e)[:200])
    return rc


def _urls(d):
    u = os.environ.get("DISTRICT_URLS", "").split()
    if not u:
        f = d["out"] / "powercut_urls.txt"
        u = f.read_text(encoding="utf-8").split() if f.exists() else []
    return [x for x in u if x.startswith("http")]


def cmd_write(key):
    """the reference powercut.yml writing step for one district: PICK_ONLY collect.py with the found links"""
    d = PL.page(key)
    urls = _urls(d)
    if not urls:
        print(f"{key}: no new power-cut notice to write")
        return 0
    for k, v in {"PICK_ONLY": "1", "COLLECT_MODE": "both", "WRITE_STORIES": "1", "AUTO_IMAGES": "1", "WRITE_WORKERS": "2", "BUDGET_MIN": "40",
                 "FRESH_DAYS": "2", "DAILY_CAP": "1000", "CITY_ONLY": "0"}.items():
        os.environ.setdefault(k, v)
    os.environ["MANUAL_URL"], os.environ["MAX_STORIES"] = " ".join(urls), str(len(urls))
    PL.use_bridge()
    PL.apply(key)
    PL.make_dirs(d)
    import collect as C
    sys.argv = ["collect.py"]
    return C.main() or 0


def cmd_writenews(key):
    """owner 13 Nov (Chennai): write the page's new local news found by find_news (news preface, news follow lines)"""
    d = PL.page(key)
    u = os.environ.get("DISTRICT_NEWS_URLS", "").split()
    if not u:
        f = d["out"] / "news_urls.txt"
        u = f.read_text(encoding="utf-8").split() if f.exists() else []
    urls = [x for x in u if x.startswith("http")]
    if not urls:
        print(f"{key}: no new news to write")
        return 0
    for k, v in {"PICK_ONLY": "1", "COLLECT_MODE": "both", "WRITE_STORIES": "1", "AUTO_IMAGES": "1", "WRITE_WORKERS": "1", "BUDGET_MIN": "40",
                 "FRESH_DAYS": "1", "DAILY_CAP": "1000", "CITY_ONLY": "0"}.items():
        os.environ.setdefault(k, v)
    os.environ["MANUAL_URL"], os.environ["MAX_STORIES"] = " ".join(urls), str(len(urls))
    PL.use_bridge()
    PL.apply(key, mode="news")
    PL.make_dirs(d)
    import collect as C
    sys.argv = ["collect.py"]
    return C.main() or 0


def cmd_post(key):
    """make the reel of every waiting notice of this district and post it on the district's page (one story per pass)"""
    PL.use_bridge()
    d = PL.page(key)
    PL.use_facebook(d)
    PL.apply(key)
    PL.make_dirs(d)
    import post as P
    if P.missing_setup():
        return 0
    rows = P.bridge_get("queue")["rows"]
    n = len(P.pick_all(rows)) if rows else 0
    print(f"{key}: {n} reel(s) to make", flush=True)
    # owner 14 Nov: like the reference - one story at a time, at least posting.spacing_min (12) minutes after the page's last post;
    # urgent news (power cuts, High) never waits. A job may run 90 minutes: what does not fit waits for the next run.
    import time
    spacing = float((P.CONFIG.get("posting") or {}).get("spacing_min", 12))
    t0, last = time.time(), None
    for i in range(min(n, 8)):      # post.py run = the top waiting story; the next pass takes the next one
        if last is not None:
            rows = P.bridge_get("queue")["rows"]
            nxt = P.pick_all(rows) if rows else []
            if not nxt:
                break
            wait = 0 if P.is_urgent(nxt[0]) else spacing * 60 - (time.time() - last)
            if time.time() - t0 + max(0, wait) > 70 * 60:
                print(f"{key}: the next stories wait for the next run (job time)", flush=True)
                break
            if wait > 0:
                print(f"{key}: waiting {wait / 60:.0f} min before the next post ({spacing:.0f} minutes apart, like the reference)", flush=True)
                time.sleep(wait)
        sys.argv = ["post.py", "run"]
        P.main()
        last = time.time()
    return 0


def cmd_verify(key):
    PL.use_bridge()
    PL.apply(key)
    import powercut as PC
    return PC.cmd_verify()


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else ""
    if cmd == "list":
        sys.exit(cmd_list())
    if cmd == "find":
        sys.exit(cmd_find(a[1:]) if switched_on() else 0)
    if cmd in ("_find", "write", "writenews", "post", "verify") and len(a) == 2:
        if not switched_on(a[1]):
            sys.exit(0)
        if cmd == "writenews" and not PL.news_on(a[1]):
            print(f"{a[1]}: local news is off (district_powercut.news_live) - nothing done")
            sys.exit(0)
        sys.exit({"_find": _find_one, "write": cmd_write, "writenews": cmd_writenews, "post": cmd_post, "verify": cmd_verify}[cmd](a[1]))
    sys.exit(__doc__)
