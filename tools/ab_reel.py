"""Writer comparison (owner 11 Nov): turn a test draft from research_free/run.py (research_free/results/<n>.json) into a reel with
the given pictures, using the posting job's own final_caption() + render_reel(). Nothing is uploaded or posted, the Sheet is untouched.

  .venv/bin/python tools/ab_reel.py research_free/results/1.json out/ab-claude out/RN-2/img1.jpg out/RN-2/img2.jpg
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "poster"))
sys.path.insert(0, str(ROOT / "research_free"))
os.chdir(ROOT)
import post  # noqa: E402

res, out = Path(sys.argv[1]), Path(sys.argv[2])
images = [Path(p).resolve() for p in sys.argv[3:]]
r = json.loads(res.read_text(encoding="utf-8"))
d = r["draft"]
spec_raw = d.get("slides_spec") or {}
row = {"story_id": out.name, "published": r["article"].get("published", ""), "headline_ta": d.get("tamil_headline", ""),
       "headline_en": d.get("english_headline", ""), "category": d.get("category", ""), "location": d.get("location", ""),
       "importance": d.get("importance", ""), "source": r.get("url", ""), "caption": d.get("caption", ""), "post_to": d.get("post_to", ""),
       "reel_script": d.get("reel_script", ""), "slides_spec": spec_raw if isinstance(spec_raw, str) else json.dumps(spec_raw, ensure_ascii=False)}
spec = json.loads(row["slides_spec"])
spec["date"] = post.tamil_date_today()
out.mkdir(parents=True, exist_ok=True)
(out / "caption.txt").write_text(post.final_caption(row), encoding="utf-8")
mp4 = post.render_reel(row, spec, images, out)
print("writer:", r.get("model"), "| problems:", len(r.get("problems") or []))
print("reel:", mp4)
print("caption:", out / "caption.txt")
