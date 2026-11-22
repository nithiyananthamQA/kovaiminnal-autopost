"""owner 22 Nov (a viewer's comment): never 'நாளை' alone - people watch the reel later, so the date goes with it.

  voice (reel_script):        நாளை காலை 9 மணி   ->  நாளை, நவம்பர் 23ஆம் தேதி, காலை 9 மணி
  caption / headline:         நாளை மின்தடை       ->  நாளை (நவம்பர் 23) மின்தடை
  short screen text (hl1/2):  நாளை (நவ.23), or only நவ.23 when the line has no room

'நாளை மறுநாள்' / 'நாளை மறுதினம்' get the day after tomorrow. A நாளை that already has a date next to it is left alone.
The date is counted from the day the story is written (the writer's rule: இன்று / நாளை as from TODAY), and a story whose
நாளை has come is never posted (poster/freshness.tomorrow_is_late)."""
import datetime
import re

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
MONTHS = ["ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்", "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"]
SHORT = ["ஜன.", "பிப்.", "மார்ச்", "ஏப்.", "மே", "ஜூன்", "ஜூலை", "ஆக.", "செப்.", "அக்.", "நவ.", "டிச."]
_MONTH_WORDS = "|".join(re.escape(m) for m in MONTHS + SHORT)
# நாளை as its own word (not நாளைய / நாளைக்கு / நாளையும்), optionally followed by மறுநாள் / மறுதினம்
DAY = re.compile(r"(?<![஀-௿])நாளை(\s*(?:மறுநாள்|மறுதினம்))?(?![஀-௿])")
HAS_DATE = re.compile(r"\d{1,2}\s*(?:ஆம்|ம்)?\s*தேதி|\d{1,2}[./-]\d{1,2}|" + _MONTH_WORDS)      # a clock time (9 மணி) is not a date


def _dated(text, m):
    """a date already sits right after (or just before) this நாளை"""
    after = text[m.end():m.end() + 22]
    before = text[max(0, m.start() - 14):m.start()]
    return bool(HAS_DATE.search(after) or HAS_DATE.search(before))


def _sub(text, make):
    out, pos = [], 0
    for m in DAY.finditer(text):
        out.append(text[pos:m.end()])
        if not _dated(text, m):
            out.append(make(m))
        pos = m.end()
    out.append(text[pos:])
    return "".join(out)


def spoken(text, today):
    def make(m):
        d = today + datetime.timedelta(days=2 if m.group(1) else 1)
        return f", {MONTHS[d.month - 1]} {d.day}ஆம் தேதி,"
    s = _sub(text, make)
    return re.sub(r",\s*([.?!,])", r"\1", s)        # no comma right before a full stop


def written(text, today, short=False):
    def make(m):
        d = today + datetime.timedelta(days=2 if m.group(1) else 1)
        return f" ({SHORT[d.month - 1]}{d.day})" if short else f" ({MONTHS[d.month - 1]} {d.day})"
    return _sub(text, make)


def screen(text, today, limit):
    """on-screen line with a length limit: 'நாளை (நவ.23)' when it fits, else the date in place of நாளை, else as it was"""
    t = written(text, today, short=True)
    if len(t) <= limit:
        return t
    def only_date(m):
        if _dated(text, m):
            return m.group(0)
        d = today + datetime.timedelta(days=2 if m.group(1) else 1)
        return f"{SHORT[d.month - 1]}{d.day}"
    t = DAY.sub(only_date, text)
    return t if len(t) <= limit else text


def add_dates(d, today=None):
    """the finished draft (writer JSON): every நாளை gets its date - voice, headline, screen lines and caption"""
    if not isinstance(d, dict):
        return d
    today = today or datetime.datetime.now(IST).date()
    if d.get("reel_script"):
        d["reel_script"] = spoken(str(d["reel_script"]), today)
    for k in ("tamil_headline", "caption"):
        if d.get(k):
            d[k] = written(str(d[k]), today)
    sp = d.get("slides_spec")
    if isinstance(sp, dict):
        if sp.get("hl1"):
            sp["hl1"] = screen(str(sp["hl1"]), today, 40)
        if sp.get("hl2"):
            sp["hl2"] = screen(str(sp["hl2"]), today, 28)
        for x in sp.get("slides") or []:
            if isinstance(x, dict):
                if x.get("title"):
                    x["title"] = screen(str(x["title"]), today, 18)
                x["lines"] = [screen(str(l), today, 60) for l in (x.get("lines") or [])]
    return d
