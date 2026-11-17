"""Daily gold & silver rate carousel - one post per page per day, every morning (owner 14 Nov).

  python goldrate/gold_daily.py            -> every page in GOLD_PAGES (default: this repo's pages)
  DRY_RUN=1 -> read the rates and make the slides only, never post (slides in out/goldrate/<page>)

When: the Chennai jewellers' association fixes the day's rate at 9:30 AM; the rate pages show it a little later. The job starts
09:40 IST and checks every 5 minutes until GIVE_UP_AT. It posts only when at least 2 pages show TODAY's date and the same 22K
rate (silver: the same per-gram rate). If silver is not confirmed by SILVER_WAIT_UNTIL, the gold slide is posted alone.
Today is compared with the last day saved in goldrate/state/history.json (normally yesterday).
Environment: BRIDGE_URL, BRIDGE_KEY (page tokens), CLOUDINARY_CLOUD, CLOUDINARY_PRESET, FB_* (optional)."""
import json, os, sys, time
from datetime import datetime, timedelta, timezone, date
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import gold_sources as sources      # noqa: E402
import gold_render as render      # noqa: E402
import minnal_render      # noqa: E402  (owner 17 Nov: our own slide design for Minnal pages)
import gold_reel      # noqa: E402

IST = timezone(timedelta(hours=5, minutes=30))
# 17 Nov (forced): Meta gives our app only the Unified login - the same Instagram connection as every Kovai job (poster/ig_api.py):
# graph.facebook.com/v24.0 + config.json instagram.user_id, token = the one minnal-bot token. A page without settings: as the reference.
sys.path.insert(0, str(ROOT / "poster"))
import ig_api      # noqa: E402
CONFIG = json.loads((ROOT / "poster" / "config.json").read_text(encoding="utf-8"))
IG, IG_VER, IG_USER_ID = ig_api.settings(CONFIG)
DRY = os.environ.get("DRY_RUN", "") in ("1", "true", "yes")
START_AT = os.environ.get("START_AT", "09:40")
SILVER_WAIT_UNTIL = os.environ.get("SILVER_WAIT_UNTIL", "11:30")
GIVE_UP_AT = os.environ.get("GIVE_UP_AT", "13:00")
REEL_ON = os.environ.get("GOLD_REEL", "1") not in ("0", "false", "no")      # owner 17 Nov: the rate reel (pages with "reel": True)
FORCE_DATE = os.environ.get("GOLD_DATE", "")      # testing only (dry runs): YYYY-MM-DD the pages still show
HISTORY = HERE / "state" / "history.json"
STATE_DIR = HERE / "state"

PAGES = {      # owner 14 Nov: every page, each with its own logo and handle; the rate is the same Tamil Nadu (Chennai) rate
    "namakkal": {"town": "நாமக்கல்", "name1": "நாமக்கல்", "handle": "namakkal.360", "tag": "#Namakkal360", "brand_px": 54},
    "rasipuram": {"town": "இராசிபுரம்", "name1": "இராசிபுரம்", "handle": "rasipuram.360", "tag": "#Rasipuram360", "brand_px": 50},
    "coimbatore": {"town": "கோவை", "name1": "கோவை", "brand2": " மின்னல்", "handle": "kovai_minnal", "tag": "#KovaiMinnal", "brand_px": 40,
                   "design": "minnal", "brand_en": "KOVAI MINNAL", "city": "coimbatore",      # city: its own rate pages (owner 17 Nov)
                   "reel": True, "post": False},      # owner 17 Nov (ours): "only one post thats reel" - the rate as a reel with our
                                                      # music + sound effects (gold_reel.py), no image carousel
    "salem": {"town": "சேலம்", "name1": "சேலம்", "handle": "salem360.official", "tag": "#Salem360", "brand_px": 54},
    "erode": {"town": "ஈரோடு", "name1": "ஈரோடு", "handle": "erode360.official", "tag": "#Erode360", "brand_px": 54},
    "tirupur": {"town": "திருப்பூர்", "name1": "திருப்பூர்", "handle": "tiruppur360.official", "tag": "#Tiruppur360", "brand_px": 52},
    "trichy": {"town": "திருச்சி", "name1": "திருச்சி", "handle": "trichy360.official", "tag": "#Trichy360", "brand_px": 54},
    "karur": {"town": "கரூர்", "name1": "கரூர்", "handle": "karur360.official", "tag": "#Karur360", "brand_px": 54},
}
MONTH_TA = ["ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்", "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"]
MONTH_SHORT = ["ஜன", "பிப்", "மார்", "ஏப்", "மே", "ஜூன்", "ஜூலை", "ஆக", "செப்", "அக்", "நவ", "டிச"]


def log(*a):
    print(datetime.now(IST).strftime("%H:%M:%S"), *a, flush=True)


def clock(hhmm, day):
    h, m = map(int, hhmm.split(":"))
    return datetime(day.year, day.month, day.day, h, m, tzinfo=IST)


def date_ta(day):
    return f"{day.day} {MONTH_TA[day.month - 1]} {day.year}"


def bridge_get(action, **params):
    r = requests.get(os.environ["BRIDGE_URL"], params={"action": action, "key": os.environ["BRIDGE_KEY"], **params}, timeout=120)
    r.raise_for_status()
    d = r.json()
    if not d.get("ok"):
        raise RuntimeError(f"bridge {action}: {d.get('error')}")
    return d


def ig(method, path, token, **params):
    params["access_token"] = token
    if path == "me" and not ig_api.me_allowed(IG):
        raise RuntimeError(f"Instagram: no account id for {IG} ('me' there is the system user) - fill poster/config.json instagram.user_id")
    r = requests.request(method, f"{IG}/{IG_VER + '/' if IG_VER else ''}{path}", params=params if method == "GET" else None,
                         data=params if method == "POST" else None, timeout=120)
    d = r.json()
    if r.status_code >= 400 or "error" in d:
        raise RuntimeError(f"Instagram {path}: {d.get('error', d)}")
    return d


def account_id(token):
    """the page's Instagram account id: config.json's id on the Unified login, else "me" (Instagram login)"""
    return IG_USER_ID or ig("GET", "me", token, fields="user_id")["user_id"]


def page_token(pg):
    """the one minnal-bot token (IG_SYSTEM_TOKEN secret / Minnal bridge), else the page bridge's own token (the reference way)"""
    return ig_api.shared_token(CONFIG, os.environ.get("BRIDGE_URL", ""), page=pg) or bridge_get("token", page=pg)["token"]


def wait_ready(cid, token, minutes=6):
    end = time.time() + minutes * 60
    while time.time() < end:
        st = ig("GET", cid, token, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"container {cid} {st}")
        time.sleep(5)
    raise RuntimeError(f"container {cid} not ready")


def upload(path, kind="image"):
    with open(path, "rb") as f:
        r = requests.post(f"https://api.cloudinary.com/v1_1/{os.environ['CLOUDINARY_CLOUD']}/{kind}/upload",
                          data={"upload_preset": os.environ["CLOUDINARY_PRESET"], "folder": "goldrate"}, files={"file": f}, timeout=300)
    r.raise_for_status()
    return r.json()["secure_url"]


def publish(token, urls, cap):
    uid = account_id(token)
    if len(urls) == 1:
        cid = ig("POST", f"{uid}/media", token, image_url=urls[0], caption=cap)["id"]
    else:
        kids = []
        for u in urls:
            kids.append(ig("POST", f"{uid}/media", token, image_url=u, is_carousel_item="true")["id"])
        for k in kids:
            wait_ready(k, token)
        cid = ig("POST", f"{uid}/media", token, media_type="CAROUSEL", children=",".join(kids), caption=cap)["id"]
    wait_ready(cid, token)
    mid = ig("POST", f"{uid}/media_publish", token, creation_id=cid)["id"]
    link = ig("GET", mid, token, fields="permalink").get("permalink", "")
    return mid, link


def publish_reel(token, video_url, cap, cover_url=""):
    """owner 17 Nov (ours): the rate reel - Instagram's own cover when ours is refused (like post.py's reels)"""
    uid = account_id(token)
    prm = dict(media_type="REELS", video_url=video_url, caption=cap, share_to_feed="true")
    if cover_url:
        prm["cover_url"] = cover_url
    try:
        cid = ig("POST", f"{uid}/media", token, **prm)["id"]
    except RuntimeError as e:
        if not cover_url:
            raise
        log("reel refused with the cover, posting with Instagram's own cover:", str(e)[:150])
        prm.pop("cover_url")
        cid = ig("POST", f"{uid}/media", token, **prm)["id"]
    wait_ready(cid, token, 15)
    mid = ig("POST", f"{uid}/media_publish", token, creation_id=cid)["id"]
    return mid, ig("GET", mid, token, fields="permalink").get("permalink", "")


# ---------- history: one row per day {"date", "g22", "g24", "silver"} ----------
def load_history():
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:
        return []


def save_today(hist, day, gold, silver):
    row = next((h for h in hist if h["date"] == day.isoformat()), None)
    if row is None:
        row = {"date": day.isoformat()}
        hist.append(row)
    row.update({"g22": gold["g22"], "g24": gold["g24"], "gold_sources": gold["sources"]})
    if silver:
        row.update({"silver": silver["silver"], "silver_sources": silver["sources"]})
    hist.sort(key=lambda h: h["date"])
    del hist[:-60]      # keep two months
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")


def previous(hist, day, key):
    """the last saved value before today (normally yesterday) and its date"""
    rows = [h for h in hist if h["date"] < day.isoformat() and h.get(key)]
    return (rows[-1][key], date.fromisoformat(rows[-1]["date"])) if rows else (None, None)


def week(hist, day, key, today_val):
    """the last 7 days for the chart: a day with no saved rate (e.g. Sunday) keeps the day before's rate"""
    have = {h["date"]: h[key] for h in hist if h.get(key)}
    start = (day - timedelta(days=6)).isoformat()
    before = [d for d in have if d < start]
    last = have[max(before)] if before else None      # a quiet first day (Sunday) keeps the rate of the last day before it
    pts = []
    first = min(have) if have else day.isoformat()
    for i in range(6, -1, -1):
        d = day - timedelta(days=i)
        v = today_val if i == 0 else have.get(d.isoformat(), last)
        if v is None:
            continue
        last = v
        if d.isoformat() >= first or i == 0:
            pts.append((f"{d.day} {MONTH_SHORT[d.month - 1]}", v))
    return pts


def rates_for_slides(hist, day, gold, silver):
    g22p, pday = previous(hist, day, "g22")
    g24p, _ = previous(hist, day, "g24")
    r = {"date": date_ta(day), "g22": gold["g22"], "g24": gold["g24"],
         "g22_prev": g22p if g22p is not None else gold["g22"], "g24_prev": g24p if g24p is not None else gold["g24"],
         "vs": "நேற்றைய விலையைவிட" if pday == day - timedelta(days=1) else "முந்தைய விலையைவிட",
         "week22": week(hist, day, "g22", gold["g22"])}
    if silver:
        sp, _ = previous(hist, day, "silver")
        r.update({"silver": silver["silver"], "silver_prev": sp if sp is not None else silver["silver"],
                  "weeksilver": week(hist, day, "silver", silver["silver"])})
    return r


def change_text(d, unit):
    if d < 0:
        return f"₹{abs(d):,} குறைவு{unit}"
    if d > 0:
        return f"₹{d:,} உயர்வு{unit}"
    return "மாற்றமில்லை"


def caption(p, day, r):
    lines = [f"💰 இன்றைய தங்கம், வெள்ளி விலை | {date_ta(day)}", "",
             f"🟡 22K தங்கம் (1 கிராம்): ₹{render.inr(r['g22'])} ({change_text(r['g22'] - r['g22_prev'], '')})",
             f"🟡 24K தங்கம் (1 கிராம்): ₹{render.inr(r['g24'])} ({change_text(r['g24'] - r['g24_prev'], '')})"]
    if p.get("design") == "minnal":      # owner 17 Nov: how Tamil Nadu buys gold - the sovereign, and what 3% GST adds
        lines.insert(2, f"🟡 22K 1 சவரன் (8 கிராம்): ₹{render.inr(r['g22'] * 8)} ({change_text((r['g22'] - r['g22_prev']) * 8, '')})")
        lines.append(f"💡 1 சவரன் + 3% ஜிஎஸ்டி: ₹{render.inr(r['g22'] * 8 * 1.03)} (செய்கூலி, சேதாரம் தனி)")
    if r.get("silver"):
        lines.append(f"⚪ வெள்ளி (1 கிராம்): ₹{render.inr(r['silver'])} ({change_text(r['silver'] - r['silver_prev'], '')})")
    market = f"{p['town']} விலை நிலவரம்" if p.get("city") else "சென்னை சந்தை விலை (தமிழ்நாடு)"      # owner 17 Nov: Kovai says Kovai
    lines += ["", f"{market}. ஜிஎஸ்டி, செய்கூலி, சேதாரம் தனி; கடைகளுக்கு ஏற்ப விலை சற்று மாறலாம்.", "",
              f"தினமும் காலை தங்கம், வெள்ளி விலை அறிய Follow செய்யுங்கள் 🙏 @{p['handle']}", "",
              f"#தங்கம்விலை #GoldRate #SilverRate #GoldPriceToday #{p['town']} {p['tag']}"]
    return "\n".join(lines)


def state_path(page, kind="post"):
    return STATE_DIR / (f"posted_{page}.json" if kind == "post" else f"posted_{kind}_{page}.json")


REEL_HEAD = "⚡ தங்கம், வெள்ளி விலை இன்று"      # the reel caption's first words (never inside the carousel caption)


def reel_caption(p, day, r):
    return caption(p, day, r).replace("💰 இன்றைய தங்கம், வெள்ளி விலை |", REEL_HEAD + " |", 1)


def already_posted(page, day, token=None, kind="post"):
    """kind "post" (the carousel) or "reel" - each is checked on its own, so a failed reel never posts the carousel again"""
    try:
        st = json.loads(state_path(page, kind).read_text(encoding="utf-8"))
        if st.get("date") == day.isoformat():
            return f"state file: {st.get('permalink')}"
    except Exception:
        pass
    if token:
        try:
            uid = account_id(token)
            mark = f"இன்றைய தங்கம், வெள்ளி விலை | {date_ta(day)}" if kind == "post" else f"{REEL_HEAD} | {date_ta(day)}"
            for m in ig("GET", f"{uid}/media", token, fields="caption,permalink", limit=15).get("data", []):
                if mark in (m.get("caption") or ""):
                    return f"Instagram already has today's {kind} {m.get('permalink')}"
        except Exception as e:
            log("could not read recent posts:", str(e)[:150])
    return ""


def main():
    pages = [p for p in os.environ.get("GOLD_PAGES", "namakkal rasipuram").split() if p in PAGES]
    now = datetime.now(IST)
    day = date.fromisoformat(FORCE_DATE) if FORCE_DATE else now.date()
    log(f"gold & silver rate for {', '.join(pages)} - {date_ta(day)}{' (DRY RUN)' if DRY else ''}")
    tokens = {}
    if not DRY:
        for pg in pages:
            try:
                tokens[pg] = page_token(pg)
            except Exception as e:
                log(f"{pg}: no Instagram token - skipped ({str(e)[:120]})")
        pages = [pg for pg in pages if pg in tokens]
    kinds = {pg: (["post"] if PAGES[pg].get("post", True) else []) + (["reel"] if PAGES[pg].get("reel") and REEL_ON else [])
             for pg in pages}
    need = {pg: [k for k in kinds[pg] if DRY or not already_posted(pg, day, tokens.get(pg), k)] for pg in pages}
    todo = [pg for pg in pages if need[pg]]
    for pg in pages:
        for k in set(kinds[pg]) - set(need[pg]):
            log(f"{pg}: {k} already posted today - {already_posted(pg, day, tokens.get(pg), k)}")
    if not todo:
        return 0
    start = clock(START_AT, day)
    if not FORCE_DATE and datetime.now(IST) < start:
        wait = (start - datetime.now(IST)).total_seconds()
        log(f"waiting {int(wait)} s until {START_AT} (the rate is fixed at 9:30 AM)")
        time.sleep(max(0, wait))
    cities = {PAGES[pg].get("city", "chennai") for pg in todo}      # owner 17 Nov: a page with its own city reads that city's pages
    city = cities.pop() if len(cities) == 1 else "chennai"
    while True:
        log(f"reading today's rate ({city})")
        got = sources.collect(day, log, city=city)
        gold, silver = got["gold"], got["silver"]
        t = datetime.now(IST)
        if gold and (silver or FORCE_DATE or t >= clock(SILVER_WAIT_UNTIL, day)):
            break
        if FORCE_DATE or t >= clock(GIVE_UP_AT, day):
            if gold:
                break
            raise SystemExit(f"today's gold rate was not confirmed by 2 pages by {GIVE_UP_AT} - nothing posted")
        log(f"not confirmed yet (gold {'ok' if gold else 'waiting'}, silver {'ok' if silver else 'waiting'}) - trying again in 5 minutes")
        time.sleep(300)
    log(f"CONFIRMED gold 22K ₹{gold['g22']} 24K ₹{gold['g24']} ({', '.join(gold['sources'])})"
        + (f"; silver ₹{silver['silver']}/g ({', '.join(silver['sources'])})" if silver else "; silver not confirmed - gold slide only"))
    hist = load_history()
    r = rates_for_slides(hist, day, gold, silver)
    if not DRY:
        save_today(hist, day, gold, silver)
    for pg in todo:
        p = dict(PAGES[pg], logo=ROOT / "kit" / f"logo_{pg}.png")
        out = ROOT / "out" / "goldrate" / pg
        if "post" in need[pg]:
            post_carousel(pg, p, day, r, out, tokens.get(pg))
        if "reel" in need[pg]:      # after the carousel when a page has both (Kovai: the reel only)
            post_reel(pg, p, day, r, out, tokens.get(pg))
    return 0


def post_carousel(pg, p, day, r, out, token):
    jpgs = (minnal_render if p.get("design") == "minnal" else render).render(p, r, out, log)
    cap = caption(p, day, r)
    (out / "caption.txt").write_text(cap, encoding="utf-8")
    log(f"{pg} caption:\n{cap}")
    if DRY:
        log(f"DRY RUN: {pg} slides in {out} - not posted")
        return
    try:
        if already_posted(pg, day, token):
            log(f"{pg}: posted meanwhile - stop")
            return
        urls = [upload(j) for j in jpgs]
        mid, link = publish(token, urls, cap)
        log(f"{pg}: POSTED {link}")
        state_path(pg).write_text(json.dumps({"date": day.isoformat(), "media_id": mid, "permalink": link,
                                              "posted_at": datetime.now(IST).isoformat()}, ensure_ascii=False), encoding="utf-8")
        try:      # same carousel to the page's Facebook page when it is set up (never touches the Instagram post)
            sys.path.insert(0, str(ROOT / "poster"))
            import facebook
            facebook.share(pg, f"goldrate-{day.isoformat()}", "photos", urls, cap, p["tag"], always=True, story=False)
        except Exception as e:
            log("Facebook step skipped:", str(e)[:150])
    except Exception as e:
        log(f"{pg}: NOT POSTED - {str(e)[:300]}")


def post_reel(pg, p, day, r, out, token):
    """owner 17 Nov (ours): the rate reel. Never stops the carousel: any failure is logged and the carousel goes on."""
    try:
        made = gold_reel.make(p, r, out / "reel", log)
        cap = reel_caption(p, day, r)
        (out / "reel" / "caption.txt").write_text(cap, encoding="utf-8")
        if DRY:
            log(f"DRY RUN: {pg} reel {made['mp4']} - not posted")
            return
        if already_posted(pg, day, token, "reel"):
            log(f"{pg}: reel posted meanwhile - stop")
            return
        video = upload(made["mp4"], "video")
        try:
            cover = upload(made["cover"])
        except Exception as e:
            log("reel cover not uploaded (Instagram's own cover):", str(e)[:120])
            cover = ""
        mid, link = publish_reel(token, video, cap, cover)
        log(f"{pg}: REEL POSTED {link}")
        state_path(pg, "reel").write_text(json.dumps({"date": day.isoformat(), "media_id": mid, "permalink": link,
                                                      "posted_at": datetime.now(IST).isoformat()}, ensure_ascii=False), encoding="utf-8")
        try:      # same reel to the page's Facebook page when it is set up
            sys.path.insert(0, str(ROOT / "poster"))
            import facebook
            facebook.share(pg, f"goldrate-reel-{day.isoformat()}", "reel", [video], cap, p["tag"], always=True, story=False)
        except Exception as e:
            log("Facebook reel step skipped:", str(e)[:150])
    except Exception as e:
        log(f"{pg}: REEL NOT POSTED - {str(e)[:300]}")


if __name__ == "__main__":
    sys.exit(main())
