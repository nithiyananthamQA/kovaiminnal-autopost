"""reference f4547cce (22 Nov), ported 25 Nov: the other Tamil outlets are searched on Google only; when Google News is busy (503 - in
our pick logs most days) that outlet's search falls back to Bing instead of finding nothing."""
import sys, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research_free"))
import allnews      # noqa: E402
import pick      # noqa: E402


class BingBackup(unittest.TestCase):
    def test_google_busy_bing_finds_the_outlet_news(self):
        def from_google(q):
            raise RuntimeError("503 Server Error: Service Unavailable")

        def from_bing(q):
            dom = q.split("site:")[1]
            return [{"url": f"https://www.{dom}/news/x-{len(dom)}", "site": dom, "title": "செய்தி", "published": ""}]
        with mock.patch.object(allnews, "from_dinamalar_list", return_value=[]), mock.patch.object(allnews, "from_listing", return_value=[]), \
                mock.patch.object(allnews, "from_google", from_google), mock.patch.object(allnews, "from_bing", from_bing):
            log = []
            got = {u["url"].split("/")[2] for u in pick.candidates(log)}
        others = {f"www.{d}" for d in pick.OUTLETS if d not in ("dinamalar.com", "dinamani.com")}
        self.assertTrue(others <= got, others - got)      # every Google-only outlet still found through Bing
        self.assertTrue(any("from_google" in l and "failed" in l for l in log))


if __name__ == "__main__":
    unittest.main()
