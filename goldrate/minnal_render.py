"""Gold + silver rate visuals in OUR design (owner 17 Nov: "dont copy his template ... give better data for the users";
"he uses golden background for gold and silver for silver ... not feel same like him, just design well for ours").

The look: the GOLD slide is a warm gold field, the SILVER slide a cool brushed-silver field; on both, the Minnal navy carries
the brand (header band with our logo, the navy price plate with the metal-foil number, the week plate, the footer) and the
lightning yellow sits on the navy only (never on the metal, where it would vanish).
Every number is the confirmed rate or plain arithmetic on it - nothing estimated:
  gold:   1 சவரன் (8 g) 22K = the hero (how Tamil Nadu buys gold), 22K / 24K per gram, 24K 10 g, 1 சவரன் + 3% GST (GST on
          gold is 3%; making charges / wastage vary by shop, so they are left out and said so), this week's bars + high / low
  silver: 1 kg = the hero, 1 g / 10 g / 100 g, this week's bars + high / low
render(page_cfg, rates, outdir) -> [jpg, ...]   the feed post, 1080 x 1350 (same call as gold_render.render)
reel_page(page_cfg, rates) -> html              the reel, 1080 x 1920: gold, silver (when confirmed), follow card. The page has
                                                window.DUR, window.seek(t) (every frame is computed from t), window.CUES
                                                (where the sound effects land) and window.COVER_T (the built gold screen)"""
import json
from pathlib import Path

from gold_render import ff, inr, change_words

NAVY, NAVY2, YELLOW, WHITE, RED, GREEN = "#06142E", "#0D2A5C", "#FFC400", "#FFFFFF", "#E53935", "#2E9E5B"
GST = 0.03      # GST on gold and silver (CGST 1.5% + SGST 1.5%)
BOLT = '<svg class="bolt" viewBox="0 0 20 24"><path d="M12.5 0 2 13.2h6.2L5.4 24 18 9.4h-6.3L15.2 0z"/></svg>'


def chip(d, unit="", a=""):
    cls, word, ar = change_words(d)
    if cls == "same":
        return f'<span class="chg same"{a}>● மாற்றமில்லை</span>'
    return f'<span class="chg {cls}"{a}>{ar} ₹{inr(abs(d))}{unit} {word}</span>'


def bars(points, a=lambda k: ""):
    """this week's rates as bars (today = the lightning-yellow one) + the week's high / low"""
    vals = [v for _, v in points]
    if not vals:
        return ""
    hi, lo = max(vals), min(vals)
    base = lo - max(hi - lo, 1) * 0.6      # a small move stays a small step
    out = []
    for i, (lab, v) in enumerate(points):
        h = 24 + int((v - base) / ((hi - base) or 1) * 76)      # % of the bar track
        today = i == len(points) - 1
        out.append(f'<div class="bar{" today" if today else ""}"><div class="trk"><div class="in"><b{a("barv%d" % i)}>₹{inr(v)}</b>'
                   f'<i style="height:{h}%"{a("bar%d" % i)}></i></div></div><span>{lab}</span></div>')
    return (f'<div class="bars">{"".join(out)}</div>'
            f'<div class="hl"{a("hl")}><span>▲ வாரத்தின் அதிகம் ₹{inr(hi)}</span><span>▼ வாரத்தின் குறைவு ₹{inr(lo)}</span></div>')


def css():
    fonts = ff("Noto Sans Tamil", "noto-sans-tamil", (600, 700, 800, 900)) + "\n" + ff("Catamaran", "catamaran", (800, 900))
    return fonts + f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;overflow:hidden;font-family:'Noto Sans Tamil',sans-serif;color:{NAVY};position:relative;background:{NAVY}}}
.bolt{{display:block;fill:currentColor}}
/* the two metals */
.gold{{--bg:linear-gradient(140deg,#FFF1B8 0%,#F7CF5E 22%,#E9B233 45%,#F9DC7F 63%,#DDA021 82%,#BC800F 100%);
 --tex:repeating-conic-gradient(from 8deg at 92% 14%,rgba(255,255,255,.13) 0 3deg,rgba(255,255,255,0) 3deg 9deg);
 --foil:linear-gradient(180deg,#FFF6CF 0%,#FFD95C 42%,#E9A91F 58%,#FFE894 100%);
 --bar:linear-gradient(180deg,#F3CD62,#A9771A);--panel:rgba(255,250,232,.66);--edge:rgba(255,255,255,.75);
 --rim:#E9B233;--soft:#F6E3A6;--r:34px}}
.silver{{--bg:linear-gradient(140deg,#FBFCFE 0%,#D7DDE6 22%,#B6BFCC 45%,#EEF1F6 63%,#ABB5C3 82%,#838EA0 100%);
 --tex:repeating-linear-gradient(4deg,rgba(255,255,255,.2) 0 1px,rgba(255,255,255,0) 1px 5px);
 --foil:linear-gradient(180deg,#FFFFFF 0%,#E3E8EF 42%,#A3AEBD 58%,#F4F6FA 100%);
 --bar:linear-gradient(180deg,#EDF1F6,#8691A2);--panel:rgba(255,255,255,.62);--edge:rgba(255,255,255,.85);
 --rim:#C3CBD7;--soft:#DCE2EB;--r:12px}}
.metal{{position:absolute;inset:0;background:var(--bg)}}
.metal:before{{content:"";position:absolute;inset:0;background:var(--tex)}}
.metal:after{{content:"";position:absolute;inset:0;background:radial-gradient(90% 60% at 20% 30%,rgba(255,255,255,.35),rgba(255,255,255,0) 70%)}}
/* brand band */
.top{{position:relative;background:linear-gradient(100deg,{NAVY} 0%,{NAVY2} 100%);color:{WHITE};display:flex;align-items:center;
 gap:22px;padding:0 48px;border-bottom:7px solid {YELLOW};overflow:hidden}}
.top img{{width:108px;height:108px;border-radius:50%;border:4px solid {YELLOW};background:#fff;flex:none}}
.brand b{{display:block;font-size:46px;font-weight:900;line-height:1.2;white-space:nowrap}}
.brand small{{display:block;font-family:'Catamaran';font-weight:800;font-size:23px;letter-spacing:6px;color:{YELLOW};white-space:nowrap}}
.top .deco{{position:absolute;right:150px;top:-40px;width:210px;color:{YELLOW};opacity:.13;transform:rotate(8deg)}}
.date{{background:{NAVY};color:{YELLOW};border-radius:40px;padding:8px 24px;font-size:26px;font-weight:800;white-space:nowrap;line-height:1.45}}
.col{{position:relative;display:flex;flex-direction:column;padding:0 48px}}
.kickrow{{display:flex;align-items:center;justify-content:space-between}}
.kick{{font-size:30px;font-weight:800;color:{NAVY};opacity:.82;white-space:nowrap;line-height:1.5}}
.titlerow{{display:flex;align-items:center;justify-content:space-between}}
.title{{font-size:96px;font-weight:900;line-height:1.3;color:{NAVY};white-space:nowrap;text-shadow:0 2px 0 rgba(255,255,255,.45)}}
/* the emblem: our bolt struck on a gold coin / a silver bar */
.emb{{position:absolute;right:44px;top:50%;display:flex;align-items:center;justify-content:center;color:{NAVY}}}
.gold .emb{{width:168px;height:168px;margin-top:-84px;border-radius:50%;background:radial-gradient(circle at 34% 28%,#FFF8D6,#F4C847 48%,#B47C14 100%);
 box-shadow:inset 0 0 0 9px rgba(255,255,255,.38),inset 0 0 0 13px rgba(140,92,8,.5),0 0 0 6px rgba(255,196,0,.18),0 14px 30px rgba(0,0,0,.5)}}
.silver .emb{{width:196px;height:124px;margin-top:-62px;background:linear-gradient(180deg,#FFFFFF,#C9D1DC 50%,#8E99AA);
 clip-path:polygon(13% 0,87% 0,100% 100%,0 100%);filter:drop-shadow(0 14px 20px rgba(0,0,0,.5))}}
.silver .emb:before{{content:"";position:absolute;left:11%;right:11%;top:9%;bottom:12%;background:linear-gradient(180deg,#DDE3EB,#F8FAFC);
 clip-path:polygon(9% 0,91% 0,100% 100%,0 100%)}}
.emb .bolt{{width:62px;position:relative}}
/* the price plate */
.hero{{position:relative;overflow:hidden;background:linear-gradient(120deg,{NAVY2} 0%,{NAVY} 70%);color:{WHITE};border-radius:var(--r);
 padding:20px 40px 26px;box-shadow:0 18px 36px rgba(6,20,46,.38),inset 0 0 0 3px var(--rim),inset 0 0 0 9px {NAVY}}}
.hero .sheen{{position:absolute;top:-20%;bottom:-20%;left:0;width:150px;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.2),rgba(255,255,255,0));
 transform:translateX(-400px) skewX(-18deg);pointer-events:none}}
.hero .lbl{{position:relative;font-size:30px;font-weight:800;color:var(--soft);white-space:nowrap;line-height:1.5}}
.hero .v{{position:relative;display:inline-block;font-family:'Catamaran';font-size:112px;font-weight:900;line-height:1.08;letter-spacing:-1px;
 padding-right:8px;white-space:nowrap;background:var(--foil);-webkit-background-clip:text;background-clip:text;color:transparent;
 filter:drop-shadow(0 3px 0 rgba(0,0,0,.35))}}
.hero .cv{{position:relative;display:flex;align-items:center;gap:14px;margin-top:2px}}
.chg{{display:inline-block;border-radius:30px;padding:6px 22px;font-size:28px;font-weight:800;color:#fff;white-space:nowrap;line-height:1.5}}
.chg.down{{background:{RED}}} .chg.up{{background:{GREEN}}} .chg.same{{background:#5F6F90}}
.hero .vs{{font-size:24px;font-weight:700;color:#B9C6E0;white-space:nowrap}}
/* the rate rows */
.rows{{background:var(--panel);border:2px solid var(--edge);border-radius:24px;padding:0 28px;box-shadow:0 10px 22px rgba(6,20,46,.12)}}
.row{{display:flex;align-items:center;gap:16px;height:70px;border-top:2px solid rgba(6,20,46,.12)}}
.row:first-child{{border-top:0}}
.row .k{{font-size:28px;font-weight:800;white-space:nowrap}}
.row .k em{{font-style:normal;display:inline-block;background:{NAVY};color:{YELLOW};border-radius:10px;padding:0 12px;margin-right:12px;
 font-family:'Catamaran';font-weight:900;font-size:28px;line-height:1.5}}
.row .chg{{font-size:21px;padding:3px 14px}}
.row .n{{margin-left:auto;font-family:'Catamaran';font-size:54px;font-weight:900;line-height:1;white-space:nowrap}}
/* the tip */
.tip{{display:flex;align-items:center;gap:20px;border:3px dashed rgba(6,20,46,.55);border-radius:22px;padding:10px 24px;background:rgba(255,255,255,.22)}}
.tip .ic{{flex:none;width:62px;height:62px;border-radius:50%;background:{NAVY};color:{YELLOW};display:flex;align-items:center;justify-content:center}}
.tip .ic .bolt{{width:28px}}
.tip p{{font-size:26px;font-weight:800;line-height:1.5;white-space:nowrap}}
.tip p b{{display:inline-block;background:{NAVY};color:{YELLOW};border-radius:12px;padding:0 14px;font-family:'Catamaran';font-weight:900;font-size:34px;line-height:1.3;vertical-align:middle}}
.tip p.s{{font-size:23px;font-weight:700;opacity:.85}}
/* the week */
.week{{display:flex;flex-direction:column;background:linear-gradient(180deg,{NAVY2},{NAVY});color:{WHITE};border-radius:26px;padding:14px 26px 12px;
 box-shadow:0 14px 28px rgba(6,20,46,.3)}}
.week h3{{font-size:27px;font-weight:800;color:var(--soft);white-space:nowrap;line-height:1.5}}
.bars{{flex:1;display:flex;align-items:stretch;gap:12px;min-height:0}}
.bar{{flex:1;max-width:190px;display:flex;flex-direction:column;align-items:center;margin:0 auto}}
.bar .trk{{flex:1;width:100%;position:relative;min-height:0}}
.bar .trk .in{{position:absolute;left:0;right:0;top:30px;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-end}}
.bar i{{display:block;flex:none;width:64%;border-radius:9px 9px 0 0;background:var(--bar);opacity:.8;transform-origin:50% 100%}}
.bar b{{font-family:'Catamaran';font-size:20px;font-weight:900;color:#D5DEF0;white-space:nowrap;line-height:1.3}}
.bar.today i{{background:linear-gradient(180deg,#FFE066,{YELLOW});opacity:1;box-shadow:0 0 22px rgba(255,196,0,.55)}}
.bar.today b{{color:{YELLOW};font-size:24px}}
.bar span{{font-size:20px;font-weight:700;color:#D5DEF0;white-space:nowrap;line-height:1.7}}
.bar.today span{{color:{NAVY};background:{YELLOW};border-radius:14px;padding:0 10px;font-weight:800}}
.hl{{display:flex;justify-content:space-between;gap:20px;font-size:22px;font-weight:700;color:#D5DEF0;border-top:2px solid rgba(255,255,255,.14);
 margin-top:8px;padding-top:4px;white-space:nowrap;line-height:1.6}}
.src{{font-size:22px;font-weight:700;white-space:nowrap;line-height:1.5}}

/* ---------- the feed post, 1080 x 1350 ---------- */
body.post{{height:1350px}}
.post .top{{height:138px}}
.post .col{{height:1126px;padding-top:14px;padding-bottom:16px;gap:14px}}
.post .titlerow{{margin-top:-14px;margin-bottom:-6px}}
.post .week{{flex:1;min-height:0}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:86px;background:{NAVY};color:{YELLOW};display:flex;align-items:center;
 justify-content:space-between;padding:0 48px;font-size:30px;font-weight:900;border-top:5px solid {YELLOW};white-space:nowrap}}
.foot small{{font-size:22px;font-weight:700;color:#D5DEF0}}
"""


def blocks(p, r, kind, a=lambda k: ""):
    """the pieces of one metal's screen (the post and the reel lay the same pieces out); a(key) -> the reel's animation attribute"""
    brand = f'{p["name1"]} {p.get("brand2", "").strip()}'.strip()
    src = r.get("source" if kind == "gold" else "source_silver") or ""
    b = {"top": (f'<div class="top"><div class="deco">{BOLT}</div><img src="file://{Path(p["logo"]).resolve()}"{a("logo")}>'
                 f'<div class="brand"{a("brand")}><b>{brand}</b><small>{p.get("brand_en", "")}</small></div>%s</div>'),
         "date": f'<div class="date"{a("date")}>{r["date"]}</div>',
         "kick": f'<div class="kick"{a("kick")}>{p["town"]} • காலை நிலவரம்</div>',
         "market": f'{p["town"]} நிலவரம்{" • " + src if src else ""}'}
    if kind == "gold":
        sov, sov_prev = r["g22"] * 8, r["g22_prev"] * 8
        title, lbl, val, prev = "தங்கம் விலை", "22 காரட் • 1 சவரன் (8 கிராம்)", sov, sov_prev
        rows = [("<em>22K</em>1 கிராம்", r["g22"], r["g22"] - r["g22_prev"]), ("<em>24K</em>1 கிராம்", r["g24"], r["g24"] - r["g24_prev"]),
                ("<em>24K</em>10 கிராம்", r["g24"] * 10, None)]
        tip = (f'1 சவரன் + 3% ஜிஎஸ்டி = <b>₹{inr(sov * (1 + GST))}</b>', "செய்கூலி, சேதாரம் கடைக்கு ஏற்ப தனியாகச் சேரும்")
        wk, pts = "இந்த வாரம் • 22K, 1 கிராம்", r.get("week22") or []
    else:
        kg, kg_prev = r["silver"] * 1000, r["silver_prev"] * 1000
        title, lbl, val, prev = "வெள்ளி விலை", "வெள்ளி • 1 கிலோ", kg, kg_prev
        rows = [("1 கிராம்", r["silver"], r["silver"] - r["silver_prev"]), ("10 கிராம்", r["silver"] * 10, None),
                ("100 கிராம்", r["silver"] * 100, None)]
        tip = (f'1 கிலோ + 3% ஜிஎஸ்டி = <b>₹{inr(kg * (1 + GST))}</b>', "கொலுசு, பாத்திரம் போன்றவற்றுக்கு செய்கூலி தனி")
        wk, pts = "இந்த வாரம் • வெள்ளி, 1 கிராம்", r.get("weeksilver") or []
    b["title"] = (f'<div class="titlerow"><div class="title"{a("title")}>{title}</div>'
                  f'</div>')
    cnt = a("count")      # the reel counts up from yesterday's price (from 97% when unchanged) and lands on today's
    if cnt:
        cnt += f' data-from="{int(round(prev if prev != val else val * 0.97))}" data-to="{int(round(val))}"'
    b["hero"] = (f'<div class="hero"{a("hero")}><div class="emb"{a("emb")}>{BOLT}</div><div class="sheen"></div><div class="lbl">{lbl}</div>'
                 f'<div class="v"{cnt}>₹{inr(val)}</div>'
                 f'<div class="cv">{chip(val - prev, a=a("chip"))}<span class="vs"{a("vs")}>{r["vs"]}</span></div></div>')
    b["rows"] = '<div class="rows"%s>' % a("rows") + "".join(
        f'<div class="row"{a("row%d" % i)}><div class="k">{k}</div>{chip(d) if d is not None else ""}<div class="n">₹{inr(n)}</div></div>'
        for i, (k, n, d) in enumerate(rows)) + "</div>"
    b["tip"] = (f'<div class="tip"{a("tip")}><div class="ic">{BOLT}</div><div><p>{tip[0]}</p><p class="s">{tip[1]}</p></div></div>')
    b["week"] = f'<div class="week"{a("week")}><h3>{wk}</h3>{bars(pts, a)}</div>'
    return b


def page(p, r, kind):
    b = blocks(p, r, kind)
    body = (f'<div class="metal"></div>{b["top"] % ""}<div class="col"><div class="kickrow">{b["kick"]}{b["date"]}</div>'
            f'{b["title"]}{b["hero"]}{b["rows"]}{b["tip"]}{b["week"]}</div>'
            f'<div class="foot"><span>Follow @{p["handle"]}</span><small>{b["market"]}</small></div>')
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body class="post {kind}">{body}</body></html>'


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


# ---------------------------------------------------------------- the reel, 1080 x 1920
# One metal's screen, seconds after its lightning strike: key -> (start, length, effect). Everything on the page (and every sound
# cue) comes from this one table, so a cue always sits on something that happens on screen.
SCENE = 5.8                                             # one metal's screen
END = 2.2                                               # the follow card
STEPS = {"logo": (0.05, 0.35, "pop"), "brand": (0.12, 0.35, "fade"), "date": (0.22, 0.35, "fade"),
         "kick": (0.30, 0.35, "fade"), "title": (0.40, 0.45, "wipe"), "emb": (0.62, 0.40, "pop"),
         "hero": (0.90, 0.40, "pop"), "count": (1.05, 0.95, "count"), "chip": (2.10, 0.35, "pop"), "vs": (2.25, 0.30, "fade"),
         "rows": (2.50, 0.30, "fade"), "row0": (2.55, 0.30, "fade"), "row1": (2.90, 0.30, "fade"), "row2": (3.25, 0.30, "fade"),
         "week": (3.65, 0.35, "pop"), "hl": (4.50, 0.30, "fade"), "tip": (4.90, 0.40, "pop"), "src": (5.10, 0.30, "fade")}
BAR0, BAR_STEP, BAR_LEN = 3.80, 0.09, 0.40             # the week's bars grow one after another; today's lands last
COVER = 5.5                                            # the gold screen is fully built here (reel cover)
CUES = [(0.0, "hit"), (0.40, "whoosh"), (1.05, "tick"), (1.35, "tick"), (1.65, "tick"), (2.0, "chime"), (2.55, "tick"),
        (2.90, "tick"), (3.25, "tick"), (3.80, "whoosh"), (4.90, "chime"), (5.30, "riser")]
END_STEPS = {"elogo": (0.10, 0.45, "pop"), "ename": (0.40, 0.35, "fade"), "esub": (0.60, 0.35, "fade"), "efollow": (0.85, 0.40, "pop")}

REEL_CSS = f"""
body.reel{{height:1920px}}
.scene{{position:absolute;left:0;top:0;width:1080px;height:1920px;overflow:hidden;visibility:hidden}}
.reel .metal{{left:-60px;right:-60px}}
.reel .top{{height:352px;align-items:flex-start;padding-top:228px}}
.reel .top .deco{{right:60px;top:-30px;width:250px}}
.reel .top .date{{margin-left:auto;margin-top:24px;background:{YELLOW};color:{NAVY}}}
.reel .col{{position:absolute;left:0;right:0;top:352px;padding-top:12px}}
.reel .title{{font-size:100px}}
.reel .titlerow{{margin-top:-8px}}
.reel .hero{{margin-top:2px;padding:22px 40px 28px}}
.reel .hero .v{{font-size:124px}}
.reel .rows{{margin-top:16px}}
.reel .row{{height:78px}}
.reel .low{{margin-right:104px}}
.reel .week{{margin-top:18px;height:344px}}
.reel .tip{{margin-top:16px}}
.reel .tip p{{font-size:25px}}
.reel .tip p.s{{font-size:21px}}
.reel .src{{margin-top:8px;opacity:.85}}
.end{{background:radial-gradient(90% 55% at 50% 42%,{NAVY2} 0%,{NAVY} 75%);color:{WHITE};text-align:center}}
.end .deco{{position:absolute;left:50%;top:150px;width:900px;margin-left:-450px;color:{YELLOW};opacity:.07}}
.end img{{position:absolute;left:50%;top:470px;width:330px;height:330px;margin-left:-165px;border-radius:50%;border:7px solid {YELLOW};
 background:#fff;box-shadow:0 0 90px rgba(255,196,0,.35)}}
.end .nm{{position:absolute;left:60px;right:60px;top:836px;font-size:84px;font-weight:900;line-height:1.3;white-space:nowrap}}
.end .sub{{position:absolute;left:60px;right:60px;top:952px;font-size:34px;font-weight:700;color:#D5DEF0;line-height:1.5;white-space:nowrap}}
.end .fw{{position:absolute;left:0;right:0;top:1024px}}
.end .fw span{{display:inline-block;background:{YELLOW};color:{NAVY};border-radius:50px;padding:10px 44px;font-size:42px;font-weight:900;
 line-height:1.5;white-space:nowrap;box-shadow:0 12px 30px rgba(0,0,0,.4)}}
.flash{{position:absolute;inset:0;opacity:0;pointer-events:none;mix-blend-mode:screen;
 background:radial-gradient(80% 60% at 55% 36%,#FFFFFF 0%,#FFF3B0 40%,{YELLOW} 100%)}}
.strike{{position:absolute;left:50%;top:230px;width:800px;margin-left:-400px;color:#fff;opacity:0;pointer-events:none;
 filter:drop-shadow(0 0 30px #FFE066) drop-shadow(0 0 90px {YELLOW})}}
.base{{position:absolute;left:0;right:0;top:1700px;bottom:0;background:linear-gradient(100deg,{NAVY} 0%,{NAVY2} 100%);border-top:7px solid {YELLOW};overflow:hidden}}
.base .bolt{{position:absolute;right:70px;top:-30px;width:230px;color:{YELLOW};opacity:.13;transform:rotate(8deg)}}
"""

REEL_JS = """
const cl=x=>x<0?0:x>1?1:x, eo=x=>1-Math.pow(1-x,3), back=x=>1+2.4*Math.pow(x-1,3)+1.4*Math.pow(x-1,2);
function inr(n){let s=String(Math.round(n)),l=s.slice(-3),r=s.slice(0,-3),p=[];while(r.length>2){p.unshift(r.slice(-2));r=r.slice(0,-2)}
 if(r)p.unshift(r);p.push(l);return p.join(',')}
const scenes=[...document.querySelectorAll('.scene')], flash=document.querySelector('.flash'), strike=document.querySelector('.strike');
const els=[...document.querySelectorAll('[data-a]')].map(e=>{const a=e.dataset.a.split(',');
 return {e,t0:+a[0],d:+a[1],fx:a[2],fin:e.textContent,from:+e.dataset.from,to:+e.dataset.to}});
window.seek=t=>{
 t=Math.max(0,Math.min(window.DUR,+t||0));
 scenes.forEach((s,i)=>{
  const on=t>=SC[i][0]&&(t<SC[i][1]||i==scenes.length-1), u=t-SC[i][0];
  s.style.visibility=on?'visible':'hidden';
  const m=s.querySelector('.metal'); if(m) m.style.transform='translateX('+(-30+u*8).toFixed(2)+'px)';
  const sh=s.querySelector('.sheen'); if(sh){const q=cl((u-2.2)/1.1);      // one glint across the plate, done long before the cover frame
   sh.style.transform='translateX('+(-400+q*1700).toFixed(1)+'px) skewX(-18deg)';}
 });
 for(const o of els){
  const x=cl((t-o.t0)/o.d), k=eo(x), st=o.e.style;
  if(o.fx=='count'){o.e.textContent=x>=1?o.fin:'\\u20B9'+inr(o.from+(o.to-o.from)*k);continue}
  st.visibility=x<=0?'hidden':'inherit';
  if(o.fx=='pop'){st.opacity=cl(x*2.5).toFixed(3);st.transform='scale('+(0.9+0.1*back(x)).toFixed(4)+')'}
  else if(o.fx=='fade'){st.opacity=k.toFixed(3)}
  else if(o.fx=='wipe'){st.clipPath='inset(-10% '+((1-k)*100).toFixed(2)+'% -10% 0)'}
  else if(o.fx=='grow'){st.transform='scaleY('+k.toFixed(4)+')'}
 }
 let f=0, b=0;      // the lightning strike: a white frame, a flicker, the bolt stays a moment, the glow dies away
 for(const ft of FL){const d=t-ft; if(d>=0&&d<0.46){
  f=Math.max(f, d<0.10?1-d/0.10*0.7 : d<0.16?0.3+(d-0.10)/0.06*0.3 : 0.6*Math.pow(1-(d-0.16)/0.30,2));
  b=Math.max(b, d<0.20?1:d<0.36?1-(d-0.20)/0.16:0);}}
 flash.style.opacity=f.toFixed(3); flash.style.visibility=f>0?'visible':'hidden';
 strike.style.opacity=b.toFixed(3); strike.style.visibility=b>0?'visible':'hidden';
};
window.seek(0);
"""


def reel_timeline(r):
    """-> (kinds, scene windows [(start, end)], DUR, CUES, COVER_T) for today's rates (no silver screen when silver is not confirmed)"""
    kinds = ["gold"] + (["silver"] if r.get("silver") else [])
    win = [(round(i * SCENE, 2), round((i + 1) * SCENE, 2)) for i in range(len(kinds))]
    end0 = win[-1][1]
    win.append((end0, round(end0 + END, 2)))
    cues = []
    for i, kind in enumerate(kinds):
        n = len(r.get("week22" if kind == "gold" else "weeksilver") or [])
        for t, k in CUES:
            if k == "whoosh" and t == BAR0 and not n:
                continue
            cues.append({"t": round(win[i][0] + t, 2), "kind": k})
        if n:      # today's bar lands
            cues.append({"t": round(win[i][0] + BAR0 + (n - 1) * BAR_STEP + BAR_LEN, 2), "kind": "tick"})
    cues += [{"t": end0, "kind": "hit"}, {"t": round(end0 + END_STEPS["efollow"][0], 2), "kind": "chime"}]
    return kinds, win, win[-1][1], sorted(cues, key=lambda c: c["t"]), COVER


def reel_page(p, r):
    kinds, win, dur, cues, cover = reel_timeline(r)

    def anim(s0, steps):
        def a(k):
            if k.startswith("bar"):
                i = int(k.lstrip("barv"))
                t = BAR0 + i * BAR_STEP
                st = (t + BAR_LEN - 0.1, 0.25, "fade") if k.startswith("barv") else (t, BAR_LEN, "grow")
            else:
                st = steps.get(k)
            return f' data-a="{s0 + st[0]:.2f},{st[1]},{st[2]}"' if st else ""
        return a

    scenes = []
    for i, kind in enumerate(kinds):
        a = anim(win[i][0], STEPS)
        b = blocks(p, r, kind, a)
        scenes.append(f'<div class="scene {kind}"><div class="metal"></div>{b["top"] % b["date"]}<div class="col">'
                      f'<div class="kickrow">{b["kick"]}</div>{b["title"]}{b["hero"]}{b["rows"]}'
                      f'<div class="low">{b["week"]}{b["tip"]}<div class="src"{a("src")}>{b["market"]}</div></div></div>'
                      f'<div class="base">{BOLT}</div></div>')
    a = anim(win[-1][0], END_STEPS)
    brand = f'{p["name1"]} {p.get("brand2", "").strip()}'.strip()
    both = "தங்கம், வெள்ளி" if len(kinds) > 1 else "தங்கம்"
    scenes.append(f'<div class="scene end"><div class="deco">{BOLT}</div><img src="file://{Path(p["logo"]).resolve()}"{a("elogo")}>'
                  f'<div class="nm"{a("ename")}>{brand}</div><div class="sub"{a("esub")}>தினமும் {both} விலை நிலவரம்</div>'
                  f'<div class="fw"><span{a("efollow")}>Follow @{p["handle"]}</span></div></div>')
    js = (f'window.DUR={dur};window.COVER_T={cover};window.CUES={json.dumps(cues)};'
          f'const SC={json.dumps(win)},FL={json.dumps([w[0] for w in win])};' + REEL_JS)
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}{REEL_CSS}</style></head><body class="reel">'
            f'{"".join(scenes)}<div class="flash"></div><div class="strike">{BOLT}</div><script>{js}</script></body></html>')
