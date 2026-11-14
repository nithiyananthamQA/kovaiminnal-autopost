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
| 2026-11-14 | `634e481` | Kovai job timer in the bridge: startKovaiJobs every 5 min starts post / powercut / comments / pick / rasipalan / insights on their schedule times (GitHub's own timer almost never fires) |
| 2026-11-14 | `8bfc761` | District place tag: 'not' words (Thiruporur is not Porur), check ids on facebook.com/<id>; reach tests independent of the comments_live switch |
| 2026-11-14 | `60679bc` | district powercut: notices found |
| 2026-11-14 | `f660389` | District pages (Chennai first): Instagram place tag from districts/locations.json + comment-reply flow in district_powercut.yml |
| 2026-11-14 | `99fb684` | One shared minnal-bot token for every page (owner 14 Nov: same account for Chennai and Kovai) |
| 2026-11-14 | `3343ced` | Video length like the reference (owner 14 Nov): no 6-sentence limit and no 'short reel' writer rule for power cuts - every area read, up to ~90 s |
| 2026-11-14 | `dc79b5e` | PAGE_SETUP.md: the complete per-page checklist (Facebook page, Instagram account, portfolio + minnal-bot, tokens, switch-on, checks) as done for Chennai and Kovai; city_minnal username pattern; 5-account web limit; status table |
| 2026-11-14 | `c17c42c` | Kovai Minnal Instagram (@kovai_minnal, id 17841410844667843) on the Unified login - Kovai workflows stay off until the owner sets IG_TOKEN_COIMBATORE and switches Kovai on |
| 2026-11-14 | `0c754e8` | Ignore .claude/ (agent worktrees) |
| 2026-11-14 | `3917eee` | Kovai Unified switch: tests pass with the account id empty AND filled (Kovai-unchanged test pins its own config; the shipped-config test checks the import wiring, not the value), so the commit that fills the id keeps tests.yml green. meta_fb_token.sh shows the Instagram account id next to each page. SETUP step 9: reuse minnal-bot's token (never Revoke), the account id from meta_fb_token.sh, ig-probe only after the id is pushed. Audit: POCSO row made exact |
| 2026-11-14 | `7656c84` | docs/KOVAI_AUDIT.md: Kovai vs the reference (copied at 6c6ade2, checked at 4ed994f): differences on purpose, 15 gaps the reference has and Kovai lacks, which of its 21 code commits since the copy to port (and why), out-of-date docs, porting cautions, Instagram connection (Unified login) and the endpoint differences. SETUP step 9 + Meta app row: Unified login with Minnal Pages like Chennai; stray text on line 1 removed |
| 2026-11-14 | `e298717` | Kovai Instagram via Meta Unified login, switched by config only: poster/config.json instagram {api: unified, user_id: ""} (poster/ig_api.py) - empty id = Instagram login as before (graph.instagram.com + "me"); filled = graph.facebook.com/v24.0 + that account id, "me" never asked there. post.py (and everything using post.ig: comments, insights, ig_comments, ig_probe, story catch-up, collect) and rasipalan follow the same rule; a district on the Instagram login never inherits Kovai's setting. Bridge: system-user tokens (EAA...) are never refreshed (no weekly failure e-mail); comment reply / hide use graph.facebook.com for them. make_bridge.py: timer code as a raw string (Code.districts.gs had real line breaks inside JS strings - Apps Script would not save it). 368 tests pass |
| 2026-11-14 | `09efef1` | Chennai Minnal as a general Chennai news page (owner 14 Nov): Kovai-style scene logo/footer with Chennai landmarks, new name/bio/Facebook texts (power-cut closing unchanged); docs/PRIVACY.md for the Meta app's Live mode |
| 2026-11-14 | `684a116` | Brand images: Chennai scene (Chennai Central clock tower, Kapaleeshwarar gopuram, Marina lighthouse, sea) in the Kovai style - city='chennai' |
| 2026-11-14 | `9b16d9c` | Our own pictures only (owner 14 Nov, Instagram's rules: no copies, no third-party watermarks): config real_photo_enabled=false stops using the news site's photo |
| 2026-11-14 | `0813caa` | district powercut: chennai posted |
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
<!-- recent-changes:end -->
