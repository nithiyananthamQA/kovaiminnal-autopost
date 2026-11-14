# Kovai Minnal (கோவை மின்னல்) – setup from zero to live

This is the same system that runs **Coimbatore 360** (github.com/news360-tn/coimbatore360-autopost), copied as it runs today
(11 Nov 2026) with our name, our images and our own accounts. Nothing in the flow changed: same workflows, same timings, same checks.

Do the steps **in order**. Steps marked **(you)** are yours; the only **(Claude)** step is 7 (I fill the Apps Script copy). Claude never pushes or changes GitHub.
Never paste passwords or API keys into the chat: secret values are typed only into the hidden prompts of `tools/set_secrets.sh`,
`tools/meta_fb_token.sh` or the Apps Script editor.

## What the system does every day (his current setup, unchanged)

| When (IST) | Workflow | What |
|---|---|---|
| 06:00, 10:00, 19:00 | `pick` | Collects Coimbatore news from Dinamalar + Dinamani Coimbatore pages, writes the top **8 + 6 + 6 = 20 news a day** (no e-mail to approve: `PICK_EMAIL: "0"`), makes one AI picture each, saves them in the Sheet and starts posting |
| every 30 min 05:50–21:50 | `powercut` | TNEB power-shutdown notices → reel at once (never twice for the same day + place, never after the cut is over) |
| every 5 min | `post` | Builds the reel (v4 design, Valluvar voice) and posts it to Instagram, plus the top news (max 5 a day, 2 h apart) to Facebook; max 44 a day (6 kept for urgent news) |
| 07:31 | `rasipalan` | Daily rasipalan carousel (calendar design) |
| every 30 min 06:00–23:00 | `comments` | New Instagram comments → 3 reply options e-mailed to you → posted only after you choose |
| 02:10 | `insights` | Reads Instagram insights → learned topic weights (which news gets written first) |

## Accounts you create (all free)

| # | Account | Why |
|---|---|---|
| 1 | New Gmail, e.g. `kovaiminnal.news@gmail.com` | Owns the Sheet, Apps Script, Drive folder, receives reports; also used to sign up for the AI keys and Cloudinary |
| 2 | Instagram `@kovaiminnal` (professional) | The page |
| 3 | Facebook Page "Kovai Minnal" (from your own Facebook profile) | Same reels on Facebook; Instagram is linked to it |
| 4 | Cloudinary (free) | Hosts the reel videos/pictures so Instagram can fetch them |
| 5 | Google AI Studio (Gemini), Groq, Cloudflare, NVIDIA | Free AI for writing and pictures (new keys, never Namenector's) |
| – | Meta app | Our own app **Minnal Pages** in the business portfolio **Minnal Media** (system user minnal-bot), the same as Chennai Minnal - see step 9 |
| – | GitHub | Your current account **nithiyananthamQA**, public repository `kovaiminnal-autopost` (public = unlimited free Actions minutes) |

---

## 1. Brand kit (images and texts)

All images are made by `python3 tools/make_brand.py` (our own drawings, nothing from Coimbatore 360): Coimbatore at dusk –
Adiyogi (Isha), a textile-mill chimney, the Ukkadam lakefront, coconut palms and one lightning bolt (மின்னல்).

| File | Size / format | Where it goes |
|---|---|---|
| `brand/profile_1080.png` | 1080 x 1080 PNG, round | **You upload:** Instagram profile picture **and** Facebook Page profile picture (same file) |
| `brand/fb_cover_1640x624.png` | 1640 x 624 PNG | **You upload:** Facebook Page cover photo (desktop shows 820 x 312; mobile crops the sides – the name stays in the middle) |
| `kit/logo_coimbatore.png` | 1092 x 1092 PNG, transparent | **Used by the system** (same file name as his): round logo top-right in every reel, carousels, daily rasipalan |
| `reel/assets/footer_coimbatore.png` | 2172 x 724 PNG, transparent | **Used by the system:** name strip at the bottom of every reel, with the same round logo (approved 11 Nov) |

### Texts (copy exactly)

**Instagram username:** `kovaiminnal`

**Instagram Name** (30 characters max; this field is searchable, so it carries the keywords):
```
Kovai Minnal | Coimbatore News
```

**Instagram bio** (150 max – this one is 122):
```
கோவை செய்திகள் உடனுக்குடன் ⚡
மின்தடை • விபத்து • மழை • வேலை
Coimbatore local news, fast.
Follow பண்ணுங்க | செய்தி இருந்தா DM
```

**Instagram category:** News & Media Website · **Account type:** Business

**Facebook Page name:** `Kovai Minnal - கோவை மின்னல்` (if Facebook refuses the mixed script: `Kovai Minnal`)

**Facebook category:** Media/News Company (second: News & Media Website)

**Facebook Intro / bio** (101 max – this one is 89):
```
கோவை நகர செய்திகள் உடனுக்குடன். மின்தடை, விபத்து, மழை, வேலை. Coimbatore local news, fast.
```

**Facebook About / description:**
```
கோவை மின்னல் - கோயம்புத்தூர் நகர மக்களுக்கான உள்ளூர் செய்திப் பக்கம். மின்தடை அறிவிப்பு, விபத்து, போக்குவரத்து, மழை, குடிநீர், மாநகராட்சி பிரச்சினைகள், வேலை வாய்ப்பு - செய்தி வந்தவுடன் குறுகிய வீடியோவாக.
Kovai Minnal is an independent local news page for Coimbatore: power cuts, accidents, traffic, rain, civic issues and jobs, posted as short Tamil Reels as news breaks. We are not affiliated with any government body or political party. News is compiled from public sources; corrections are welcome by message.
உங்கள் பகுதி செய்தியை எங்களுக்கு message செய்யுங்கள். #KovaiMinnal
```

**What every reel already says (set in the code):**
- Spoken last line (Valluvar voice): `மேலும் செய்திகளுக்கு கோவை மின்னல் பக்கத்தை பின்தொடருங்கள்.`
- Caption last line: `கோயம்புத்தூர் செய்திகளைத் தவறவிடாமல் இருக்க Save செய்து Follow செய்யுங்கள் 📌`
- Hashtags (5, fixed lists): `#KovaiMinnal #Coimbatore` + the area tag (e.g. `#Gandhipuram`) + topic (`#CoimbatorePowerCut` / `#CoimbatoreRain` / `#CoimbatoreNews`) + `#கோவை`

---

## 2. Instagram account (you)

1. On the phone, Instagram → add account → **Create new account** with the new Gmail. Username **`kovaiminnal`** (if taken: `kovai.minnal`, `kovaiminnal_news` – tell me which one you got).
2. Profile picture: `brand/profile_1080.png`. Name, bio: from section 1.
3. Settings → **Account type and tools → Switch to professional account → Business** → category **News & Media Website** → contact options: skip.
4. Settings → Privacy: account **public**; Comments: allow from everyone; Mentions: everyone.
5. Post nothing by hand yet (the first post comes from the system).

## 3. Facebook Page (you)

1. facebook.com (your own profile) → Pages → **Create new Page**. Name: from section 1. Category: **News & media website**. Bio: from section 1.
2. Profile picture `brand/profile_1080.png`, cover `brand/fb_cover_1640x624.png`.
3. Page → Settings → **Linked accounts → Instagram → Connect** → log in to `@kovaiminnal`.
4. Page → Settings → Page setup → **Page access**: you must have full control (needed for the token in step 8).

## 4. Google side (you, logged in as the NEW Gmail)

1. **Sheet**: sheets.new → name it `Kovai Minnal Log` → rename the first tab to **`News`** → paste this header into row 1 (A1, one cell per word – paste as one line, then Data → Split text to columns → separator: comma):

   ```
   story_id,researched,published,headline_ta,headline_en,category,location,importance,verification,source,other_sources,review_page,doc,notion,caption,email_sent,gmail_id,review,post_to,reel,reel_script,slides_spec,post_status,posted_at,spare_link,coimbatore_link,reel_link,notes,batch,prompts,images
   ```
   (31 columns, A … AE. The other tabs – All News, Pick, Comments – are created by the script itself.)
   Copy the Sheet id from the address bar: `docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit`.
2. **Drive folder**: drive.google.com → New folder `Kovai Minnal` → open it → copy the id from the address bar: `drive.google.com/drive/folders/`**`THIS_PART`**.

## 5. Cloudinary (you)

1. cloudinary.com → sign up free with the new Gmail. Dashboard → copy the **Cloud name**.
2. Settings (gear) → **Upload → Upload presets → Add upload preset** → Name `kovaiminnal`, **Signing mode: Unsigned**, Folder `kovaiminnal` → Save.

## 6. Keys – paste them into ONE file: `/home/nathi/coimbatore insta/.env` (never pushed; only you see it)

Already filled: `GEMINI_API_KEY` (from Namenector, free – its Google project must have **no billing**), `NVIDIA_API_KEY`,
`CLOUDFLARE_ACCOUNT_ID` (FashionFreelancing Cloudflare account), `CLOUDINARY_PRESET=kovaiminnal`.

You paste (open the file in any editor, put the value after `=`):

| Line in .env | Where you get it | Cost |
|---|---|---|
| `GROQ_API_KEY=` | your existing Groq key | free |
| `CLOUDFLARE_API_TOKEN=` | dash.cloudflare.com (FashionFreelancing login) → My Profile → API Tokens → Create Token → template **"Workers AI"** → Create → copy | free (~230 pictures/day) |
| `CLOUDINARY_CLOUD=` | step 5 | free |
| `BRIDGE_URL=` and `BRIDGE_KEY=` | step 8 | free |
| `ANTHROPIC_API_KEY=` (optional) | console.anthropic.com → API keys (prepaid credits) – backup writer, ~₹20/day | paid, optional |
| `FAL_KEY=` (optional) | fal.ai → API keys (prepaid) – pictures after Cloudflare's free daily allowance | paid, optional |

Then step 10.3 copies everything from `.env` to GitHub in one command.

## 7. Send me (Claude) these 5 values – not secret, but keep them out of public places

`SHEET_ID`, `ROOT_FOLDER_ID`, the new Gmail (`OWNER_EMAIL`), Cloudinary `CLOUD_NAME`, upload preset name (`kovaiminnal`).
**(Claude)** I write them into `apps_script/Code.local.gs` (a copy that is never pushed to GitHub).

## 8. Apps Script bridge (you, NEW Gmail)

1. script.google.com → **New project** → name `Kovai Minnal bridge` → delete the sample → paste the whole `apps_script/Code.local.gs` → Save.
2. Run (top bar) the function **`setup`** → allow every permission Google asks (Gmail, Sheets, Drive). It creates `BRIDGE_KEY`, the Voice folder, a 5-minute mail trigger and the weekly Instagram token refresh.
3. Run **`authorizeForms`** once → allow (needed by the pick / comment pages).
4. **Deploy → New deployment → type Web app** → Execute as: **Me** → Who has access: **Anyone** → Deploy → copy the **Web app URL** (this is `BRIDGE_URL`).
5. Project Settings (gear) → **Script properties**: copy the value of `BRIDGE_KEY` (for step 10). Add the property `IG_TOKEN_COIMBATORE` in step 9.

After every later change to `Code.gs`: paste the new `Code.local.gs`, run `setup` again, Deploy → Manage deployments → pencil → Version: **New version** → Deploy (the URL stays the same).

## 9. Meta tokens (you, in the browser) - Meta Unified login, exactly like Chennai Minnal

Our Meta app **Minnal Pages** is new, and Meta gives new apps only the "Unified login" (system-user token, `graph.facebook.com`).
The code supports it since 14 Nov: `poster/config.json` `"instagram": {"api": "unified", "user_id": ""}`. While `user_id` is empty,
Kovai stays on the old Instagram login; once Claude fills the id, every Kovai job uses the Unified login. Never paste a token into the chat.

The screens are the same ones used for chennaiminnal on 13 Nov (Business settings of the portfolio **Minnal Media**). If a menu
name is different on your screen, stop and paste the page text to Claude. If Meta shows any warning: **stop**.

**Instagram (token goes into the Kovai Minnal bridge):**
1. `@kovaiminnal` is a professional (Business) account and is linked to the Facebook Page Kovai Minnal
   (Page → Settings → Linked accounts → Instagram). You do the Instagram side yourself.
2. Business settings → portfolio **Minnal Media** → Accounts → **Instagram accounts** → **Add** → `@kovaiminnal` (you log in).
   Check that Accounts → **Pages** lists Kovai Minnal.
3. Users → **System users** → **minnal-bot** → **Assign assets**: the Instagram account `@kovaiminnal` (all tasks: content, comments,
   insights) and the Page Kovai Minnal (full control) → Save.
4. The token: minnal-bot's token (the one Chennai already uses) reaches every account assigned to minnal-bot, so use it again:
   script.google.com → **Minnal bridge** → Project Settings → Script properties → `IG_TOKEN_CHENNAI` → copy the value (starts with `EAA`).
   Never press **Revoke tokens** - that stops Chennai too.
5. script.google.com → **Kovai Minnal bridge** (not "Minnal bridge") → Project Settings → Script properties → `IG_TOKEN_COIMBATORE`
   = that token → Save. (Paste the 14 Nov Code.gs first - step 8 "after every later change" - so the bridge never tries to refresh it.)

**Facebook Page token + the Instagram account id:** in this folder `bash tools/meta_fb_token.sh` → paste the same token (hidden; it is
used as it is). It saves `FB_PAGE_ID_COIMBATORE` and `FB_TOKEN_COIMBATORE`, and its page list shows
`Kovai Minnal (Instagram: kovaiminnal, account id 17841...)`. Send that account id to Claude (it is not secret).
Claude writes it into `poster/config.json` → `instagram.user_id` and commits; you push. Only from then on Kovai uses the Unified login.

**Check (posts nothing) - only after that push:** Actions → **ig-probe** → Run (reads the account, recent posts, reel insights and the
posting quota) and **Facebook check** → Run. Claude reads the results. If ig-probe says a permission is missing (comments or insights):
minnal-bot → **Generate token** → app **Minnal Pages** → expiry **Never** → add `instagram_basic`, `instagram_content_publish`,
`instagram_manage_comments`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`,
`business_management` → copy → put it into `IG_TOKEN_COIMBATORE` (a new token does not stop the old one - only Revoke does).

## 10. GitHub (you – Claude never pushes)

1. **Create the public repo and push** (in this folder, in the Claude prompt type `!` first, or in any terminal):
   ```
   cd "/home/nathi/coimbatore insta"
   gh repo create nithiyananthamQA/kovaiminnal-autopost --public --source . --remote origin --push
   ```
2. **Right away, switch off every scheduled workflow** (nothing may run before go-live):
   ```
   for w in post.yml pick.yml powercut.yml rasipalan.yml comments.yml insights.yml; do gh workflow disable "$w" -R nithiyananthamQA/kovaiminnal-autopost; done
   ```
   Why: his `PAUSED` variable is read by no code, and the `LIVE` file only stops the 5-minute scheduled posting – pick, powercut and
   rasipalan post on their own schedule. A disabled workflow never runs.
3. **Secrets:** `bash tools/set_secrets.sh` – copies every key from `.env` to the repository's secrets (asks only for an empty required one).
4. **Facebook secrets:** `bash tools/meta_fb_token.sh` (step 9, Facebook part).
5. Repository → Settings → Actions → General → Workflow permissions: **Read and write** (the bot commits its state).

## 11. Test – nothing is posted (you run, from GitHub → Actions → workflow → Run workflow)

1. **tests** – 335 tests must pass.
2. **ig-probe** – reads the Instagram account with the token (no post).
3. **Facebook check** – shows which Facebook page the secrets point to.
4. **pick** → `dry = 1` – collects today's Coimbatore news and shows the list (nothing written or posted).
5. **powercut** → `dry = 1`.
6. **Post stories** → `dry_run` – builds a reel without posting; download it from the run's artifacts and check it.
   A disabled workflow cannot be run by hand either: `gh workflow enable <file> -R nithiyananthamQA/kovaiminnal-autopost`, run the
   test, then `gh workflow disable <file> -R ...` again (tests, ig-probe and Facebook check have no schedule – they never need it).

## 12. Go live (you)

1. Add the `LIVE` file and push:
   ```
   cd "/home/nathi/coimbatore insta" && echo "$(date -u '+%Y-%m-%d %H:%M UTC') - Kovai Minnal live" > LIVE && git add LIVE && git commit -m "Go live" && git push
   ```
2. Actions → **collect-switch → start** (writes `research_free/ENABLED` and `START_AT` = now, exactly like his).
3. Switch the scheduled workflows on:
   ```
   for w in post.yml pick.yml powercut.yml rasipalan.yml comments.yml insights.yml; do gh workflow enable "$w" -R nithiyananthamQA/kovaiminnal-autopost; done
   ```
4. **keeper** (owner 14 Nov: GitHub's own timer almost never starts the jobs - 1 scheduled run in a whole day; no Apps Script step).
   `keeper.yml` (tools/keeper.py) runs all the time on GitHub and starts every switched-on workflow at its own cron times, each time once,
   with the inputs of a scheduled run (post.yml `timer` = needs `LIVE`; pick.yml `top` 8 at 06:00, else 6). Once step 3 is done the jobs
   start within 5 minutes. Check that keeper runs: Actions → **keeper** (one run in progress); if none, **Run workflow** once.
   (The bridge's Google timer, `startKovaiTimer`, is not needed.)
5. First posts come at the next 06:00 / 10:00 / 19:00 pick or the next power-cut notice (a pick time less than an hour ago,
   e.g. 10:00 when step 3 is done at 10:40, starts at once - keeper starts a missed time up to 60 minutes late).

**Stop everything at once:** run the step-10.2 `disable` line again (keeper never starts a disabled workflow;
`gh workflow disable keeper.yml` stops keeper itself - the district job too). Deleting `LIVE` stops only the 5-minute posting (GitHub's and keeper's); posts started by
pick / powercut and manual runs do not look at `LIVE`.

## Cost

₹0: public GitHub repo (free Actions minutes), free Gemini (no billing on its project), Groq, Cloudflare (10,000 neurons a day), NVIDIA credits,
Cloudinary free plan, edge-tts Valluvar voice. Only `FAL_KEY` would cost money, and it is left empty.
