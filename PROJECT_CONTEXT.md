# kovaiminnal-autopost - project context

Automatic Coimbatore-district news reels for the Instagram page **கோவை மின்னல்** (`@kovaiminnal`; hashtag `#KovaiMinnal`;
`post_to` value in the Sheet: `Kovai Minnal`), also shared to its Facebook Page. Copied on 11 Nov 2026 from the friend's working
project github.com/news360-tn/coimbatore360-autopost (page "Coimbatore 360") as it ran that day, with our name, images and accounts.
Internal page key stays `coimbatore` and the file structure / function names are unchanged, so upstream fixes can be ported by diff.
Everything runs on GitHub Actions; the Google Sheet (through the Apps Script bridge) is the working store.
Setup from zero: `docs/SETUP_KOVAI_MINNAL.md`. Brand images: `python3 tools/make_brand.py`.

**Status: not live** (no `LIVE` file, no `research_free/ENABLED`). See the owner setup checklist in `README.md`.

## How it works (end to end)

```
every 2 h    research_free.yml  collect news (newspaper sites incl. Dinamalar Coimbatore page, Google/Bing News, Coimbatore searches)
                                 -> open + check each article -> only Coimbatore-district news of today/yesterday
                                 -> queue by priority (research_free/archive/queue.json)
every 20 min write_stories.yml  write each queued news by priority (free LLM chain only) -> ONE AI image of the main scene
                                 (Cloudflare FLUX schnell -> NVIDIA FLUX -> paid FAL only if both fail) -> story saved in the Sheet
                                 -> starts posting at once
every 5 min  post.yml           checks (Coimbatore only, not stale, no duplicate, daily cap 50; posts at once) -> reel (reel/reel4.py,
                                 Valluvar voice) -> Instagram (one page, no collab)
daily        insights.yml       Instagram insights -> learned topic weights (writer priority)
```

## Rules the owner decided (keep them)

| Area | Rule |
|---|---|
| News scope | Only Coimbatore-district news, published today or yesterday (Coimbatore city, Pollachi, Mettupalayam, Sulur, Annur, Valparai, Kinathukadavu, Madukkarai, Perur, Thondamuthur, Anaimalai, Karamadai ...). Tiruppur, Nilgiris, Erode, Palakkad and every other district are not ours, even when close. "Avinashi Road" is a Coimbatore city road: a headline that also names a Coimbatore place is ours |
| One page | Only கோவை மின்னல். No second page, no collaborator, no Rasipuram routing |
| Priority | power cut (TNEB) > crime > accident > civic > the rest |
| Never miss news | Everything eligible is queued and written; duplicates and other-district news are skipped; nothing eligible is dropped |
| Daily cap | 50 reels a day (Instagram's limit) (`DAILY_CAP` in post.yml, also in the collector / writer); urgent news first |
| Posting time | No fixed times (owner 29 Oct): every reel posts the moment it is made (`poster/config.json` `prime_time.enabled: false`) |
| Format | Reel only (no carousel) |
| Voice | **Valluvar only** (free edge-tts `ta-IN-ValluvarNeural`). Google voices are never used, even if a Google key exists |
| Follow line | Spoken: மேலும் செய்திகளுக்கு கோவை மின்னல் பக்கத்தை பின்தொடருங்கள். Caption: கோயம்புத்தூர் செய்திகளைத் தவறவிடாமல் இருக்க Save செய்து Follow செய்யுங்கள் 📌 |
| Images | ONE new photo-realistic AI image per reel (main scene of THIS news, no text/logos); the reel uses different camera moves / crops of it. Free first: Cloudflare FLUX schnell -> NVIDIA FLUX; paid FAL `flux/schnell` -> `flux/dev` only as the last fallback. Picture check (free Gemini) as in Namakkal |
| Writing | Free LLM chain only; Claude backup OFF (`CLAUDE_MAX_CALLS=0`, no `ANTHROPIC_API_KEY`) |
| Reel language | Formal news Tamil, no slang; everyday Tamil Nadu words in voice, subtitles and cards (பஸ், டூவீலர், போலீசார், கலெக்டர் ...); dates always with the month |
| Website | Off for now (later). `poster/website.py` does nothing without `WEBSITE_INGEST_KEY`; workflows do not pass it |
| Separation | Own accounts and keys, so Namakkal's free API limits are never used; bridge e-mails tagged `KOVAIMINNAL` |
| Privacy | Personal project; bot commits as `kovaiminnal-bot`; no office account, office email or Claude lines in commits |

## Main files

| Path | What |
|---|---|
| `research_free/collect.py`, `allnews.py`, `sources.py` | collection, Coimbatore district checks, queue, writer, image |
| `research_free/rules.md`, `examples.json`, `names.py` | writing rules and spoken-word fixes |
| `poster/post.py` | posting checks, prime time, daily cap, Instagram publishing |
| `poster/freshness.py` | stale / duplicate / power-cut timing rules |
| `poster/config.json` | voice (Valluvar), prime time, design switches |
| `reel/reel4.py` | reel renderer (one image, camera moves, voice, opening, dates) |
| `apps_script/Code.gs` | Google Sheet bridge for the Kovai Minnal account (set the `..._HERE` values; redeploy after changes) |
| `tests/test_regressions.py` | regression tests (run before every push) |

## Sheet bridge (apps_script/Code.gs)

- Page key `coimbatore`, label `கோவை மின்னல்`, `post_to` `Kovai Minnal`, token property `IG_TOKEN_COIMBATORE` (refreshed weekly).
- Columns: same 31 as Namakkal; column 25 `spare_link` (unused), column 26 `coimbatore_link` (carousel link, unused while reel only),
  27 `reel_link`.
- GET actions: `queue`, `posted_rows`, `token`, `voice`, `recent`, `ping`, `autoPending`.
  POST actions: `posted`, `error`, `addStories`, `archiveNews`, `reoffer`, `setImages`, `repost`.
- E-mail subjects: `KOVAIMINNAL STORY`, `KOVAIMINNAL REEL`, `[KOVAIMINNAL IMAGES NEEDED]` ...

## Secrets (GitHub -> Settings -> Secrets -> Actions; values never in the repo)

BRIDGE_URL, BRIDGE_KEY, GEMINI_API_KEY, GROQ_API_KEY, NVIDIA_API_KEY, CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID,
CLOUDINARY_CLOUD, CLOUDINARY_PRESET; optional MISTRAL_API_KEY, OPENROUTER_API_KEY, GH_MODELS_TOKEN, FAL_KEY (paid image fallback).
Not used: ANTHROPIC_API_KEY, GOOGLE_TTS_API_KEY, WEBSITE_INGEST_KEY. Local copies live only in `.env` (git-ignored).

## Run and check

```
python3 -m unittest discover -s tests        # regression tests (also run by tests.yml on every code push)
python3 tools/repost.py RN-158               # (Actions: repost) post a reel again after it was removed from Instagram
```

## Recent changes
<!-- recent-changes:start (updated automatically by .github/workflows/context.yml - do not edit by hand) -->
| Date | Commit | Change |
|---|---|---|
| 2026-11-14 | `b991ee5` | district-powercut: 'post only' run (workflow input post_only=1) posts the stories already waiting in the Sheet now - no search, nothing new written |
| 2026-11-14 | `844f833` | Chennai posts 12 minutes apart like the reference (posting.spacing_min); power cuts / urgent news never wait; a job stops starting posts after 70 min (the rest waits for the next run) |
| 2026-11-14 | `7f98185` | District job timer in the bridge (GitHub's own timer never started it): startDistrictJob every 30 min 05:30-22:10 IST via GitHub API (token GH_DISPATCH_TOKEN); each news round runs once in its hour whoever starts the job |
| 2026-11-14 | `13b6440` | district-powercut: re-save so GitHub registers the schedule (0 scheduled runs since the push) |
| 2026-11-14 | `466bae4` | district powercut: chennai posted |
| 2026-11-14 | `5b8fcbe` | district powercut: notices found |
| 2026-11-14 | `ca9a8d4` | Chennai news: the first round posts too (the per-round cap stops a flood; same as the reference) |
| 2026-11-14 | `b06290e` | DIFFERENCES: round limit, same-job posting and config switch kept by the owner (14 Nov) |
| 2026-11-14 | `0a4c56d` | Tests: news tests never touch the Sheet (fast, offline) |
| 2026-11-14 | `25941ba` | News round limit (60 articles / 6 min, newest first) so the power-cut check in the same job is never held up; docs/DIFFERENCES.md lists every difference from the reference |
| 2026-11-14 | `f48d0f5` | Chennai news from every source like the reference (owner 14 Nov): Dinamalar district list + each outlet's district page (sources.json) + Google/Bing searches on all 7 outlets; each article checked with the reference check_article; same news from several papers merged (+points) |
| 2026-11-14 | `947b373` | Chennai news like the reference: 8 + 6 + 6 = 20 a day (06 / 10 / 19 h) |
| 2026-11-14 | `47e3728` | Like the reference (owner 14 Nov): district check every 30 min; Chennai news only in 3 rounds a day (06 / 10 / 19 h: 4 + 3 + 3 = 10), news up to 12 h old |
| 2026-11-14 | `931d1d1` | Test: writenews off-switch checked offline (never runs the real writer) |
| 2026-11-14 | `552d315` | Chennai news ON (owner approved the sample 14 Nov): news closing = follow line only (no send-to-friends); the 'முழு விவரம்' card no longer overlaps the yellow strip (district reels) |
| 2026-11-13 | `3042ece` | Chennai local news (owner 13 Nov): district pages can post their other local news too - reference points system picks the best new news, 1 per check, 10 a day, max 6 h old; first run only remembers (no flood); power cuts / obituaries / other districts left out; news preface + news follow lines; writenews step in the workflow. OFF (news_live empty) until the owner approves a sample. 355 tests pass |
| 2026-11-13 | `0dc15c6` | District reels: one common closing line for all non-power-cut news (power-cut closing unchanged) |
| 2026-11-13 | `9fd4bf1` | District reels: non-power-cut news ends with the news follow line + share line by type (one area -> that area's people; city-wide -> friends and family); power-cut reels unchanged |
| 2026-11-13 | `aa835a6` | Old-cut rule only when the cut day is written in the notice (a dateless notice is never blocked by the publish date) |
| 2026-11-13 | `a089434` | Never post a power cut whose day has passed (blocks the 13 Nov Chennai test row); district check every 15 min |
| 2026-11-13 | `10d7e55` | Chennai Minnal live: district power-cut pages switched on (live: chennai only) |
| 2026-11-13 | `15115fe` | District reel fixes: applied once only (a re-render never repeats the share line); follow line from districts.json |
| 2026-11-13 | `c912669` | District reels (owner 13 Nov, Chennai test): follow said once, share line for that area's people (voice + end card), full cut time on the band, real date instead of 'naalai marudhinam', one-word மின்தடை, short voice (max 6 sentences; caption has every area) |
| 2026-11-13 | `1a1d56e` | District switch: live list (pages go live one by one; chennai first) - still off until the owner approves a Chennai test reel |
| 2026-11-13 | `bb4b37f` | meta_fb_token.sh: accept a never-expiring system-user token as it is (no exchange) |
| 2026-11-13 | `54c4721` | Chennai Minnal Instagram account id (Business settings, portfolio Minnal Media) |
| 2026-11-13 | `63f8358` | District Unified login: a missing Instagram account id blocks only posting (finding and writing go on); 351 tests pass |
| 2026-11-13 | `465a919` | Instagram via Meta Unified login for district pages (app Minnal Pages): graph.facebook.com + the page's Instagram account id; Chennai marked unified (account id filled once its token exists); Kovai unchanged |
| 2026-11-13 | `4cfa995` | Chennai go-live steps: Instagram token from the old app Namenector Social (new Meta apps only get Unified login, which needs a business portfolio and graph.facebook.com); Facebook token from the new app Minnal Pages; steps 1-2 done |
| 2026-11-13 | `a2bfc88` | meta_fb_token.sh: use our own Meta app Minnal Pages (1448178013559937); secret asked once, kept only in ~/.config/minnal-pages |
<!-- recent-changes:end -->
