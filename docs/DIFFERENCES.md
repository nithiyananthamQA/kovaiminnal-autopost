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
- Reel end card: ours (reference cee3548 "Source: <paper> (<date>)" end card is template - not taken; our top strip shows the source).
- Pictures: our own generated pictures only, no news-site photos (config `real_photo_enabled: false`, owner 14 Nov, part of the video).
- Gold-rate slides: OUR design (goldrate/minnal_render.py, owner 17 Nov "dont copy his template"): Minnal navy + yellow, the 22K
  sovereign (8 g) as the hero, 22K / 24K per gram, 24K 10 g, sovereign + 3% GST, this week's bars with high / low; silver 1 kg
  hero + 1 / 10 / 100 g. Same rate reading and two-source rule as the reference (gold_daily.py, gold_sources.py).

## 2. Names (branding)

Kovai Minnal / கோவை மின்னல், #KovaiMinnal, @kovai_minnal, bot name kovaiminnal-bot, Cloudinary folder kovaiminnal,
e-mail tag KOVAIMINNAL. Never "360".

## 3. Forced (Meta / GitHub give us no other way)

- Instagram connection: Meta's Unified login (app Minnal Pages, minnal-bot system-user token, graph.facebook.com + account id,
  poster/ig_api.py). Reference: Instagram login (graph.instagram.com, "me"). Same for comments, rasipalan, gold rate, Facebook.
  The token can come from the GitHub secret IG_SYSTEM_TOKEN or the Minnal bridge.
- Instagram views: our minnal-bot token lacks `instagram_manage_insights`, so poster/insights.py cannot add OUR reels' views.
  research_free/learned.json is still rebuilt every night from poster/insights/history.json, which holds the reference page's
  197 measured reels copied on 11 Nov - so our pick uses HIS insight weights as of 11 Nov, frozen. The reference learns from its
  own new views every night; ours will too as soon as the owner's new token (with that permission) is saved as IG_SYSTEM_TOKEN.
- Posting chain (reference f43a08d / eac718e): the next run it starts carries timer=true, so our LIVE file still stops posting.
- Scheduler: GitHub's own timer rarely starts our jobs, so tools/keeper.py (keeper.yml) starts each workflow at its own cron times.
  The schedules themselves are the reference's.
- Comment reply forms (reference f7697da / 192dd17): ported; the Apps Script part (apps_script/Code.gs) works only after the owner
  pastes the new Code.gs into the Kovai bridge and runs setupCommentPoll once.
- Cloudinary clean-up (reference 5603740 / 9e5d3ed): ported; it needs the GitHub secrets CLOUDINARY_API_KEY and
  CLOUDINARY_API_SECRET (owner) - until then it deletes nothing.

## 4. Held until the owner says yes

- Gold & silver rate carousel (reference bc0eaec): code ported and rebranded, schedule HELD (show-first rule).
  Sample (our design): ~/Videos/kovai-minnal/goldrate-OUR-design-17nov.jpg. To start it: put the three cron lines back in .github/workflows/goldrate.yml
  and add `"goldrate.yml": {"dry": "0", "date": ""}` to tools/keeper.py LIVE_INPUTS.

## 5. Correctness fixes of ours (owner 17 Nov: "you kept ours better" - the friend is told to fix his copy)

- Tamil proofread never doubles words (poster/tamilcheck.py): a full stop no longer hides a repeat, and a "fix" that only adds
  words that already follow it is refused. 16 Nov RN-68 went out saying "கைது செய்யப்பட்டனர் செய்யப்பட்டனர்." (also RN-21, RN-23).

- A power-cut notice the paper filed under another district (e.g. Dinamani /edition-coimbatore/tiruppur/) passes only when its
  title has OUR district's own name (allnews.SECTION_NAMES) - the reference lets any shared place name through ("மேட்டுப்பாளையம்" is a
  Coimbatore town and a Tiruppur village: the Vellakoil cut RN-11 went out on Kovai). Tested on the real link 17 Nov.
- A Tiruppur / Erode power-cut notice printed in the paper's Coimbatore edition never posts on Kovai (16 Nov RN-52, Uthiyur cut
  posted wrongly): extra Tiruppur town names in allnews.OTHER_PLACES / OTHER_EN and the notice-text check in powercut.check.
  The reference refuses Tiruppur / Erode edition pages (aba8a65) but not this case.

## 6. Chennai Minnal (until it is a copy of the Kovai code like the reference's pages)

Chennai still runs on districts/pipeline.py (my own engine - the reason Kovai and Chennai drifted). Its counts now follow the
reference (24 a day: 01:00 2, 05:00 5, 09:00 5, 13:00 3, 17:00 5, 21:00 4; no score floor, no skip list; its timer runs
05:35-22:05, so the 01:00 round does not run there). Plan: Chennai becomes its own repo, a copy of this one with only the
district words changed (as the reference does for Tirupur, Salem, Erode, Karur, Trichy, Namakkal); the engine stays until the
owner has seen the copy's reels. The hooks this engine needs (pick.HOME_DINAMALAR, collect.IG_PAGES, powercut.PAGE_KEY,
validate.DISTRICT_WORDS, post.PAGE_TAGS / PAGE_LOGOS / DEFAULT_LOC / HOME_PLACES) hold Kovai's own values and change nothing on Kovai.

## Removed 17 Nov (our own rules - the reference's way instead)

14 news a day + peak split, score floor 7, extras 11+ (3 a day), the nightly skip list (reference_sync.py, reference_reach.json,
learned.py blending), the school / club event filter, the 01:00 power-cut-only round, the extra free writers (Gemma, Cloudflare
Llama - the reference writes with Gemini then Groq, Claude only when both fail).
