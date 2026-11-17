# Where our pages differ from the reference

Reference = news360-tn/coimbatore360-autopost (the friend's Coimbatore page; his 7 pages run the same code, one repo each).

**Owner rule 17 Nov 2026: "follow his same all, only template and voice is differ ... when we create new pages then follow it."**
Every Minnal page is the reference's code with only the page's names changed. This file lists every difference that remains;
nothing else may differ. Re-checked with `git diff ref/main` (remote `ref` = the reference repo).

Reference ported up to: **b204b4d (17 Nov 2026 06:48 UTC)** - all 21 of his code changes since our copy (11 Nov, abb1ac1),
plus ab06a9d (16 Nov). Next port: `git log abb1ac1..ref/main` for commits after b204b4d.

## 1. Owner's choice: reel template and voice (owner 17 Nov: "voice and video template is ours")

- Reel design v5 (reel/reel5.py on reel4.py): our layout, top strip, place pin, no footer; our own music bed (tools/make_music.py,
  config `music`). Reference: v4.
- Voice: ElevenLabs Nila (config `reel_voice`), place-name listen-back check. Reference: edge-tts Valluvar.
- Reel end card: ours (reference cee3548 "Source: <paper> (<date>)" end card is template - not taken).
- No source label in the video (owner 17 Nov: "remove the source from the video"): no 📰 paper in the top strip, no Source line
  on the end card (config `reel_source_label: false`, reel5.source_label_on; true = both back). The caption still ends with
  "📰 Source: paper (date): link".
- Pictures: our own generated pictures only, no news-site photos (config `real_photo_enabled: false`, owner 14 Nov, part of the video).
- Gold-rate slides: OUR design (goldrate/minnal_render.py, owner 17 Nov "dont copy his template"): Minnal navy + yellow, the 22K
  sovereign (8 g) as the hero, 22K / 24K per gram, 24K 10 g, sovereign + 3% GST, this week's bars with high / low; silver 1 kg
  hero + 1 / 10 / 100 g. Same rate reading and two-source rule as the reference (gold_daily.py, gold_sources.py).
  Owner 17 Nov: the gold slide feels gold and the silver slide silver, in our own layout (designed by Fable, not his look).

## 2. Names (branding)

Kovai Minnal / கோவை மின்னல், #KovaiMinnal, @kovai_minnal, bot name kovaiminnal-bot, Cloudinary folder kovaiminnal,
e-mail tag KOVAIMINNAL. Never "360".

## 3. Forced (Meta / GitHub give us no other way)

- Instagram connection: Meta's Unified login (app Minnal Pages, minnal-bot system-user token, graph.facebook.com + account id,
  poster/ig_api.py). Reference: Instagram login (graph.instagram.com, "me"). Same for comments, rasipalan, gold rate, Facebook.
  The token can come from the GitHub secret IG_SYSTEM_TOKEN or the Minnal bridge.
- Instagram views: our minnal-bot token lacks `instagram_manage_insights`, so poster/insights.py cannot add OUR reels' views
  until the owner's new token (with that permission) is saved as IG_SYSTEM_TOKEN.

## 3a. Owner's choice: insights = ours first, his live numbers help (owner 17 Nov: "main is ours, in the meantime his one also helps us")

- poster/reference_insights.py (called by poster/insights.py before every pick round and nightly): a news type's weight is OUR
  page's once we have 5 measured reels of it (learned.TRUST_N), else the reference page's LIVE weight (his public
  research_free/learned.json, 350 reels on 17 Nov), else learned.PATTERN; best hours / openings / watch time: ours from 12 measured
  reels, else his. learned.json "topic_source" says whose number each type uses. learned.py itself = the reference's.
- poster/insights.py counts only OUR reels: rows before our first reel (config insights.own_since, 14 Nov - his 198 rows copied
  on 11 Nov) are left out; his numbers come live. A reel is "final" only once its numbers were really read (the reference marks
  it final after 3 days even with none), and reels past the latest 50 are read again by id - so the 50+ reels posted before the
  new token are all measured once it exists. Until then every number is his (live, not frozen any more).

## 3b. Owner's choice: each page's own city rate (owner 17 Nov: "keep chennai and kovai separate")

- The gold rate is read from the same four sites' Coimbatore pages for Kovai (gold_sources.pages_for, page "city"), and the
  slides / caption say "கோவை விலை நிலவரம்", never Chennai. The reference reads Chennai pages for all its pages (same numbers in Tamil
  Nadu on 17 Nov). Chennai Minnal reads the Chennai pages.

## 3c. Owner's choice: the rate also as a REEL (owner 17 Nov: "we need to do this also as a reel with our best sound effect")

- goldrate/gold_reel.py: minnal_render.reel_page (1080x1920, inside the reel safe area of reel5.SAFE) -> frames -> H.264 with our
  own music (reel/assets/music/alert.wav, 120 BPM - owner 17 Nov "use music we have ... no sad music"), music only: the
  synthesized sound effects are in the code but off (gold_reel.SFX_ON). No voice. 10 s, opens already showing today's price.
- Owner 17 Nov "only one post thats reel": our pages post the REEL ONLY (gold_daily.PAGES "post": False); the reference posts
  the image carousel only. The slide design (minnal_render.page) stays in the code, unused. A page with both posts the carousel
  first, then the reel, tracked apart (state posted_<page>.json / posted_reel_<page>.json). GOLD_REEL=0 switches the reel off.
- Posting chain (reference f43a08d / eac718e): the next run it starts carries timer=true, so our LIVE file still stops posting.
- Scheduler: GitHub's own timer rarely starts our jobs, so tools/keeper.py (keeper.yml) starts each workflow at its own cron times.
  The schedules themselves are the reference's.
- Comment reply forms (reference f7697da / 192dd17): ported; the Apps Script part (apps_script/Code.gs) works only after the owner
  pastes the new Code.gs into the Kovai bridge and runs setupCommentPoll once.
- Cloudinary clean-up (reference 5603740 / 9e5d3ed): ported; it needs the GitHub secrets CLOUDINARY_API_KEY and
  CLOUDINARY_API_SECRET (owner) - until then it deletes nothing.

## 4. Held until the owner says yes

- (none) - the gold & silver rate reel went live on the owner's OK 17 Nov ("nice music use it"): goldrate.yml crons 09:35 /
  11:00 / 12:30 IST + keeper LIVE_INPUTS. Samples: ~/Videos/kovai-minnal/goldrate-REEL-10s-17nov.mp4 (music then changed to alert).

## 4a. Owner's choice: business names (owner 17 Nov: "which shop where - add the shop name if available")

- research_free/rules.md: a shop / hotel / company / school / hospital / temple ... that the article names is written by its name
  (the shop that caught fire, the hotel that was sealed). The reference's writer already names businesses most of the time (its
  rules only forbid private persons, victims, minors and accused); ours now says it outright. Private persons stay unnamed.

## 4b. Owner's choice: our own sentences (owner 17 Nov: "is it legal to take news from Dinamalar? ... fix the gap")

- rules.md OWN WORDS + validate.copy_problems: the facts, names and numbers come from the article, the sentences are ours. A
  reel_script or caption that copies 15+ article words in a row, or 40 %+ of its 6-word phrases, is sent back to the writer.
  Power-cut notices are left out (area lists stay as published). Measured 17 Nov: most posted reels re-used 11-20 words in a
  row. The reference has no such check. The reel's top strip still credits the source by name (📰 தினமலர்), no logo, no link.

## 5. Correctness fixes of ours (owner 17 Nov: "you kept ours better" - the friend is told to fix his copy)

- Tamil proofread never doubles words (poster/tamilcheck.py): a full stop no longer hides a repeat, and a "fix" that only adds
  words that already follow it is refused. 16 Nov RN-68 went out saying "கைது செய்யப்பட்டனர் செய்யப்பட்டனர்." (also RN-21, RN-23).

- A power-cut notice the paper filed under another district (e.g. Dinamani /edition-coimbatore/tiruppur/) passes only when its
  title has OUR district's own name (allnews.SECTION_NAMES) - the reference lets any shared place name through ("மேட்டுப்பாளையம்" is a
  Coimbatore town and a Tiruppur village: the Vellakoil cut RN-11 went out on Kovai). Tested on the real link 17 Nov.
- A Tiruppur / Erode power-cut notice printed in the paper's Coimbatore edition never posts on Kovai (16 Nov RN-52, Uthiyur cut
  posted wrongly): extra Tiruppur town names in allnews.OTHER_PLACES / OTHER_EN and the notice-text check in powercut.check.
  The reference refuses Tiruppur / Erode edition pages (aba8a65) but not this case.

## 6. Chennai Minnal = a copy of this repo (17 Nov, the reference's way)

- LIVE 17 Nov evening: repo nithiyananthamQA/chennaiminnal-autopost, all jobs on, the old Chennai engine in this repo off
  (config district_powercut live / news_live empty).
- One push updates every page, like the reference (it pushes each change to all 6 page repos in the same minute):
  tools/sync_pages.py rebuilds each page from Kovai with make_page.py, keeps the page's own live data (sync_pages.PROTECT -
  tests/test_sync_pages.py checks every file a workflow commits is protected), runs the page's tests, pushes only when they pass.
  The owner's /tmp/push.sh = push Kovai, then python3 tools/sync_pages.py.

`python tools/make_page.py chennai ~/chennaiminnal-autopost` makes the copy: the same files with only the district's words and values
(names, handle @chennaiminnal, #ChennaiMinnal, Kovai's closing lines with Chennai's name, Chennai's place lists and searches, its
city look for pictures, Instagram 17841452418440882, Facebook page 1450975134763291 via the minnal-bot token, Cloudinary folder
chennaiminnal, its Sheet = the Minnal bridge). Coimbatore-only tests are skipped there; tests/test_page_values.py checks Chennai's.
Every Kovai change is carried to Chennai by running make_page again (new pages: the same command with their key).
Go-live: /tmp/chennai_setup.sh (secrets, push, all jobs off) then /tmp/chennai_live.sh (old engine off + copy on, one step).
Until then Chennai runs on districts/pipeline.py with the reference's counts. The district engine stays for power-cut-only pages.

## Removed 17 Nov (our own rules - the reference's way instead)

14 news a day + peak split, score floor 7, extras 11+ (3 a day), the nightly skip list (reference_sync.py, reference_reach.json,
learned.py blending), the school / club event filter, the 01:00 power-cut-only round, the extra free writers (Gemma, Cloudflare
Llama - the reference writes with Gemini then Groq, Claude only when both fail).
