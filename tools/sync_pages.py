"""One push updates every page (owner 17 Nov: "like his setup - if he pushes, all pages follow"; the reference pushes the same change
to all 6 of its page repos in the same minute, e.g. 14 Nov 09:45 "pick: each round's news chosen by the page's insights").

Kovai Minnal is the master. Every other page repo (make_page.PAGE, cloned at ~/<repo name>) is rebuilt from it with
tools/make_page.py and gets ONLY the code: the page's live data - what it posted, picked, measured, its gold-rate and power-cut state,
LIVE / ENABLED / START_AT (PROTECT) - is never copied over or deleted. A page whose tests fail is put back and not pushed.

  python3 tools/sync_pages.py            every page whose folder exists
  python3 tools/sync_pages.py chennai    one page
  --no-push                              rebuild + test + commit only"""
import shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import make_page      # noqa: E402

# a page's own live data (written by its bots) - never taken from Kovai, never deleted
PROTECT = ["/.git/", "/LIVE", "/.last_check", "/.heartbeat", "/PROJECT_CONTEXT.md", "/out/",
           "/research_free/ENABLED", "/research_free/START_AT", "/research_free/archive/", "/research_free/results/",
           "/research_free/learned.json", "/research_free/reference_reach.json",
           "/poster/prebuilt/", "/poster/fb_posted/", "/poster/insights/", "/poster/probe/", "/poster/queue*",
           "/poster/story_shared.json", "/poster/comments_ignored.json", "/goldrate/state/", "/rasipalan/state/",
           "/apps_script/*.local.gs"]      # 19 Nov: the page's own filled Apps Script (Sheet / folder ids) - git-ignored, never deleted


def run(cmd, cwd, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, capture_output=True)


def only_jobs(key):
    """19 Nov: a power-cut-only page (make_page.PAGE[key]["jobs"]) keeps every other workflow OFF on GitHub - a workflow file that is
    new in Kovai arrives switched on, so this runs after every push (needs GH_TOKEN, as /tmp/push.sh sets)."""
    keep = [] if make_page.PAGE[key].get("live") is False else make_page.PAGE[key].get("jobs")      # 20 Nov: not live yet = every job off
    if keep is None:
        return
    repo = make_page.PAGE[key]["repo"]
    r = run(["gh", "workflow", "list", "--all", "-R", repo, "--json", "path,state"], ROOT, check=False)
    if r.returncode:
        print(f"{key}: workflows not read ({r.stderr.strip()[:120]}) - check them by hand")
        return
    import json
    for w in json.loads(r.stdout or "[]"):
        name = w["path"].rsplit("/", 1)[-1]
        if name not in keep and w["state"] == "active":
            ok = run(["gh", "workflow", "disable", name, "-R", repo], ROOT, check=False).returncode == 0
            print(f"{key}: {name} switched off" if ok else f"{key}: {name} could NOT be switched off")


def sync(key, push=True):
    d = Path.home() / make_page.PAGE[key]["repo"].split("/")[1]
    if not (d / ".git").is_dir():
        print(f"{key}: no clone at {d} - skipped")
        return True
    if run(["git", "status", "--porcelain"], d).stdout.strip():
        print(f"{key}: {d} has uncommitted changes - not touched")
        return False
    run(["git", "pull", "-q", "--no-rebase", "--no-edit", "origin", "main"], d)      # its bots' latest data first
    src = run(["git", "log", "-1", "--format=%h %s"], ROOT).stdout.strip()
    tmp = Path(tempfile.mkdtemp(prefix=f"page-{key}-"))
    try:
        run([sys.executable, str(ROOT / "tools" / "make_page.py"), key, str(tmp / "out")], ROOT)
        run(["rsync", "-a", "--delete"] + [f"--exclude={p}" for p in PROTECT] + [f"{tmp / 'out'}/", f"{d}/"], ROOT)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    t = run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"], d, check=False)
    if t.returncode:
        print(f"{key}: TESTS FAIL - nothing pushed, the page keeps its code:\n" + "\n".join(t.stderr.splitlines()[-15:]))
        run(["git", "reset", "-q", "--hard", "HEAD"], d)
        run(["git", "clean", "-qfd", "--", "."] + [f":(exclude){p.strip('/').rstrip('*')}" for p in PROTECT if p != "/.git/"], d)
        return False
    run(["git", "add", "-A"], d)
    if run(["git", "status", "--porcelain"], d).stdout.strip():
        run(["git", "commit", "-q", "-m", f"Same code as Kovai Minnal {src}"], d)
    else:
        print(f"{key}: already the same code as Kovai ({src[:9]})")
    ahead = run(["git", "rev-list", "--count", "origin/main..HEAD"], d).stdout.strip()
    if ahead in ("", "0"):      # 17 Nov: commits made earlier (e.g. --no-push) are pushed too, not only a new one
        return True
    if push:
        for _ in range(4):      # its bots commit often: take theirs and push again
            if run(["git", "push", "-q", "origin", "main"], d, check=False).returncode == 0:
                print(f"{key}: PUSHED - same code as Kovai ({src[:60]})")
                only_jobs(key)
                return True
            run(["git", "pull", "-q", "--no-rebase", "--no-edit", "origin", "main"], d)
        print(f"{key}: push failed - committed locally in {d}")
        return False
    print(f"{key}: committed in {d} (not pushed)")
    return True


def main(argv):
    push = "--no-push" not in argv
    keys = [a for a in argv if not a.startswith("--")] or list(make_page.PAGE)
    ok = all([sync(k, push) for k in keys])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
