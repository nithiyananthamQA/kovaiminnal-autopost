"""What Instagram insights taught us (written by poster/insights.py into learned.json). Used ONLY to order candidate stories and to give the
writer style hints. It never relaxes a fact / quality check."""
import json, pathlib

HERE = pathlib.Path(__file__).parent
TOPICS = {
    "weather": ["மழை", "வெயில்", "வானிலை", "எச்சரிக்கை", "புயல்", "வெள்ளம்"],
    "crime": ["கொலை", "கைது", "திருட", "போலீஸ்", "குற்ற", "மோசடி", "தற்கொலை", "கொள்ளை"],
    "accident": ["விபத்து", "பலி", "உயிரிழ", "தீ விபத்து", "மோதி"],
    "temple": ["கோயில்", "கோவில்", "திருவிழா", "தேரோட்ட", "தேர்த்திருவிழா", "சாமி", "பூஜை", "குடமுழுக்கு"],      # not "தேர்": it is inside தேர்வு / தேர்தல்
    "politics": ["முதல்வர்", "அமைச்சர்", "திமுக", "அதிமுக", "எம்எல்ஏ", "எம்.எல்.ஏ", "தேர்தல்", "ஆட்சியர்", "கட்சி"],
    "poultry_agri": ["முட்டை", "கோழி", "விவசாய", "விலை", "கொள்முதல்", "மஞ்சள்", "பண்ணை", "லாரி"],
    "education": ["மாணவ", "பள்ளி", "கல்லூரி", "தேர்வு"],
    "civic": ["குடிநீர்", "சாலை", "பேருந்து", "நகராட்சி", "பஞ்சாயத்து", "குப்பை"],
    "sports_culture": ["போட்டி", "கபடி", "விளையாட்டு", "கலை", "சினிமா", "விருது"],
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


def reference(data=None):
    """the reference page's insights summed per news type (reference_sync.py, refreshed every night); {} when not there"""
    if data is not None:
        return data
    try:
        return json.loads((HERE / "reference_reach.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def reach_weight(text, data=None, ref=None):
    """(weight, topic, 'page' | 'page+reference' | 'reference' | 'pattern') - how well news of this headline's topic reaches people.
    owner 16 Nov ("give importance to his better concepts"): this page's measured weight and the reference page's are blended by how
    many reels each measured; a topic only one of them measured uses that one; neither = the proven pattern."""
    t = topic(text)
    d = load() if data is None else data
    r = reference() if ref is None else ref
    n = (d.get("topic_n") or {}).get(t, 0)
    w = (d.get("topic_weight") or {}).get(t)
    rn = (r.get("topic_n") or {}).get(t, 0)
    rw = (r.get("topic_weight") or {}).get(t)
    own = w is not None and n >= TRUST_N
    theirs = rw is not None and rn >= TRUST_N
    if own and theirs:
        return round((n * float(w) + rn * float(rw)) / (n + rn), 3), t, "page+reference"
    if own:
        return float(w), t, "page"
    if theirs:
        return float(rw), t, "reference"
    return PATTERN.get(t, 0.0), t, "pattern"


# owner 16 Nov ("based on the reach we omit the contents"): a news type is left out when BOTH pages' reels together show people skip
# it - its median views under SKIP_RATIO of the page's usual (median) views, measured on at least SKIP_MIN_N reels. The core news
# people need is never left out, whatever the numbers say. Recomputed every run from the latest insights (ours + the reference's).
SKIP_RATIO, SKIP_MIN_N = 0.55, 10
NEVER_SKIP = {"power_cut", "civic", "crime", "accident", "weather", "other"}


def own_ratios(page="coimbatore", history=None):
    import reference_sync
    if history is None:
        try:
            history = json.loads((HERE.parent / "poster" / "insights" / "history.json").read_text(encoding="utf-8"))
        except Exception:
            history = {}
    return reference_sync.topic_ratios(history, page)[0]


def reach_map(page="coimbatore", own=None, ref=None):
    """{topic: {"ratio": blended, "n": reels, "ours": [n, ratio], "reference": [n, ratio]}} - ratio = topic median / page median"""
    own = own_ratios(page) if own is None else own
    rt = (reference() if ref is None else ref).get("topics") or {}
    out = {}
    for t in set(own) | set(rt):
        a, b = own.get(t) or {"n": 0, "ratio": 0}, rt.get(t) or {"n": 0, "ratio": 0}
        n = a["n"] + b["n"]
        if n:
            out[t] = {"ratio": round((a["n"] * a["ratio"] + b["n"] * b["ratio"]) / n, 3), "n": n,
                      "ours": [a["n"], a["ratio"]], "reference": [b["n"], b["ratio"]]}
    return out


def skip_topics(page="coimbatore", own=None, ref=None):
    m = reach_map(page, own, ref)
    return sorted(t for t, x in m.items() if t not in NEVER_SKIP and x["n"] >= SKIP_MIN_N and x["ratio"] < SKIP_RATIO)


def hints():
    """short style guidance for the writer prompt; '' until enough posts have been measured"""
    d = load()
    out = []
    if d.get("avg_watch_s"):
        out.append(f"Viewers leave after about {d['avg_watch_s']} seconds on average: the FIRST sentence of reel_script must carry the most surprising fact (a number, place or consequence), never a greeting or background.")
    if d.get("top_openings"):
        out.append("Openings of our best-performing reels (style reference only, never copy facts): " + " | ".join(d["top_openings"][:4]))
    return "\n".join(out)
