"""Writes workers/timer/src/schedule.json for the Cloudflare Worker timer (owner 17-18 Nov: "use GitHub only when needed").

For every page repo (Kovai = this checkout, the others = their clones at ~/<repo name>, tools/make_page.PAGE) and every workflow with a
schedule: its OWN cron lines (the .yml's schedule block - the same times tools/keeper.py used) and the inputs of a live run
(tools/keeper.LIVE_INPUTS). keeper.yml itself is left out (the Worker replaces it).
  python3 tools/make_timer.py        then: cd workers/timer && npx wrangler deploy"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import keeper      # noqa: E402

OUT = ROOT / "workers" / "timer" / "src" / "schedule.json"
KOVAI = "nithiyananthamQA/kovaiminnal-autopost"


def jobs(repo_dir, only=None):
    """only: the page's own job list (make_page.PAGE[key]["jobs"], a power-cut-only page) - no other workflow is started"""
    out = []
    for p in sorted((Path(repo_dir) / ".github" / "workflows").glob("*.yml")):
        lines = keeper.crons(p.read_text(encoding="utf-8"))
        if lines and p.name != "keeper.yml" and (only is None or p.name in only):
            if p.name not in keeper.LIVE_INPUTS:
                raise SystemExit(f"{repo_dir}: {p.name} has a schedule but no live inputs in tools/keeper.py LIVE_INPUTS")
            out.append({"file": p.name, "crons": lines, "inputs": keeper.LIVE_INPUTS[p.name]})
    return out


def build():
    import make_page
    repos = {KOVAI: jobs(ROOT)}
    for key, pg in make_page.PAGE.items():
        d = Path.home() / pg["repo"].split("/")[1]
        if (d / ".github").is_dir() and pg.get("live") is not False:      # 20 Nov: a page set up but not live yet is never started
            repos[pg["repo"]] = jobs(d, pg.get("jobs"))
    return {"note": "made by tools/make_timer.py - do not edit by hand", "repos": repos}


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    for r, j in data["repos"].items():
        print(r, len(j), "jobs:", ", ".join(x["file"] for x in j))
