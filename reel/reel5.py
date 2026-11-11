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
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel as R          # noqa: E402
import reel4 as V4        # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
FOOTER_WIDE = ASSETS / "footer_wide_coimbatore.png"
HEADER_SUFFIX = "செய்திகள்"

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


_orig_build = V4.build_html


def build_html(spec, shots, sents, caps, hook_end, end_t, total, page):
    html = _orig_build(spec, shots, sents, caps, hook_end, end_t, total, page)
    # owner 11 Nov: the header at the top says "கோவை மின்னல் செய்திகள்" (Kovai Minnal News), not only the page name
    name = page["name"]
    html = html.replace(f'<div class="nm">{name}</div>', f'<div class="nm">{name} {HEADER_SUFFIX}</div>', 1)
    if FOOTER_WIDE.exists():
        old_foot = f"file://{(ASSETS / page.get('footer', 'footer_coimbatore.png')).as_posix()}"
        html = html.replace(f'<img id="foot" src="{old_foot}">', f'<img id="foot" src="file://{FOOTER_WIDE.as_posix()}">', 1)
        html = html.replace("</style>", FOOT_CSS + "</style>", 1)
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
    V4.main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "coimbatore")
