"""ref_lists - a new page takes the reference's OWN district values (owner 17 Nov "follow his same all"; 19 Nov Salem).

The reference (news360-tn) runs one repo per district, each a copy of coimbatore360-autopost with only the district's values changed.
For a district he runs (salem, tirupur, erode, karur, trichy, namakkal) those values are taken from HIS repo - never typed from
memory: every top-level value of research_free/allnews.py and research_free/powercut.py that differs between his Coimbatore copy and his
district copy, + the CITY LOOK paragraph of the picture prompt (research_free/collect.py). Saved in districts/ref_lists/<key>.json,
used by tools/make_page.py. His district word list SALEM_WORDS is our COIMBATORE_WORDS (our code keeps one name for every page).

  python3 tools/ref_lists.py salem news360-tn/salem360-autopost"""
import ast, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "districts" / "ref_lists"
REF_HOME = "news360-tn/coimbatore360-autopost"


def segments(src):
    out = {}
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = ast.get_source_segment(src, n.value)
    return out


def city_look(src):
    a = re.search(r"^CITY LOOK", src, re.M).start()      # the paragraph itself (not "see CITY LOOK" in the rules above it)
    return src[a:src.index("CATEGORY GUIDE:", a)]


def extract(home, page, key):
    words = f"{key.upper()}_WORDS"
    out = {"from": "", "allnews": {}, "powercut": {}, "city_look": city_look((page / "research_free/collect.py").read_text(encoding="utf-8"))}
    for f, part in (("research_free/allnews.py", "allnews"), ("research_free/powercut.py", "powercut")):
        a = segments((home / f).read_text(encoding="utf-8"))
        b = segments((page / f).read_text(encoding="utf-8"))
        for name, seg in b.items():
            if a.get(name) == seg or name in ("HERE", "UA", "IST", "AREA"):
                continue
            mine = "COIMBATORE_WORDS" if name == words else name
            out[part][mine] = seg.replace(words, "COIMBATORE_WORDS")
    return out


def main(key, repo):
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        for r, d in ((REF_HOME, t / "home"), (repo, t / "page")):
            subprocess.run(["git", "clone", "-q", "--depth", "1", f"https://github.com/{r}", str(d)], check=True)
        data = extract(t / "home", t / "page", key)
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=t / "page", capture_output=True, text=True).stdout.strip()
    data["from"] = f"{repo} {sha}"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{key}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{key}: {len(data['allnews'])} allnews + {len(data['powercut'])} powercut values from {data['from']}:",
          ", ".join(list(data["allnews"]) + list(data["powercut"])))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
