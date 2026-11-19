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
| 2026-11-19 | `f4b6cab` | pages: Salem ids (salem-bot token, own Meta app Salem Pages) + insights job (owner 19 Nov: "add insight also") |
| 2026-11-19 | `b12856f` | pages: Salem Minnal = power cuts only, its own Apps Script + Meta app, the reference's own Salem lists (owner 19 Nov) |
| 2026-11-19 | `18cc826` | powercut: notices written |
| 2026-11-19 | `fa2b0a0` | powercut: notices written |
| 2026-11-19 | `5acd4ca` | pick: written and posted |
| 2026-11-19 | `de5ee94` | facebook RN-146 |
| 2026-11-19 | `8142d02` | pick: picked news saved |
| 2026-11-19 | `d1a7b13` | pick: picked news saved |
| 2026-11-19 | `3ab19f2` | pick: list sent |
| 2026-11-19 | `7ff01c8` | powercut: notices written |
| 2026-11-19 | `9bb09c0` | comments: normal comments recorded (not e-mailed) |
| 2026-11-19 | `31513de` | voice: free Anbu reads every reel, ElevenLabs off and its key removed (owner 19 Nov: no cost for voice) |
| 2026-11-19 | `7f4dd93` | powercut: notices written |
| 2026-11-19 | `a73d9f9` | powercut: notices written |
| 2026-11-19 | `556449d` | comments: normal comments recorded (not e-mailed) |
| 2026-11-19 | `e611032` | facebook RN-145 |
| 2026-11-19 | `f1ffc99` | pick: written and posted |
| 2026-11-19 | `4b95ea7` | powercut: notices written |
| 2026-11-19 | `a5a00c4` | facebook RN-143 |
| 2026-11-19 | `b7cad9d` | Worker schedule without rasipalan |
| 2026-11-19 | `0a18c57` | No rasipalan post (owner 19 Nov: 'that rasipalan news we dont need') |
| 2026-11-19 | `19b5830` | Same-cut check: the page's own city name never makes two power cuts one (Chennai: 'சென்னை' is in every notice) |
| 2026-11-19 | `6dcd00c` | The same power cut from a second paper is a duplicate: same cut day + the same areas in the script (owner 19 Nov: 'we need to block like this') |
| 2026-11-19 | `05262af` | facebook RN-144 |
| 2026-11-19 | `1d4f617` | powercut: notices written |
| 2026-11-19 | `bbcf95e` | pick: picked news saved |
| 2026-11-19 | `3e0c967` | pick: picked news saved |
| 2026-11-19 | `460001c` | pick: list sent |
| 2026-11-19 | `33f6322` | powercut: notices written |
| 2026-11-19 | `9f6335d` | The right day: never 'நாளை' about a day that came; power cuts only before their day, first in the queue; party names spoken letter by letter (owner 19 Nov) |
<!-- recent-changes:end -->
