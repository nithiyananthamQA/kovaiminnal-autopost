"""District power-cut pages (owner 11 Nov) - turns the Kovai Minnal pipeline into ONE district page's pipeline, in this process only.

Kovai Minnal's files run exactly as they are. Every page-specific value (page name, follow line, writer rules, place lists, Sheet,
state files, logo, hashtags) is switched here, after import, for one district. districts/run.py starts one process per district,
so two pages never share a value. Every switch is checked: a missing target (a renamed constant after a reference-repo update)
or a Kovai / Coimbatore word left in a district prompt stops the run - a district page never posts Kovai Minnal branding.

Own Sheet: the district pages use their own Apps Script bridge (DISTRICT_BRIDGE_URL / DISTRICT_BRIDGE_KEY); Kovai's Sheet and
jobs never see a district row. Own state: districts/state/<key>/ (power cuts found, writer state, Facebook state).
"""
import datetime
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "districts"
STATE_ROOT = HERE / "state"
OUT_ROOT = ROOT / "out" / "districts"
for _p in (ROOT / "reel", ROOT / "poster", ROOT / "research_free"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

# words that must never reach a district page (prompts, captions, reels)
LEAK = re.compile(r"கோவை|கோயம்புத்தூர்|கோயமுத்தூர்|Kovai|KOVAI|kovai|Coimbatore|COIMBATORE|coimbatore|பொள்ளாச்சி|Pollachi|மேட்டுப்பாளையம்|Mettupalayam")
POWER_SLUG = re.compile(r"power|electric|current|shutdown|outage|supply|maintenance|eb-|tneb|tangedco|substation", re.I)


def log(*a):
    print(datetime.datetime.now(IST).strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- the switch and the list
def settings():
    cfg = json.loads((ROOT / "poster" / "config.json").read_text(encoding="utf-8"))
    return cfg.get("district_powercut") or {}


def districts():
    return json.loads((HERE / "districts.json").read_text(encoding="utf-8"))["districts"]


def enabled_keys():
    """[] when the feature is off (poster/config.json district_powercut.enabled = false): then nothing of it runs"""
    s = settings()
    if s.get("enabled") is not True:
        return []
    off = set(s.get("disabled") or [])
    live = s.get("live")      # 13 Nov: pages go live one by one - when the list is there, only the pages named in it run
    return [k for k in districts() if k not in off and (live is None or k in live)]


def page(key):
    d = dict(districts()[key], key=key)
    d["tag"] = "#" + re.sub(r"[^A-Za-z0-9]", "", d["name_en"])
    d["en_tag"] = re.sub(r"[^A-Za-z0-9]", "", d["en"])
    d["ta_tag"] = "#" + d["ta"].replace(" ", "")
    d["logo"] = HERE / key / "logo.png"
    d["footer"] = HERE / key / "footer.png"
    d["state"] = STATE_ROOT / key
    d["out"] = OUT_ROOT / key
    return d


# ---------------------------------------------------------------- text: Kovai Minnal -> this district
def swaps(d):
    ta, en, et = d["ta"], d["en"], d["en_tag"]
    return [
        (r"மேலும் செய்திகளுக்கு கோவை மின்னல் பக்கத்தை பின்தொடருங்கள்\.?", d["follow_spoken"]),
        (r"உள்ளூர் செய்திகளுக்கு Follow செய்யுங்கள் 🙏", d["follow_caption"]),
        (r"#KovaiMinnal", d["tag"]),
        (r"Kovai Minnal", d["name_en"]),
        (r"KOVAIMINNAL", d["handle"].upper()),
        (r"kovaiminnal", d["handle"]),
        (r"கோவை மின்னல்", d["name_ta"]),
        (r"\(Coimbatore city, Pollachi[^)]*\)", f"({en} town, its taluks and the villages)"),
        (r"Coimbatore city / Pollachi / Mettupalayam", f"any town or village of {en} district"),
        (r"\(கோவை, கோயம்புத்தூர், பொள்ளாச்சி[^)]*\)", f"({ta} and every town / village exactly as the article spells it)"),
        (r"மே\.பாளையம் = மேட்டுப்பாளையம், பெ\.நா\.பாளையம் = பெரியநாயக்கன்பாளையம், கோயமுத்தூர் = கோயம்புத்தூர் \(கோவை is the well-known name and is fine\)",
         "the short form = the full official name (as the government writes it)"),
        (r"\(#Pollachi, #Mettupalayam, #Gandhipuram[^)]*\)", "(the town's own tag)"),
        (r"பொள்ளாச்சி அருகே நெகமத்தில்", f"{ta} அருகே உள்ள கிராமத்தில்"),
        (r"நெகமம், பொள்ளாச்சி", f"கிராமம், {ta}"),
        (r"பொள்ளாச்சியில்|கோவையில்|மேட்டுப்பாளையத்தில்", f"{ta} பகுதியில்"),
        (r"#Coimbatore", "#" + et),
        (r"#கோவை", d["ta_tag"]),
        (r"COIMBATORE CITY", f"{en.upper()} DISTRICT"),
        (r"Coimbatore", en), (r"COIMBATORE", en.upper()), (r"coimbatore", d["key"]),
        (r"கோயம்புத்தூர்|கோயமுத்தூர்|கோவை", ta),
        (r"பொள்ளாச்சி|மேட்டுப்பாளையம்", ta), (r"Pollachi|Mettupalayam", en),
    ]


def swap(text, d, what="text"):
    for pat, rep in swaps(d):
        text = re.sub(pat, lambda _m, r=rep: r, text)
    left = LEAK.search(text)
    if left:
        i = left.start()
        raise RuntimeError(f"{what}: Kovai Minnal word left for {d['key']}: ...{text[max(0, i - 60):i + 60]}...")
    return text


def preface(d):
    return (f'POWER-CUT PAGE (read this first): "{d["name_ta"]}" ({d["name_en"]}) is the page for {d["en"]} district ({d["ta"]} மாவட்டம்) '
            f"and posts ONLY power-cut / maintenance shutdown notices (மின்தடை அறிவிப்பு) of {d['en']} district, so people know early. "
            "Every article you get is such a notice: read the cut day, the time, the substation and EVERY affected area exactly as "
            "published (none dropped, never guessed). The CAPTION lists every affected area. The reel_script is SHORT (owner 13 Nov: "
            "30-40 seconds): at most 6 sentences - the one-line story, the day + time, the main areas in at most 2 sentences (up to 8 "
            "names, then 'உள்ளிட்ட பகுதிகள்'), then the follow line. category is always \"மின் தடை\", importance \"High\", post_to exactly "
            f"\"{d['name_en']}\". The LAST sentence of reel_script is exactly: {d['follow_spoken']}\n\n")


def news_texts(d):
    """the NEWS follow lines of a district page (owner 13 Nov: never the power-cut line on other news)"""
    try:
        top = json.loads((HERE / "districts.json").read_text(encoding="utf-8"))
    except Exception:
        top = {}
    sp = top.get("follow_news_spoken") or "{city} செய்திகளை உடனுக்குடன் தெரிந்துகொள்ள {page} பக்கத்தை ஃபாலோ செய்யுங்கள்."
    cp = top.get("follow_news_caption") or "{city} செய்திகளுக்கு {page} பக்கத்தை Follow செய்யுங்கள் 📌"
    return {"spoken": sp.format(city=d["ta"], page=d["name_ta"]), "caption": cp.format(city=d["ta"], page=d["name_ta"])}


def news_preface(d):
    return (f'LOCAL NEWS PAGE (read this first): "{d["name_ta"]}" ({d["name_en"]}) is the local news page for {d["en"]} ({d["ta"]}). '
            f"Write this {d['en']} news exactly as the article says - nothing invented, no opinion, names and numbers only as published. "
            f"post_to exactly \"{d['name_en']}\". The reel_script is short (30-45 seconds). "
            f"The LAST sentence of reel_script is exactly: {d['follow_spoken']}\n\n")


def news_on(key):
    s = settings()
    return s.get("enabled") is True and key in (s.get("news_live") or [])


def dinamalar_meta(d):
    """newsid -> publish time + short description, from the district page's own data"""
    import sources as S
    h = S._get(f"https://www.dinamalar.com/news/tamil-nadu-district-news-{d['dinamalar']}")
    out = {}
    for m in re.finditer(r'"newsid":(\d+),"newstitle":"(?:[^"\\]|\\.)*","newsdescription":"((?:[^"\\]|\\.)*)".{0,200}?"newsdate":"([0-9: -]{16,19})"', h):
        try:
            desc = json.loads('"' + m.group(2) + '"')
        except Exception:
            desc = ""
        out[m.group(1)] = {"published": m.group(3).replace(" ", "T") + "+05:30", "snippet": desc}
    return out


def find_news(d, dry=False, log=print):
    """owner 13 Nov (Chennai): every new local news of the page, highest points first (the reference's score: reader interest,
    outlets, our insights, freshness), at most news_per_run per check and news_per_day a day. The first run only remembers what
    is already on the page (no flood). Power cuts, obituaries, ceremonies and other districts' news are left out."""
    import collect, pick
    import freshness as F
    import allnews
    s = settings()
    per_run, per_day = int(s.get("news_per_run", 1)), int(s.get("news_per_day", 10))
    max_age = float(s.get("news_max_age_hours", 6))
    path = d["state"] / "news_state.json"
    first = not path.exists()
    try:
        st = json.loads(path.read_text(encoding="utf-8")) if not first else {}
    except Exception:
        st = {}
    seen, days = st.setdefault("seen", {}), st.setdefault("days", {})
    now = datetime.datetime.now(IST)
    today = now.date().isoformat()
    meta = dinamalar_meta(d)
    cands, skipped = [], {}
    for x in dinamalar_list(d):
        u, t = x["url"], x.get("title") or ""
        if u in seen:
            continue
        if first:
            seen[u] = today
            continue
        m = meta.get(u.rsplit("/", 1)[-1], {})
        why = ("power cut (own finder)" if F.is_power_cut(t) else "") or pick.auto_ok({"title": t, "url": u}) \
            or ("another district" if allnews.other_district(t) else "") or ("no headline" if not t else "")
        try:
            age = (now - datetime.datetime.fromisoformat(m["published"])).total_seconds() / 3600 if m.get("published") else None
        except Exception:
            age = None
        if not why and (age is None or age > max_age):
            why = "older than %g h" % max_age if age is not None else "no publish time"
        if why:
            seen[u] = today
            skipped[why[:30]] = skipped.get(why[:30], 0) + 1
            continue
        n = {"title": t, "snippet": m.get("snippet", ""), "mentions": 1, "published": m.get("published", "")}
        cands.append((collect.score(n), t, u))
    cands.sort(key=lambda c: -c[0])
    room = max(0, min(per_run, per_day - int(days.get(today, 0))))
    take = cands[:room]
    for _, _, u in take:
        seen[u] = today
    days[today] = int(days.get(today, 0)) + len(take)
    cut = (now - datetime.timedelta(days=7)).date().isoformat()
    st["seen"] = {k: v for k, v in seen.items() if v >= cut}
    st["days"] = {k: v for k, v in days.items() if k >= cut}
    if first:
        log(f"news, first run for {d['key']}: {len(st['seen'])} links already on the page remembered - only newer news is written")
    for sc, t, u in take:
        log(f"NEWS {sc:.1f} points: {t[:90]} <{u}>")
    if skipped:
        log("news skipped: " + ", ".join(f"{k}={v}" for k, v in skipped.items()))
    if cands[room:]:
        log(f"news waiting for a later check: {len(cands) - len(take)} (today {days[today]}/{per_day})")
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    (d["out"]).mkdir(parents=True, exist_ok=True)
    (d["out"] / "news_urls.txt").write_text("\n".join(u for _, _, u in take), encoding="utf-8")
    return [u for _, _, u in take]


def make_dirs(d):
    d["state"].mkdir(parents=True, exist_ok=True)
    d["out"].mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- environment (before ANY pipeline module is imported)
def use_bridge():
    """the district pages' own Sheet. Kovai's bridge is refused - a district row must never reach Kovai Minnal's Sheet."""
    url, key = os.environ.get("DISTRICT_BRIDGE_URL", "").strip(), os.environ.get("DISTRICT_BRIDGE_KEY", "").strip()
    if not url or not key:
        raise SystemExit("DISTRICT_BRIDGE_URL / DISTRICT_BRIDGE_KEY missing - the district pages have their own Sheet; nothing done")
    if url == os.environ.get("KOVAI_BRIDGE_URL", os.environ.get("BRIDGE_URL", "")).strip():
        raise SystemExit("DISTRICT_BRIDGE_URL is Kovai Minnal's bridge - refused (district rows must never reach Kovai's Sheet)")
    os.environ["KOVAI_BRIDGE_URL"] = os.environ.get("KOVAI_BRIDGE_URL", os.environ.get("BRIDGE_URL", ""))
    os.environ["BRIDGE_URL"], os.environ["BRIDGE_KEY"] = url, key


def use_facebook(d):
    """the workflow gives this district's Facebook page as FB_PAGE_ID / FB_TOKEN; poster/facebook.py reads FB_PAGE_ID_<KEY>"""
    k = re.sub(r"[^A-Z0-9]", "_", d["key"].upper())
    for name in ("FB_PAGE_ID", "FB_TOKEN"):
        if os.environ.get(name):
            os.environ[f"{name}_{k}"] = os.environ[name]
    for v in [v for v in os.environ if v.startswith(("FB_PAGE_ID_", "FB_TOKEN_")) and not v.endswith("_" + k)]:
        del os.environ[v]      # never another page's Facebook


# ---------------------------------------------------------------- module switches
def _set(mod, name, value):
    if not hasattr(mod, name):
        raise RuntimeError(f"district switch: {mod.__name__}.{name} no longer exists - check districts/pipeline.py after the update")
    setattr(mod, name, value)


def _own_rows(d, r):
    if isinstance(r, dict) and isinstance(r.get("rows"), list):
        return dict(r, rows=[x for x in r["rows"] if str(x.get("post_to") or "").strip() == d["name_en"]])
    return r


_APPLIED = []


def apply(key, mode="powercut"):
    """switch every pipeline module to the district page `key` (once per process); returns the page dict.
    mode "news" (owner 13 Nov, Chennai): the page's other local news - news preface, all writer examples, news follow lines"""
    if _APPLIED:
        if _APPLIED[0] != key:
            raise RuntimeError(f"this process already runs {_APPLIED[0]} - one district per process")
        return page(key)
    _APPLIED.append(key)
    d = page(key)
    if mode == "news":
        d = dict(d, follow_spoken=news_texts(d)["spoken"], follow_caption=news_texts(d)["caption"])
    import allnews as A
    import sources as S
    import validate as V
    import run as RN
    import collect as C
    import powercut as PC
    import post as P
    import freshness as F
    import facebook as FB
    import tamilcheck as T
    import factgate as G
    slug = d["dinamalar"]

    # places: this district only (a Dinamalar link filed under the district is the district's news)
    words = [d["ta"], d["en"]]
    _set(A, "DISTRICT_SLUGS", (slug, key))
    _set(A, "COIMBATORE_WORDS", words)
    _set(A, "PLACE_STEMS", list(dict.fromkeys(f for w in words if not w.isascii() for f in A._stem_forms(w))))
    for name in ("TOWNS", "CITY_AREAS", "TOWN_ROADS", "CITY_ROADS", "NOT_PLACE", "CANON_PLACES"):
        _set(A, name, [])
    _set(A, "CITY_ONLY", False)
    # "another district" = the other Tamil Nadu districts (Kovai's list holds Coimbatore's neighbour towns - Attur is Salem's own town)
    others = {k: x for k, x in districts().items() if k != key}
    _set(A, "OTHER_PLACES", [x["ta"] for x in others.values()] + ["கோவை", "கோயம்புத்தூர்"])
    _set(A, "OTHER_EN", sorted({w for x in others.values() for w in (x["en"].lower(), x["dinamalar"]) if w.isalpha()} | {"coimbatore", "kovai"}))
    _set(A, "QUERIES", list(d["queries"]))
    _set(A, "SITE_QUERIES", [d["ta"]])
    _set(S, "DISTRICT", f"tamil-nadu-district-news-{slug}")
    _set(S, "LIST_URL", "https://www.dinamalar.com/news/" + S.DISTRICT)
    _set(A, "from_dinamalar_list", lambda: dinamalar_list(d))
    stem = d["ta"][:3]
    _set(F, "_POWER_COMMON", F._POWER_COMMON + (stem, d["en"].lower()[:5]))
    _set(F, "_PLACE_COMMON", F._PLACE_COMMON + (stem, d["en"].lower()[:5]))
    _set(F, "_GENERIC", F._GENERIC + (stem, d["en"].lower()[:5]))

    # writer: the reference rules, with this page's name, follow line and place, + the power-cut page note
    _set(RN, "SYSTEM", (news_preface(d) if mode == "news" else preface(d)) + swap(RN.SYSTEM, d, "writer rules"))
    pc_ex = [e for e in RN.EX if (e.get("output") or {}).get("category") == "மின் தடை"][:1]
    _set(RN, "EX", json.loads(swap(json.dumps(RN.EX[:3] if mode == "news" else pc_ex, ensure_ascii=False), d, "writer example")))
    _set(RN, "CHECK", swap(RN.CHECK, d, "fact-check prompt"))
    _set(RN, "PROOF", swap(RN.PROOF, d, "proofread prompt"))
    _set(C, "BRIEF_SYSTEM", swap(C.BRIEF_SYSTEM, d, "picture prompt"))
    _set(G, "CONFIRM", swap(G.CONFIRM, d, "fact-gate prompt"))
    _set(G, "SOFT", tuple(G.SOFT) + (d["name_ta"],))
    _set(V, "PAGE", d["name_en"])
    _set(V, "LAST", d["follow_spoken"])
    _set(V, "FOLLOW", d["follow_caption"])
    _set(V, "DISTRICT_WORDS", tuple(V.DISTRICT_WORDS) + (d["ta"],))
    _set(T, "LAST", d["follow_spoken"])
    _set(T, "KEEP", tuple(T.KEEP) + (d["ta"], d["name_ta"], "பவர்கட்", "சேனல்", "ஃபாலோ"))

    # collector: own Sheet, own state, no Kovai workflow started
    _set(C, "BRIDGE_URL", os.environ["BRIDGE_URL"])
    _set(C, "BRIDGE_KEY", os.environ["BRIDGE_KEY"])
    _set(C, "PAGE_NAME", d["name_en"])
    _set(C, "IG_PAGES", (key,))
    _set(C, "ARCHIVE", d["state"])
    _set(C, "QUEUE", d["state"] / "queue.json")
    _set(C, "trigger_posting", lambda log=None: None)
    _set(C, "trigger_workflow", lambda name, inputs=None, log=None: False)
    _bridge = C.bridge
    _set(C, "bridge", lambda action, **kw: _own_rows(d, _bridge(action, **kw)) if action in ("recent", "queue") else _bridge(action, **kw))

    # power-cut finder: the district's own Dinamalar page + one news search per paper
    _set(PC, "QUERIES", [])      # the news searches run once per run for all districts (shared_search)
    _set(PC, "SITES", ("dinamalar.com", "dinamani.com"))
    _set(PC, "DISTRICT_URL", (f"district-news-{slug}",))
    _set(PC, "PAGE_KEY", key)
    _set(PC, "STATE", d["state"] / "powercut_state.json")
    _set(PC, "URLS", d["out"] / "powercut_urls.txt")
    _set(PC, "links", lambda: district_links(d))
    _set(PC, "same_cut", same_cut(PC.same_cut))

    # poster: this page only
    _set(P, "BRIDGE_URL", os.environ["BRIDGE_URL"])
    _set(P, "BRIDGE_KEY", os.environ["BRIDGE_KEY"])
    _set(P, "PAGE", key)
    _set(P, "PAGES", (key,))
    _set(P, "LABEL", {key: d["name_ta"]})
    _set(P, "PAGE_TAGS", {key: d["tag"]})
    _set(P, "PAGE_LOGOS", {key: d["logo"]})
    _set(P, "LOGO", d["logo"])
    _set(P, "TAG", d["tag"])
    _set(P, "PAGE_EN", d["name_en"])
    _set(P, "FOLLOW_LINE", d["follow_spoken"])
    _set(P, "SAVE_LINE", d["follow_caption"])
    _set(P, "FIRST_COMMENTS", [x for x in P.FIRST_COMMENTS if not LEAK.search(x)] + [d["follow_caption"]])
    _set(P, "DISTRICTS", (slug, key))
    _set(P, "DEFAULT_LOC", d["ta"])
    _set(P, "HOME_PLACES", P.HOME_PLACES + "|" + re.escape(d["ta"]))
    _set(P, "OUT", d["out"])
    _set(P, "CACHE", d["out"] / "prebuilt")
    _set(P, "pages_of", lambda row: [key])
    ig = d.get("instagram") or {}
    if ig.get("api") == "unified":      # 13 Nov: Meta Unified login (app Minnal Pages): system-user token, graph.facebook.com, account id
        uid = str(ig.get("user_id") or "").strip()
        _set(P, "IG_HOST", "https://graph.facebook.com")
        _set(P, "IG_VER", P.IG_VER or "v24.0")
        _set(P, "IG_USER_ID", uid)
        if not uid:      # finding and writing go on; only posting waits ('me' there is the system user, never the page)
            _set(P, "missing_setup", lambda: print(f"{key}: Instagram account id missing (districts.json instagram.user_id) - nothing posted", flush=True) or True)
    try:
        picked = set(json.loads(PC.STATE.read_text(encoding="utf-8")).get("done", {}))
    except Exception:
        picked = set()
    _set(P, "_PICKED", picked)      # the cuts this page's finder chose are posted like Kovai's (no owner tick)
    _pget = P.bridge_get
    _set(P, "bridge_get", lambda action, **kw: _own_rows(d, _pget(action, **kw)) if action in ("recent", "queue") else _pget(action, **kw))
    reach = dict(P.CONFIG.get("reach") or {})
    et = d["en_tag"]
    reach.update({"hashtag_profiles": {d["tag"].lower(): {"page": d["tag"], "area": "#" + et, "news": f"#{et}PowerCut", "tamil": d["ta_tag"],
                                                          "fallback": f"#{et}News", "topic": {"power_cut": f"#{et}PowerCut"}}},
                  "place_tags": {}, "district_tag": "#" + et, "broad_tag": f"#{et}PowerCut", "extra_tag": f"#{et}News",
                  "search_suffix": f"{d['en']} power cut"})
    P.CONFIG["reach"] = reach
    P.CONFIG["locations"] = {}
    P.CONFIG["location_tags"] = False
    _set(FB, "STATE", d["state"] / "fb_posted")
    return d


# ---------------------------------------------------------------- finder: the district's Dinamalar page (headlines read from the page data)
_LINKS = {}


def dinamalar_list(d, limit=80):
    import sources as S
    slug = d["dinamalar"]
    h = S._get(f"https://www.dinamalar.com/news/tamil-nadu-district-news-{slug}")
    titles = {}
    for m in re.finditer(r'"newsid":(\d+),"newstitle":"((?:[^"\\]|\\.)*)"', h):
        try:
            titles[m.group(1)] = json.loads('"' + m.group(2) + '"')
        except Exception:
            pass
    links = []
    for m in re.finditer(r"/news/(tamil-nadu-district-news-" + re.escape(slug) + r")/(?:(\d{6,})/([a-z0-9-]+)|([a-z0-9-]+)/(\d{6,}))", h):
        s_, nid = (m.group(3), m.group(2)) if m.group(2) else (m.group(4), m.group(5))
        u = f"https://www.dinamalar.com/news/{m.group(1)}/{s_}/{nid}"
        if u not in [x["url"] for x in links]:
            links.append({"key": u, "url": u, "title": titles.get(nid, ""), "source": "தினமலர்", "published": "", "via": "dinamalar-list",
                          "query": "district list", "snippet": "", "_slug": s_})
    return links[:limit]


# Dinamani files a district under its own spelling (edition-trichy/tanjore/...): these names are the same district
ALIASES = {"thanjavur": ["tanjore"], "thoothukudi": ["tuticorin"], "viluppuram": ["villupuram"], "tirupathur": ["tirupattur"],
           "chengalpattu": ["chengalpet"], "trichy": ["tiruchi", "tiruchirappalli"], "tirunelveli": ["nellai"],
           "kanyakumari": ["nagercoil"], "nilgiris": ["ooty", "udhagamandalam"], "kanchipuram": ["kanchi"]}
SHARED = OUT_ROOT / "search.json"
SHARED_QUERIES = ["மின்தடை", "மின் தடை நாளை", "மின் நிறுத்தம்"]


def names_of(d):
    return {d["key"], d["dinamalar"], re.sub(r"[^a-z]", "", d["en"].lower())} | set(ALIASES.get(d["key"], []))


OTHER_AREAS = {"coimbatore", "kovai", "puducherry", "pondicherry", "karaikal"}      # filed under a place that is no district page here


def filed_under(url):
    """the district a paper filed the link under ('' when the link does not say, or names a section like 'tamilnadu')"""
    import allnews as A
    m = re.search(r"dinamani\.com/([a-z]+)/20\d\d/", url or "")
    w = A.url_district(url) or (m.group(1) if m else "")
    known = OTHER_AREAS.union(*(names_of(dict(x, key=k)) for k, x in districts().items()))
    return w if w in known else ""


def shared_search(log_=print):
    """ONE news search per run for every district (the same results used to be fetched and opened 37 times): power-cut headlines of
    Dinamalar and Dinamani, Google links decoded -> out/districts/search.json; each district takes the ones filed under it"""
    import concurrent.futures as cf
    import allnews as A
    import powercut as PC
    F = PC.fr()
    items = []
    for q in SHARED_QUERIES:
        for dom in ("dinamalar.com", "dinamani.com"):
            for fn in (A.from_google, A.from_bing):
                try:
                    items += [x for x in fn(f"{q} site:{dom}") if dom in (x.get("site", "") + x.get("url", "")) and F.is_power_cut(x.get("title", ""))]
                except Exception as e:
                    log_(f"{fn.__name__} '{q}' {dom} failed: {str(e)[:80]}")

    def real(it):
        u = it["url"]
        if "news.google.com" in u:
            try:
                u = A.resolve(u)
            except Exception:
                return None
        return dict(it, url=PC.norm(u))
    with cf.ThreadPoolExecutor(8) as ex:
        res = [x for x in ex.map(real, items) if x]
    out, seen = [], set()
    for it in res:
        if it["url"] in seen or not any(s in it["url"] for s in ("dinamalar.com", "dinamani.com")):
            continue
        seen.add(it["url"])
        out.append({k: it.get(k, "") for k in ("url", "title", "published", "source", "via", "query")})
    SHARED.parent.mkdir(parents=True, exist_ok=True)
    SHARED.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    log_(f"shared search: {len(out)} power-cut links ({len(items)} results)")
    return out


def same_link(url):
    """one notice = one link: Dinamalar's /amp/ page and Dinamani's %-encoded link are the same article (seen 12 Nov: posted twice)"""
    import urllib.parse
    import powercut as PC
    return PC.norm(urllib.parse.unquote(url or "").replace("dinamalar.com/amp/news/", "dinamalar.com/news/"))


def same_cut(orig):
    """the reference rule + the same headline for the same cut day (a district's own name is no place, so two copies of
    'நாளை (நவ.12) மின் தடை: சிவகங்கை' shared no place word)"""
    def norm_t(x):
        return re.sub(r"[\s\W]+", "", x.get("title") or "")
    return lambda a, b: orig(a, b) or (a.get("cut_day") == b.get("cut_day") and bool(norm_t(a)) and norm_t(a) == norm_t(b))


def district_links(d):
    """the reference finder (research_free/powercut.py links) for one district: its own Dinamalar page + the run's shared search
    results filed under this district (or, when the link does not say, whose headline names it)"""
    if d["key"] in _LINKS:
        return _LINKS[d["key"]]
    import allnews as A
    import powercut as PC
    items = []
    try:
        items += A.from_dinamalar_list()
    except Exception as e:
        log(f"Dinamalar {d['dinamalar']} page failed: {str(e)[:120]}")
    try:
        shared = json.loads(SHARED.read_text(encoding="utf-8")) if SHARED.exists() else []
    except Exception:
        shared = []
    mine = names_of(d)
    for it in shared:
        where = filed_under(it["url"])
        if (where in mine) if where else A.has_place(it.get("title", "")):
            items.append(it)
    out, seen = [], set()
    for it in items:
        u = same_link(it["url"])
        if u in seen or not any(s in u for s in PC.SITES):
            continue
        seen.add(u)
        out.append(dict(it, url=u))
    _LINKS[d["key"]] = out
    return out


def seed_first_run(d):
    """first run of a district: the links already on its page that are clearly no power cut (no headline in the page data, no power
    word in the link) are remembered unopened - otherwise the first run would open about 2,000 old articles"""
    import powercut as PC
    if PC.STATE.exists():
        return 0
    now = datetime.datetime.now(IST).isoformat()
    st = {"seen": {}, "done": {}, "retried": {}}
    n = 0
    for it in district_links(d):
        if it.get("via") == "dinamalar-list" and not it.get("title") and not POWER_SLUG.search(it.get("_slug", "")):
            st["seen"][it["url"]] = {"at": now, "power_cut": False, "why": "first run: not opened (no power word)", "title": ""}
            n += 1
    PC.STATE.parent.mkdir(parents=True, exist_ok=True)
    PC.STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    return n
