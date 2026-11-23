"""owner 13 Nov: power cuts printed only in the daily STATE-WIDE lists (News18 / ABP Live / Samayam): only Coimbatore's part is written;
a list without one is refused; a notice filed under another district's page is refused."""
import datetime, json, sys, unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research_free"))
import allnews      # noqa: E402
import powercut     # noqa: E402

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
LIST_URL = "https://tamil.abplive.com/news/tamil-nadu/tamilnadu-power-shutdown-12-11-2026"
BODY = ("தமிழ்நாட்டில் நாளை காலை 9 மணி முதல் மாலை 5 மணி வரை பராமரிப்புப் பணிகள் காரணமாக மின் விநியோகம் நிறுத்தப்படும். "
        "வேலூர் மாவட்டம் காட்பாடி, சத்துவாச்சாரி. கோவை மாவட்டம் ஆலயபுரம், புதுநகர், காந்திபுரம். "
        "கரூர் மாவட்டம் பாலம்பாள்புரம், ஐந்து ரோடு.")


def page(title, body):
    ld = json.dumps({"@type": "NewsArticle", "headline": title, "datePublished": "2026-11-11T19:15:00+05:30", "articleBody": body}, ensure_ascii=False)
    return mock.Mock(text=f'<html><script type="application/ld+json">{ld}</script></html>')


class StateWideList(unittest.TestCase):
    def test_only_our_district_part(self):
        with mock.patch.object(allnews, "_get", return_value=page("தமிழகத்தில் நாளை (12-11-2026) மின் தடை", BODY)):
            a = allnews.article_any(LIST_URL + allnews.SECTION_MARK)
        self.assertEqual(a["title"], "கோவை மாவட்டத்தில் நாளை (12-11-2026) மின்தடை: ஆலயபுரம், புதுநகர், காந்திபுரம்")
        self.assertIn("காலை 9 மணி", a["text"])
        for other in ("வேலூர்", "காட்பாடி", "கரூர்", "பாலம்பாள்புரம்"):
            self.assertNotIn(other, a["text"] + a["title"], other)

    def test_list_without_our_district_gives_no_text(self):
        body = BODY.replace("கோவை மாவட்டம் ஆலயபுரம், புதுநகர், காந்திபுரம். ", "")
        with mock.patch.object(allnews, "_get", return_value=page("தமிழகத்தில் நாளை மின்தடை", body)):
            self.assertEqual(allnews.article_any(LIST_URL + allnews.SECTION_MARK)["text"], "")

    def test_state_lists_are_searched_and_marked(self):
        hit = {"url": LIST_URL, "title": "தமிழகத்தில் நாளை (12-11-2026) மின்தடை அறிவிப்பு", "site": "tamil.abplive.com", "published": ""}
        with mock.patch.object(allnews, "from_dinamalar_list", return_value=[]), mock.patch.object(allnews, "from_listing", return_value=[]), \
                mock.patch.object(allnews, "from_google", side_effect=lambda q: [hit] if "abplive" in q else []), \
                mock.patch.object(allnews, "from_bing", return_value=[]):
            got = [x["url"] for x in powercut.links()]
        self.assertIn(LIST_URL + allnews.SECTION_MARK, got)

    def test_other_district_page_refused(self):
        now = datetime.datetime(2026, 11, 10, 19, 0, tzinfo=IST)
        url = "https://www.dinamani.com/all-editions/edition-coimbatore/tiruppur/2026/Nov/12/x"
        art = {"title": "நாளைய மின் தடை", "text": "கோவை சாலை பகுதிகளில் காலை 9 மணி முதல் மின்தடை", "published": "2026-11-10T18:00:00+05:30"}
        with mock.patch.object(allnews, "article_any", return_value=dict(art, url=url)):
            got, why = powercut.check({"url": url, "title": art["title"]}, now.date(), now)
        self.assertIsNone(got)
        self.assertEqual(why, "other district")


class SamayamFormat(unittest.TestCase):
    def test_quoted_headings_and_two_parts_of_one_district(self):
        body = ('தமிழகத்தில் நாளை காலை 9 மணி முதல் பராமரிப்பு பணிகள் காரணமாக மின்தடை."கோவை/மெட்ரோ மின் தடை பகுதிகள்":- "இருகூர், ஒண்டிப்புதூர்",'
                '"கோவை /வடக்கு மின்வெட்டு பகுதிகள்":- "யமுனா நகர், கணுவாய்","திண்டுக்கல் மின்வெட்டு பகுதிகள்": - "நிலக்கோட்டை, சாணார்பட்டி"')
        with mock.patch.object(allnews, "_get", return_value=page("தமிழகத்தில் நாளை (13-11-2026) மின்தடை அறிவிப்பு", body)):
            a = allnews.article_any(LIST_URL + allnews.SECTION_MARK)
        for w in ("இருகூர்", "ஒண்டிப்புதூர்", "யமுனா நகர்", "கணுவாய்"):
            self.assertIn(w, a["text"], w)
        for w in ("திண்டுக்கல்", "நிலக்கோட்டை"):
            self.assertNotIn(w, a["text"] + a["title"], w)
        self.assertTrue(a["title"].startswith("கோவை மாவட்டத்தில் நாளை (13-11-2026) மின்தடை: இருகூர், ஒண்டிப்புதூர்"), a["title"])

    # 23 Nov (ours): Samayam prints the hours only in its synopsis (JSON-LD / og description), never in the article body - the reels
    # RN-83, RN-97, RN-241 (Kovai) and RN-2 (Salem) went out with no time. The synopsis now gives the hours when the body has none.
    SYN = "தமிழகம் முழுவதும் நாளை நவம்பர் 23-ந் தேதி திங்கட்கிழமை அன்று காலை 9 மணி முதல் மாலை 4 மணி வரை  மின்தடை ஏற்படும் பகுதிகள் குறித்த அறிவிப்பு வெளியாகியுள்ளது."
    NO_HOURS = ("தமிழகத்தில் நவம்பர் 23-ந் தேதி திங்கட்கிழமை அன்று துணை மின் நிலையங்களில் மின்வாரிய பராமரிப்பு பணிகள் காரணமாக மின்தடை செய்யப்படும் "
                "பகுதிகள் குறித்த முழு விவரங்களை இங்கு காணலாம்.கோவை மின் தடை பகுதிகள்:- அத்திகடவு திட்டம், ஹவுசிங் போர்டு, ஏஆர் நகர், "
                "சேலம் மின் தடை பகுதிகள்:- சுமங்கலி நகர், சந்தைப்பேட்டை")

    def samayam(self, body, desc):
        ld = json.dumps({"@type": "NewsArticle", "headline": "தமிழகத்தில் நாளை (23-11-2026) மின்தடை அறிவிப்பு!", "description": desc,
                         "datePublished": "2026-11-22T15:43:27+05:30", "articleBody": body}, ensure_ascii=False)
        with mock.patch.object(allnews, "_get", return_value=mock.Mock(text=f'<html><script type="application/ld+json">{ld}</script></html>')):
            return allnews.article_any(LIST_URL + allnews.SECTION_MARK)

    def test_hours_from_the_synopsis(self):
        a = self.samayam(self.NO_HOURS, self.SYN)
        self.assertIn("காலை 9 மணி முதல் மாலை 4 மணி வரை", a["text"])
        self.assertIn("அத்திகடவு திட்டம்", a["text"])
        self.assertNotIn("சுமங்கலி நகர்", a["text"])

    def test_hours_in_the_body_are_kept_alone(self):
        body = self.NO_HOURS.replace("அன்று துணை", "அன்று காலை 10 மணி முதல் மாலை 5 மணி வரை துணை")
        a = self.samayam(body, self.SYN)
        self.assertIn("காலை 10 மணி", a["text"])
        self.assertNotIn("மாலை 4 மணி", a["text"])

    def test_synopsis_of_another_district_not_used(self):
        a = self.samayam(self.NO_HOURS, "சேலம் மாவட்டத்தில் நாளை காலை 9 மணி முதல் மாலை 4 மணி வரை மின்தடை.")
        self.assertNotIn("மாலை 4 மணி", a["text"])
        self.assertIn("அத்திகடவு திட்டம்", a["text"])

    def test_article_gives_its_description(self):
        ld = json.dumps({"@type": "NewsArticle", "headline": "x", "description": self.SYN, "articleBody": "y" * 300}, ensure_ascii=False)
        with mock.patch.object(allnews, "_get", return_value=mock.Mock(text=f'<html><script type="application/ld+json">{ld}</script></html>')):
            self.assertEqual(allnews.article_any(LIST_URL)["description"], self.SYN)


if __name__ == "__main__":
    unittest.main()
