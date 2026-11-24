# Where our pages differ from the reference

Reference = news360-tn/coimbatore360-autopost (the friend's Coimbatore page; his 7 pages run the same code, one repo each).

**Owner rule 17 Nov 2026: "follow his same all, only template and voice is differ ... when we create new pages then follow it."**
Every Minnal page is the reference's code with only the page's names changed. This file lists every difference that remains;
nothing else may differ. Re-checked with `git diff ref/main` (remote `ref` = the reference repo).

Reference ported up to: **b204b4d (17 Nov 2026 06:48 UTC)** - all 21 of his code changes since our copy (11 Nov, abb1ac1),
plus ab06a9d (16 Nov). Next port: `git log abb1ac1..ref/main` for commits after b204b4d.
Also ported (owner 20 Nov "yes please"): **7312326 (19 Nov) posting time first** - pick rounds 04:00 / 08:30 / 13:00 / 16:30 / 18:30
IST (PICK_ROUND_TOP 7/5/4/4/4 = 24 a day) and news posting only in 06:00-12:00 + 15:00-21:00 IST (config prime_time, his exact
object; power cuts at once). post.py already had his window code (prime_wait / in_prime_time are identical). Not taken from it:
watchdog.py (the Worker starts a missed round). NOT yet ported (owner to decide): 77703119 (NVIDIA picture 'seed' fix),
1f1bc053 (rasipalan / gold times + watchdog), c9cf170a (reel length + wording, automatic source first comment, insights paging,
gold reel, posting spacing 0), 94ed96f8 (reel length back to full news, captions fit 2,200), 9acb0c59 / eafa3597 / 84674b84 (his
gold reel / 360 clock design = template, not taken).
- Posting gap: the reference posts every ready news of a window at once (c9cf170a, config posting.spacing_min 0); we keep 12 minutes
  between posts (not ported - owner to decide: 0 = his way, 7-10 reels in one burst when a window opens).

## 1. Owner's choice: reel template and voice (owner 17 Nov: "voice and video template is ours")

- Reel design v5 (reel/reel5.py on reel4.py): our layout, top strip, place pin, no footer; our own music bed (tools/make_music.py,
  config `music`). Reference: v4.
- Voice: free Anbu (edge-tts ta-SG-AnbuNeural, +5% = Nila's speaking speed). Owner 19 Nov: "from now no cost for voice" - ElevenLabs Nila off, its key removed from .env, workflows and GitHub secrets. Reference: free edge-tts Valluvar.
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

## 3d. GITHUB SAFE MODE (owner 17 Nov, temporary): a friend's account was suspended for this kind of Actions load

- post.yml hourly backup (was every 5 min) - posting goes one by one through its chain (pick / powercut start the first run,
  each run starts the next after the 12-minute gap); comments and power cuts hourly (were every 30 min); district engine
  schedule off (Chennai has its own repo); keeper no longer starts district_powercut. About 75 runs a day per page (was ~400).
- The owner stops the Google Apps Script timer (stopKovaiTimer) - it could start post.yml every 5 minutes.
- REVERT when the Cloudflare Workers timer takes over: git revert this commit (tests test_keeper / test_kovai_timer say what).

## 3e. Cloudflare Worker timer (owner 18 Nov: "can we move to the workers now", "one worker for all our pages", plain name)

- workers/timer = Cloudflare Worker "test" (owner's Cloudflare account): every minute it starts each page's workflows at their own
  cron times (schedule.json from tools/make_timer.py: Kovai + every page clone), once - a run since that time (GitHub's own timer)
  counts. It replaces keeper.yml (switched off on GitHub) and the Google Apps Script timers. Secret GH_TOKEN = the nithiyananthamQA
  GitHub login. A new page: clone it, python3 tools/make_timer.py, cd workers/timer && npx wrangler deploy.
- Posting chain (owner 18 Nov: "safe from ban?"): a posting run that leaves news waiting no longer sleeps 6 / 11 minutes on a
  GitHub machine before starting the next one - it asks the Worker (POST https://test.freelancingfashion.workers.dev/next, secrets
  TIMER_URL / TIMER_KEY) and ends; the Worker keeps the time in KV (NEXT) and starts exactly one posting run when it comes. No
  TIMER_URL = the old sleep. Posts stay one by one, 12 minutes apart.
- Round gate (owner 20 Nov: "chennai why 45 post"): pick.yml's first job (poster/round_gate.py) stops a GitHub schedule run when a
  workflow_dispatch run (the Worker's or the owner's) already started at or after that cron's time - GitHub's own schedule fired
  1-2 hours after the Worker (19-20 Nov 22:13, 06:54, 09:36 IST) and ran a SECOND round: 9 rounds a day, Chennai 31 news reels +
  14 stories in 24 h, then Instagram's limit held the next round (pick run 44672143820 failed). The Worker missed the time = GitHub's
  run is the round; any error = the round runs. The pick job's concurrency is on the job, so a stopped run never queues. The reference
  has no Worker (its watchdog.py restarts a missed round instead) - not taken: the Worker does that job.

## 4. Held until the owner says yes

- (none) - the gold & silver rate reel went live on the owner's OK 17 Nov ("nice music use it"): goldrate.yml crons 09:35 /
  11:00 / 12:30 IST + keeper LIVE_INPUTS. Samples: ~/Videos/kovai-minnal/goldrate-REEL-10s-17nov.mp4 (music then changed to alert).

## 4a. Owner's choice: business names (owner 17 Nov: "which shop where - add the shop name if available")

- research_free/rules.md: a shop / hotel / company / school / hospital / temple ... that the article names is written by its name
  (the shop that caught fire, the hotel that was sealed). The reference's writer already names businesses most of the time (its
  rules only forbid private persons, victims, minors and accused); ours now says it outright. Private persons stay unnamed.

- Names as the newspaper gives them (owner 17 Nov: "if newspaper do then post that"): rules.md lets the writer name a person
  exactly as the article does (arrested / accused adults, people in accidents, officials). The reference forbids naming private
  persons, victims and accused. NEVER (law: POCSO s.23, JJ Act s.74, BNS s.72): a minor or a sexual-offence victim, or a detail
  that identifies them - research_free/run.py CHECK (the independent fact-check of every draft) reports it and the draft is rewritten.

## 4b. Owner's choice: our own sentences (owner 17 Nov: "is it legal to take news from Dinamalar? ... fix the gap")

- rules.md OWN WORDS + validate.copy_problems: the facts, names and numbers come from the article, the sentences are ours. A
  reel_script or caption that copies 15+ article words in a row, or 40 %+ of its 6-word phrases, is sent back to the writer.
  Power-cut notices are left out (area lists stay as published). Measured 17 Nov: most posted reels re-used 11-20 words in a
  row. The reference has no such check. The reel's top strip still credits the source by name (📰 தினமலர்), no logo, no link.

## 4c. Owner's choice 19 Nov: the right day, and power cuts only ahead

- freshness.tomorrow_is_late (posting) + run.day_problems (writing): a reel that says நாளை about a day that has come is never posted
  and a draft doing it is sent back (19 Nov: 'கோவையில் நாளை மின்தடை ... (நவம்பர் 19)' went out on the 19th at 11:27).
- freshness.power_cut_over: a power cut is posted only BEFORE its day - on the day it is skipped (owner: "if the news came today and
  today is the power cut, we are not worth to give that information"); post.pick_all puts power cuts first in the queue.
- freshness.same_cut_areas: the same power cut from a second paper (other headline words, same cut day, 2+ of the district's
  known areas in the script) is a duplicate (19 Nov: RN-102 = RN-97 from ABP Live, posted on the cut day). The reference has the same
  gap: 4 of his last 23 dated power-cut reels went out on / after the cut day saying நாளை.
- names.spoken: party short names without dots (தவெக, திமுக, அதிமுக, பாஜக ...) are read letter by letter - voice only.

## 4d. No rasipalan (owner 19 Nov: "that rasipalan news we dont need")

- rasipalan.yml has no schedule (manual run still possible), keeper / Worker never start it; the workflow is switched off on GitHub.
  The reference posts a daily rasipalan.

## 5. Correctness fixes of ours (owner 17 Nov: "you kept ours better" - the friend is told to fix his copy)

- Tamil proofread never doubles words (poster/tamilcheck.py): a full stop no longer hides a repeat, and a "fix" that only adds
  words that already follow it is refused. 16 Nov RN-68 went out saying "கைது செய்யப்பட்டனர் செய்யப்பட்டனர்." (also RN-21, RN-23).

- A power-cut notice the paper filed under another district (e.g. Dinamani /edition-coimbatore/tiruppur/) passes only when its
  title has OUR district's own name (allnews.SECTION_NAMES) - the reference lets any shared place name through ("மேட்டுப்பாளையம்" is a
  Coimbatore town and a Tiruppur village: the Vellakoil cut RN-11 went out on Kovai). Tested on the real link 17 Nov.
- A Tiruppur / Erode power-cut notice printed in the paper's Coimbatore edition never posts on Kovai (16 Nov RN-52, Uthiyur cut
  posted wrongly): extra Tiruppur town names in allnews.OTHER_PLACES / OTHER_EN and the notice-text check in powercut.check.
  The reference refuses Tiruppur / Erode edition pages (aba8a65) but not this case.

- Never "நாளை" alone (owner 22 Nov, a viewer's comment: people watch the reel later). research_free/daydate.py adds the date to every
  நாளை / நாளை மறுநாள் of the finished draft (run.write, after the checks): voice "நாளை, நவம்பர் 23ஆம் தேதி,", caption and headline
  "நாளை (நவம்பர் 23)", screen lines "நாளை (நவ.23)" or only "நவ.23" when the line is full. A நாளை that already has a date is left alone.
- Power-cut hours for Samayam's state-wide list (owner 23 Nov: "some video missed the timings", "at least try to get or post what we
  have"). Samayam's body prints no hours, so Kovai RN-83, RN-97, RN-241 and Salem RN-2 went out with no time. allnews.district_section,
  when the list gives no hours, adds: 1) the same areas' hours from the district papers' own notices of that cut day (the power-cut
  check's written list, saved 20+ minutes before; Dinamani > Dinamalar > Covai Mail; 2+ areas must match as whole names; in a notice
  with several substations each area takes the hours printed before it) - "X, Y ஆகிய பகுதிகளில் காலை 10 முதல் மதியம் 3 மணி வரை
  மின்தடை (மின்வாரிய அறிவிப்பு)", no paper's name (the writer never names a source); 2) Samayam's synopsis line ("தமிழகம் முழுவதும்
  ... காலை 9 மணி முதல் மாலை 4 மணி வரை" - one line for the whole state, not always right: Dinamalar gave 10-3 for RN-241's areas). The
  synopsis always stays, so the post run's fact check (it re-reads the text) backs a draft written with either time. Any error = the
  list as before (never stops a power cut).

- The pick ENGINE (owner 24 Nov: "an Instagram monster ... post the reels our users loved to see - watch hours, news topics,
  everything ... it's an engine", "separate insights for each district"). The reference orders a round by a fixed keyword score
  (it reads the article body too: an opinion piece with 'டேட்டா திருட்டுக்கும்' scored as crime, 10.0) + a topic weight from
  shares / saves per reach; 73% of our candidates were topic 'other' (weight 0), so the keyword score decided (5 PM 24 Nov:
  'மிஸ்டர் ஏஐ.. நீங்க நல்லவரா' picked, two public complaints left out). Ours: poster/insights.py learns each night, per page from
  its OWN final reels (> 3 days), learned.learn: love = 0.7 log(views / that day's median) + 0.3 log(watch / page median);
  topic -> area -> city / town tier -> headline words, each fitted on what is left and shrunk by its reel count; hour learned
  (not used yet). pick.reach_score = 8 x learned.engine_score + 0.5 x the HEADLINE's keyword score - age; power cuts first; extra
  posts unchanged (replay: 0 and 0); engine not ready (< 30 final reels, e.g. Salem) or any error = the reference's order.
  Used now: topic + tier. Areas and words are used only from 400 final reels (24 Nov backtest, learn on older reels / score newer:
  71 reels 0.30 vs old order 0.30, 92: 0.34 vs 0.32, 126: 0.44 vs 0.35 rank correlation with real views; areas / words added nothing
  yet). Topics: civic (people's problems) split from infra (plans / projects), feature (opinion / explainer, start value -0.3)
  added, more crime / accident words ('சிறை' alone is not crime). The writer's style examples (top_openings) = most-watched
  openings against their day, never a POCSO / sexual / suicide / death story. Replay of the last 28 rounds: 21 pick differently.

## 6. Chennai Minnal = a copy of this repo (17 Nov, the reference's way)

- Chennai's own places (owner 18 Nov: "chennai is the most populated city ... add even more small areas", suburbs yes):
  tools/make_page.AREAS - ~136 Tamil + ~123 English area names (city, small areas, Tambaram / Avadi / Pallavaram / Chromepet /
  Poonamallee ...), city services (corporation, Metro rail / water, MTC, suburban trains, CSK) and the big suburbs that count for a
  power cut filed under Chengalpattu / Tiruvallur; party / assembly words make a Chennai-datelined state-politics story "state
  news". tests/test_page_values checks real headlines (17 Nov list + Chennai's best reels).

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

## Power-cut-only pages (owner 19 Nov: "create pages for only the powercut for that particular city")

- Salem Minnal (and every new district page after it) posts ONLY its district's power cuts: the same code as Kovai
  (tools/make_page.py), but only `POWERCUT_JOBS` run (powercut, post, comments, insights, cloudclean, tests): the timer starts only those
  (tools/make_timer.py) and every push switches the page's other workflows off (tools/sync_pages.only_jobs). Reference: his
  salem360 page posts all Salem news.
- Each such page has its OWN Apps Script + Sheet (owner 19 Nov) and its OWN Meta app token (owner 17 Nov "meta new app for new
  channel"; config instagram.shared_token_page ""), so a problem on one page never reaches another.
- Place lists, power-cut searches, papers and the picture prompt's city look = the REFERENCE's own Salem values
  (news360-tn/salem360-autopost, tools/ref_lists.py -> districts/ref_lists/salem.json) - same as his Salem page, not a difference.

## Tiruvallur Minnal = a full-news page (owner 20 Nov: "this district is for full news like others"; "dont live as of now")

- Every job, like Chennai (no `jobs` list); its OWN Meta app token + Apps Script, and its OWN free AI accounts on a new e-mail (owner
  20 Nov) - Kovai's free AI keys are never copied; Claude (paid) = Kovai's key, only when every free AI fails ("when free fails then
  only paid"). The reference has no Tiruvallur page, so its lists are ours (tools/make_page.py AREAS / CITY_LOOK, like Chennai).
- Ours: AREAS `roads` -> CITY_ROADS = "சென்னையை அடுத்த / சென்னை அருகே ..." taken out before the other-district / state check (the papers
  write Tiruvallur news as "near Chennai"; without it such a story counted as Chennai news and never made a round's top).
- Gold rate: Chennai's rate pages (`gold_city`) - the four rate sites have no Tiruvallur page (3 of 4 answer 404, 20 Nov).
- Avadi / Poonamallee / Thiruverkadu / Minjur / Redhills news may post on Chennai AND Tiruvallur (owner 20 Nov: both pages).
- `live: False` in make_page.PAGE until the owner says go: the timer never starts it, every push keeps all its jobs off.
