"""owner 16 Nov ("give importance to his better concepts and modify ours once a day - over the long term the setup must have the
maturity to decide what reels to create"): every night the reference page's own published insights (news360-tn/coimbatore360-autopost,
public repo: poster/insights/history.json = views of every reel + its topic, research_free/learned.json) are read and summed up per
news type into research_free/reference_reach.json. learned.py blends it with this page's own reels (reach_map / skip_topics /
reach_weight). A failed download keeps yesterday's file - nothing else changes."""
import datetime, json, pathlib, statistics, sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "reference_reach.json"
RAW = "https://raw.githubusercontent.com/news360-tn/coimbatore360-autopost/main/"
KEEP = ("topic_weight", "topic_n", "best_topics", "weak_topics", "avg_watch_s", "best_hours_ist")


def topic_ratios(history, page=None):
    """{topic: {"n": reels, "ratio": topic median views / the page's median views}}, page median - reels without views are left out"""
    by, allv = {}, []
    for v in (history or {}).values():
        views = v.get("views") or 0
        if views <= 0 or (page and v.get("page") != page):
            continue
        by.setdefault(v.get("topic") or "other", []).append(views)
        allv.append(views)
    if not allv:
        return {}, 0
    med = statistics.median(allv)
    return {t: {"n": len(x), "ratio": round(statistics.median(x) / med, 3)} for t, x in by.items()}, med


def build(history, learned):
    topics, med = topic_ratios(history)
    out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"), "source": RAW,
           "reels": sum(t["n"] for t in topics.values()), "median_views": med, "topics": topics}
    out.update({k: learned[k] for k in KEEP if k in (learned or {})})
    return out


def main(get=None):
    if get is None:
        import requests
        get = lambda path: requests.get(RAW + path, timeout=60)
    try:
        h, l = get("poster/insights/history.json"), get("research_free/learned.json")
        h.raise_for_status(); l.raise_for_status()
        data = build(h.json(), l.json())
    except Exception as e:
        print("reference insights not read (yesterday's kept):", str(e)[:160])
        return 0
    if data["reels"] < 20:
        print("reference insights too few reels - yesterday's kept:", data["reels"])
        return 0
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"reference insights: {data['reels']} reels, median {data['median_views']:.0f} views")
    for t, x in sorted(data["topics"].items(), key=lambda kv: -kv[1]["ratio"]):
        print(f"  {t:15} {x['n']:3} reels  {x['ratio']:.2f}x the median")
    return 0


if __name__ == "__main__":
    sys.exit(main())
