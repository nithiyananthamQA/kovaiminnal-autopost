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
| 2026-11-22 | `825e366` | Never நாளை alone: the date goes with it in the voice, caption, headline and screen lines (owner 22 Nov, viewer comment) |
| 2026-11-22 | `c0b949c` | facebook RN-241 |
| 2026-11-22 | `e9c2606` | powercut: notices written |
| 2026-11-22 | `867d753` | pick: written and posted |
| 2026-11-22 | `22b9603` | powercut: notices written |
| 2026-11-22 | `3a816a2` | comments: normal comments recorded (not e-mailed) |
| 2026-11-22 | `bcaebb2` | powercut: notices written |
| 2026-11-22 | `bc1c15d` | facebook RN-240 |
| 2026-11-22 | `ac82c46` | pick: picked news saved |
| 2026-11-22 | `0ecc39a` | pick: picked news saved |
| 2026-11-22 | `213c841` | pick: list sent |
| 2026-11-22 | `a153598` | powercut: notices written |
| 2026-11-22 | `b379e56` | powercut: notices written |
| 2026-11-22 | `e47e6ad` | powercut: notices written |
| 2026-11-22 | `bdc7293` | pick: written and posted |
| 2026-11-22 | `6197dc4` | powercut: notices written |
| 2026-11-22 | `11c2205` | facebook RN-236 |
| 2026-11-22 | `5db23e3` | comments: normal comments recorded (not e-mailed) |
| 2026-11-22 | `34e5b72` | facebook RN-237 |
| 2026-11-22 | `51e0159` | facebook RN-234 |
| 2026-11-22 | `165e5ee` | facebook RN-233 |
| 2026-11-22 | `07211b7` | powercut: notices written |
| 2026-11-22 | `79f2c06` | facebook RN-235 |
| 2026-11-22 | `6c1262a` | goldrate posted |
| 2026-11-22 | `4dcb227` | pick: picked news saved |
| 2026-11-22 | `bf9afbc` | pick: picked news saved |
| 2026-11-22 | `78204d1` | pick: list sent |
| 2026-11-22 | `9600ab7` | pick: written and posted |
| 2026-11-22 | `d8ae504` | facebook RN-228 |
| 2026-11-22 | `9137c16` | facebook RN-231 |
<!-- recent-changes:end -->
