"""round_gate - a LATE GitHub schedule run never starts a second round (ours, owner 20 Nov: "chennai why 45 post").

The Cloudflare Worker (workers/timer) starts each pick round on time. GitHub's own schedule for the same round still fires, often
1-2 hours late (19-20 Nov: 22:13, 06:54, 09:36 IST on Kovai and Chennai), and that late run collected and posted a SECOND round -
9 rounds a day instead of 6, 31 news reels + 14 stories on Chennai in 24 h, then Instagram's 24-hour limit held the next round.

A schedule run asks GitHub: did a workflow_dispatch run of this workflow (the Worker's, or the owner's) start at or after this cron's
time and was not cancelled? Yes = this run stops (the round already ran). No = the Worker missed it, so GitHub's run IS the round.
Any error = the round runs (a round is never lost because of this check).

  CRON="30 22 * * *" WF=pick.yml python3 poster/round_gate.py      (in the workflow: writes go=1 / go=0 to $GITHUB_OUTPUT)"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

EARLY_MIN = 2      # a Worker run started up to 2 minutes before the cron time still counts as this round


def fire_time(cron, now):
    """the latest time <= now (UTC) at which this cron ("M H * * *", H may be a list like "23,3") was due; None = not a daily cron"""
    try:
        m, h = cron.split()[:2]
        best = None
        for hh in h.split(","):
            for back in (0, 1):
                t = (now - timedelta(days=back)).replace(hour=int(hh), minute=int(m), second=0, microsecond=0)
                if t <= now and (best is None or t > best):
                    best = t
        return best
    except Exception:
        return None


def decide(cron, now, runs, self_id=0):
    """'go' or 'skip'. runs = GitHub workflow runs [{id, event, conclusion, created_at}]"""
    t = fire_time(cron, now)
    if t is None:
        return "go"
    since = t - timedelta(minutes=EARLY_MIN)
    for r in runs:
        if r.get("id") == self_id or r.get("event") != "workflow_dispatch" or r.get("conclusion") == "cancelled":
            continue
        try:
            created = datetime.fromisoformat(str(r.get("created_at", "")).replace("Z", "+00:00"))
        except ValueError:
            continue
        if created >= since:
            return "skip"
    return "go"


def runs_since(repo, wf, since, token):
    url = (f"{os.environ.get('GITHUB_API_URL', 'https://api.github.com')}/repos/{repo}/actions/workflows/{wf}/runs"
           f"?event=workflow_dispatch&per_page=30&created=%3E%3D{since:%Y-%m-%dT%H:%M:%SZ}")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("workflow_runs", [])


def main():
    out, cron = "go", os.environ.get("CRON", "").strip()
    if os.environ.get("GITHUB_EVENT_NAME") == "schedule" and cron:
        try:
            now = datetime.now(timezone.utc)
            t = fire_time(cron, now)
            if t is not None:
                runs = runs_since(os.environ["GITHUB_REPOSITORY"], os.environ.get("WF", "pick.yml"), t - timedelta(minutes=EARLY_MIN),
                                  os.environ["GH_TOKEN"])
                out = decide(cron, now, runs, int(os.environ.get("GITHUB_RUN_ID", "0") or 0))
                print(f"round gate: cron '{cron}' was due {t:%H:%M} UTC; {len(runs)} started run(s) since ->",
                      "SKIP - the timer already ran this round" if out == "skip" else "this run is the round")
        except Exception as e:
            out = "go"
            print("round gate: not checked -", str(e)[:150], "- the round runs")
    else:
        print("round gate: not a schedule run - the round runs")
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"go={0 if out == 'skip' else 1}\n")


if __name__ == "__main__":
    main()
