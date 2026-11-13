"""Kovai Minnal - news reel v5 (OUR video part; everything else - writing, picking, posting, voice, timing, cards - is the
Coimbatore 360 setup unchanged). Usage: python3 reel5.py spec.json out.mp4 [page]   (same spec as reel4.py)

v5 = reel4.py (his v4 design, untouched in its own file) + two changes asked by the owner on 11 Nov:
  1. the brand footer runs edge to edge across the bottom of the reel, double height (reel/assets/footer_wide_coimbatore.png)
  2. a story with no picture (the source had no photo and every picture service failed -> post.plain_background) no longer
     shows the faded logo with camera moves: our own code draws an animated news scene for the story's kind - police lights
     (crime), siren + moving road (accident), a city whose windows go dark (power cut), rain (weather), flames (fire),
     else a city map - always with the location pin, ripples, slow map drift and light sweeps. Free: drawn frame by frame
     in the same headless browser, no AI service, nothing photo-realistic (never looks like real footage of the event).
"""
import json
import math
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel as R          # noqa: E402
import reel4 as V4        # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
FOOTER_WIDE = ASSETS / "footer_wide_coimbatore.png"
HEADER_SUFFIX = ""      # owner 11 Nov (later): no "செய்திகள்" in the header - only the page name

# owner 11 Nov: the district power-cut pages (districts/districts.json) - same look, each page its own name, logo and footer
DISTRICTS_FILE = Path(__file__).resolve().parent.parent / "districts" / "districts.json"


def district_pages():
    try:
        ds = json.loads(DISTRICTS_FILE.read_text(encoding="utf-8"))["districts"]
    except Exception:
        return {}
    base = DISTRICTS_FILE.parent
    out = {}
    for k, d in ds.items():
        foot = str((base / k / "footer.png").resolve())
        out[k] = {"logo": str((base / k / "logo.png").resolve()), "name": d["name_ta"], "handle": d["handle"], "tagline": d["name_ta"],
                  "follow": d["end_card"], "ticker": d["name_ta"], "footer": foot, "footer_wide": foot,
                  "hashtag": "#" + d["name_en"].replace(" ", ""), "end_card": d["end_card"], "name_en": d["name_en"], "district": True,
                  "share_spoken": SHARE.get("share_spoken", ""), "share_card": SHARE.get("share_card", ""), "follow_spoken": d.get("follow_spoken", ""),
                  "city": d["ta"], "page_ta": d["name_ta"]}
    return out


try:
    SHARE = {k: v for k, v in json.loads(DISTRICTS_FILE.read_text(encoding="utf-8")).items() if k.startswith(("share_", "follow_news"))}
except Exception:
    SHARE = {}
# owner 14 Nov: the "முழு விவரம்" card (இடம் / யார் / எப்போது) must not sit on top of the yellow headline strip - while the card
# is on screen the strip is hidden (district pages)
NO_CLASH_JS = """<script>(function(){const _r=window.renderAt;window.renderAt=function(t){_r(t);
const sm=document.getElementById('sum'),m=document.getElementById('mini');
if(sm&&m&&parseFloat(sm.style.opacity||'0')>0)m.style.opacity=0;};})();</script>"""
MAX_SPOKEN = 6      # owner 13 Nov: a power-cut reel is 30-40 s; the caption carries the full area list
_TIME = __import__("re").compile(r"(காலை|மதியம்|பிற்பகல்|மாலை|இரவு)\s*(\d{1,2}(?:[.:]\d{2})?)\s*மணி\s*(?:முதல்|தொடங்கி)\s*"
                                 r"(காலை|மதியம்|பிற்பகல்|மாலை|இரவு)?\s*(\d{1,2}(?:[.:]\d{2})?)\s*மணி\s*வரை")


def _norm(t):
    return "".join(ch for ch in str(t or "") if ch.isalnum())


def district_spec(spec, page):
    """owner 13 Nov (Chennai test reel): follow said ONCE (the writer's last sentence was spoken again as the closing line),
    a share line for the people of that area, the full cut time on the yellow band, the real date instead of 'நாளை மறுதினம்',
    'மின்தடை' as one word, and at most MAX_SPOKEN spoken sentences"""
    import re
    if spec.get("district_done"):      # already applied (a re-render of the same reel.json)
        return spec
    if "மின்" not in str(spec.get("cat") or "") or "தடை" not in str(spec.get("cat") or ""):
        return news_spec(spec, page)
    spec = json.loads(json.dumps(spec, ensure_ascii=False))
    sents = list(spec.get("sentences") or [])
    follow = page.get("follow_spoken") or (spec.get("outro") or {}).get("say") or ""
    while sents and (_norm(sents[-1].get("say")) == _norm(follow) or "ஃபாலோ" in sents[-1].get("say", "") or "Follow" in sents[-1].get("say", "")):
        sents.pop()
    if len(sents) > MAX_SPOKEN:
        print(f"district reel: {len(sents)} sentences -> {MAX_SPOKEN} spoken (the caption has the full list)")
        sents = sents[:MAX_SPOKEN]
    spec["sentences"] = sents
    place = str(spec.get("location") or "").strip()
    share = page.get("share_spoken", "").format(place=place) if place and page.get("share_spoken") else ""
    spec["outro"] = dict(spec.get("outro") or {}, say=(share + " " + follow).strip())
    fix = lambda t: re.sub(r"மின்\s+தடை", "மின்தடை", str(t or ""))
    hook = [fix(h) for h in (spec.get("hook") or ["", ""])]
    whole = " ".join(str(x.get(k) or "") for x in sents for k in ("say", "fact"))
    m = _TIME.search(whole)
    if m and len(hook) > 1:
        a, h1, b, h2 = m.group(1), m.group(2), m.group(3) or m.group(1), m.group(4)
        day = hook[1].split(":")[0].strip() if ":" in hook[1] else ""
        day = re.sub(r"நவம்பர்", "நவ.", day)
        hook[1] = (f"{day} • " if day else "") + f"{a} {h1} – {b} {h2}"
    spec["hook"] = hook
    if spec.get("mini"):
        spec["mini"] = fix(re.sub(r"(நாளை\s*மறுதினம்|நாளை|இன்று)\s*\(([^)]*)\)", r"\2", spec["mini"]))
    spec["share_card"] = page.get("share_card", "").format(place=place) if place and page.get("share_card") else ""
    spec["district_done"] = True
    return spec


def news_spec(spec, page):
    """owner 13-14 Nov: a district page's NON-power-cut news ends with ONE common closing line - the NEWS follow line only
    (never the power-cut one). Power-cut reels keep their own closing (district_spec)."""
    spec = json.loads(json.dumps(spec, ensure_ascii=False))
    follow = SHARE.get("follow_news_spoken", "").format(city=page.get("city", ""), page=page.get("page_ta", page.get("name", "")))
    sents = list(spec.get("sentences") or [])
    while sents and ("ஃபாலோ" in sents[-1].get("say", "") or "Follow" in sents[-1].get("say", "")):
        sents.pop()
    spec["sentences"] = sents
    # owner 14 Nov: every non-power-cut news has the SAME closing - only "follow to get the news at once" (no send-to-friends line)
    spec["outro"] = dict(spec.get("outro") or {}, say=follow)
    spec["share_card"] = SHARE.get("follow_news_card", "").format(city=page.get("city", ""))
    spec["district_done"] = True
    return spec


for _k, _p in district_pages().items():
    R.PAGES.setdefault(_k, _p)

FOOT_CSS = """
#foot{left:0!important;right:0;bottom:0!important;width:1080px!important;height:200px!important;opacity:1!important;object-fit:fill}
"""

SCENE_CSS = """
#scene{position:absolute;inset:0;z-index:4;overflow:hidden;background:radial-gradient(ellipse at 50% 55%,#13306E 0%,#0B1B4D 45%,#050C24 100%)}
#scene .tint{position:absolute;inset:0;background:radial-gradient(circle at 50% 54%,var(--sc) 0%,rgba(0,0,0,0) 55%);opacity:.22}
#scene #map{position:absolute;left:-460px;top:-340px;width:2000px;height:2600px;transform-origin:50% 50%}
#scene .glow{position:absolute;border-radius:50%;filter:blur(40px);opacity:0}
#scene .beam{position:absolute;left:-200px;width:1500px;height:160px;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.10),rgba(255,255,255,0));transform:rotate(-24deg)}
#scene #halo{position:absolute;left:540px;top:1030px;width:520px;height:520px;margin:-260px 0 0 -260px;border-radius:50%;
  background:radial-gradient(circle,var(--sc) 0%,rgba(0,0,0,0) 68%);opacity:.35}
#scene #disc{position:absolute;left:540px;top:1030px;width:300px;height:300px;margin:-150px 0 0 -150px;border-radius:50%;
  background:radial-gradient(circle at 50% 38%,#1C3F8F,#0A1A47);border:8px solid var(--sc);box-shadow:0 0 60px var(--sc),inset 0 0 40px rgba(0,0,0,.5);
  display:flex;align-items:center;justify-content:center;color:#fff}
#scene #disc .ic{width:150px;height:150px;filter:drop-shadow(0 6px 18px rgba(0,0,0,.6))}
#scene .ring{position:absolute;left:540px;top:1030px;border-radius:50%;border:6px solid var(--sc);opacity:0}
#scene .drop{position:absolute;top:0;width:4px;height:70px;border-radius:2px;background:linear-gradient(180deg,rgba(170,210,255,0),rgba(170,210,255,.75))}
#scene .bld{position:absolute;bottom:330px;background:#0A1430;border-top:4px solid #1E2E5E}
#scene .win{position:absolute;width:18px;height:22px;background:#FFD86B;box-shadow:0 0 10px rgba(255,216,107,.8)}
#scene #road{position:absolute;left:0;right:0;top:1560px;height:150px;background:#1A2240;border-top:6px solid #39466F;border-bottom:6px solid #39466F;overflow:hidden}
#scene #road .dash{position:absolute;top:66px;width:110px;height:14px;background:#FFD233;border-radius:4px}
#scene .flame{position:absolute;bottom:330px;border-radius:50% 50% 40% 40%;background:radial-gradient(circle at 50% 75%,#FFE08A,#FF8A00 45%,rgba(227,21,27,.0) 75%);filter:blur(6px)}
"""

KINDS = [  # (match in the category / headline, kind, icon, accent colour)
    (("விபத்து", "மோதி", "மோதல்", "கவிழ்ந்", "accident"), "accident", "car-burst", "#E3151B"),
    (("மின் தடை", "மின்தடை", "மின்வெட்டு", "power"), "power", "plug-circle-xmark", "#F5B400"),
    (("தீ விபத்து", "தீப்பிடி", "எரிந்", "fire"), "fire", "fire", "#FF6A00"),
    (("மழை", "வானிலை", "வெள்ள", "புயல்", "rain", "weather"), "rain", "cloud-showers-heavy", "#3FA9F5"),
    (("குற்ற", "கைது", "கொலை", "திருட்டு", "கத்தி", "போலீஸ்", "போலீசார்", "crime"), "crime", "handcuffs", "#E3151B"),
    (("ரயில்", "train"), "train", "train", "#2BB673"),
    (("கோவில்", "கோயில்", "திருவிழா", "temple"), "temple", "gopuram", "#FF8A00"),
    (("வேலை", "வேலைவாய்ப்பு", "jobs"), "jobs", "briefcase", "#2BB673"),
    (("கல்வி", "பள்ளி", "கல்லூரி", "education"), "education", "graduation-cap", "#3FA9F5"),
]


def kind_of(spec):
    text = " ".join(str(spec.get(k) or "") for k in ("cat", "mini")) + " " + " ".join(spec.get("hook") or [])
    for words, kind, icon, col in KINDS:
        if any(w in text for w in words):
            return kind, icon, col
    return "news", "newspaper", "#FFD233"


def is_plain(spec):
    return all("plain_bg" in Path(str(p)).name for p in (spec.get("images") or ["plain_bg"]))


def map_svg(rng):
    """a made-up city street map (never a real map), drawn once; the JS drifts and zooms it slowly"""
    lines = []
    for _ in range(26):
        x0, y0 = rng.uniform(0, 2000), rng.uniform(0, 2600)
        ang, ln = rng.uniform(0, math.pi), rng.uniform(500, 1800)
        x1, y1 = x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln
        cx, cy = (x0 + x1) / 2 + rng.uniform(-200, 200), (y0 + y1) / 2 + rng.uniform(-200, 200)
        w = rng.choice((5, 5, 8, 14))
        lines.append(f'<path d="M{x0:.0f} {y0:.0f} Q{cx:.0f} {cy:.0f} {x1:.0f} {y1:.0f}" stroke="#5B7FD6" stroke-opacity="{0.16 if w < 10 else 0.26}" '
                     f'stroke-width="{w}" fill="none" stroke-linecap="round"/>')
    blocks = "".join(f'<rect x="{rng.uniform(0, 1950):.0f}" y="{rng.uniform(0, 2550):.0f}" width="{rng.uniform(40, 120):.0f}" height="{rng.uniform(40, 120):.0f}" '
                     f'fill="#5B7FD6" fill-opacity=".06" rx="6"/>' for _ in range(70))
    return f'<svg id="map" viewBox="0 0 2000 2600" xmlns="http://www.w3.org/2000/svg">{blocks}{"".join(lines)}</svg>'


def scene_html(spec):
    kind, icon, col = kind_of(spec)
    rng = random.Random(str(spec.get("story", "")) + kind)
    parts = [f'<div id="scene" style="--sc:{col}"><div class="tint"></div>', map_svg(rng)]
    parts += [f'<div class="beam" id="beam{i}" style="top:{200 + i * 700}px"></div>' for i in range(2)]
    extra = {"kind": kind, "drops": [], "wins": [], "dashes": 0, "flames": 0}
    if kind in ("crime", "accident"):
        parts.append('<div class="glow" id="gR" style="left:-260px;top:-160px;width:900px;height:900px;background:#FF1E2D"></div>')
        parts.append(f'<div class="glow" id="gB" style="right:-260px;top:-160px;width:900px;height:900px;background:{"#1E6BFF" if kind == "crime" else "#FFFFFF"}"></div>')
    if kind == "accident":
        parts.append('<div id="road">' + "".join(f'<div class="dash" id="d{i}"></div>' for i in range(8)) + "</div>")
        extra["dashes"] = 8
    if kind in ("power", "fire", "news", "temple", "jobs", "education", "train"):
        x = -20
        while x < 1100:
            w, h = rng.randint(90, 170), rng.randint(220, 520)
            parts.append(f'<div class="bld" style="left:{x}px;width:{w}px;height:{h}px"></div>')
            for wy in range(30, h - 30, 52):
                for wx in range(16, w - 24, 38):
                    if rng.random() < 0.55:
                        k = len(extra["wins"])
                        parts.append(f'<div class="win" id="win{k}" style="left:{x + wx}px;bottom:{330 + h - wy - 22}px"></div>')
                        extra["wins"].append(round(rng.uniform(0.15, 0.95), 3))
            x += w + rng.randint(6, 26)
    if kind == "fire":
        for i in range(5):
            parts.append(f'<div class="flame" id="fl{i}" style="left:{120 + i * 190}px;width:{rng.randint(120, 200)}px;height:{rng.randint(220, 360)}px"></div>')
        extra["flames"] = 5
    if kind == "rain":
        for i in range(80):
            parts.append(f'<div class="drop" id="r{i}" style="left:{rng.uniform(0, 1080):.0f}px"></div>')
            extra["drops"].append([round(rng.uniform(0, 2000), 1), round(rng.uniform(1300, 1900), 1)])
    parts += ['<div id="halo"></div>'] + [f'<div class="ring" id="ring{i}"></div>' for i in range(3)]
    parts.append(f'<div id="disc">{R.icon(icon)}</div></div>')
    return "".join(parts), extra


SCENE_JS = """
<script>
(function(){
const X=__EXTRA__, sin=Math.sin;
const _render=window.renderAt;
window.renderAt=function(t){
  _render(t);
  const sc=document.getElementById('scene'); if(!sc)return;
  for(let i=0;i<D.n;i++){const e=document.getElementById('p'+i); if(e)e.style.opacity=0;}
  const m=document.getElementById('map');
  m.style.transform='translate('+(-14*t)+'px,'+(-18*t)+'px) scale('+(1.06+0.004*t)+') rotate('+(0.25*t)+'deg)';
  for(let i=0;i<2;i++){const b=document.getElementById('beam'+i); const p=((t*0.22+i*0.5)%1); b.style.transform='translateX('+(-1400+2800*p)+'px) rotate(-24deg)';}
  const pulse=1+0.035*sin(t*3.1);
  document.getElementById('disc').style.transform='scale('+pulse+')';
  document.getElementById('halo').style.transform='scale('+(1+0.08*sin(t*2.2))+')';
  for(let i=0;i<3;i++){const r=document.getElementById('ring'+i), f=((t+i*0.6)%1.8)/1.8, s=300+f*520;
    r.style.width=s+'px'; r.style.height=s+'px'; r.style.margin=(-s/2)+'px 0 0 '+(-s/2)+'px'; r.style.opacity=(1-f)*0.55;}
  if(X.kind==='crime'||X.kind==='accident'){const a=sin(t*9.5), b=sin(t*9.5+Math.PI);
    document.getElementById('gR').style.opacity=Math.max(0,a)*0.55; document.getElementById('gB').style.opacity=Math.max(0,b)*0.45;}
  for(let i=0;i<X.dashes;i++){const d=document.getElementById('d'+i); d.style.left=(((i*160-420*t)%1280)+1280)%1280-140+'px';}
  const nW=X.wins.length;
  for(let i=0;i<nW;i++){const w=document.getElementById('win'+i); if(!w)continue;
    let on=1;
    if(X.kind==='power'){const cut=X.wins[i]*Math.max(6,D.end_t*0.7); on=t<cut?(0.75+0.25*sin(t*23+i)):(t<cut+0.25?(sin(t*60+i)>0?1:0):0);}
    else on=0.55+0.45*Math.max(0,sin(t*0.6+i*1.7));
    w.style.opacity=on;}
  for(let i=0;i<X.flames;i++){const f=document.getElementById('fl'+i); f.style.transform='scaleY('+(0.85+0.2*sin(t*7+i*1.3))+') scaleX('+(0.95+0.08*sin(t*5+i))+')'; f.style.opacity=0.75+0.25*sin(t*11+i);}
  for(let i=0;i<X.drops.length;i++){const d=document.getElementById('r'+i), o=X.drops[i]; d.style.transform='translateY('+(((o[0]+t*o[1])%2100)-120)+'px)';}
  sc.style.filter=t>=D.end_t?'blur('+(18*Math.min(1,(t-D.end_t)/0.3))+'px)':'none';
};
})();
</script>"""


# ---- owner 11 Nov: "our own super cool template" - style K (Kovai Minnal lightning look), so our reels never look like Coimbatore 360's v4.
# Same layout, timing, voice and text as v4; only the look changes. REEL_STYLE=A gives his original look back.
_BOLT_URI = ("data:image/svg+xml;utf8," "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 160'><path d='M62 0 L8 92 L44 92 L30 160 L94 58 L56 58 L78 0 Z' "
             "fill='%23FFD21F' stroke='%23060E2B' stroke-width='6' stroke-linejoin='round'/></svg>")
STYLE_K = """
:root{--acc:#FFD21F;--navy:#0B1B4D;--yellow:#FFD21F;--red:#E3151B}
#shade{background:linear-gradient(180deg,rgba(6,14,43,.88) 0%,rgba(6,14,43,.30) 19%,rgba(6,14,43,0) 34%,rgba(6,14,43,0) 50%,rgba(6,14,43,.45) 64%,rgba(6,14,43,.93) 100%)}
#hdr .nm{color:#FFD21F;font-size:46px;display:flex;align-items:center;text-shadow:0 3px 12px rgba(0,0,0,.8)}
#hdr .nm::before{content:"";flex:none;width:30px;height:48px;margin-right:12px;background:url("__BOLT__") no-repeat center/contain;filter:drop-shadow(0 0 10px rgba(255,210,31,.8))}
#hdr .tag{background:#E3151B}
#plogo{border:5px solid #FFD21F;box-shadow:0 0 0 7px rgba(255,210,31,.28),0 0 34px rgba(255,210,31,.55),0 8px 24px rgba(0,0,0,.5)}
#pin{background:#FFD21F;color:#0B1B4D;box-shadow:0 10px 30px rgba(0,0,0,.45),0 0 0 4px rgba(11,27,77,.6)}
#pin .ic{color:#E3151B}
#hook .h1{-webkit-text-stroke:0;color:#fff;text-shadow:0 7px 0 #0B1B4D,0 14px 34px rgba(0,0,0,.7);font-size:100px}
#hook .h2{background:#FFD21F;color:#0B1B4D;transform:skewX(-7deg);border-radius:8px;box-shadow:12px 12px 0 #E3151B}
#mini{left:0;border-left:0;padding:12px 26px 6px 48px;background:linear-gradient(90deg,rgba(11,27,77,.95),rgba(11,27,77,.55) 85%,rgba(11,27,77,0));
  border-top:5px solid #FFD21F;text-shadow:none;color:#fff}
.card{background:rgba(11,27,77,.93);border:3px solid rgba(255,210,31,.9);border-radius:24px;box-shadow:0 18px 50px rgba(0,0,0,.55),0 0 30px rgba(255,210,31,.18)}
.card .ico{background:#FFD21F;color:#0B1B4D}
.card .lb{color:#FFD21F}
.card .vl{color:#fff}
.ph{-webkit-text-stroke:11px #0B1B4D}
.ph span.on{color:#0B1B4D;background:#FFD21F;border-radius:12px;padding:0 10px;-webkit-text-stroke:0;box-shadow:0 7px 0 #E3151B}
#sum{background:rgba(11,27,77,.96);border:3px solid #FFD21F;box-shadow:0 20px 60px rgba(0,0,0,.6),0 0 40px rgba(255,210,31,.2)}
#sum .st{background:#FFD21F;color:#0B1B4D}
#sum .row{border-top:2px solid rgba(255,255,255,.12)}
#sum .row .ic{color:#FFD21F}
#sum .row .l{color:#AFC0E8}
#sum .row .v{color:#fff}
#end{background:radial-gradient(circle at 50% 38%,rgba(19,48,110,.88),rgba(5,12,36,.96))}
#end img{border-color:#FFD21F;box-shadow:0 0 0 10px rgba(255,210,31,.25),0 0 60px rgba(255,210,31,.5)}
#end .e2{background:#FFD21F;color:#0B1B4D}
#zap{position:absolute;inset:0;z-index:45;pointer-events:none;opacity:0;background:radial-gradient(circle at 50% 40%,rgba(255,255,240,.95),rgba(255,236,150,.55) 35%,rgba(255,210,31,0) 70%)}
#zapbolt{position:absolute;z-index:46;top:-120px;width:420px;height:1500px;opacity:0;pointer-events:none;
  background:url("__BOLT__") no-repeat center/contain;filter:drop-shadow(0 0 30px #FFD21F) drop-shadow(0 0 60px #fff)}
""".replace("__BOLT__", _BOLT_URI)
V4.STYLES["K"] = STYLE_K

# ---- owner 11 Nov: "a 100% better template" - two NEW LAYOUTS (not only colours): D = News Desk, B = Broadcast.
STYLE_D = STYLE_K + """
body{background:radial-gradient(ellipse at 50% 30%,#13306E 0%,#071433 55%,#030919 100%)}
#shade{display:none}
#stage{left:34px;right:34px;top:206px;bottom:auto;width:auto;height:1010px;border-radius:42px;overflow:hidden;border:7px solid #FFD21F;
  box-shadow:0 0 0 7px rgba(255,210,31,.16),0 0 60px rgba(255,210,31,.25),0 30px 80px rgba(0,0,0,.6)}
#stage .pic{width:100%;height:100%}
#stage::after{content:"";position:absolute;inset:0;z-index:3;background:linear-gradient(180deg,rgba(6,14,43,.35) 0%,rgba(6,14,43,0) 22%,rgba(6,14,43,0) 48%,rgba(6,14,43,.88) 100%)}
#hdr{top:62px}
#plogo{top:46px;width:124px;height:124px}
#pin{top:236px;left:66px}
#hook{top:auto;bottom:752px;left:66px;right:66px}
#hook .h1{font-size:88px}
#mini{top:1232px;left:34px;right:34px;background:#FFD21F;color:#0B1B4D;border:0;padding:16px 28px 8px;border-radius:20px;font-size:44px;text-shadow:none;
  box-shadow:0 12px 30px rgba(0,0,0,.45)}
.card{top:auto;bottom:760px;left:66px;width:880px}
#cap{top:1290px;height:300px;left:52px;right:140px}
.ph{-webkit-text-stroke:0;text-shadow:0 4px 18px rgba(0,0,0,.6)}
#sum{top:206px;left:34px;right:34px}
"""
STYLE_B = STYLE_K + """
#hdr{left:0;right:0;top:118px;padding:16px 180px 12px 40px;background:linear-gradient(90deg,#0B1B4D 0%,#13306E 70%,rgba(19,48,110,.0) 100%);
  border-bottom:6px solid #FFD21F;box-shadow:0 10px 30px rgba(0,0,0,.45)}
#plogo{top:96px;right:28px;width:140px;height:140px}
#pin{top:300px;left:40px;background:#E3151B;color:#fff}
#pin .ic{color:#FFD21F}
#hook{top:560px;left:40px;right:40px}
#hook .h1{font-size:96px;text-shadow:0 6px 0 #E3151B,0 14px 34px rgba(0,0,0,.7)}
#mini{left:-60px;right:-60px;top:1040px;transform:skewY(-5deg);background:#FFD21F;color:#0B1B4D;border:0;padding:30px 100px 22px;font-size:50px;
  text-shadow:none;box-shadow:0 22px 50px rgba(0,0,0,.55)}
.card{left:auto;right:40px;top:640px;width:780px}
#cap{top:1236px;height:330px;left:40px;right:140px}
.ph{text-align:center;-webkit-text-stroke:0;color:#0B1B4D;background:rgba(255,255,255,.97);border-radius:22px;padding:16px 28px 8px;
  text-shadow:none;box-shadow:0 14px 34px rgba(0,0,0,.5);font-size:62px}
.ph span.on{color:#0B1B4D;background:#FFD21F;box-shadow:0 6px 0 #E3151B}
"""
V4.STYLES["D"] = STYLE_D
V4.STYLES["B2"] = STYLE_B

ZAP_JS = """
<script>
(function(){
const _r=window.renderAt;
window.renderAt=function(t){
  _r(t);
  const z=document.getElementById('zap'), b=document.getElementById('zapbolt'); if(!z)return;
  // lightning at the start and at every camera cut (not during the end card)
  const hits=[0].concat(D.shots.slice(1).map(s=>s.a)).filter(x=>x<D.end_t);
  let k=99; hits.forEach(h=>{const d=t-h; if(d>=0&&d<k)k=d;});
  const L=k<0.22?(1-k/0.22):0, first=(k===t&&t<0.5);
  z.style.opacity=(first?0.95:0.55)*L*(0.7+0.3*Math.sin(k*90));
  b.style.opacity=L>0?Math.min(1,L*1.6):0;
  b.style.left=(first?330:(120+((hits.indexOf(t-k)*277)%600)))+'px';
  b.style.transform='translateY('+(-200*(1-L))+'px) rotate(10deg)';
};
})();
</script>"""

_orig_build = V4.build_html


def build_html(spec, shots, sents, caps, hook_end, end_t, total, page):
    if not os.environ.get("REEL_STYLE") and not spec.get("style"):
        spec = dict(spec, style="B2")      # owner 11 Nov: B2 (Broadcast) is our look
    html = _orig_build(spec, shots, sents, caps, hook_end, end_t, total, page)
    if (os.environ.get("REEL_STYLE") or spec.get("style")) in ("K", "D", "B2"):
        html = html.replace('<div id="flash"></div>', '<div id="flash"></div><div id="zap"></div><div id="zapbolt"></div>', 1)
        html = html.replace("</body></html>", ZAP_JS + "</body></html>", 1)
    # owner 11 Nov: the header at the top says "கோவை மின்னல் செய்திகள்" (Kovai Minnal News), not only the page name
    name = page["name"]
    if HEADER_SUFFIX:
        html = html.replace(f'<div class="nm">{name}</div>', f'<div class="nm">{name} {HEADER_SUFFIX}</div>', 1)
    # owner 11 Nov: the end card shows the news SOURCE - "Source:", not "ஆதாரம்:" (that word reads as "evidence")
    html = html.replace('<div class="e5">ஆதாரம்: ', '<div class="e5">📰 Source: ', 1)
    wide = Path(page["footer_wide"]) if page.get("footer_wide") else FOOTER_WIDE      # a district page has its own footer
    if wide.exists():
        old_foot = f"file://{(ASSETS / page.get('footer', 'footer_coimbatore.png')).as_posix()}"
        html = html.replace(f'<img id="foot" src="{old_foot}">', f'<img id="foot" src="file://{wide.as_posix()}">', 1)
        html = html.replace("</style>", FOOT_CSS + "</style>", 1)
    if page.get("district"):      # owner 13 Nov: the end card asks to SEND the video to that area's people (the FOLLOW button stays)
        import re as _re
        card = spec.get("share_card") or f'⚡ {page["end_card"]} Follow செய்யுங்கள் 📌'
        html = _re.sub(r'<div class="e4">[^<]*</div>', f'<div class="e4">{card}</div>', html, count=1)
        html = html.replace("</body></html>", NO_CLASH_JS + "</body></html>", 1)
    if is_plain(spec):
        scene, extra = scene_html(spec)
        html = html.replace("</style>", SCENE_CSS + "</style>", 1)
        html = html.replace('<div id="stage">', '<div id="stage">' + scene, 1)
        html = html.replace("</body></html>", SCENE_JS.replace("__EXTRA__", json.dumps(extra)) + "</body></html>", 1)
    return html



_orig_pick_voice = V4.pick_voice


def pick_voice(spec):
    """owner 11 Nov: Kovai Minnal's news voice is chosen in poster/config.json reel_voice.voice - a FREE edge-tts Tamil voice
    (ta-..-...Neural, e.g. ta-SG-AnbuNeural). Never Google / Chirp; anything else keeps v4's Valluvar."""
    vs, alt = _orig_pick_voice(spec)
    v = (V4.voice_setting() or {}).get("voice", "")
    if isinstance(v, str) and v.startswith("ta-") and v.endswith("Neural") and "Chirp" not in v:
        vs["voice"] = v
    return vs, alt


V4.build_html = build_html
V4.pick_voice = pick_voice

if __name__ == "__main__":
    _key = sys.argv[3] if len(sys.argv) > 3 else "coimbatore"
    if R.PAGES.get(_key, {}).get("district"):      # owner 12 Nov: the closing follow line in the SAME news voice (Tamil), no English voice
        V4.english_outro = lambda work, idx, voice: print("closing share + follow line in the news voice (district page)")
        _sp = Path(sys.argv[1])
        _sp.write_text(json.dumps(district_spec(json.loads(_sp.read_text()), R.PAGES[_key]), ensure_ascii=False))
    V4.main(sys.argv[1], sys.argv[2], _key)
