"""What Instagram insights taught us (written by poster/insights.py into learned.json). Used ONLY to order candidate stories and to give the
writer style hints. It never relaxes a fact / quality check."""
import json, pathlib

HERE = pathlib.Path(__file__).parent
TOPICS = {
    "weather": ["மழை", "வெயில்", "வானிலை", "எச்சரிக்கை", "புயல்", "வெள்ளம்", "பனி", "குளிர்"],
    "crime": ["கொலை", "கைது", "திருட", "போலீஸ்", "குற்ற", "மோசடி", "தற்கொலை", "கொள்ளை", "பாலியல்", "போக்சோ", "பறிமுதல்", "கஞ்சா",
              "தாக்கு", "தகராறு", "சிறையில்", "சிறை தண்டனை", "வழிப்பறி", "பறிப்பு", "கடத்த", "லஞ்ச", "போதை", "புகையிலை", "சஸ்பெண்ட்", "முறைகேடு"],
    "accident": ["விபத்து", "பலி", "உயிரிழ", "தீ விபத்து", "மோதி", "தீப்பிடி", "கவிழ்ந்", "நசுங்கி", "சடலம்", "மீட்பு"],
    "temple": ["கோயில்", "கோவில்", "திருவிழா", "தேரோட்ட", "தேர்த்திருவிழா", "சாமி", "பூஜை", "குடமுழுக்கு", "பிரதோஷ", "அபிஷேக", "தரிசன"],      # not "தேர்": it is inside தேர்வு / தேர்தல்
    "politics": ["முதல்வர்", "அமைச்சர்", "திமுக", "அதிமுக", "எம்எல்ஏ", "எம்.எல்.ஏ", "தேர்தல்", "ஆட்சியர்", "கட்சி", "ஆர்ப்பாட்ட", "பாஜக", "காங்கிரஸ்"],
    "poultry_agri": ["முட்டை", "கோழி", "விவசாய", "விலை", "கொள்முதல்", "மஞ்சள்", "பண்ணை", "தேங்காய்", "யானை", "காட்டு"],
    "education": ["மாணவ", "பள்ளி", "கல்லூரி", "தேர்வு", "ஆசிரிய", "பல்கலை"],
    # people's own daily problems (the reels people share: water stolen, a hospital leak, garbage trucks waiting for hours)
    "civic": ["குடிநீர்", "சாலை", "பேருந்து", "நகராட்சி", "பஞ்சாயத்து", "குப்பை", "மாநகராட்சி", "கழிவுநீர்", "தெருவிளக்கு", "குழாய்", "கசிவு",
              "ரேஷன்", "பத்திரப்பதிவு", "மருத்துவமனை", "ஆக்கிரமிப்பு", "நெரிசல்", "அதிருப்தி", "அவதி", "காத்திருப்பு", "அபராதம்", "விதிமீறல்",
              "பொதுமக்கள்", "பாதாள", "கள்ளத்தனம", "இடையூறு", "சிரம"],
    # plans and projects (a rail line, a flyover design, a new park) - a topic of its own: they reach far fewer people than the problems
    "infra": ["மேம்பால", "சுரங்க", "ரயில்", "திட்டம்", "வடிவமைப்", "அடிக்கல்", "திறப்பு", "விரிவாக்க", "புதிய"],
    "sports_culture": ["போட்டி", "கபடி", "விளையாட்டு", "கலை", "சினிமா", "விருது", "கண்காட்சி"],
    # owner 24 Nov (engine): opinion / explainer / awareness pieces were 'other' with the news - they are their own topic now, so
    # the engine learns how they do (today's 5 PM round picked 'மிஸ்டர் ஏஐ.. நீங்க நல்லவரா, கெட்டவரா..?')
    "feature": ["..?", "?", "விழிப்புணர்வு", "கருத்தரங்", "பயிற்சி", "கவிதை", "இலக்கண", "ஆண்டு விழா", "கடிதம்", "அதிசய", "காலம்", "பூங்கா"],
}


# owner 28 Oct: power cuts and jobs were filed under civic / education_jobs (both -0.5) although they are our most watched news
# ('நாளை 9 பகுதிகளில் மின் தடை' 17,328 views, 'தனியார் வேலைவாய்ப்பு முகாம்' 17,209; page median 374). They are their own topics and
# win over any other topic word in the headline ('சாலை' in a power-cut notice is still a power cut).
FIRST = {
    "power_cut": ["மின்தடை", "மின் தடை", "மின் நிறுத்த", "மின்விநியோகம் நிறுத்த", "power cut", "power shutdown"],
    "jobs": ["வேலைவாய்ப்பு", "வேலை வாய்ப்பு", "காலிப்பணி", "பணியிடங்கள்", "ஆட்சேர்ப்பு", "job fair", "recruitment", "vacanc"],
}
# starting weight until insights has measured MIN_PER_TOPIC posts of the topic (then the measured weight is used)
PRIOR = {"power_cut": 1.5, "crime": 1.2, "accident": 1.0, "civic": 0.8}      # owner 29 Oct (Coimbatore order); measured insights replace these later


def topic(text):
    t = text or ""
    low = t.lower()
    for k, words in FIRST.items():
        if any(w.lower() in low for w in words):
            return k
    best, n = "other", 0
    for k, words in TOPICS.items():
        c = sum(1 for w in words if w in t)
        if c > n:
            best, n = k, c
    return best


def load():
    try:
        return json.loads((HERE / "learned.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def boost(text):
    """score adjustment for a candidate headline from its topic's measured performance (weights are already clamped by insights.py)"""
    t = topic(text)
    w = (load().get("topic_weight") or {}).get(t)
    return float(w) if w is not None else PRIOR.get(t, 0.0)


# owner 14 Nov: each round's news is chosen by THIS page's insights. A topic's own weight is trusted once this page has at least
# TRUST_N measured reels of it; until then the pattern proven on Coimbatore 360 (272 reels) + Namakkal 360 is used
# (power cut > accident / rain > crime > jobs; politics and temple news lowest). Switches over by itself as views build up.
TRUST_N = 5
PATTERN = {"power_cut": 1.5, "accident": 0.9, "weather": 0.8, "crime": 0.7, "jobs": 0.6, "civic": 0.0, "education": -0.1,
           "temple": -0.1, "sports_culture": -0.2, "poultry_agri": -0.3, "politics": -0.5, "other": 0.0}


def reach_weight(text, data=None):
    """(weight, topic, 'page' | 'pattern') - how well news of this headline's topic reaches people on this page"""
    t = topic(text)
    d = load() if data is None else data
    n = (d.get("topic_n") or {}).get(t, 0)
    w = (d.get("topic_weight") or {}).get(t)
    if w is not None and n >= TRUST_N:
        return float(w), t, "page"
    return PATTERN.get(t, 0.0), t, "pattern"


def hints():
    """short style guidance for the writer prompt; '' until enough posts have been measured"""
    d = load()
    out = []
    if d.get("avg_watch_s"):
        out.append(f"Viewers leave after about {d['avg_watch_s']} seconds on average: the FIRST sentence of reel_script must carry the most surprising fact (a number, place or consequence), never a greeting or background.")
    if d.get("top_openings"):
        out.append("Openings of our best-performing reels (style reference only, never copy facts): " + " | ".join(d["top_openings"][:4]))
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------------------------------------------
# owner 24 Nov ("it should be an Instagram monster ... post the reels our users loved to see - watch, hours, news, topics, everything;
# it's an engine", "separate insights for each district"): every page learns from ITS OWN reels each night (poster/insights.py) what
# its viewers watch - and the pick orders each round by that. Learned, not fixed: topic, area, headline words (the odd twist people
# share: 'எச்சில் துப்பியதால் தகராறு' 26x, 'கள்ளத்தனமாக குடிநீர்' 18x), posting hour.
#   love of a reel = 0.7 * log(views / median views of reels posted that day) + 0.3 * log(watch time / page median watch time)
#   (a day's own median: a good or bad Instagram day is not credited to the news; only reels older than 3 days = final numbers)
#   effects fitted one after another on what is left (topic -> area -> words), each shrunk towards 0 by its number of reels
#   (n / (n + K)): one lucky reel never moves the order much. Power cuts stay first (pick.reach_rank); nothing is ever dropped.
import math, re as _re, statistics as _st

ENGINE_K = {"topic": 4, "area": 6, "tier": 6, "word": 10}
ENGINE_MIN = {"topic": 3, "area": 4, "tier": 5, "word": 8}      # words: only with 8+ reels (fewer = noise)
ENGINE_MIN_REELS = 30      # fewer final reels: the engine is not used (the topic pattern above stays)
_STOP = {"கோவை", "கோவையில்", "கோயம்புத்தூர்", "நாளை", "இன்று", "நேற்று", "மற்றும்", "உள்ளிட்ட", "பகுதிகளில்", "பகுதியில்", "அருகே",
         "மாவட்டத்தில்", "மாவட்ட", "சென்னை", "சென்னையில்", "சேலம்", "சேலத்தில்", "மணி", "வரை", "முதல்", "அன்று", "இருந்து", "செய்து"}


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def head_words(text):
    """the headline's own words as short stems ('திருடப்பட்ட' / 'திருட்டு' -> 'திருட'), once each; place names and filler left out"""
    try:
        import allnews
        places = {p for p in allnews.places_in(text or "")}
    except Exception:
        places = set()
    out = []
    for w in _re.findall(r"[஀-௿]+", (text or "").split("\n")[0]):
        if len(w) < 3 or w in _STOP or any(p and (w.startswith(p[:4]) and len(p) >= 4) for p in places):
            continue
        s = w[:5]
        if s not in out:
            out.append(s)
    return out


def area_of(text):
    """(places, tier): the headline's district places and 'city' (a city area) / 'town' (another place) / 'none'"""
    try:
        import allnews
        head = (text or "").split("\n")[0]
        ps = sorted(allnews.places_in(head))
        tier = "city" if any(w in head for w in allnews.CITY_AREAS) else ("town" if ps else "none")
        return ps, tier
    except Exception:
        return [], "none"


def _fit(rows, key, kind, resid):
    """shrunk mean of what is left (resid) per value of key(row) -> {value: [effect, n]}"""
    by = {}
    for i, r in enumerate(rows):
        for v in key(r):
            by.setdefault(v, []).append(resid[i])
    k, mn = ENGINE_K[kind], ENGINE_MIN[kind]
    return {v: [round(sum(x) / (len(x) + k), 3), len(x)] for v, x in by.items() if len(x) >= mn}


def learn(rows, tz=None):
    """rows = final insights rows of ONE page (caption, t, views, ig_reels_avg_watch_time) -> the engine block of learned.json"""
    import datetime
    tz = tz or datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    rows = [r for r in rows if (r.get("views") or 0) > 0]
    if len(rows) < ENGINE_MIN_REELS:
        return {"reels": len(rows), "ready": False}
    day = {}
    for r in rows:
        r["_d"] = datetime.datetime.fromisoformat(str(r["t"]).replace("+0000", "+00:00")).astimezone(tz)
        day.setdefault(r["_d"].date(), []).append(r["views"])
    dmed = {d: _st.median(v) for d, v in day.items()}
    watch = [r.get("ig_reels_avg_watch_time") or 0 for r in rows if r.get("ig_reels_avg_watch_time")]
    wmed = _st.median(watch) if watch else 0
    love = []
    for r in rows:
        lv = _clamp(math.log(r["views"] / max(dmed[r["_d"].date()], 1)), -2.5, 2.5)
        if wmed and r.get("ig_reels_avg_watch_time"):
            lv = 0.7 * lv + 0.3 * _clamp(math.log(r["ig_reels_avg_watch_time"] / wmed), -2.5, 2.5)
        love.append(lv)
    heads = [(r.get("caption") or "").split("\n")[0] for r in rows]
    resid = list(love)
    eng = {}
    for kind, key in (("topic", lambda i: [topic(heads[i])]),
                      ("area", lambda i: area_of(heads[i])[0][:1]),
                      ("tier", lambda i: [area_of(heads[i])[1]]),
                      ("word", lambda i: head_words(heads[i]))):
        idx = list(range(len(rows)))
        eff = _fit(idx, key, kind, resid)
        eng[kind] = eff
        for i in idx:      # what this kind explains is taken out before the next kind is fitted
            vals = [eff[v][0] for v in key(i) if v in eff]
            if vals:
                resid[i] -= (sum(vals) / len(vals)) if kind == "word" else vals[0]
    hours = {}
    for r, lv in zip(rows, love):
        hours.setdefault(r["_d"].hour, []).append(lv)
    eng["hour"] = {str(h): [round(sum(v) / (len(v) + 4), 3), len(v)] for h, v in sorted(hours.items()) if len(v) >= 3}
    eng.update({"reels": len(rows), "ready": True, "median_views": round(_st.median([r["views"] for r in rows])),
                "median_watch_s": round(wmed / 1000, 1) if wmed else None})
    return eng


def engine_score(text, data=None):
    """(predicted love, why) of a news headline from THIS page's learned engine; (None, why) when the engine is not ready"""
    d = load() if data is None else data
    e = d.get("engine") or {}
    if not e.get("ready"):
        return None, "engine not ready"
    head = (text or "").split("\n")[0]
    t = topic(head)
    ps, tier = area_of(head)
    parts, s = [], 0.0
    if t in e.get("topic", {}):
        s += e["topic"][t][0]; parts.append(f"{t} {e['topic'][t][0]:+.2f}")
    a = next((p for p in ps if p in e.get("area", {})), None)
    if a:
        s += e["area"][a][0]; parts.append(f"{a} {e['area'][a][0]:+.2f}")
    elif tier in e.get("tier", {}):
        s += e["tier"][tier][0]; parts.append(f"{tier} {e['tier'][tier][0]:+.2f}")
    ws = sorted((e["word"][w][0], w) for w in head_words(head) if w in e.get("word", {}))
    if ws:
        top = sorted(ws, key=lambda x: -abs(x[0]))[:3]
        v = sum(x[0] for x in top) / len(top)
        s += 0.5 * v; parts.append("words " + ",".join(f"{w}{x:+.2f}" for x, w in top))      # half weight: the weakest of the signals
    return round(_clamp(s, -1.5, 1.5), 3), "; ".join(parts) or "nothing learned for this headline"


SENSITIVE = _re.compile(r"போக்சோ|பாலியல்|சீண்ட|தற்கொலை|தூக்கிட்|உயிரிழ|பலி|சடலம்|கொலை|சிறுமி|சிறுவன்|குழந்தை")


def best_openings(rows, n=4):
    """first lines of the most-watched final reels (views / that day's median, > 1.5x), sensitive stories left out"""
    import datetime
    tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    day = {}
    for r in rows:
        if (r.get("views") or 0) > 0:
            d = datetime.datetime.fromisoformat(str(r["t"]).replace("+0000", "+00:00")).astimezone(tz).date()
            day.setdefault(d, []).append(r)
    scored = []
    for d, rs in day.items():
        med = _st.median([x["views"] for x in rs]) or 1
        scored += [(x["views"] / med, (x.get("caption") or "").split("\n")[0][:80]) for x in rs]
    out = []
    for ratio, head in sorted(scored, key=lambda x: -x[0]):
        if ratio < 1.5 or SENSITIVE.search(head) or topic(head) == "power_cut" or head in out:
            continue
        out.append(head)
        if len(out) >= n:
            break
    return out
