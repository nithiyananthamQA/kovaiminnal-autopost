"""Kovai Minnal (கோவை மின்னல்) brand images, drawn from HTML/SVG with the repo's own fonts (kit/node_modules/@fontsource).

    python3 tools/make_brand.py

Outputs (all ours - nothing from the Coimbatore 360 page):
  kit/logo_coimbatore.png              1092x1092 round logo - reel top-right corner, carousels, rasipalan (file name kept so the code is unchanged)
  reel/assets/footer_coimbatore.png    2172x724 name strip at the bottom of every reel (the round logo inside)
  brand/profile_1080.png               Instagram + Facebook profile picture (upload by hand)
  brand/fb_cover_1640x624.png          Facebook Page cover photo (upload by hand)
"""
import sys, base64
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reel"))
import reel as R      # noqa: E402  (font-face helper)

FONTS = R.ff("CT", "catamaran", [700, 800, 900]) + R.ff("NST", "noto-sans-tamil", [700, 800]) + R.ff("BT", "baloo-thambi-2", [800])

NAVY, NAVY2, RED, YELLOW, ORANGE, WHITE = "#06122E", "#0E2A66", "#E3151B", "#FFD233", "#FF8A00", "#FFFFFF"

# one lightning bolt, used everywhere (viewBox 0 0 100 160)
BOLT = """<svg viewBox="0 0 100 160" xmlns="http://www.w3.org/2000/svg" style="{style}">
<defs><linearGradient id="bg{id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF27A"/><stop offset=".45" stop-color="#FFD233"/>
<stop offset="1" stop-color="#FF8A00"/></linearGradient></defs>
<path d="M62 0 L8 92 L44 92 L30 160 L94 58 L56 58 L78 0 Z" fill="url(#bg{id})" stroke="#1A0B00" stroke-width="3" stroke-linejoin="round"/>
</svg>"""

BASE = FONTS + """
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:transparent}
body{font-family:'NST','CT',sans-serif}
.ta{font-family:'BT','NST',sans-serif;font-weight:800}
.en{font-family:'CT',sans-serif;font-weight:900;letter-spacing:.04em}
"""


def footer_html(logo_uri):
    return f"""<html><head><style>{BASE}
body{{width:2172px;height:724px}}
#bar{{position:absolute;left:470px;top:214px;width:1640px;height:310px;background:linear-gradient(90deg,{NAVY} 0%,{NAVY2} 100%);
   border:8px solid {RED};border-left:none;border-radius:0 48px 48px 0;box-shadow:0 18px 40px rgba(0,0,0,.45)}}
#logo{{position:absolute;left:100px;top:118px;width:490px;height:490px;border-radius:50%;box-shadow:0 0 0 10px {RED},0 18px 40px rgba(0,0,0,.5)}}
#name{{position:absolute;left:660px;top:228px;display:flex;align-items:center;gap:26px;font-size:128px;line-height:1;color:#fff}}
#name b{{color:{YELLOW};font-weight:900}}
#name svg{{width:74px;height:118px}}
#tag{{position:absolute;left:660px;top:392px;background:{YELLOW};color:{NAVY};border-radius:18px;padding:16px 42px 4px;font-size:64px;line-height:1.15}}
#fol{{position:absolute;right:62px;top:380px;background:{RED};color:#fff;border-radius:34px;padding:16px 40px 8px;text-align:center;font-size:44px;line-height:1.2}}
#fol b{{color:{YELLOW};display:block}}
</style></head><body>
<div id="bar"></div><img id="logo" src="{logo_uri}">
<div id="name" class="en">KOVAI <b>MINNAL</b>{BOLT.format(id="F", style="")}</div>
<div id="tag" class="ta">நம்ம கோவை செய்திகள்</div>
<div id="fol" class="en">FOLLOW FOR<b>KOVAI UPDATES</b></div>
</body></html>"""


def shot(page, html, w, h, out, transparent=True):
    page.set_viewport_size({"width": w, "height": h})
    page.set_content(html, wait_until="load")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(200)
    out.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out), omit_background=transparent, clip={"x": 0, "y": 0, "width": w, "height": h})
    print("wrote", out.relative_to(ROOT))


def _palm(x, y, lean, scale=1.0, flip=False):
    """one coconut palm: curved trunk from (x, y) up, fronds at the top"""
    s, f = scale, (-1 if flip else 1)
    tx, ty = x + f * lean * s, y - 300 * s
    trunk = (f'<path d="M{x-9*s} {y} Q{x + f*lean*0.2*s} {y-170*s} {tx-6*s} {ty} L{tx+6*s} {ty} Q{x + f*lean*0.2*s + 16*s} {y-170*s} {x+9*s} {y} Z" '
             f'fill="#5A3A1E"/>')
    rings = "".join(f'<path d="M{x + f*lean*(k/7)**1.6*s - 9*s} {y - k*42*s} l{18*s} {-4*s}" stroke="#3A2410" stroke-width="{2.4*s}"/>' for k in range(1, 7))
    fronds = []
    for ang, ln in ((-160, 150), (-125, 165), (-90, 120), (-55, 165), (-20, 150), (15, 120), (-195, 120)):
        import math
        a = math.radians(ang)
        ex, ey = tx + math.cos(a) * ln * s, ty + math.sin(a) * ln * s * 0.75 + 40 * s
        cx, cy = tx + math.cos(a) * ln * 0.5 * s, ty + math.sin(a) * ln * 0.5 * s - 30 * s
        fronds.append(f'<path d="M{tx} {ty} Q{cx} {cy} {ex} {ey} Q{cx+8*s} {cy+26*s} {tx} {ty+8*s} Z" fill="#1E6B3A" stroke="#134A27" stroke-width="{2*s}"/>')
    nuts = f'<circle cx="{tx-8*s}" cy="{ty+12*s}" r="{9*s}" fill="#7A5A1E"/><circle cx="{tx+9*s}" cy="{ty+14*s}" r="{9*s}" fill="#6B4E18"/>'
    return trunk + rings + "".join(fronds) + nuts


def _mill(x, base, w=340):
    """Kovai's textile mill ("Manchester of South India"): long low shed, sawtooth roof, one tall slim brick chimney"""
    h, teeth = 62, 8
    tw = w / teeth
    roof = "".join(f"L{x + k*tw} {base-h} L{x + k*tw + tw*0.78} {base-h-34} L{x + (k+1)*tw - 0.01} {base-h-34} L{x + (k+1)*tw} {base-h} " for k in range(teeth))
    shed = f'<path d="M{x} {base} L{x} {base-h} {roof} L{x+w} {base} Z" fill="#1A1440"/>'
    glass = "".join(f'<path d="M{x + k*tw + tw*0.80} {base-h-30} L{x + (k+1)*tw - 3} {base-h-30} L{x + (k+1)*tw - 3} {base-h-4} Z" fill="#FF9F1C" opacity=".55"/>' for k in range(teeth))
    wins = "".join(f'<rect x="{x + 14 + k*38}" y="{base-40}" width="18" height="22" fill="#FFD86B" opacity=".8"/>' for k in range(int((w-20)/38)))
    cx = x + w * 0.80
    chim = (f'<path d="M{cx-17} {base-h} L{cx-11} {base-h-250} L{cx+11} {base-h-250} L{cx+17} {base-h} Z" fill="#6E2E1E"/>'
            f'<rect x="{cx-15}" y="{base-h-262}" width="30" height="14" fill="#4E1F14"/>'
            + "".join(f'<rect x="{cx-14+k*0.4}" y="{base-h-60-k*48}" width="{28-k*0.8}" height="6" fill="#4E1F14"/>' for k in range(4)))
    return chim + shed + glass + wins


def _adiyogi(x, base, sc=1.0):
    """Adiyogi bust (Isha Yoga Centre, at the foot of the Velliangiri hills) - owner 11 Nov asked for it like Coimbatore 360's badge.
    Local box 240 x 260, base line at the bottom; dark stone with a warm sunset rim light."""
    return f"""<g transform="translate({x} {base-260*sc}) scale({sc})">
 <path d="M70 118 C58 62 88 30 120 28 C152 30 182 62 170 118 C186 150 192 176 178 190 L62 190 C48 176 54 150 70 118 Z" fill="#1C1F28"/>
 <ellipse cx="120" cy="30" rx="27" ry="22" fill="#1C1F28"/><ellipse cx="120" cy="11" rx="15" ry="12" fill="#1C1F28"/>
 <path d="M146 20 a16 16 0 1 0 6 22 a12 12 0 1 1 -6 -22 Z" fill="#EDE6D2"/>
 <path d="M0 260 C6 204 50 184 88 176 L152 176 C190 184 234 204 240 260 Z" fill="#2E323E"/>
 <path d="M96 146 L144 146 L150 180 L90 180 Z" fill="#323743"/>
 <ellipse cx="120" cy="104" rx="41" ry="52" fill="#3A3F4C"/>
 <path d="M159 80 C166 100 164 128 150 146" fill="none" stroke="#FF9F1C" stroke-width="4" opacity=".55"/>
 <path d="M190 200 C214 214 232 234 238 258" fill="none" stroke="#FF9F1C" stroke-width="4" opacity=".45"/>
 <path d="M92 98 q12 6 22 0 M126 98 q12 6 22 0" fill="none" stroke="#1C1F28" stroke-width="3.5" stroke-linecap="round"/>
 <path d="M120 100 L114 124 L124 124" fill="none" stroke="#2A2E38" stroke-width="3" stroke-linejoin="round"/>
 <path d="M108 136 q12 7 24 0" fill="none" stroke="#1C1F28" stroke-width="3.5" stroke-linecap="round"/>
 <path d="M114 66 L126 66 L124 84 L116 84 Z" fill="#EDE6D2"/><ellipse cx="120" cy="88" rx="4" ry="5" fill="#C9302C"/>
 <path d="M80 196 Q120 232 160 196" fill="none" stroke="#7A5A3A" stroke-width="7" stroke-dasharray="2 8" stroke-linecap="round"/>
</g>"""


def scene_svg(shape="circle", band=True, nested=False):
    """Kovai Minnal illustrated logo (1000x1000 units): Coimbatore at monsoon dusk - Western Ghats, a textile mill with its
    chimney on the skyline, the Ukkadam lakefront, coconut palms and ONE lightning bolt (மின்னல்) reflected in the lake.
    The lower part is a flat navy band for the name (Fable brand advice 11 Nov: one scene, big wordmark, nothing from Coimbatore 360's badge)."""
    clip = {"circle": '<circle cx="500" cy="500" r="472"/>', "square": '<rect x="0" y="0" width="1000" height="1000"/>'}.get(
        shape, '<rect x="-3000" y="-3000" width="7000" height="7000"/>')
    bld = "".join(f'<rect x="{x}" y="{470-h}" width="{w}" height="{h}" fill="#241D55"/><rect x="{x}" y="{470-h}" width="{w}" height="{h}" fill="url(#win)"/>'
                  for x, w, h in ((404, 52, 96), (880, 56, 120), (944, 50, 80), (830, 44, 64)))
    posts = "".join(f'<rect x="{x}" y="468" width="4" height="16" fill="#D8CCE6"/>' for x in range(20, 1000, 36))
    shimmer = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="#FFE3A6" opacity=".45"/>'
                      for x, y, w in ((180, 512, 120), (690, 506, 150), (300, 536, 90), (740, 540, 110), (120, 548, 70)))
    band_svg = ('<path d="M0 566 Q500 520 1000 566 L1000 1000 L0 1000 Z" fill="#0B1B4D"/>'
                '<path d="M0 566 Q500 520 1000 566" fill="none" stroke="#FFD21F" stroke-width="6"/>') if band else ""
    head = ('<svg x="0" y="0" width="1000" height="1000" viewBox="0 0 1000 1000" overflow="visible">' if nested else
            '<svg viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">')
    return f"""{head}
<defs>
 <clipPath id="cp">{clip}</clipPath>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#060E2B"/><stop offset=".22" stop-color="#0B1B4D"/><stop offset=".36" stop-color="#5B3A8C"/>
  <stop offset=".44" stop-color="#C2547A"/><stop offset=".50" stop-color="#FF9F1C"/></linearGradient>
 <linearGradient id="lake" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9894A"/><stop offset=".45" stop-color="#7A3F86"/><stop offset="1" stop-color="#1B1650"/></linearGradient>
 <linearGradient id="boltg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFBD0"/><stop offset=".45" stop-color="#FFD21F"/><stop offset="1" stop-color="#FF9F1C"/></linearGradient>
 <radialGradient id="flash"><stop offset="0" stop-color="#FFF6C8" stop-opacity=".75"/><stop offset=".45" stop-color="#B996FF" stop-opacity=".28"/><stop offset="1" stop-color="#5B3A8C" stop-opacity="0"/></radialGradient>
 <radialGradient id="hz"><stop offset="0" stop-color="#FFD27A" stop-opacity=".9"/><stop offset="1" stop-color="#FF9F1C" stop-opacity="0"/></radialGradient>
 <pattern id="win" width="12" height="18" patternUnits="userSpaceOnUse"><rect x="3" y="4" width="5" height="7" fill="#FFD86B" opacity=".8"/></pattern>
 <filter id="glow" x="-60%" y="-30%" width="220%" height="160%"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<g clip-path="url(#cp)">
 {'' if nested else '<rect width="1000" height="1000" fill="url(#sky)"/>'}
 <ellipse cx="520" cy="470" rx="420" ry="70" fill="url(#hz)"/>
 <circle cx="520" cy="200" r="250" fill="url(#flash)"/>
 <g fill="#0A1440" opacity=".96"><ellipse cx="250" cy="70" rx="260" ry="80"/><ellipse cx="560" cy="40" rx="240" ry="90"/><ellipse cx="830" cy="80" rx="250" ry="82"/>
  <ellipse cx="400" cy="140" rx="180" ry="50"/><ellipse cx="690" cy="150" rx="170" ry="46"/></g>
 <g fill="#2A2470" opacity=".85"><ellipse cx="330" cy="172" rx="130" ry="26"/><ellipse cx="640" cy="186" rx="140" ry="24"/></g>
 <!-- Western Ghats ridge -->
 <path d="M0 380 L100 318 L190 352 L300 286 L410 340 L520 300 L630 352 L740 290 L850 344 L1000 300 L1000 480 L0 480 Z" fill="#3A2D7A"/>
 <path d="M0 420 L130 372 L250 404 L380 366 L500 400 L640 370 L770 402 L900 372 L1000 396 L1000 480 L0 480 Z" fill="#2B2266"/>
 <!-- the lightning: ONE bolt from the top centre, striking behind the skyline -->
 <g filter="url(#glow)"><path d="M574 96 L458 290 L526 290 L446 468 L622 248 L552 248 L626 96 Z" fill="url(#boltg)" stroke="#FFF7C2" stroke-width="5" stroke-linejoin="round"/></g>
 <!-- skyline: city blocks, Adiyogi (Isha) and the textile mill with its chimney -->
 {bld}
 {_adiyogi(150, 474, 1.0)}
 {_mill(480, 470, 330)}
 <!-- Ukkadam lakefront -->
 {'' if nested else '<rect x="0" y="482" width="1000" height="120" fill="url(#lake)"/>'}
 <g filter="url(#soft)" opacity=".85"><path d="M500 488 L470 520 L520 524 L486 590 L540 540 L500 536 L530 488 Z" fill="#FFD21F"/></g>
 {shimmer}
 {'' if nested else '<rect x="0" y="478" width="1000" height="7" fill="#D8CCE6"/>' + posts}
 <!-- coconut palms framing the edges -->
 {'' if nested else _palm(70, 640, 46, 0.86, flip=True) + _palm(915, 640, 56, 0.92, flip=True) + _palm(20, 690, 20, 0.66) + _palm(985, 700, 22, 0.66, flip=True)}
 {band_svg}
</g>
</svg>"""


def cover_scene_html():
    """Facebook cover 1640x624 in the illustrated style: the logo scene widened (mirrored hills, longer lake, extra palms and
    buildings at the sides), the name in a navy band. Adiyogi, bolt and mill sit in the middle 60% (mobile crops the sides)."""
    side_bld = "".join(f'<rect x="{x}" y="{470-h}" width="{w}" height="{h}" fill="#241D55"/><rect x="{x}" y="{470-h}" width="{w}" height="{h}" fill="url(#wwin)"/>'
                       for x, w, h in ((-300, 60, 90), (-230, 48, 140), (-170, 70, 70), (-90, 50, 110), (1010, 60, 130), (1080, 52, 90), (1150, 70, 150), (1230, 50, 80)))
    posts = "".join(f'<rect x="{x}" y="468" width="4" height="16" fill="#D8CCE6"/>' for x in range(-420, 1430, 36))
    ridge1 = "M0 380 L100 318 L190 352 L300 286 L410 340 L520 300 L630 352 L740 290 L850 344 L1000 300 L1000 480 L0 480 Z"
    ridge2 = "M0 420 L130 372 L250 404 L380 366 L500 400 L640 370 L770 402 L900 372 L1000 396 L1000 480 L0 480 Z"
    svg = f"""<svg viewBox="-420 40 1840 700" xmlns="http://www.w3.org/2000/svg" width="1640" height="624">
<defs>
 <linearGradient id="wsky" x1="0" y1="0" x2="0" y2="1000" gradientUnits="userSpaceOnUse">
  <stop offset="0" stop-color="#060E2B"/><stop offset=".22" stop-color="#0B1B4D"/><stop offset=".36" stop-color="#5B3A8C"/>
  <stop offset=".44" stop-color="#C2547A"/><stop offset=".50" stop-color="#FF9F1C"/></linearGradient>
 <linearGradient id="wlake" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E9894A"/><stop offset=".45" stop-color="#7A3F86"/><stop offset="1" stop-color="#1B1650"/></linearGradient>
 <pattern id="wwin" width="12" height="18" patternUnits="userSpaceOnUse"><rect x="3" y="4" width="5" height="7" fill="#FFD86B" opacity=".8"/></pattern>
</defs>
 <rect x="-500" y="0" width="2000" height="1000" fill="url(#wsky)"/>
 <g fill="#0A1440" opacity=".96"><ellipse cx="-150" cy="90" rx="260" ry="80"/><ellipse cx="1150" cy="90" rx="260" ry="80"/><ellipse cx="250" cy="70" rx="260" ry="80"/><ellipse cx="830" cy="80" rx="250" ry="82"/></g>
 <g transform="translate(0 0) scale(-1 1)"><path d="{ridge1}" fill="#3A2D7A"/><path d="{ridge2}" fill="#2B2266"/></g>
 <g transform="translate(2000 0) scale(-1 1)"><path d="{ridge1}" fill="#3A2D7A"/><path d="{ridge2}" fill="#2B2266"/></g>
 {side_bld}
 <rect x="-500" y="482" width="2000" height="120" fill="url(#wlake)"/>
 {scene_svg("none", band=False, nested=True)}
 <rect x="-500" y="478" width="2000" height="7" fill="#D8CCE6"/>{posts}
 {_palm(-60, 640, 50, 0.95)}{_palm(1060, 640, 50, 0.95, flip=True)}{_palm(-330, 660, 24, 0.8)}{_palm(1330, 660, 24, 0.8, flip=True)}
 <path d="M-500 566 Q500 520 1500 566 L1500 800 L-500 800 Z" fill="#0B1B4D"/>
 <path d="M-500 566 Q500 520 1500 566" fill="none" stroke="{YELLOW}" stroke-width="6"/>
</svg>"""
    return f"""<html><head><style>{BASE}
body{{width:1640px;height:624px;overflow:hidden;background:#0B1B4D;position:relative}}
#t{{position:absolute;left:0;right:0;top:474px;text-align:center;white-space:nowrap;font-size:88px;line-height:1;color:#fff;-webkit-text-stroke:10px #060E2B;paint-order:stroke fill}}
#t b{{color:{YELLOW}}}
#s{{position:absolute;left:0;right:0;top:578px;text-align:center;white-space:nowrap;font-size:28px;color:#E8ECF5;letter-spacing:.08em}}
</style></head><body><div style="position:absolute;inset:0">{svg}</div>
<div id="t" class="ta">கோவை <b>மின்னல்</b></div>
<div id="s" class="en">COIMBATORE NEWS · FAST · EVERY DAY</div>
</body></html>"""


def scene_logo_html(size=1092, shape="circle", ribbon=False):
    s = size / 1000
    rings = (f'<svg viewBox="0 0 1000 1000" style="position:absolute;inset:0;width:100%;height:100%">'
             f'<circle cx="500" cy="500" r="485" fill="none" stroke="{YELLOW}" stroke-width="26"/>'
             f'<circle cx="500" cy="500" r="471" fill="none" stroke="#0B1B4D" stroke-width="5"/></svg>') if shape == "circle" else ""
    rib = (f'<div id="rib" class="en">COIMBATORE NEWS</div>') if ribbon else ""
    return f"""<html><head><style>{BASE}
body{{width:{size}px;height:{size}px;position:relative;overflow:hidden;background:transparent}}
#t1,#t2{{position:absolute;left:0;right:0;text-align:center;line-height:1;-webkit-text-stroke:{14*s:.0f}px #060E2B;paint-order:stroke fill}}
#t1{{top:{578*s:.0f}px;font-size:{128*s:.0f}px;color:#fff}}
#t2{{top:{708*s:.0f}px;font-size:{152*s:.0f}px;color:{YELLOW}}}
#rib{{position:absolute;left:50%;top:{884*s:.0f}px;transform:translateX(-50%);color:{YELLOW};white-space:nowrap;font-size:{34*s:.0f}px;letter-spacing:.12em}}
</style></head><body>
<div style="position:absolute;inset:0">{scene_svg(shape)}</div>{rings}
<div id="t1" class="ta">கோவை</div><div id="t2" class="ta">மின்னல்</div>{rib}
</body></html>"""


def main():
    """Owner 11 Nov (approved): illustrated Coimbatore style everywhere - profile picture, reel corner logo, Facebook cover, and the
    reel footer strip with that same round logo inside. The first flat design was removed at the owner's request."""
    logo = ROOT / "kit" / "logo_coimbatore.png"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        shot(pg, scene_logo_html(1092, ribbon=True), 1092, 1092, logo)
        shot(pg, scene_logo_html(1080), 1080, 1080, ROOT / "brand" / "profile_1080.png")
        shot(pg, footer_html("data:image/png;base64," + base64.b64encode(logo.read_bytes()).decode()), 2172, 724, ROOT / "reel" / "assets" / "footer_coimbatore.png")
        shot(pg, cover_scene_html(), 1640, 624, ROOT / "brand" / "fb_cover_1640x624.png", transparent=False)
        b.close()


if __name__ == "__main__":
    main()
