"""Gold + silver rate slides in OUR design (owner 17 Nov: "dont copy his template ... give better data for the users").

Minnal look (the reel's navy + yellow, our logo), 1080 x 1350, two slides like the reference job (silver left out when today's
silver rate is not confirmed). Every number is the confirmed rate or plain arithmetic on it - nothing estimated:
  gold:   1 சவரன் (8 g) 22K = the hero (how Tamil Nadu buys gold), 22K / 24K per gram, 24K 10 g, 1 சவரன் + 3% GST (GST on
          gold is 3%; making charges / wastage vary by shop, so they are left out and said so), this week's bars + high / low
  silver: 1 kg = the hero, 1 g / 10 g / 100 g, this week's bars + high / low
render(page_cfg, rates, outdir) -> [jpg, ...]  (same call as gold_render.render)"""
from pathlib import Path

from gold_render import ff, inr, change_words

NAVY, NAVY2, YELLOW, WHITE, RED, GREEN = "#06142E", "#0D2A5C", "#FFC400", "#FFFFFF", "#E53935", "#2E9E5B"
GST = 0.03      # GST on gold and silver (CGST 1.5% + SGST 1.5%)


def chip(d, unit=""):
    cls, word, ar = change_words(d)
    if cls == "same":
        return '<span class="chg same">● மாற்றமில்லை</span>'
    return f'<span class="chg {cls}">{ar} ₹{inr(abs(d))}{unit} {word}</span>'


def bars(points, accent):
    """this week's rates as bars (today in the accent colour) + the week's high / low"""
    vals = [v for _, v in points]
    if not vals:
        return ""
    hi, lo = max(vals), min(vals)
    base = lo - max(hi - lo, 1) * 0.6      # a small move stays a small step
    out = []
    for i, (lab, v) in enumerate(points):
        h = 40 + int((v - base) / ((hi - base) or 1) * 110)
        today = i == len(points) - 1
        out.append(f'<div class="bar{" today" if today else ""}"><b>₹{inr(v)}</b><i style="height:{h}px;'
                   f'{"background:" + accent if today else ""}"></i><span>{lab}</span></div>')
    return (f'<div class="bars">{"".join(out)}</div>'
            f'<div class="hl"><span>▲ வாரத்தின் அதிகம் ₹{inr(hi)}</span><span>▼ வாரத்தின் குறைவு ₹{inr(lo)}</span></div>')


def css():
    fonts = ff("Noto Sans Tamil", "noto-sans-tamil", (600, 700, 800, 900)) + "\n" + ff("Catamaran", "catamaran", (900,))
    return fonts + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden;font-family:'Noto Sans Tamil',sans-serif;color:{WHITE};
 background:radial-gradient(120% 70% at 85% 0%,{NAVY2} 0%,{NAVY} 60%);position:relative}}
.bolt{{position:absolute;right:-60px;top:120px;width:520px;height:900px;opacity:.07;
 background:{YELLOW};clip-path:polygon(55% 0,20% 55%,48% 55%,30% 100%,82% 40%,52% 40%,75% 0)}}
.top{{display:flex;align-items:center;gap:22px;padding:46px 54px 0}}
.top img{{width:116px;height:116px;border-radius:50%;border:4px solid {YELLOW};background:#fff}}
.brand b{{display:block;font-size:48px;font-weight:900;line-height:1.1;white-space:nowrap}}
.brand small{{font-family:'Catamaran';font-size:24px;letter-spacing:6px;color:{YELLOW}}}
.date{{margin-left:auto;border:3px solid {YELLOW};border-radius:40px;padding:10px 24px;font-size:26px;font-weight:800;color:{YELLOW};white-space:nowrap}}
.kick{{padding:26px 56px 0;font-size:30px;font-weight:700;color:#C9D6EE}}
.title{{padding:0 54px 0;font-size:84px;font-weight:900;line-height:1.15;color:{YELLOW}}}
.hero{{margin:24px 54px 0;background:{WHITE};color:{NAVY};border-radius:30px;padding:22px 40px 26px;position:relative;
 box-shadow:0 18px 40px rgba(0,0,0,.35)}}
.hero .lbl{{font-size:30px;font-weight:800;color:#3A4A6B}}
.hero .v{{font-family:'Catamaran';font-size:100px;font-weight:900;line-height:1.05;letter-spacing:-1px}}
.chg{{display:inline-block;border-radius:30px;padding:8px 22px;font-size:28px;font-weight:800;color:#fff}}
.chg.down{{background:{RED}}} .chg.up{{background:{GREEN}}} .chg.same{{background:#6B7A99}}
.hero .vs{{font-size:24px;font-weight:700;color:#6B7A99;margin-left:12px}}
.grid{{display:flex;gap:18px;margin:24px 54px 0}}
.cell{{flex:1;background:rgba(255,255,255,.07);border-left:8px solid {YELLOW};border-radius:18px;padding:18px 20px}}
.cell .k{{font-size:24px;font-weight:700;color:#C9D6EE}}
.cell .n{{font-family:'Catamaran';font-size:52px;font-weight:900;line-height:1.15}}
.cell .chg{{font-size:20px;padding:4px 12px}}
.tip{{margin:20px 54px 0;background:rgba(255,196,0,.13);border:2px dashed {YELLOW};border-radius:18px;padding:12px 24px;
 font-size:26px;font-weight:700;line-height:1.4}}
.tip b{{color:{YELLOW};font-family:'Catamaran';font-size:34px}}
.week{{margin:20px 54px 0;background:rgba(255,255,255,.06);border-radius:22px;padding:18px 26px 14px}}
.week h3{{font-size:28px;font-weight:800;color:#C9D6EE}}
.bars{{display:flex;align-items:flex-end;gap:14px;height:205px;margin-top:6px}}
.bar{{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end}}
.bar i{{display:block;width:62%;border-radius:10px 10px 0 0;background:rgba(201,214,238,.35)}}
.bar b{{font-family:'Catamaran';font-size:19px;font-weight:900;margin-bottom:6px;color:#C9D6EE}}
.bar.today b{{color:{YELLOW};font-size:22px}}
.bar span{{font-size:20px;font-weight:700;margin-top:8px;color:#C9D6EE}}
.hl{{display:flex;justify-content:space-between;font-size:23px;font-weight:700;color:#C9D6EE;margin-top:10px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:96px;background:{YELLOW};color:{NAVY};display:flex;align-items:center;
 justify-content:space-between;padding:0 54px;font-size:30px;font-weight:900}}
.foot small{{font-size:22px;font-weight:700}}
"""


def page(p, r, kind):
    brand = f'{p["name1"]} {p.get("brand2", "").strip()}'.strip()
    head = (f'<div class="bolt"></div><div class="top"><img src="file://{Path(p["logo"]).resolve()}">'
            f'<div class="brand"><b>{brand}</b><small>{p.get("brand_en", "")}</small></div><div class="date">{r["date"]}</div></div>')
    src = r.get("source" if kind == "gold" else "source_silver") or ""
    foot = (f'<div class="foot"><span>Follow @{p["handle"]}</span>'
            f'<small>சென்னை சந்தை விலை{" • " + src if src else ""}</small></div>')
    if kind == "gold":
        sov, sov_prev = r["g22"] * 8, r["g22_prev"] * 8
        body = (f'<div class="kick">{p["town"]} • காலை நிலவரம்</div><div class="title">தங்கம் விலை</div>'
                f'<div class="hero"><div class="lbl">22 காரட் • 1 சவரன் (8 கிராம்)</div><div class="v">₹{inr(sov)}</div>'
                f'{chip(sov - sov_prev)}<span class="vs">{r["vs"]}</span></div>'
                f'<div class="grid">'
                f'<div class="cell"><div class="k">22K • 1 கிராம்</div><div class="n">₹{inr(r["g22"])}</div>{chip(r["g22"] - r["g22_prev"])}</div>'
                f'<div class="cell"><div class="k">24K • 1 கிராம்</div><div class="n">₹{inr(r["g24"])}</div>{chip(r["g24"] - r["g24_prev"])}</div>'
                f'<div class="cell"><div class="k">24K • 10 கிராம்</div><div class="n">₹{inr(r["g24"] * 10)}</div></div></div>'
                f'<div class="tip">💡 1 சவரன் + 3% ஜிஎஸ்டி = <b>₹{inr(sov * (1 + GST))}</b><br>செய்கூலி, சேதாரம் கடைக்கு ஏற்ப தனியாகச் சேரும்</div>'
                f'<div class="week"><h3>இந்த வாரம் • 22K, 1 கிராம்</h3>{bars(r.get("week22") or [], YELLOW)}</div>')
    else:
        kg, kg_prev = r["silver"] * 1000, r["silver_prev"] * 1000
        body = (f'<div class="kick">{p["town"]} • காலை நிலவரம்</div><div class="title" style="color:#E6ECF5">வெள்ளி விலை</div>'
                f'<div class="hero"><div class="lbl">வெள்ளி • 1 கிலோ</div><div class="v">₹{inr(kg)}</div>'
                f'{chip(kg - kg_prev)}<span class="vs">{r["vs"]}</span></div>'
                f'<div class="grid">'
                f'<div class="cell"><div class="k">1 கிராம்</div><div class="n">₹{inr(r["silver"])}</div>{chip(r["silver"] - r["silver_prev"])}</div>'
                f'<div class="cell"><div class="k">10 கிராம்</div><div class="n">₹{inr(r["silver"] * 10)}</div></div>'
                f'<div class="cell"><div class="k">100 கிராம்</div><div class="n">₹{inr(r["silver"] * 100)}</div></div></div>'
                f'<div class="tip">💡 1 கிலோ + 3% ஜிஎஸ்டி = <b>₹{inr(kg * (1 + GST))}</b><br>கொலுசு, பாத்திரம் போன்றவற்றுக்கு செய்கூலி தனி</div>'
                f'<div class="week"><h3>இந்த வாரம் • வெள்ளி, 1 கிராம்</h3>{bars(r.get("weeksilver") or [], "#E6ECF5")}</div>')
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body>{head}{body}{foot}</body></html>'


def render(p, r, outdir, log=print):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    kinds = ["gold"] + (["silver"] if r.get("silver") else [])
    from playwright.sync_api import sync_playwright      # only here: the test machine has no browser
    out = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, kind in enumerate(kinds, 1):
            h = outdir / f"{i}_{kind}.html"
            h.write_text(page(p, r, kind), encoding="utf-8")
            pg.goto(f"file://{h.resolve()}")
            pg.wait_for_timeout(900)
            j = outdir / f"{i}_{kind}.jpg"
            pg.screenshot(path=str(j), type="jpeg", quality=92)      # Instagram takes JPEG only
            out.append(j)
            log("slide", j.name)
        b.close()
    return out
