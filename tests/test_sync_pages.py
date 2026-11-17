"""owner 17 Nov ("like his setup - if he pushes, all pages follow"): tools/sync_pages.py gives every page Kovai's code and never touches
a page's own live data. Every file a workflow commits (its bots' data) must be in sync_pages.PROTECT, or one push would wipe it."""
import re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import sync_pages      # noqa: E402

# whole-folder adds that only ever carry protected files: flow_switch.yml (ENABLED / START_AT), powercut.yml's "$f" loop
# (archive / results), the district engine (Kovai only - not in page copies)
BROAD = {"research_free", "$f", "districts/state", "districts/state/$KEY"}


class Protect(unittest.TestCase):
    def test_every_file_a_bot_commits_is_protected(self):
        prot = [p.strip("/").rstrip("*") for p in sync_pages.PROTECT]
        missing = []
        for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
            for line in re.findall(r"git add ([^;&|\n]+)", wf.read_text(encoding="utf-8")):
                for a in line.split():
                    a = a.strip('"\'')
                    if a.startswith("-") or a in ("2>/dev/null", "||", "true") or a in BROAD or a.startswith("2>"):
                        continue
                    if not any(a == p or a.startswith(p.rstrip("/") + "/") or a.startswith(p) for p in prot):
                        missing.append(f"{wf.name}: {a}")
        self.assertEqual(missing, [])

    def test_code_is_never_protected(self):
        for p in sync_pages.PROTECT:
            self.assertFalse(p.endswith(".py") or p.startswith(("/poster/post", "/reel/", "/research_free/collect")), p)

    def test_page_copies_do_not_get_the_sync_tool(self):
        import make_page
        self.assertTrue(make_page.SKIP.match("tools/sync_pages.py"))
        self.assertTrue(make_page.SKIP.match("tests/test_sync_pages.py"))


if __name__ == "__main__":
    unittest.main()
