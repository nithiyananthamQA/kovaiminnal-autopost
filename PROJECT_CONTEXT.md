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
| 2026-11-14 | `78cd1c1` | Reel layout A for every reel (owner 14 Nov night): picture left clear, one lower text block, slim top strip, smaller footer with a small gap above it; outro in the news voice on every page and without the news location |
| 2026-11-14 | `93200cd` | Heartbeat |
| 2026-11-14 | `bdc30dd` | Heartbeat |
| 2026-11-14 | `98640a7` | Heartbeat |
| 2026-11-14 | `73c6db3` | Heartbeat |
| 2026-11-14 | `9bd572e` | powercut: notices written |
| 2026-11-14 | `1860f7b` | powercut: notices written |
| 2026-11-14 | `92b32ec` | district powercut: notices found |
| 2026-11-14 | `3081c1a` | powercut: notices written |
| 2026-11-14 | `684f04b` | powercut: notices written |
| 2026-11-14 | `0a22201` | Our own news music under the reels (owner 14 Nov, no copyright): serious / alert / calm composed by tools/make_music.py, mood from the news (post.music_mood), 14 dB under the voice while it speaks and back up in every pause and on the end card (voice track decides); config music.enabled |
| 2026-11-14 | `cd8409e` | Reel B2: top-right logo above the header bar, header shade fades out before it (owner 14 Nov: logo was hidden by the shade) |
| 2026-11-14 | `cd5d3f6` | district powercut: notices found |
| 2026-11-14 | `534c7e5` | facebook RN-6 |
| 2026-11-14 | `19ed47c` | pick: written and posted |
| 2026-11-14 | `d2b574f` | powercut: notices written |
| 2026-11-14 | `8abb9dd` | Reel B2: footer back inside the safe area (y 1085-1246, x 70-940 - owner 14 Nov: in the opened reel the bottom footer hid behind Instagram's name/caption/Follow); captions 880-1070, headline 520-860, summary 410-870 |
| 2026-11-14 | `e9f700e` | facebook RN-4 |
| 2026-11-14 | `b721b2c` | powercut: notices written |
| 2026-11-14 | `cde2f40` | facebook RN-11 |
| 2026-11-14 | `9a84127` | WIP: Fable design notes 1-7 as rendered in preview-10s-new.mp4 (footer still off, plain background) - owner 14 Nov: some parts fine, picture + footer missing |
| 2026-11-14 | `76f46a2` | facebook RN-7 |
| 2026-11-14 | `e8aed86` | powercut: notices written |
| 2026-11-14 | `1893b1e` | facebook RN-3 |
| 2026-11-14 | `683a4af` | pick: picked news saved |
| 2026-11-14 | `b09de88` | stories shared |
| 2026-11-14 | `e824780` | test_today_only: independent of research_free/START_AT (failed for 2 h after every collect-switch start) |
| 2026-11-14 | `d545796` | Kovai Minnal live (LIVE file: scheduled posting on); tests job installs pyyaml (test_district_reach needs it) |
| 2026-11-14 | `179471b` | pick: picked news saved |
| 2026-11-14 | `79589ef` | pick: list sent |
<!-- recent-changes:end -->
