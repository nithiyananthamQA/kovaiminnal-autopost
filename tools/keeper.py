"""keeper - owner 14 Nov: GitHub's own timer (cron) almost never starts our scheduled workflows (1 scheduled run in a whole day).

.github/workflows/keeper.yml runs this for about 5 h 40 min. Every minute it reads each workflow's OWN cron lines (the schedule:
block of its .yml - no other times). When a cron time has passed and that workflow has no run created since then, it starts the
workflow with `gh workflow run` and the inputs of a normal scheduled run (LIVE_INPUTS). Only switched-on (active) workflows are
started, so `gh workflow disable` still stops a job. A time more than LATE_MIN old is left (GitHub's own timer is rarely later).
At the end keeper.yml starts itself again; its own cron lines only restart the chain if it broke.

  python tools/keeper.py           the loop (KEEPER_MINUTES, default 340)
  python tools/keeper.py --once    one check
"""
import datetime as dt
import functools
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WF = ROOT / ".github" / "workflows"
SELF = "keeper.yml"
LATE_MIN = 60
STATES_MAX_AGE = 300      # seconds: switched on / off on GitHub is seen within 5 minutes
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
# the inputs of a normal scheduled (LIVE) run - the manual defaults of post.yml and rasipalan.yml are TEST runs.
# Same values as the bridge timer (apps_script/Code.gs KOVAI_JOBS) and the district bridge timer (make_bridge.py DISPATCH).
LIVE_INPUTS = {
    "post.yml": {"dry_run": "false", "prebuild": "false", "timer": "true"},      # timer: counts as scheduled (LIVE file, no check-log commit)
    "pick.yml": {"dry": "0", "resume": "0"},      # owner 16 Nov: news per round = pick.yml PICK_ROUND_TOP (the reference's 6 rounds)
    "powercut.yml": {"dry": "0"},
    "comments.yml": {"dry_run": "0"},
    "rasipalan.yml": {"dry": "0", "date": "", "repost": "0"},
    "insights.yml": {},
    "cloudclean.yml": {"keep_hours": "48", "dry": "false"},      # 17 Nov: the reference's clean-up (manual default = count only)
    "goldrate.yml": {"dry": "0", "date": ""},      # owner 17 Nov: the gold & silver rate reel, every morning
}


def log(*a):
    print(dt.datetime.now(IST).strftime("%H:%M:%S"), *a, flush=True)


def crons(text):
    return re.findall(r'^\s*-\s*cron:\s*["\']([^"\']+)["\']', text, re.M)


def scheduled():
    """{workflow file: [its cron lines]} for every workflow with a schedule, keeper itself left out"""
    out = {}
    for p in sorted(WF.glob("*.yml")):
        c = crons(p.read_text(encoding="utf-8"))
        if c and p.name != SELF:
            out[p.name] = c
    return out


def _field(spec, lo, hi):
    vals = set()
    for part in spec.split(","):
        rng, _, step = part.partition("/")
        if rng == "*":
            a, b = lo, hi
        elif "-" in rng:
            a, b = map(int, rng.split("-"))
        else:
            a = b = int(rng)
            if step:
                b = hi
        vals.update(range(a, b + 1, int(step or 1)))
    return vals


@functools.lru_cache(maxsize=None)
def _parse(cron):
    mi, h, dom, mon, dow = cron.split()
    days = _field(dow, 0, 7)
    if 7 in days:
        days.add(0)
    return _field(mi, 0, 59), _field(h, 0, 23), _field(dom, 1, 31), _field(mon, 1, 12), days, dom != "*", dow != "*"


def matches(cron, t):
    """does the cron line (UTC, GitHub's meaning) fire at minute t?"""
    mi, h, dom, mon, dow, dom_set, dow_set = _parse(cron)
    if t.minute not in mi or t.hour not in h or t.month not in mon:
        return False
    d_ok, w_ok = t.day in dom, t.isoweekday() % 7 in dow
    return (d_ok or w_ok) if (dom_set and dow_set) else (d_ok and w_ok)


def last_time(lines, now):
    """the latest cron time of these lines at or before now, not older than LATE_MIN -> (time, cron line) or None"""
    t = now.astimezone(dt.timezone.utc).replace(second=0, microsecond=0)
    for _ in range(LATE_MIN + 1):
        for c in lines:
            if matches(c, t):
                return t, c
        t -= dt.timedelta(minutes=1)
    return None


def inputs_for(wf, cron):
    return dict(LIVE_INPUTS[wf])


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=90)
    if r.returncode:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {(r.stderr or r.stdout).strip()[:300]}")
    return r.stdout


def states(run):
    data = json.loads(run("api", "repos/{owner}/{repo}/actions/workflows?per_page=100"))
    return {Path(w["path"]).name: w["state"] for w in data.get("workflows", [])}


def ran_since(run, wf, t):
    q = "%3E%3D" + t.strftime("%Y-%m-%dT%H:%M:%SZ")      # created >= t
    out = run("api", f"repos/{{owner}}/{{repo}}/actions/workflows/{wf}/runs?per_page=1&created={q}", "--jq", ".total_count")
    return int(out.strip() or 0) > 0


def check(now, done, cache, run=gh, jobs=None):
    """start every workflow whose cron time has come; done = {workflow: time already handled}. Returns the started workflows."""
    due = []
    for wf, lines in (jobs or scheduled()).items():
        hit = last_time(lines, now)
        if hit and done.get(wf) != hit[0]:
            due.append((wf, *hit))
    if not due:
        return []
    if not cache.get("at") or (now - cache["at"]).total_seconds() > STATES_MAX_AGE:
        cache["states"], cache["at"] = states(run), now
    started = []
    for wf, t, cron in due:
        if cache["states"].get(wf) != "active":
            continue      # switched off: not started (started late, within LATE_MIN, if switched on in time)
        if wf not in LIVE_INPUTS:
            log(f"{wf}: has a schedule but no keeper inputs (tools/keeper.py LIVE_INPUTS) - not started")
            done[wf] = t
            continue
        try:
            if ran_since(run, wf, t):
                done[wf] = t      # GitHub's own timer or another start already ran it
                continue
            args = ["workflow", "run", wf, "--ref", "main"]
            for k, v in inputs_for(wf, cron).items():
                args += ["-f", f"{k}={v}"]
            run(*args)
            done[wf] = t
            started.append(wf)
            log(f"started {wf} for {t.astimezone(IST):%H:%M} IST ({cron})")
        except Exception as e:      # tried again next minute
            log(f"{wf}: could not start - {str(e)[:300]}")
    return started


def main():
    done, cache = {}, {}
    log("keeper: " + "; ".join(f"{wf} {lines}" for wf, lines in scheduled().items()))
    if "--once" in sys.argv:
        check(dt.datetime.now(dt.timezone.utc), done, cache)
        return
    end = time.time() + 60 * int(os.environ.get("KEEPER_MINUTES", "340"))
    while time.time() < end:
        try:
            check(dt.datetime.now(dt.timezone.utc), done, cache)
        except Exception as e:
            log("check failed:", str(e)[:300])
        time.sleep(max(1, min(65 - time.time() % 60, end - time.time())))      # 5 s after the next full minute


if __name__ == "__main__":
    main()
