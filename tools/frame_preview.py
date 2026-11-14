"""Still frames of a reel in ~20 s, without rendering the video (layout checks before a full render).

The reel page is built EXACTLY like the real render: reel5.py (district pages: district_spec + no English outro) -> reel4.main()
with the same spec changes and timing code, stopped right after build_html. Only the voice is a stand-in: silent lines whose
length is estimated from the text (0.07 s per letter, measured on real Anbu lines), or the real lines of an earlier render
with --voice. No network, nothing posted. Then the chosen moments are screenshot to PNG and every visible element is checked
against Instagram's Reels safe area (Meta 9:16 guidance; numbers in reel5.SAFE):
  top 14 % (270 px) and bottom 35 % (from y 1250) covered by Instagram's own UI, 6 % (65 px; we keep 70) at each side cropped
  on tall phones, and the like/comment/share buttons over the right 140 px of the lower half (from y 1000).
A sweep over the whole reel (every 0.2 s) then prints the worst place each element ever reaches.

  python3 tools/frame_preview.py SPEC.json PAGE OUTDIR [--times 0,0.5,2,8,20,sum,end] [--prefix after_] [--voice WORKDIR] [--sweep 0.2]
    PAGE   coimbatore (Kovai Minnal) or a district key (chennai, salem, ...)
    times  seconds, or: hook (just before the headline leaves), card (first fact card), sum (summary card full), end (end card)
  Fonts/icons come from kit/node_modules; in a git worktree without it: KIT=/path/to/main/checkout/kit python3 tools/...
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "reel"))
import reel as R      # noqa: E402
import reel5 as R5    # noqa: E402  (patches reel4: B2 look, footer, district end card)
V4 = R5.V4

SAFE = R5.SAFE      # the B2 design numbers (side 70 px >= Meta's 6 % = 65 px)
SEC_PER_LETTER = 0.07

# what is checked (full-screen backgrounds - photo, shade, flashes, end-card dimmer - are not); full-width bars (header, yellow
# strip) may bleed to the edges, so only their TEXT is measured; the headline has no box of its own, so its text too
CHECK_JS = """([S,minOp])=>{
  const vis=e=>{let o=1;for(let x=e;x&&x.nodeType===1;x=x.parentElement){const c=getComputedStyle(x);if(c.display==='none'||c.visibility==='hidden')return 0;o*=parseFloat(c.opacity);}return o;};
  const textOnly=['#hdr .nm','#mini','#hook .h1'];
  const sel=textOnly.concat(['#hdr .sub','#plogo','#pin','#hook .h2','.card','#sum','.ph','#foot','#end img','#end > div']);
  const out=[];
  sel.forEach(s=>document.querySelectorAll(s).forEach(e=>{
    if(vis(e)<minOp)return;
    let r=e.getBoundingClientRect();
    if(textOnly.includes(s)){const g=document.createRange();g.selectNodeContents(e);r=g.getBoundingClientRect();}
    if(r.width<2||r.height<2)return;
    const f=[];
    if(r.top<S.top)f.push('TOP '+Math.round(S.top-r.top)+'px');
    if(r.bottom>S.bottom)f.push('BOTTOM '+Math.round(r.bottom-S.bottom)+'px');
    if(r.left<S.side)f.push('LEFT '+Math.round(S.side-r.left)+'px');
    if(r.right>1080-S.side)f.push('RIGHT '+Math.round(r.right-(1080-S.side))+'px');
    if(r.right>S.buttons_x+0.5&&r.bottom>S.buttons_y+0.5)f.push('IG-BUTTONS');
    out.push({el:s+(e.id?'#'+e.id:''),box:[r.left,r.top,r.right,r.bottom].map(Math.round),flags:f});
  }));
  return out;}"""


class _Built(Exception):
    pass


def build_page(spec_path, page_key, work, voice_dir=None):
    """the reel's HTML exactly as reel4.main makes it (silent stand-in voice); returns the html path"""
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    page = R.PAGES.get(page_key)
    if not page:
        raise SystemExit(f"unknown page {page_key!r}")
    if page.get("district"):      # what reel5.py's __main__ does for a district page
        spec = R5.district_spec(spec, page)
        V4.english_outro = lambda *a: None
    else:
        V4.english_outro = lambda *a: None      # the stand-in already made the outro line
    work.mkdir(parents=True, exist_ok=True)
    spec_copy = work / "spec.json"      # never touch the original spec (reel5's __main__ rewrites it)
    spec_copy.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")

    def stand_in_voice(wdir, texts, *a, **k):
        for i, t in enumerate(texts):
            real = Path(voice_dir) / f"line{i}.wav" if voice_dir else None
            if real and real.exists():
                shutil.copy(real, wdir / f"line{i}.wav")
                continue
            dur = max(1.0, SEC_PER_LETTER * len(str(t).replace(" ", "")))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", f"{dur:.2f}",
                            str(wdir / f"line{i}.wav")], check=True)
    V4.edge_lines = stand_in_voice
    real_build = V4.build_html
    html_path = work / "reel_preview" / "reel4.html"

    def capture(*a, **k):
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(real_build(*a, **k), encoding="utf-8")
        raise _Built()
    V4.build_html = capture
    try:
        V4.main(str(spec_copy), str(work / "reel_preview.mp4"), page_key)
    except _Built:
        pass
    finally:
        V4.build_html = real_build
    return html_path


def shoot(html_path, times, outdir, prefix, sweep=0.2):
    """screenshots at the chosen times (every element listed), then a sweep over the whole reel every `sweep` s (no
    screenshots; elements at >= 90 % opacity, so slide-ins are skipped) that prints the worst place of each element"""
    from playwright.sync_api import sync_playwright
    outdir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": V4.W, "height": V4.H})
        pg.goto(html_path.resolve().as_uri())      # same start-up as reel4.main
        pg.wait_for_function("document.fonts.status==='loaded'")
        pg.evaluate("document.fonts.ready")
        pg.evaluate("fitAll()")
        D = pg.evaluate("D")
        cards = [s["a"] for s in D["sents"] if s["card"]]
        named = {"hook": D["hook_end"] - 0.35, "end": D["end_t"] + 0.9, "card": (cards[0] + 0.8) if cards else D["hook_end"] + 1,
                 "sum": min(D["end_t"] - 0.1, D["sum_a"] + 0.6 + 0.28 * D["rows"])}
        print(f"reel {D['total']:.1f}s  hook until {D['hook_end']:.1f}s  summary from {D['sum_a']:.1f}s  end card {D['end_t']:.1f}s")
        for name in times:
            t = max(0.0, min(named[name] if name in named else float(name), D["total"] - 0.05))
            pg.evaluate(f"renderAt({t})")
            png = outdir / (f"{prefix}{name}.png" if name in named else f"{prefix}{name.replace('.', '_')}s.png")
            pg.screenshot(path=str(png))
            boxes = pg.evaluate(CHECK_JS, [SAFE, 0.05])
            print(f"\n{png.name}  t={t:.2f}s  {sum(1 for x in boxes if x['flags'])} of {len(boxes)} elements outside the safe area")
            for x in boxes:
                print(f"  {'!!' if x['flags'] else 'ok'} {x['el']:<22} {x['box']}  {' '.join(x['flags'])}")
        if sweep:
            worst, n = {}, int(D["total"] / sweep)
            for i in range(n + 1):
                t = round(i * sweep, 3)
                pg.evaluate(f"renderAt({t})")
                for x in pg.evaluate(CHECK_JS, [SAFE, 0.9]):
                    key = x["el"].split("#")[0] if x["el"].startswith((".ph", ".card")) else x["el"]
                    w = worst.setdefault(key, {"top": 9999, "bottom": 0, "left": 9999, "right": 0, "flags": set(), "at": []})
                    l, tp, r, bt = x["box"]
                    w["top"], w["bottom"], w["left"], w["right"] = min(w["top"], tp), max(w["bottom"], bt), min(w["left"], l), max(w["right"], r)
                    if x["flags"]:
                        w["flags"].update(f.split()[0] for f in x["flags"])
                        w["at"].append(t)
            print(f"\nsweep every {sweep}s ({n + 1} moments): x {SAFE['side']}-{1080 - SAFE['side']}, y {SAFE['top']}-{SAFE['bottom']}, "
                  f"right of {SAFE['buttons_x']} only above y {SAFE['buttons_y']}")
            for k, w in worst.items():
                bad = f"!! {' '.join(sorted(w['flags']))} at {w['at'][0]:.1f}s ({len(w['at'])}x)" if w["flags"] else "ok"
                print(f"  {k:<16} x {w['left']}-{w['right']}  y {w['top']}-{w['bottom']}  {bad}")
        b.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("page")
    ap.add_argument("outdir")
    ap.add_argument("--times", default="0,0.5,2,8,20,sum,end")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--voice", help="work folder of an earlier render: its line<i>.wav are used instead of silent stand-ins")
    ap.add_argument("--sweep", type=float, default=0.2, help="check the whole reel every N seconds (0 = off)")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory(prefix="frame_preview_") as tmp:
        html = build_page(a.spec, a.page, Path(tmp), a.voice)
        shoot(html, [x.strip() for x in a.times.split(",") if x.strip()], Path(a.outdir), a.prefix, a.sweep)
