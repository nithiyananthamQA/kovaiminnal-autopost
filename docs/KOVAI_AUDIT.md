# Kovai Minnal vs the reference - audit (14 Nov)

Reference = news360-tn/coimbatore360-autopost (page "Coimbatore 360"), checked at its commit `4ed994f` (14 Nov).
Report only: none of the gaps below is changed in the code yet (only the Instagram connection, last section). A port needs the owner's yes, like every difference.

## How we checked

| Check | Result |
|---|---|
| Which reference commit we copied | `6c6ade2` (11 Nov 14:54 IST). Our first commit `f6bccc2` came 25 minutes later. The next reference commit (`6a0bacd`, 15:26) is NOT in our copy |
| What the copy changed | Names only: Coimbatore 360 -> Kovai Minnal, #KovaiMinnal, bot name, Cloudinary folder, `..._HERE` placeholders in Code.gs. No logic was changed at copy time |
| Reference changes since then | 791 commits; 21 by people, the rest are the bot's data commits (check log, prebuilt, facebook, powercut state) |
| Our changes since the copy | reel v5 / B2, Anbu voice, writer order, old-cut rule, district pages (all listed below) |
| Kovai workflows | Still exactly the 11 Nov reference workflows (only names differ). Every reference workflow change after 11 Nov is missing |

## 1. Different on purpose (already written down)

| Area | Reference | Kovai Minnal | Written in |
|---|---|---|---|
| Name, logo, handle, hashtags, bot name | Coimbatore 360 | Kovai Minnal (internal page key stays `coimbatore`) | SETUP section 1, PROJECT_CONTEXT |
| Reel design | v4 (`reel/reel4.py`) | v5 = B2 "Broadcast" look (`reel/reel5.py`, built on reel4), full-width footer | DIFFERENCES 1, config `reel_design` |
| Voice | Valluvar, +12% | Anbu (`ta-SG-AnbuNeural`, +5%) | DIFFERENCES 1, config `reel_voice` |
| End card | "Source: paper (date)" since 13 Nov | "📰 Source: ..." since 11 Nov (reel5) | same result, done earlier |
| Header / footer / end card | page tagline | only "கோவை மின்னல்" | reel.py, owner 11 Nov |
| District power-cut pages | none | 37 pages, Chennai live (`districts/`, `district_powercut.yml`, `Code.districts.gs`), off-switch in config | districts/README.md, DIFFERENCES |
| Power cut whose day has passed | posted until the cut time is over | never posted when the notice names a past day (same `freshness.py` code, so Kovai too) | DIFFERENCES 4 |
| Instagram connection | Instagram login (`graph.instagram.com`) | Chennai: Meta Unified login (`graph.facebook.com`). Kovai: see the last section | DIFFERENCES 5 |
| Live state | live (`LIVE` + `research_free/ENABLED`) | not live; Kovai schedules switched off on GitHub | SETUP 10-12 |

## 2. Gaps: the reference has it, Kovai lacks it (or differs with no note)

| # | Area | Reference now | Kovai now | Why it matters |
|---|---|---|---|---|
| 1 | News rounds (`pick.yml`, `pick.py`) | every 4 h (01/05/09/13/17/21 IST); at least 2+5+5+3+5+4 = 24 news a day, up to 3 more a round from well-watched topics; ranked by the page's insights (`learned.reach_weight`) | 06/10/19 IST, 8+6+6 = 20; ranked by points only | fewer news, slower to new news, older ranking |
| 2 | News age (`post.yml`) | `POST_MAX_AGE_DAYS: 1` (today + yesterday) | `0` (today only) | late-evening news is never posted |
| 3 | Posting backlog (`post.yml`) | `continue` job starts the next posting run after the 12-minute gap | missing | GitHub runs the 5-minute timer about once an hour: a backlog posts ~1 story an hour |
| 4 | Power-cut sources (`powercut.py`, `allnews.py`) | also the daily state-wide lists (News18, ABP, Samayam), only our district's part read; a notice filed under another district's page is refused | district pages only | cuts printed only in the state lists are missed |
| 5 | Cut cancelled / postponed (`freshness.py`, `powercut.py`, `post.py`, `rules.md`) | posted as urgent news, only when the page posted that cut; the writer's refusals are remembered (`powercut.py remember`) | treated as a duplicate of the first notice and dropped; refusals forgotten next job | missed urgent news; red verify checks |
| 6 | Gmail daily limit (`post.py`) | "posted" record accepted when only the owner e-mail hit Gmail's limit | retried 5 times, then the run errors (the Sheet row was saved) | Kovai's and the district bridge run in ONE Gmail, so the limit comes sooner |
| 7 | Story share (`post.py`, config `stories_urgent_only`) | only power cuts / urgent news get a story | every post also gets a story (2 of Instagram's 50 daily posts per news) | Instagram's daily limit is used twice as fast |
| 8 | Cloudinary clean-up (`cloudclean.yml`, `poster/cloudclean.py`) | every 2nd day, keeps 48 h; a ready reel whose link is gone (404) is uploaded again | none | the free plan fills up; old ready reels may point to deleted files |
| 9 | First spoken sentence (`validate.py`) | must name the town and state the news; no question / teaser | no such check | half the viewers leave in ~7 s (reference insights) |
| 10 | Topics (`collect.py`, `learned.py`) | POCSO / sexual harassment = crime; health tips and "day functions" not written | missing | ranking |
| 11 | Numbers in the voice (`reel/tamilnum.py`) | English names in English (பிளஸ் டூ, 5ஜி, டி ட்வென்டி), endings joined (நாற்பதுக்கும்), நெ. -> எண் | old reading (பிளஸ் இரண்டு) | voice mistakes (reel5 uses the same tts.py) |
| 12 | Comment replies (`comments.py`, `comments.yml`, Code.gs) | one Google Form per batch (5-7 options, tick one or more, own reply, Reply / Skip / Hide, checked every 5 min); only important comments e-mailed; normal ones saved as hashed ids | e-mail with one link per option (3 options); every comment e-mailed | more e-mail for the owner |
| 13 | Source names (`post.py`) | ABP Nadu, Samayam Tamil named | missing | "Source:" line wrong for those papers |
| 14 | Gold rate (`goldrate.yml`, `goldrate/`) | daily gold / silver carousel, 09:40 IST | none | new feature - owner decides |
| 15 | Custom reel (`custom_reel.yml`) | manual one-off reel, never posts | none | optional |

Our own differences that are NOT in DIFFERENCES.md:

| What | Reference | Kovai | Note |
|---|---|---|---|
| Free writer order (config `writers`) | Gemini, then Groq; Cloudflare not for writing | Gemini, Gemma, Groq, Cloudflare (`cloudflare_for_writing: true`) | owner's choice 11 Nov, only in commit history |
| Claude fallback | last fallback (no per-run limit) | the same (workflows pass `ANTHROPIC_API_KEY`) | PROJECT_CONTEXT wrongly says "Claude backup OFF" |
| District hooks in Kovai code | - | `IG_PAGES`, `PAGE_KEY`, `HOME_DINAMALAR`, `DISTRICT_WORDS`, `PAGE_TAGS`, `PAGE_LOGOS`, `HOME_PLACES`, `IG_USER_ID` | defaults keep Kovai as before; but every port into these files also changes Chennai (live) |

## 3. Reference commits after `6c6ade2`

| Commit | What | Port? | Why |
|---|---|---|---|
| `6a0bacd` | cut cancelled / postponed posted; refusals remembered | Yes | gap 5: urgent news; also helps the district pages |
| `f7697da` `026cf77` `192dd17` `27f7af2` | comment replies by Google Form | Yes, as one set | gap 12: works on any phone; needs Code.gs repaste + `setupCommentPoll` once |
| `5d70908` | only important comments e-mailed | Yes, after the form set | gap 12: less e-mail |
| `5603740` | hourly Cloudinary clean-up | Only its 404 re-upload part | the hourly clean is replaced by `9e5d3ed` |
| `9e5d3ed` | clean-up every 2nd day, keep 48 h | Yes | gap 8; needs secrets `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET`; folder `kovaiminnal` |
| `f43a08d` | next posting run after the 12-minute gap | Yes | gap 3 |
| `bc675f7` `ee4a7a9` | numbers read as people say them | Yes | gap 11 |
| `cee3548` | end card "Source:" in reel4 | No | reel5 already does it; the reel4 edit would stop reel5's "📰 Source:" replace |
| `da359b0` | first sentence names the town; ABP / Samayam names; evening round 17:00 | Yes, but not the round time | gaps 9, 13; the round time is replaced by `aba8a65` |
| `aba8a65` | collection every 4 h; today + yesterday; state-wide power-cut lists; posting start times | Yes, except the posting start times | gaps 1, 2, 4; the start-time wait is switched off by `e9f5403` |
| `e9f5403` | posting wait off (config) | Only with `aba8a65` | config shape for the ported code; Kovai's wait is already off |
| `ab06a9d` | round news chosen by insights; stories for urgent news only | Yes | gaps 1, 7; needs `insights.py` `topic_n` |
| `73df33e` | POCSO = crime; health tips / day functions skipped | Yes | gap 10 |
| `1d7c010` | Gmail limit is not a failed post | Yes | gap 6 |
| `bc0eaec` `e687005` | gold-rate carousel | Owner decides | new daily post, uses Instagram's daily limit |
| `a88502c` | custom reel workflow | No (optional) | needs its own branch and files; a hand-made extra |

## 4. Our docs that are out of date

| File | Out of date |
|---|---|
| `docs/SETUP_KOVAI_MINNAL.md` | Daily table says v4 + Valluvar and 06/10/19 (reference now every 4 h); "335 tests"; cost line says Valluvar. (Fixed 14 Nov: stray "can i" on line 1; step 9 + Meta app row now describe the Unified login with Minnal Pages.) |
| `PROJECT_CONTEXT.md` | "How it works" shows `research_free.yml` every 2 h + `write_stories.yml` every 20 min (neither has a schedule; `pick.yml` does the rounds); reel4 + Valluvar; "Claude backup OFF"; daily cap 50 (post.yml says 44) |
| `README.md` | voice Valluvar |
| `docs/DIFFERENCES.md` (Chennai) | "Same as the reference" rows are old since 13-14 Nov: news rounds 06/10/19 and 8+6+6 (now every 4 h, 24+), ranking "same function" (now insights), freshness "same code" (now cancellation rules) |

## 5. Before porting (so nothing breaks)

| Port | Watch out |
|---|---|
| any change in `pick.py`, `collect.py`, `powercut.py`, `allnews.py`, `post.py`, `freshness.py`, config | Chennai (live) runs the same code: run `tests/test_districts.py` too |
| state-wide power-cut lists | `districts/pipeline.py` must set `allnews.SECTION_NAMES` to each district's own names, or Chennai reads Coimbatore's part |
| `ab06a9d` without the 4-hour schedule | set `PICK_ROUND_TOP: "6=8,10=6,19=6"`, or the rounds fall to 5+5+5 = 15 |
| `stories_urgent_only` | the config is shared, so it also changes Chennai |
| `comments.py` | keep `HANDLES["coimbatore"] = "kovaiminnal"` (the reference maps it to its own handle) |
| `cloudclean.py`, `rasi_daily.py` | folder `kovaiminnal`, not `coimbatore360` |
| Code.gs comment form | keep the strings `districts/make_bridge.py` replaces; regenerate `Code.districts.gs`; keep the Instagram reply host of the last section |

## Instagram connection (Kovai)

Since 14 Nov (commit `e298717`) Kovai can post through Meta's Unified login, the same way Chennai does. It is switched by configuration only:
`poster/config.json` → `"instagram": {"api": "unified", "user_id": ""}` (rule in `poster/ig_api.py`).

| `user_id` | Host | Account | Token in the bridge (`IG_TOKEN_COIMBATORE`) |
|---|---|---|---|
| empty (today) | `graph.instagram.com` | `me` | Instagram-login token (IGAA...), refreshed every Sunday - exactly as before |
| the @kovaiminnal account id (17841...) | `graph.facebook.com/v24.0` | that id; `me` is refused there (it is the system user) | system-user token (EAA...), never expires, never refreshed |

Every Kovai job that calls Instagram follows the same rule: `post.py` (reel, story, carousel, quota, duplicate check, story catch-up),
`comments.py`, `insights.py`, `ig_comments.py`, `ig_probe.py`, `collect.py` (recent posts), all through `post.ig`. `rasipalan/rasi_daily.py`
has its own copy of the calls and was switched too. A district page on the Instagram login never takes Kovai's setting.
The bridge (Code.gs) never refreshes an EAA token, and it sends comment replies / hides for an EAA token to `graph.facebook.com`.

What differs between the two hosts:

| Call (where) | Instagram login | Unified login | Status |
|---|---|---|---|
| Who am I: `me?fields=user_id,username` (post.py, rasipalan) | the page | the system user, never the page | handled: the account id from config is used, `me` refused |
| API version | no version in the URL | `v24.0` | handled |
| Story catch-up: owner of a post (`owner.id`) | an app-scoped id, so `me.id` + `user_id` are compared | the account id itself | handled (compares the id); not yet seen live |
| Publishing: `<id>/media`, `media_publish`, `status_code`, `permalink`, quota | same | same | reels: Chennai posts this way since 13 Nov. Carousel (rasipalan) not yet run on Unified |
| Reel insights: `reach, views, saved, shares, total_interactions, ig_reels_avg_watch_time` (insights.py) | same names | same names, needs `instagram_manage_insights` | not yet run on Unified (Chennai has no insights job) |
| Followers: `followers_count, media_count` | same | same | not yet run on Unified |
| Comments: `<media>/comments` fields `id,text,username,timestamp,replies{username}` | same | same, needs `instagram_manage_comments` + `pages_read_engagement` | not yet run on Unified |
| Reply / hide a comment (Code.gs) | `graph.instagram.com/v23.0` | `graph.facebook.com/v24.0` | handled: host chosen by the token |
| Token refresh (Code.gs, weekly) | `refresh_access_token` | cannot be refreshed (never expires) | handled: skipped |
| Collaborator invite / accept (`collab_username`, rasipalan `accept_collab`) | Instagram login only | - | not used by Kovai (collab is empty) |

After the switch the first check is the **ig-probe** workflow (reads account, recent posts, reel insights and quota; posts nothing).

Also found and fixed on 14 Nov: `apps_script/Code.districts.gs` (made by `districts/make_bridge.py`) had real line breaks inside two
JavaScript strings (timer e-mail), so Apps Script would refuse to save it. `make_bridge.py` now keeps them as `\n`; a test checks
both bridge files with `node --check`.
