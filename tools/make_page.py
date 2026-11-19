"""make_page - owner 17 Nov: "for chennai i want the same like kovai minnal ... when we create new pages then follow it".

A new Minnal page = a COPY of this repo (Kovai Minnal) with only the district's words / values changed - the reference's way
(news360-tn runs Coimbatore, Tirupur, Salem, Erode, Karur, Trichy, Namakkal as copies of one code). Values come from
districts/districts.json (the page) + districts/locations.json (place ids) + the PAGE dict below (ids found with the bot token).

  python tools/make_page.py chennai ~/chennaiminnal-autopost        # writes the copy (the folder must not exist)

What changes (everything else is byte-identical to Kovai):
  - names / handle / hashtags / follow lines / Cloudinary folder / bot name / repo name  (districts/pipeline.swaps - the table
    the Chennai engine has used live since 13 Nov, + branding)
  - research_free/allnews.py district lists (places, other districts, searches) - the engine's own values
  - poster/config.json page values (Instagram account id, Facebook page id, hashtags, place ids); no district engine
  - files named after the page (kit/logo_<key>.png ...), the page's logo
  - state: none of Kovai's; the page's power-cut memory and Facebook record come from districts/state/<key>/;
    START_AT = now (older news never posts); NO LIVE / ENABLED file (switched on at the cutover)
Left out of a copy: the district engine (districts/, district_powercut.yml, Code.districts.gs, make_bridge.py), Kovai's state.
"""
import ast, json, re, shutil, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "districts"), str(ROOT / "research_free"), str(ROOT / "poster")]
IST = timezone(timedelta(hours=5, minutes=30))

# found with the minnal-bot token (me/accounts, 17 Nov): the page's Facebook page id; Instagram id is in districts.json
PAGE = {"chennai": {"fb_page_id": "1450975134763291", "repo": "nithiyananthamQA/chennaiminnal-autopost", "folder": "chennaiminnal",
                    "bot": "chennaiminnal-bot"}}

# owner 18 Nov ("chennai is the most populated city ... add even more small areas", suburbs: yes): the copy had only "சென்னை" as a
# place word, so the page could not tell a Chennai area story from a state story datelined Chennai, and every pin said "சென்னை".
# Chennai city + its small areas + the suburbs people call Chennai (Tambaram, Avadi, Pallavaram, Chromepet, Poonamallee ...).
# Names that are also towns elsewhere (திருமங்கலம், கே.கே.நகர், எம்.ஜி.ஆர். நகர், அசோக் நகர், பாடி, அக்கரை) are left out.
AREAS = {"chennai": {
    "ta": ["சென்னை", "மெட்ராஸ்", "எழும்பூர்", "சென்ட்ரல்", "பாரிமுனை", "பிராட்வே", "ஜார்ஜ் டவுன்", "மண்ணடி", "சவுகார்பேட்டை", "சௌகார்பேட்டை",
           "வேப்பேரி", "புரசைவாக்கம்", "கீழ்ப்பாக்கம்", "அயனாவரம்", "பெரம்பூர்", "ஓட்டேரி", "புளியந்தோப்பு", "வியாசர்பாடி", "கொடுங்கையூர்",
           "கொருக்குப்பேட்டை", "தண்டையார்பேட்டை", "வண்ணாரப்பேட்டை", "ராயபுரம்", "காசிமேடு", "திருவொற்றியூர்", "எண்ணூர்", "மணலி", "மாதவரம்",
           "புழல்", "செங்குன்றம்", "ரெட்ஹில்ஸ்", "மூலக்கடை", "கொளத்தூர்", "வில்லிவாக்கம்", "அண்ணா நகர்", "அமைந்தகரை", "அரும்பாக்கம்",
           "கோயம்பேடு", "முகப்பேர்", "அம்பத்தூர்", "அயப்பாக்கம்", "திருமுல்லைவாயல்", "ஆவடி", "பட்டாபிராம்", "திருநின்றவூர்", "பூந்தமல்லி",
           "பூவிருந்தவல்லி", "திருவேற்காடு", "மதுரவாயல்", "வளசரவாக்கம்", "போரூர்", "ராமாபுரம்", "நெற்குன்றம்", "விருகம்பாக்கம்", "சாலிகிராமம்",
           "வடபழனி", "கோடம்பாக்கம்", "மேற்கு மாம்பலம்", "மாம்பலம்", "தி.நகர்", "தி. நகர்", "தியாகராய நகர்", "சைதாப்பேட்டை", "நந்தனம்",
           "தேனாம்பேட்டை", "நுங்கம்பாக்கம்", "சூளைமேடு", "ஆயிரம் விளக்கு", "சேப்பாக்கம்", "திருவல்லிக்கேணி", "மயிலாப்பூர்", "மந்தைவெளி",
           "ராயப்பேட்டை", "ஆழ்வார்பேட்டை", "அடையாறு", "அடையார்", "பெசன்ட் நகர்", "சாந்தோம்", "பட்டினப்பாக்கம்", "கோட்டூர்புரம்", "கிண்டி",
           "ஈக்காட்டுத்தாங்கல்", "ஆலந்தூர்", "பரங்கிமலை", "நங்கநல்லூர்", "ஆதம்பாக்கம்", "மடிப்பாக்கம்", "வேளச்சேரி", "தரமணி", "திருவான்மியூர்",
           "கொட்டிவாக்கம்", "பாலவாக்கம்", "நீலாங்கரை", "ஈஞ்சம்பாக்கம்", "உத்தண்டி", "கானத்தூர்", "துரைப்பாக்கம்", "பெருங்குடி", "கந்தன்சாவடி",
           "சோழிங்கநல்லூர்", "செம்மஞ்சேரி", "நாவலூர்", "சிறுசேரி", "கேளம்பாக்கம்", "பள்ளிக்கரணை", "மேடவாக்கம்", "ஜல்லடியன்பேட்டை",
           "கோவிலம்பாக்கம்", "கீழ்க்கட்டளை", "மீனம்பாக்கம்", "பல்லாவரம்", "குரோம்பேட்டை", "தாம்பரம்", "சேலையூர்", "சிட்லபாக்கம்", "பம்மல்",
           "அனகாபுத்தூர்", "பொழிச்சலூர்", "பெருங்களத்தூர்", "வண்டலூர்", "ஊரப்பாக்கம்", "கூடுவாஞ்சேரி", "முடிச்சூர்", "குன்றத்தூர்", "மாங்காடு",
           "ஐயப்பன்தாங்கல்", "காட்டுப்பாக்கம்", "மெரினா", "கிழக்கு கடற்கரை சாலை", "ஓ.எம்.ஆர்", "அண்ணா சாலை", "ஜி.எஸ்.டி. சாலை", "மீஞ்சூர்",
           "நந்தம்பாக்கம்", "திருநீர்மலை", "நெசப்பாக்கம்"],
    # city services: a story about them is Chennai news even without an area name
    "services": ["சென்னை மாநகராட்சி", "மாநகராட்சி மேயர்", "மெட்ரோ ரயில்", "மெட்ரோ குடிநீர்", "சென்னை குடிநீர் வாரியம்", "மாநகர பேருந்து",
                 "எம்டிசி", "புறநகர் ரயில்", "மின்சார ரயில்", "சென்னை காவல்", "சென்னை போலீஸ்", "சென்னை விமான நிலைய", "சென்னை துறைமுக",
                 "சென்னை சூப்பர் கிங்ஸ்", "சேப்பாக்கம் மைதான"],
    "en": ["Chennai", "Madras", "Egmore", "Parrys", "Broadway", "George Town", "Mannady", "Sowcarpet", "Vepery", "Purasawalkam", "Kilpauk",
           "Ayanavaram", "Perambur", "Otteri", "Pulianthope", "Vyasarpadi", "Kodungaiyur", "Korukkupet", "Tondiarpet", "Washermanpet",
           "Royapuram", "Kasimedu", "Tiruvottiyur", "Thiruvottiyur", "Ennore", "Manali", "Madhavaram", "Puzhal", "Redhills", "Red Hills",
           "Kolathur", "Villivakkam", "Anna Nagar", "Aminjikarai", "Arumbakkam", "Koyambedu", "Mogappair", "Ambattur", "Ayapakkam",
           "Thirumullaivoyal", "Avadi", "Pattabiram", "Thiruninravur", "Poonamallee", "Thiruverkadu", "Maduravoyal", "Valasaravakkam",
           "Porur", "Ramapuram", "Nerkundram", "Virugambakkam", "Saligramam", "Vadapalani", "Kodambakkam", "West Mambalam", "T Nagar",
           "T. Nagar", "Saidapet", "Nandanam", "Teynampet", "Nungambakkam", "Choolaimedu", "Chepauk", "Triplicane", "Mylapore",
           "Mandaveli", "Royapettah", "Alwarpet", "Adyar", "Besant Nagar", "Santhome", "Pattinapakkam", "Kotturpuram", "Guindy",
           "Ekkaduthangal", "Alandur", "St Thomas Mount", "Nanganallur", "Adambakkam", "Madipakkam", "Velachery", "Taramani",
           "Thiruvanmiyur", "Kottivakkam", "Palavakkam", "Neelankarai", "Injambakkam", "Uthandi", "Kanathur", "Thoraipakkam",
           "Perungudi", "Kandanchavadi", "Sholinganallur", "Semmancheri", "Navalur", "Siruseri", "Kelambakkam", "Pallikaranai",
           "Medavakkam", "Kovilambakkam", "Keelkattalai", "Meenambakkam", "Pallavaram", "Chromepet", "Tambaram", "Selaiyur",
           "Chitlapakkam", "Pammal", "Anakaputhur", "Pozhichalur", "Perungalathur", "Vandalur", "Urapakkam", "Guduvanchery",
           "Mudichur", "Kundrathur", "Mangadu", "Iyyappanthangal", "Kattupakkam", "Marina", "Anna Salai", "Minjur", "Nandambakkam"],
    # municipal bodies / big suburbs: a power-cut notice filed under Chengalpattu / Tiruvallur passes with one of these in its title
    "section": ["சென்னை", "தாம்பரம்", "ஆவடி", "பல்லாவரம்", "குரோம்பேட்டை", "பூந்தமல்லி", "அம்பத்தூர்", "திருவொற்றியூர்", "மாதவரம்",
                "சோழிங்கநல்லூர்", "போரூர்", "வேளச்சேரி", "பெருங்களத்தூர்", "வண்டலூர்", "கூடுவாஞ்சேரி", "குன்றத்தூர்", "மாங்காடு", "செங்குன்றம்"],
    # state politics datelined Chennai is not Chennai news (21:00 list 17 Nov: TVK / Mekedatu / Thiruparankundram statements)
    "politics": ["தவெக", "திமுக", "அதிமுக", "பாஜக", "காங்கிரஸ்", "நாம் தமிழர்", "பாமக", "விசிக", "மதிமுக", "தேமுதிக", "சட்டப்பேரவை",
                 "தலைமைச் செயலக", "ஆளுநர்"],
}}

SKIP = re.compile(r"^(districts/|apps_script/Code\.districts\.gs$|\.github/workflows/district_powercut\.yml$|tests/test_district|"
                  r"tests/test_districts|tests/test_kovai_timer|tests/test_kovai_unified|research_free/archive/|research_free/results/|poster/insights/history\.json$|poster/fb_posted/|"
                  r"poster/prebuilt/|poster/queue|poster/story_shared\.json$|poster/comments_ignored\.json$|goldrate/state/posted_|"
                  r"rasipalan/state/|LIVE$|research_free/ENABLED$|\.last_check$|docs/(GO_LIVE_CHENNAI|KOVAI_AUDIT|SETUP_KOVAI_MINNAL)\.md$|"
                  r"brand/|tools/make_page\.py$|tools/make_brand\.py$|tools/meta_fb_token\.sh$|tools/sync_pages\.py$|tests/test_sync_pages\.py$|workers/|tools/make_timer\.py$|tests/test_timer_worker\.py$)")
TEXT = re.compile(r"\.(py|yml|yaml|json|md|gs|txt|sh|html|css|js|cfg|toml)$|^[A-Z_]+$|^\.gitignore$")
# tests of Kovai's own places / city-only rule / the district engine: the word swap makes them meaningless on another page
KOVAI_ONLY_TESTS = {"test_regressions.py": ["test_posting_gate_city_only", "test_towns_outside_the_city_skipped", "test_places",
                                            "test_town_topic_tamil", "test_other_district_not_posted", "test_five_focused_hashtags",
                                            "test_list", "test_different_towns_are_different_news", "test_city_story_wins_a_tie",
                                            "test_same_cut", "test_other_day_or_other_areas_are_new_news"],
                    "test_powercut.py": ["test_shared_place_name_is_not_enough"]}
KEEP_ASIS = {"goldrate/state/history.json", "research_free/sources.json",      # sources.json: swapped by the engine's own rule below
             "poster/insights/reference_learned.json"}      # the reference page's insights (his own words, never swapped)


PAGE_TEST = '''"""tools/make_page.py: this page's own values (a copy of Kovai Minnal with the district's words)"""
import re, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "research_free"), str(ROOT / "poster")]
import allnews, post, validate      # noqa: E402


class PageValues(unittest.TestCase):
    def test_names(self):
        self.assertEqual(post.PAGE, "{key}")
        self.assertEqual(post.TAG, "{tag}")
        self.assertEqual(validate.LAST, "மேலும் செய்திகளுக்கு {name_ta} பக்கத்தை பின்தொடருங்கள்.")
        self.assertEqual(post.FOLLOW_LINE, validate.LAST)

    def test_own_district_only(self):
        self.assertTrue(allnews.has_place("{ta}யில் பேருந்து விபத்து"))
        self.assertTrue(allnews.other_district("கோவையில் பேருந்து விபத்து"))
        self.assertTrue(allnews.other_district("செங்கல்பட்டு அருகே விபத்து") or "{key}" == "chengalpattu")

    def test_area_news_in_state_news_out(self):      # owner 18 Nov: Chennai's real headlines (17 Nov list + its best reels)
        if "{key}" != "chennai":
            return
        own = ["சென்னையில் நாளை மிக கனமழை: ஆரஞ்ச் அலர்ட்", "வடபழனியில் பிரியாணி கடையில் தீ விபத்து", "தாம்பரம் அருகே லாரி மோதி இருவர் பலி",
               "சென்னையில் 1,610 தெருவிளக்குகள் எரியவில்லை", "வேளச்சேரியில் குடிநீர் விநியோகம் நிறுத்தம்", "அரும்பாக்கத்தில் பெண்ணுக்கு தொல்லை",
               "எண்ணூரில் பறவை மோதி ஆளில்லா விமானம் நொறுங்கியது", "கொருக்குப்பேட்டையில் போதை மாத்திரை விற்ற மூவர் கைது",
               "திருவான்மியூரில் டிஜிட்டல் மோசடி விழிப்புணர்வு", "அம்பத்தூர் அருகே லாரி மோதி மாணவி பலி", "ஆவடியில் வீட்டில் திருட்டு",
               "கூடுவாஞ்சேரி அருகே தகராறில் ஒருவர் உயிரிழப்பு", "ஓய்வுபெற்றார் தோனி! சென்னை சூப்பர் கிங்ஸ் ஆலோசகராக நியமனம்!",
               "மெட்ரோ ரயில் சேவை நாளை மாற்றம்", "குரோம்பேட்டையில் நாளை மின்தடை"]
        for t in own:
            self.assertTrue(allnews.has_place(t), t)
            self.assertFalse(allnews.outside_district(t), t)
        state = ["“சமூக நீதி என்ற பெயரில் மத அரசியல் செய்கிறதா தவெக அரசு?” - நயினார் நாகேந்திரன்",
                 "மேகேதாட்டு விவகாரத்தில் தமிழக அரசு ஏன் இன்னும் அனைத்துக்கட்சி கூட்டத்தை கூட்டவில்லை",
                 "திருச்செந்தூர் சூரசம்ஹார விவகாரம்: எடப்பாடி பழனிசாமி கண்டனம்", "“ரீல்ஸ் மோகத்தில் அமைச்சர்கள் காவல் நிலையங்களில் ஆய்வு செய்வது தவறு”"]
        for t in state:
            self.assertTrue(allnews.statewide(t) or allnews.outside_district(t), t)
        self.assertTrue(allnews.other_district("செங்கல்பட்டு அருகே விபத்து"))      # the far town stays another district
        self.assertTrue(len(allnews.COIMBATORE_WORDS) > 150)
        import sys as _s
        _s.path.insert(0, str(ROOT / "poster"))
        import freshness as F      # 19 Nov: the same cut from a second paper; the city name alone never makes two cuts one
        a_h, a_s = "சென்னையில் நாளை மின்தடை", "நாளை (நவம்பர் 21) வேளச்சேரி, தரமணி, அடையாறு பகுதிகளில் மின்தடை."
        self.assertTrue(F.same_cut_areas(a_h, a_s, "2026-11-20", "சென்னை: நாளை மின்தடை", "நாளை (நவம்பர் 21) அடையாறு, வேளச்சேரி பகுதிகள்.", "2026-11-20"))
        self.assertFalse(F.same_cut_areas(a_h, a_s, "2026-11-20", "சென்னையில் நாளை மின்தடை", "நாளை (நவம்பர் 21) தாம்பரம், குரோம்பேட்டை பகுதிகளில் மின்தடை.", "2026-11-20"))

    def test_no_kovai_name_left_in_code(self):
        out = subprocess.run(["grep", "-rIlE", "Kovai Minnal|கோவை மின்னல்|kovai_minnal|KovaiMinnal|kovaiminnal", str(ROOT), "--include=*.py",
                              "--include=*.yml", "--include=*.json", "--exclude-dir=fb_posted", "--exclude-dir=.git", "--exclude-dir=tests"],
                             capture_output=True, text=True).stdout.split()
        self.assertEqual(out, [])


if __name__ == "__main__":
    unittest.main()
'''

# the page's own look for the picture prompt (collect.py BRIEF_SYSTEM "CITY LOOK") - Kovai's names Coimbatore landmarks
CITY_LOOK = {"chennai": (
    "CITY LOOK (Chennai city): Koyambedu (CMBT) and Broadway bus terminuses with MTC buses, Anna Salai (Mount Road) and Kathipara with flyovers\n"
    " and heavy traffic, T. Nagar and Purasaiwalkam shopping streets, Ripon Building (Greater Chennai Corporation), Chennai Central and Egmore\n"
    " stations, Metro Rail and MRTS lines, Marina beach and the Cooum / Adyar rivers, IT corridor (OMR) offices, the port and Royapuram,\n"
    " TNEB substations and transformers on concrete poles; two-wheelers, autorickshaws, MTC and private buses; men in shirts with veshti or\n"
    " trousers, women in sarees or salwar; Tamil Nadu police in khaki; corporation workers; TNEB linemen.\n")}


def page_values(key):
    import pipeline as PL
    d = PL.page(key)
    # owner 17 Nov "same like kovai minnal": Kovai's own closing lines with the page's name (never the old engine's news line)
    d = dict(d, follow_spoken=f"மேலும் செய்திகளுக்கு {d['name_ta']} பக்கத்தை பின்தொடருங்கள்.",
             follow_caption="உள்ளூர் செய்திகளுக்கு Follow செய்யுங்கள் 🙏", **PAGE[key])
    return d, PL


def branding(d):
    """Kovai Minnal's own names that districts/pipeline.swaps does not cover (handle, bot, repo, English capitals)"""
    return [("kovaiminnal-autopost", d["repo"].split("/")[1]), ("kovaiminnal-bot", d["bot"]), ("kovai_minnal", d["handle"]),
            ("KOVAI MINNAL", d["name_en"].upper()), ("KovaiMinnal", re.sub(r"[^A-Za-z0-9]", "", d["name_en"])),
            ("Kovai", d["en"]), ("kovai", d["key"]), ("KOVAI", d["en"].upper())]


REF_REPO = "news360-tn/coimbatore360-autopost"      # the reference's own repo name is never a word to swap (every page learns from it)


def swap_text(text, d, PL):
    text = text.replace(REF_REPO, "\x00REF\x00")
    for pat, rep in PL.swaps(d):
        text = re.sub(pat, lambda _m, r=rep: r, text)
    for a, b in branding(d):
        text = text.replace(a, b)
    return text.replace("\x00REF\x00", REF_REPO)


def set_assign(src, name, value):
    """replace the whole top-level assignment `name = ...` with `name = <value>`"""
    t = ast.parse(src)
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == name for x in n.targets):
            lines = src.splitlines(keepends=True)
            new = f"{name} = {value!r}      # {d_note}\n"
            return "".join(lines[:n.lineno - 1]) + new + "".join(lines[n.end_lineno:])
    raise SystemExit(f"allnews.py: {name} not found")


d_note = ""


def powercut_values(src):
    """17 Nov: covaimail.com is a Coimbatore paper - not a power-cut source (or the 'own district page') of any other page"""
    return src.replace(', "covaimail.com")', ")")


def allnews_values(src, d, PL):
    """the district lists, as the Chennai engine sets them (districts/pipeline.apply) - everything else in allnews.py stays Kovai's"""
    global d_note
    d_note = f"{d['name_en']}: tools/make_page.py"
    others = {k: x for k, x in PL.districts().items() if k != d["key"]}
    words = [d["ta"], d["en"]]
    vals = {
        "DISTRICT_SLUGS": (d["dinamalar"], d["key"]),
        "QUERIES": list(d["queries"]),
        "SITE_QUERIES": [d["ta"]],
        "COIMBATORE_WORDS": list(dict.fromkeys(words + (AREAS.get(d["key"], {}).get("ta") or []) + (AREAS.get(d["key"], {}).get("services") or [])
                                               + (AREAS.get(d["key"], {}).get("en") or []))),
        "TOWNS": [], "TOWN_ROADS": [], "CITY_ROADS": [], "NOT_PLACE": [],
        "CITY_AREAS": [w for w in (AREAS.get(d["key"], {}).get("ta") or []) if w != d["ta"]],
        "OTHER_PLACES": [x["ta"] for x in others.values()] + ["கோவை", "கோயம்புத்தூர்"],
        "OTHER_EN": sorted({w for x in others.values() for w in (x["en"].lower(), x["dinamalar"]) if w.isalpha()} | {"coimbatore", "kovai"}),
        "SECTION_NAMES": tuple(AREAS.get(d["key"], {}).get("section") or (d["ta"],)),
        "OWN_NAMES": tuple(dict.fromkeys([d["ta"]] + (["மெட்ராஸ்"] if d["key"] == "chennai" else []))),      # 19 Nov: never an "area"
        "SITES": {k: v for k, v in ast.literal_eval(ast.get_source_segment(src, next(
            n for n in ast.parse(src).body if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "SITES" for x in n.targets))).split("=", 1)[1]).items()
                  if "covaimail" not in v},      # Kovai Mail is a Coimbatore paper
    }
    pol = AREAS.get(d["key"], {}).get("politics") or []
    if pol:
        seg = next(n for n in ast.parse(src).body if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "STATE_NEWS" for x in n.targets))
        vals["STATE_NEWS"] = list(dict.fromkeys(ast.literal_eval(ast.get_source_segment(src, seg).split("=", 1)[1]) + pol))
    for k, v in vals.items():
        src = set_assign(src, k, v)
    for a, b in branding(d)[:5] + [("Kovai Minnal", d["name_en"]), ("கோவை மின்னல்", d["name_ta"])]:
        src = src.replace(a, b)      # names in comments / docstrings only - the lists of OTHER districts keep கோவை
    return src


def config_values(cfg, d, PL):
    cfg.pop("district_powercut", None)      # no district engine in a page copy
    cfg["instagram"] = {"api": "unified", "user_id": str(d["instagram"]["user_id"]), "shared_token_page": "chennai",
                        "note": f"{d['name_en']}: Meta Unified login, the one minnal-bot token (Minnal bridge / IG_SYSTEM_TOKEN)"}
    cfg["facebook"] = {"page_ids": {d["key"]: d["fb_page_id"]},
                       "note": f"{d['name_en']}: the Page token comes from the one minnal-bot token (no FB secrets)"}
    et = d["en_tag"]
    reach = cfg.get("reach") or {}
    reach.update({"hashtag_profiles": {d["tag"].lower(): {"page": d["tag"], "area": "#" + et, "news": f"#{et}News", "tamil": d["ta_tag"],
                                                          "fallback": f"#{et}News", "topic": {"power_cut": f"#{et}PowerCut", "weather": f"#{et}Rain"}}},
                  "place_tags": {}, "district_tag": "#" + et, "broad_tag": f"#{et}News"})
    cfg["reach"] = reach
    words, _ = PL.place_ids(d["key"], set())
    cfg["locations"] = words
    cfg["location_tags"] = bool(words)
    return cfg


def main(key, out):
    d, PL = page_values(key)
    out = Path(out).expanduser()
    if out.exists():
        raise SystemExit(f"{out} exists - give a new folder")
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    n = 0
    for f in files:
        if SKIP.search(f):
            continue
        src = ROOT / f
        if not src.is_file():
            continue
        dst = out / swap_text(f, d, PL)      # kit/logo_coimbatore.png -> kit/logo_chennai.png
        dst.parent.mkdir(parents=True, exist_ok=True)
        if f == "research_free/allnews.py":
            dst.write_text(allnews_values(src.read_text(encoding="utf-8"), d, PL), encoding="utf-8")
        elif f == "research_free/powercut.py":
            dst.write_text(powercut_values(swap_text(src.read_text(encoding="utf-8"), d, PL)), encoding="utf-8")
        elif f == "research_free/sources.json":      # the engine's rule: each outlet's district page with this district's name
            dst.write_text(src.read_text(encoding="utf-8").replace("coimbatore", d["dinamalar"]).replace("கோவை", d["ta"]), encoding="utf-8")
        elif f == "poster/config.json":
            cfg = json.loads(swap_text(src.read_text(encoding="utf-8"), d, PL))
            dst.write_text(json.dumps(config_values(cfg, d, PL), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif f == "research_free/collect.py":      # + the page's own city look in the picture prompt
            t = src.read_text(encoding="utf-8")
            a = t.index("CITY LOOK (Coimbatore city):")
            b = t.index("CATEGORY GUIDE:", a)
            dst.write_text(swap_text(t[:a] + CITY_LOOK[key] + t[b:], d, PL), encoding="utf-8")
        elif f == "research_free/pick.py":      # the page's search words once each (the swap turns Kovai's 4 town names into one name)
            t = swap_text(src.read_text(encoding="utf-8"), d, PL)
            t = re.sub(r"for q in \(([^)]*)\)", lambda m: "for q in (" + ", ".join(dict.fromkeys(x.strip() for x in m.group(1).split(",") if x.strip())) + ",)", t, count=1)
            dst.write_text(t, encoding="utf-8")
        elif f in KEEP_ASIS or not TEXT.search(Path(f).name):
            shutil.copy2(src, dst)
        else:
            try:
                dst.write_text(swap_text(src.read_text(encoding="utf-8"), d, PL), encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(src, dst)
        n += 1
    # Kovai-only tests are skipped on a copy (the page's own checks: tests/test_page_values.py)
    for tf, names in KOVAI_ONLY_TESTS.items():
        p = out / "tests" / tf
        t = p.read_text(encoding="utf-8")
        for nm in names:
            t, k = re.subn(rf"^(    def {nm}\(self)", r'    @unittest.skip("the Coimbatore page\'s own places (tools/make_page.py)")\n\1', t, count=1, flags=re.M)
            if not k:
                raise SystemExit(f"{tf}: {nm} not found")
        p.write_text(t, encoding="utf-8")
    # no district engine in a copy: keeper does not start it
    for f, pat in (("tools/keeper.py", r'^    "district_powercut\.yml": .*\n'),
                   ("tests/test_keeper.py", r'"district_powercut\.yml": 34,\s*|^        self\.assertEqual\(first\["district_powercut\.yml"\], "05:35"\)\n')):
        p = out / f
        p.write_text(re.sub(pat, "", p.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    (out / "tests" / "test_page_values.py").write_text(PAGE_TEST.format(**{k: d[k] for k in ("key", "ta", "name_ta", "handle", "tag")}),
                                                       encoding="utf-8")
    # the page's own logo (the reel and the gold-rate slides read kit/logo_<key>.png)
    shutil.copy2(d["logo"], out / "kit" / f"logo_{key}.png")
    # state: the page's own power-cut memory + Facebook record; news only from now on; switched OFF until the cutover
    st = ROOT / "districts" / "state" / key
    (out / "research_free" / "archive").mkdir(parents=True, exist_ok=True)
    if (st / "powercut_state.json").exists():
        shutil.copy2(st / "powercut_state.json", out / "research_free" / "archive" / "powercut_state.json")
    if (st / "fb_posted").is_dir():
        shutil.copytree(st / "fb_posted", out / "poster" / "fb_posted", dirs_exist_ok=True)
    for f in ("pick_state.json", "state.json", "last_run.json"):      # the same empty shapes Kovai started with (11 Nov)
        k = subprocess.run(["git", "show", f"f6bccc2:research_free/archive/{f}"], cwd=ROOT, capture_output=True, text=True)
        if k.returncode == 0:
            (out / "research_free" / "archive" / f).write_text(k.stdout, encoding="utf-8")
    (out / "research_free" / "archive" / "pick_state.json").write_text(      # 17 Nov: the shape pick.py works with (was {})
        json.dumps({"last_end": "", "pool": {}, "rounds": {}}) + "\n", encoding="utf-8")
    (out / "research_free" / "START_AT").write_text(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n", encoding="utf-8")      # UTC, like Kovai's
    for f in ("LIVE", "research_free/ENABLED"):
        (out / f).unlink(missing_ok=True)
    (out / "poster" / "insights").mkdir(parents=True, exist_ok=True)
    (out / "poster" / "insights" / "history.json").write_text("{}\n", encoding="utf-8")
    # a new page has no reels yet: its learned.json = the reference page's live insights alone (poster/reference_insights.py)
    sys.path.insert(0, str(ROOT / "poster"))
    import reference_insights
    his = reference_insights.fetch() if not (out / "poster" / "insights" / "reference_learned.json").exists() else \
        json.loads((out / "poster" / "insights" / "reference_learned.json").read_text(encoding="utf-8"))
    first = reference_insights.blend({"updated": datetime.now(timezone.utc).isoformat(timespec="minutes"), "posts_measured": 0}, his, 5, 12)
    (out / "research_free" / "learned.json").write_text(json.dumps(first, ensure_ascii=False, indent=1), encoding="utf-8")
    leftovers = subprocess.run(["grep", "-rIlE", r"Kovai Minnal|கோவை மின்னல்|kovai_minnal|KovaiMinnal|kovaiminnal", str(out),
                                "--exclude-dir=.git"], capture_output=True, text=True).stdout.split()
    print(f"{n} files -> {out}")
    print("left with a Kovai name (check):", [str(Path(x).relative_to(out)) for x in leftovers] or "none")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
