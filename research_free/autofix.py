"""Reference port (news360-tn 84417aa27 + da6a5e5b8, 24 Nov: "post immediately all the news - daily some problem found"): a news HELD by
the writer's fact-check (a detail that is not in the article: a wrong age / name, an invented date ...) is written again from its source
article. The writer is told the exact problems of the first version; the new draft goes through the same writer checks
(collect.file_story) and the same posting hold rules (poster/post.py news_hold + the usual skip checks).
Only a draft with NO problem left is saved to poster/fixed/<story>.json - the posting job then posts that corrected text
(poster/post.py apply_fixes). Today's and yesterday's news only, at most 2 tries per news (busy AI writers do not use up a try),
AUTOFIX_MAX news per run.
Ours (owner 25 Nov): runs inside the pick round right after the round's own writing (no extra 30-minute workflow - GitHub safe mode),
with the same writers as the round (free models first, Claude Haiku as backup). AUTOFIX_DRY=1 = nothing saved. Never prints a key."""
import datetime
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "poster"))
import allnews      # noqa: E402
import collect      # noqa: E402
import freshness      # noqa: E402
import post      # noqa: E402
import run      # noqa: E402

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
FIX = ROOT / "poster" / "fixed"
TRIES = FIX / "_tries.json"
MAX_TRIES = 2
MAX_PER_RUN = int(os.environ.get("AUTOFIX_MAX", "6") or 6)
DRY = os.environ.get("AUTOFIX_DRY", "") == "1"
BUSY = re.compile(r"all free models failed|no free model answered|free models unavailable|^failed: ")


def log(*a):
    print(datetime.datetime.now(IST).strftime("%H:%M:%S"), *a, flush=True)


def problems_of(row):
    v = str(row.get("verification") or "")
    return v.split("problems:", 1)[1].strip() if "problems:" in v else v


def candidates(rows, now):
    today = now.date()
    out = []
    for row in rows:
        sid = row.get("story_id") or ""
        if not sid or (FIX / f"{sid}.json").exists() or not str(row.get("source") or "").startswith("http"):
            continue
        if (row.get("review") or "").strip().lower() == "hold":      # the owner's own Hold is never undone
            continue
        if all(post.page_done(row, p) for p in post.pages_of(row)):
            continue
        why = post.news_hold(row) or ""
        if not why.startswith("held: fact-check problems"):
            continue
        nd = freshness.news_date(row.get("published"), row.get("source"), None)
        if not nd or (today - nd).days > 1:      # today's and yesterday's news only (the posting rule)
            continue
        base = post._skip_reason_base(row)      # ours: stale / duplicate / other district would not post even when fixed - no rewrite paid for
        if base and not base.startswith("known issue"):
            continue
        out.append(row)
    return out


def rewrite(row, now):
    art = allnews.article_any(row["source"])
    art = art if isinstance(art, dict) else {"title": "", "text": str(art)}
    if len(art.get("text") or "") < 200:
        return None, "article text not available"
    art.setdefault("published", row.get("published", ""))
    art["url"] = row["source"]
    run.EXTRA[0] = ("IMPORTANT: this news was written once before and the fact-check found these mistakes - do NOT repeat them; leave out "
                    "anything the article does not say (no invented date, age, name, time or place); copy every place name, number and "
                    "amount exactly as the article writes it. The pictures already exist: keep the two scenes short. Mistakes found: "
                    + problems_of(row)[:1500])
    try:
        res = run.write(art, now.strftime("%A %d %B %Y"))
    except Exception as e:
        res = e
    finally:
        run.EXTRA[0] = ""
    story, why = collect.file_story(art, res, [], [], scenes=["(the existing picture is kept)"])
    if not story:
        return None, why
    spec = story.get("slides_spec")
    fixed = {"headline_ta": story["tamil_headline"], "headline_en": story["english_headline"], "caption": story["caption"],
             "reel_script": story["reel_script"], "location": story.get("location") or row.get("location"),
             "slides_spec": json.dumps(spec, ensure_ascii=False) if isinstance(spec, dict) else spec,
             "verification": story.get("verification") or ""}
    new = dict(row, **fixed)
    still = post.news_hold(new) or post._skip_reason_base(new)
    if still:
        return None, "still held: " + still[:200]
    return fixed, ""


def main(now=None):
    now = now or datetime.datetime.now(IST)
    try:
        tries = json.loads(TRIES.read_text(encoding="utf-8"))
    except Exception:
        tries = {}
    try:
        rows = post.bridge_get("queue")["rows"]
    except Exception as e:
        log("queue not readable - nothing fixed this run:", str(e)[:150])
        return
    post.ALL_ROWS = rows      # the duplicate checks of _skip_reason_base compare with the other stories
    todo = [r for r in candidates(rows, now) if int(tries.get(r["story_id"], 0)) < MAX_TRIES][:MAX_PER_RUN]
    log(f"{len(todo)} held news to fix:", [r["story_id"] for r in todo])
    for row in todo:
        sid = row["story_id"]
        tries[sid] = int(tries.get(sid, 0)) + 1
        try:
            fixed, why = rewrite(row, now)
        except Exception as e:
            fixed, why = None, f"failed: {str(e)[:150]}"
        if not fixed:
            if BUSY.search(why or ""):      # reference 24 Nov: busy AI writers are not the news's fault
                tries[sid] -= 1
                log(sid, "NOT fixed - the AI writers are busy; tried again in a later run (this try is not counted):", (why or "")[:160])
                break      # the writers are busy for the other news too - stop this run
            log(sid, "NOT fixed (try", tries[sid], "of", MAX_TRIES, "):", why)
            continue
        fixed.update(source=row["source"], story_id=sid, fixed_at=now.isoformat(timespec="seconds"), old_problems=problems_of(row)[:600])
        fixed["verification"] = "AUTO-FIXED (owner 25 Nov) - " + fixed["verification"]
        if DRY:
            log(sid, "FIXED (dry run - not saved):", fixed["headline_ta"][:80])
            continue
        FIX.mkdir(parents=True, exist_ok=True)
        (FIX / f"{sid}.json").write_text(json.dumps(fixed, ensure_ascii=False, indent=1), encoding="utf-8")
        log(sid, "FIXED - posts with the corrected text:", fixed["headline_ta"][:80])
    if DRY:
        return
    cut = (now - datetime.timedelta(days=3)).isoformat()
    for f in FIX.glob("*.json"):      # corrected texts older than 3 days are not needed any more
        if f.name == TRIES.name:
            continue
        try:
            if json.loads(f.read_text(encoding="utf-8")).get("fixed_at", "") < cut:
                f.unlink()
        except Exception:
            pass
    live = {r.get("story_id") for r in rows}
    tries = {k: v for k, v in tries.items() if k in live}      # a story gone from the queue needs no count
    FIX.mkdir(parents=True, exist_ok=True)
    TRIES.write_text(json.dumps(tries, indent=1), encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:      # owner: nothing here may stop a round
        log("autofix stopped (posting goes on):", str(e)[:200])
