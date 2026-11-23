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


class SamayamHours(unittest.TestCase):
    """owner 23 Nov ("some video missed the timings ... at least try to get or post what we have"): Samayam's list prints no hours in
    its body - Kovai RN-83, RN-97, RN-241 and Salem RN-2 went out with no time. First the district papers' own notice of that day
    gives the hours of the same areas; else Samayam's one synopsis line for the whole state."""
    SYN = "தமிழகம் முழுவதும் நாளை நவம்பர் 23-ந் தேதி திங்கட்கிழமை அன்று காலை 9 மணி முதல் மாலை 4 மணி வரை  மின்தடை ஏற்படும் பகுதிகள் குறித்த அறிவிப்பு வெளியாகியுள்ளது."
    NO_HOURS = ("தமிழகத்தில் நவம்பர் 23-ந் தேதி திங்கட்கிழமை அன்று துணை மின் நிலையங்களில் மின்வாரிய பராமரிப்பு பணிகள் காரணமாக மின்தடை செய்யப்படும் "
                "பகுதிகள் குறித்த முழு விவரங்களை இங்கு காணலாம்.கோவை மின் தடை பகுதிகள்:- ஹவுசிங் யூனிட், ஏஆர் நகர், சுகுணா நகர், "
                "1.மடம்பட்டி 2.ஆலாந்துறை 3.குப்பனூர், சேலம் மின் தடை பகுதிகள்:- சுமங்கலி நகர், சந்தைப்பேட்டை")
    DINAMALAR = "https://www.dinamalar.com/news/tamil-nadu-district-news-coimbatore/tomorrow-barrier-coimbatore/4382311"
    DINAMANI = "https://www.dinamani.com/all-editions/edition-coimbatore/coimbatore/2026/Nov/22/power-outage-tomorrow-x"
    COVAIMAIL = "https://covaimail.com/power-shutdown-scheduled-to-take-place-in-coimbatore-on-23rd-of-november-2026"
    KAVUNDAMPALAYAM = ("கவுண்டம்பாளையம் துணை மின்நிலையம் காலை 10 முதல் மதியம் 3 மணி வரை. நல்லாம்பாளையம் மின் பாதை: ஹவுசிங் யூனிட், "
                       "ஏ.ஆர். நகர், தாமரை நகர், சுகுணா நகர், அசோக் நகர்.")

    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp()) / "powercut_state.json"
        self.notices = {}
        allnews._NOTICE_TEXT.clear()
        p = mock.patch.object(powercut, "STATE", self.tmp)
        p.start()
        self.addCleanup(p.stop)
        self.state([])

    def state(self, urls, day="2026-11-23"):
        self.tmp.write_text(json.dumps({"done": {powercut.pid(u): {"url": u, "cut_day": day} for u in urls}, "seen": {}}), encoding="utf-8")

    def samayam(self, body, desc):
        ld = json.dumps({"@type": "NewsArticle", "headline": "தமிழகத்தில் நாளை (23-11-2026) மின்தடை அறிவிப்பு!", "description": desc,
                         "datePublished": "2026-11-22T15:43:27+05:30", "articleBody": body}, ensure_ascii=False)
        pages = {LIST_URL: f'<html><script type="application/ld+json">{ld}</script></html>'}
        for u, t in self.notices.items():
            pages[u] = '<html><script type="application/ld+json">' + json.dumps({"@type": "NewsArticle", "headline": "மின்தடை", "articleBody": t}, ensure_ascii=False) + "</script></html>"
        with mock.patch.object(allnews, "_get", side_effect=lambda u, **k: mock.Mock(text=pages[u])), \
                mock.patch.object(allnews.dinamalar, "article", side_effect=lambda u: {"url": u, "title": "மின்தடை", "published": "", "text": self.notices[u]}):
            return allnews.article_any(LIST_URL + allnews.SECTION_MARK)

    def test_hours_from_the_district_paper(self):
        self.notices = {self.DINAMALAR: self.KAVUNDAMPALAYAM}
        self.state([self.DINAMALAR])
        a = self.samayam(self.NO_HOURS, self.SYN)
        self.assertIn("ஹவுசிங் யூனிட், ஏஆர் நகர், சுகுணா நகர் உள்ளிட்ட பகுதிகளில் காலை 10 முதல் மதியம் 3 மணி வரை மின்தடை (தினமலர் அறிவிப்பு)", a["text"])
        self.assertNotIn("மாலை 4 மணி", a["text"])      # Samayam's state-wide line is not used when a paper gives the hours
        self.assertNotIn("மடம்பட்டி உள்ளிட்ட", a["text"])      # areas no paper printed get no time

    def test_each_substation_its_own_hours(self):
        self.notices = {self.COVAIMAIL: "கவுண்டம்பாளையம் துணை மின் நிலையம் : காலை 10 மணி முதல் மதியம் 3 மணி வரை ஹவுசிங் யூனிட், ஏ.ஆர். நகர். "
                                        "மடம்பட்டி துணை மின் நிலையம் : காலை 9 மணி முதல் மதியம் 2 மணி வரை மடம்பட்டி, ஆலாந்துறை, குப்பனூர்."}
        self.state([self.COVAIMAIL])
        a = self.samayam(self.NO_HOURS, self.SYN)
        self.assertIn("ஹவுசிங் யூனிட், ஏஆர் நகர் உள்ளிட்ட பகுதிகளில் காலை 10 மணி முதல் மதியம் 3 மணி வரை மின்தடை (கோவை மெயில் அறிவிப்பு)", a["text"])
        self.assertIn("மடம்பட்டி, ஆலாந்துறை, குப்பனூர் உள்ளிட்ட பகுதிகளில் காலை 9 மணி முதல் மதியம் 2 மணி வரை", a["text"])

    def test_spellings_of_the_papers(self):
        # Dinamani / Covai Mail write ஆா் for ஆர் and சாலை for ரோடு; a name inside a longer one ('கே.கே. புதூர்') is not that place
        self.notices = {self.DINAMANI: "காலை 10 மணி முதல் பிற்பகல் 3 மணி வரை: ஹவுசிங் யூனிட் சாலை, சுகுணா நகா், கே.கே. புதூர் 6வது வீதி."}
        self.state([self.DINAMANI])
        a = self.samayam(self.NO_HOURS.replace("ஹவுசிங் யூனிட்", "ஹவுசிங் யூனிட் ரோடு").replace("3.குப்பனூர்", "3.புதூர்"), self.SYN)
        self.assertIn("ஹவுசிங் யூனிட் ரோடு, சுகுணா நகர் உள்ளிட்ட பகுதிகளில் காலை 10 மணி முதல் பிற்பகல் 3 மணி வரை", a["text"])
        self.assertNotIn("புதூர் உள்ளிட்ட", a["text"])

    def test_papers_in_the_power_cut_order(self):
        self.notices = {self.COVAIMAIL: "காலை 9 மணி முதல் மாலை 4 மணி வரை ஹவுசிங் யூனிட், ஏ.ஆர். நகர், சுகுணா நகர்.",
                        self.DINAMANI: "காலை 10 மணி முதல் பிற்பகல் 3 மணி வரை ஹவுசிங் யூனிட், ஏ.ஆர். நகர், சுகுணா நகர்."}
        self.state([self.COVAIMAIL, self.DINAMANI])
        a = self.samayam(self.NO_HOURS, self.SYN)
        self.assertIn("காலை 10 மணி முதல் பிற்பகல் 3 மணி வரை மின்தடை (தினமணி அறிவிப்பு)", a["text"])
        self.assertNotIn("கோவை மெயில்", a["text"])

    def test_one_shared_area_is_not_the_same_cut(self):
        self.notices = {self.DINAMALAR: "காலை 10 முதல் மதியம் 3 மணி வரை சுகுணா நகர், தாமரை நகர்."}
        self.state([self.DINAMALAR])
        a = self.samayam(self.NO_HOURS, self.SYN)
        self.assertNotIn("தினமலர்", a["text"])
        self.assertIn("காலை 9 மணி முதல் மாலை 4 மணி வரை", a["text"])      # nothing from the papers: Samayam's own line

    def test_another_day_is_not_used(self):
        self.notices = {self.DINAMALAR: self.KAVUNDAMPALAYAM}
        self.state([self.DINAMALAR], day="2026-11-24")
        self.assertNotIn("தினமலர்", self.samayam(self.NO_HOURS, self.SYN)["text"])

    def test_hours_from_the_synopsis(self):
        a = self.samayam(self.NO_HOURS, self.SYN)
        self.assertIn("காலை 9 மணி முதல் மாலை 4 மணி வரை", a["text"])
        self.assertIn("ஹவுசிங் யூனிட்", a["text"])
        self.assertNotIn("சுமங்கலி நகர்", a["text"])

    def test_hours_in_the_body_are_kept_alone(self):
        self.notices = {self.DINAMALAR: self.KAVUNDAMPALAYAM}
        self.state([self.DINAMALAR])
        body = self.NO_HOURS.replace("அன்று துணை", "அன்று காலை 10 மணி முதல் மாலை 5 மணி வரை துணை")
        a = self.samayam(body, self.SYN)
        self.assertIn("காலை 10 மணி", a["text"])
        self.assertNotIn("மாலை 4 மணி", a["text"])
        self.assertNotIn("தினமலர்", a["text"])

    def test_synopsis_of_another_district_not_used(self):
        a = self.samayam(self.NO_HOURS, "சேலம் மாவட்டத்தில் நாளை காலை 9 மணி முதல் மாலை 4 மணி வரை மின்தடை.")
        self.assertNotIn("மாலை 4 மணி", a["text"])
        self.assertIn("ஹவுசிங் யூனிட்", a["text"])

    def test_a_broken_lookup_never_stops_the_cut(self):
        self.state([self.DINAMALAR])
        with mock.patch.object(allnews, "_paper_hours", side_effect=RuntimeError("boom")):
            a = self.samayam(self.NO_HOURS, self.SYN)
        self.assertIn("ஹவுசிங் யூனிட்", a["text"])
        self.assertIn("காலை 9 மணி முதல் மாலை 4 மணி வரை", a["text"])

    def test_paper_that_cannot_be_opened(self):
        self.state([self.DINAMALAR])
        with mock.patch.object(allnews.dinamalar, "article", side_effect=RuntimeError("502")):
            ld = json.dumps({"@type": "NewsArticle", "headline": "தமிழகத்தில் நாளை (23-11-2026) மின்தடை", "description": self.SYN,
                             "articleBody": self.NO_HOURS}, ensure_ascii=False)
            with mock.patch.object(allnews, "_get", return_value=mock.Mock(text=f'<html><script type="application/ld+json">{ld}</script></html>')):
                a = allnews.article_any(LIST_URL + allnews.SECTION_MARK)
        self.assertIn("காலை 9 மணி முதல் மாலை 4 மணி வரை", a["text"])

    def test_article_gives_its_description(self):
        ld = json.dumps({"@type": "NewsArticle", "headline": "x", "description": self.SYN, "articleBody": "y" * 300}, ensure_ascii=False)
        with mock.patch.object(allnews, "_get", return_value=mock.Mock(text=f'<html><script type="application/ld+json">{ld}</script></html>')):
            self.assertEqual(allnews.article_any(LIST_URL)["description"], self.SYN)

if __name__ == "__main__":
    unittest.main()
