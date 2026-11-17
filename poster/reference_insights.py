"""owner 17 Nov (ours, not in the reference): "we need to consider his and ours - main is ours, in the meantime his one also helps us".

learned.json = THIS page's own measured numbers wherever they are enough; the reference page's live published insights fill the gaps
(news360-tn/coimbatore360-autopost research_free/learned.json - the same insights.py formula and topic list, 350 reels on 17 Nov):
  a news type's weight: ours once we have learned.TRUST_N reels of it, else his (when he has TRUST_N), else ours / his with fewer
                        reels (learned.reach_weight then uses learned.PATTERN, exactly as on his page)
  best hours / strong openings / average watch time: ours once insights.MIN_POSTS of our reels are measured, else his
A failed download keeps the last copy (poster/insights/reference_learned.json); with neither, learned.json is ours alone."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/news360-tn/coimbatore360-autopost/main/research_free/learned.json"
CACHE = os.path.join(HERE, "insights", "reference_learned.json")
SHARED = ("best_hours_ist", "top_openings", "avg_watch_s")


def fetch(get=None):
    """his learned.json now (saved as the last copy), or the last copy when the download fails, or {}"""
    try:
        if get is None:
            import requests
            get = lambda: requests.get(RAW, timeout=60)      # noqa: E731
        r = get()
        r.raise_for_status()
        d = r.json()
        if not (isinstance(d, dict) and d.get("topic_weight") and d.get("topic_n")):
            raise ValueError("no topic weights in it")
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print(f"reference insights read: {d.get('posts_measured')} reels, updated {d.get('updated')}")
        return d
    except Exception as e:
        print("reference insights not read (last copy kept):", str(e)[:150])
    try:
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def blend(ours, his, trust_n, min_posts):
    """learned.json from ours (main) + his (helper); 'topic_source' says whose number each news type uses"""
    out = dict(ours)
    if not his:
        return out
    ow, on = ours.get("topic_weight") or {}, ours.get("topic_n") or {}
    hw, hn = his.get("topic_weight") or {}, his.get("topic_n") or {}
    tw, tn, src = {}, dict(on), {}
    for t in sorted(set(ow) | set(hw)):
        if t in ow and on.get(t, 0) >= trust_n:
            tw[t], tn[t], src[t] = ow[t], on[t], "ours"
        elif t in hw and hn.get(t, 0) >= trust_n:
            tw[t], tn[t], src[t] = hw[t], hn[t], "reference"
        elif t in ow:
            tw[t], tn[t], src[t] = ow[t], on.get(t, 0), "ours"
        else:
            tw[t], tn[t], src[t] = hw[t], hn.get(t, 0), "reference"
    out["topic_weight"], out["topic_n"], out["topic_source"] = tw, tn, src
    enough = (ours.get("posts_measured") or 0) >= min_posts
    for k in SHARED:
        if not (enough and ours.get(k)) and his.get(k):
            out[k] = his[k]
    if tw:
        out["best_topics"] = sorted(tw, key=lambda k: -tw[k])[:3]
        out["weak_topics"] = sorted(tw, key=lambda k: tw[k])[:2]
    out["reference_posts_measured"], out["reference_updated"] = his.get("posts_measured"), his.get("updated")
    return out
