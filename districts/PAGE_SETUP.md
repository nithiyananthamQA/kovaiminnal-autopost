# New Minnal page – checklist (Instagram + Facebook + posting)

Follow it top to bottom for every new page (Chennai and Kovai were done this way on 13–14 Nov 2026).
**Owner** = only the owner can do it (account creation, passwords, codes, legal "Accept"). **Claude** = done in Chrome / code.
Update this file whenever a step changes.

## POWER-CUT PAGE IN ONE DAY - follow this (Salem, 19 Nov 2026; owner: "each district a page ... do it correctly with full setup")

A power-cut page = Kovai's code (tools/make_page.py), only `POWERCUT_JOBS` run, its OWN Apps Script + Sheet, its OWN Meta app +
bot user + token. Nothing is shared with Kovai / Chennai except the Minnal Media portfolio and the AI keys. `<City>` / `<key>` = e.g.
Salem / salem. Ids of Salem: FB page 1415768578293777, IG salem_minnal 17841453291685225, app Salem Pages 1809521210337728,
bot salem-bot, Sheet "Salem Minnal Log", repo nithiyananthamQA/salemminnal-autopost.

**A. Facebook page (Claude, Chrome - Facebook is already logged in as the owner's profile)**
1. facebook.com/pages/creation → name `fb_name` (districts/districts.json) → categories **Media/news company** + **News & media
   website** → Create a Page.
2. Step 1: e-mail kovaiminnalnews@gmail.com, Town/city → pick "<City>, India", hours "No hours available". **No phone** (owner).
   Step 2: profile picture + cover = districts/<key>/upload/profile_1080.png + fb_cover_1640x624.png (file_upload on the hidden inputs).
   Step 3 WhatsApp: Skip. Step 4: Next. Step 5: marketing e-mails stay OFF → Done.
3. About → Intro → Bio = `fb_intro` → check the text with JS (the screenshot shows Tamil as boxes - the text is fine) → Save.
4. Account menu → switch back to "Nithiyanantham S".
5. business.facebook.com/latest/settings/pages?business_id=971402752320572 → + Add → **Add an existing Facebook Page** → search
   the name → Next → tick the terms → Add Page. The page id is shown (selected_asset_id in the URL).

**B. Instagram (OWNER, phone - the "same login" way, like Chennai)**
1. Instagram app → profile → tap the username → **Add Instagram account → Create new account** → username **`<key>_minnal`** →
   use the **same login** (no new e-mail, no new password). Name: `ig_name` (e.g. `Salem Minnal | Power Cut`).
2. Chrome: instagram.com/accounts/login/?force_authentication=1 → **Use another profile** → Claude types the username, OWNER types the
   password → Log in.
3. Claude, slowly (20 s pauses): instagram.com/accounts/edit → picture (the SECOND hidden file input took it) → Bio `ig_bio`
   (Shift+Enter between lines; check the textarea value with JS) → Submit.
4. instagram.com/accounts/convert_to_professional_account/ → **Business** → Next → Next → tick "Show category on profile" → search
   "News & media website" → Done → **Continue** → contact: e-mail kovaiminnalnews@gmail.com, Town/city "<City>, India", tick "Show
   contact info", **no phone** → Save → Done.

**C. Link (Claude + OWNER for 2 popups)**
1. Portfolio → Instagram profiles → + Add → **Add Instagram profile** → a POPUP opens (Claude cannot see popups; the Chrome
   connection may drop - reconnect with tabs_context createIfEmpty) → OWNER picks <key>_minnal → Continue / Allow.
2. Portfolio → Pages → <City> page → **Connected assets** → Connect assets → Instagram account → Log in to Instagram → POPUP →
   OWNER picks <key>_minnal → Connect. Check: "1 asset is connected".

**D. Meta app "<City> Pages" (Claude; OWNER types the Facebook password once)**
1. developers.facebook.com/apps/creation → App name `<City> Pages` → Next → filter **Content management** → tick **Manage messaging &
   content on Instagram** + **Manage everything on your Page** → Next → business **Minnal Media** → Next → Next → Create app →
   OWNER re-enters the Facebook password.
2. App settings → Basic: Privacy policy URL
   `https://github.com/nithiyananthamQA/kovaiminnal-autopost/blob/main/docs/PRIVACY.md`, User data deletion = same URL +
   `#your-choices-and-data-deletion`, Category **News** → Save changes.
3. Use cases → Customise (Instagram) → Add: instagram_basic, instagram_content_publish, instagram_manage_comments,
   **instagram_manage_insights**, pages_read_engagement (confirm "Add" in the dialog). Customise (Page) → Add: pages_manage_posts,
   **read_insights**. All show "Ready for testing".
4. Publish → Publish → "successfully published" (Live mode - strangers can see the posts).

**E. Bot user + token (Claude; OWNER copies the token)**
1. Portfolio → System users → + Add → `<key>-bot`, role Employee → Create.
2. ⋯ → Assign assets: Facebook page (Content, Community activity, Insights) + app <City> Pages (**Manage app**) + Instagram
   <key>_minnal (Content, Community activity, Insights) → Assign assets.
3. Generate token → app <City> Pages → expiry **Never** → permissions (9): business_management, instagram_basic,
   instagram_content_publish, instagram_manage_comments, instagram_manage_insights, pages_manage_posts, pages_read_engagement,
   pages_show_list, read_insights ("9 options selected") → Generate token.
4. OWNER: Copy → .env new line `<CITY>_IG_SYSTEM_TOKEN=<token>` - **no space after =** → Done.
5. Claude checks: `me` = <key>-bot, `me/permissions` = the 9, `me/accounts` = ONLY the <City> page,
   `<page id>?fields=instagram_business_account` = the Instagram id.

**F. Apps Script + Sheet (OWNER in Chrome - check the account circle shows kovaiminnalnews@gmail.com, NOT the work account)**
1. sheets.new → name `<City> Minnal Log` (leave it blank - setup adds the News tab + 31 column names). drive.google.com → New folder
   `<City> Minnal`. Send both links.
2. Claude fills apps_script/Code.local.gs of the page copy (SHEET_ID, ROOT_FOLDER_ID, OWNER_EMAIL, CLOUD_NAME, UPLOAD_PRESET) and opens it.
3. OWNER: Sheet → Extensions → Apps Script → rename `<City> Minnal bridge` → paste → Ctrl+S → function box: **setup** (NOT json_) →
   Run → Review permissions → Advanced → Go to … (unsafe) → Allow. Log shows "BRIDGE_KEY is saved" + "Voice folder".
4. Deploy → New deployment → gear → Web app → Execute as **Me**, access **Anyone** → Deploy → .env `<CITY>_BRIDGE_URL=<…/exec>`;
   Project Settings → Script properties → BRIDGE_KEY → .env `<CITY>_BRIDGE_KEY=<value>`.
5. Claude: `?action=queue&key=…` → `{"ok":true,"rows":[]}`; a wrong key → unauthorized.

**G. Code (Claude)**
1. If the reference runs the district (salem, tirupur, erode, karur, trichy, namakkal): `python3 tools/ref_lists.py <key>
   news360-tn/<key>360-autopost` (his towns, areas, power-cut searches, papers, city look). Else: AREAS + CITY_LOOK in make_page.py.
2. tools/make_page.py PAGE[<key>] = {fb_page_id, ig_user_id, handle `<key>_minnal`, repo, folder, bot, own_token True, ref, jobs
   POWERCUT_JOBS}. `python3 tools/make_page.py <key> ~/<key>minnal-autopost` → its tests must pass. `python3 tools/make_timer.py`.
   Full Kovai tests. Commit.

**H. GitHub (OWNER runs 2 scripts)**
1. `bash /tmp/<key>_setup.sh` = repo (public), secrets (BRIDGE_URL/KEY + IG_SYSTEM_TOKEN from the `<CITY>_` names; never
   DISTRICT_BRIDGE_*), push, EVERY job off.
2. Claude: one sample reel (DRY_RUN, nothing posted) → owner OK → delete the sample row from the Sheet.
3. `bash /tmp/<key>_live.sh` = push.sh (Kovai + sync), LIVE file, only POWERCUT_JOBS on, Cloudflare Worker deploy, first power-cut check.
4. Watch the first real cut post on Instagram + Facebook. Update the Status table below + memory current-task.

**Mistakes made on Salem - do NOT repeat**
- Google in Chrome was the iCliniq WORK account → always check the account circle before Sheets / Apps Script.
- Apps Script: Run started `json_` (the first function) → pick **setup** in the function box.
- Clicked the old `salemminnal` (scheduled for deletion) in the saved-profiles list → never reuse an old / deleted account.
- Instagram web sign-up with `kovaiminnalnews+salem@gmail.com` (this file already said: no new e-mail) → phone, same login.
- A coordinate click on the saved-profiles list opened the owner's personal account (layout shifted) → click by `find` ref.
- Token pasted as `NAME= value` (space) → .env broke → no spaces.
- insights.yml left out of the job list → POWERCUT_JOBS includes insights (owner: "add insight also").
- Kovai-place tests fail on a page with the reference's lists → REF_PLACE_TESTS skip them (make_page).
- Worker TIMER_URL/TIMER_KEY are not in .env → the page's posting chain sleeps on GitHub (11 min) when 2+ cuts wait. Fix later.

## Rules (learned the hard way)

- At most **1 new Instagram account and 1 new Facebook page per day**. Edit one Instagram account at a time, slowly.
- Never switch quickly between Instagram accounts in the browser (Madurai was suspended on 13 Nov for that).
- The Instagram **website keeps at most 5 logged-in accounts**. Log out / remove old ones first (☰ More → Log out → Remove).
- Any Meta warning ("automation", "confirm it's you", checkpoint): stop, owner clears it on the phone, rest 24–48 h.
- No new e-mail for any page: Facebook pages need none; Instagram accounts share the main login.
- Username pattern (owner 14 Nov): **`city_minnal`**, e.g. `kovai_minnal`.

## Who owns what

```
Meta account (kovaiminnalnews@gmail.com / owner's phone)
 ├─ Facebook profile "Nithiyanantham S"  -> owns every Facebook page
 ├─ Instagram s_nithiyanantham_s (main)  -> every page's Instagram is created under it
 └─ Business portfolio "Minnal Media" (971402752320572)
      ├─ app "Minnal Pages" (1448178013559937)
      ├─ Facebook pages + Instagram accounts of every Minnal page
      └─ system user "minnal-bot" -> ONE never-expiring token for all pages (never press "Revoke tokens")
```

## 1. Facebook page (Claude, Chrome, Browser 1)

1. facebook.com/pages/create → name `fb_name` (districts/districts.json), categories **Media/news company** + **News & media website**.
2. Profile picture + cover: `districts/<key>/upload/profile_1080.png` and `fb_cover_1640x624.png` (Kovai: `brand/`).
3. Intro `fb_intro`, e-mail kovaiminnalnews@gmail.com, city. WhatsApp: skip. Marketing e-mails: off.
4. Switch back to the profile before anything else.

## 2. Instagram account

1. **Owner, phone app:** Profile → tap the name → Add Instagram account → **Create new account** → same login → username `city_minnal`.
2. **Owner, Chrome:** log in to that account once on instagram.com (Claude types nothing secret).
3. **Claude, Chrome, slowly (pauses between steps):**
   - Edit profile → profile picture (same file as Facebook) → bio (`ig_bio`, max 150).
   - Switch to professional → **Business** → category **News & media website**, "show category" on.
   - Contact: e-mail kovaiminnalnews@gmail.com, city, "show contact info" on. No phone.
   - Public account. Post nothing by hand.
4. **Owner, phone:** Edit profile → **Name** `ig_name` (Accounts Center; Chrome cannot open it). Max 2 name changes per 14 days.

## 3. Business portfolio + bot user (Claude, Chrome: business.facebook.com/latest/settings/…?business_id=971402752320572)

1. Pages → the new page is in "Minnal Media" (if not: Add → claim page).
2. Instagram profiles → **Add** → **Add Instagram profile** → owner logs in / allows in the pop-up window.
3. Note the Instagram **account id** (ID: 17841…) shown there.
4. System users → minnal-bot → ⋯ → **Assign assets**:
   - Facebook page: Content, Community activity, Insights.
   - Instagram account: Content, Community activity, Insights.

## 4. Tokens and settings

One minnal-bot token for ALL pages (owner 14 Nov: "same account for Chennai and Kovai"). It is kept ONCE, in Apps Script
"Minnal bridge" → Script properties → `IG_TOKEN_CHENNAI`. Nothing is copied per page any more:
- Instagram: a page whose bridge has no `IG_TOKEN_<KEY>` reads the shared one (`poster/config.json` `instagram.shared_token_page`,
  `poster/ig_api.py shared_token`).
- Facebook: no `FB_PAGE_ID_<KEY>` / `FB_TOKEN_<KEY>` secrets needed - put the page id in `poster/config.json` `facebook.page_ids`
  and the Page token is read with the shared token (`poster/facebook.py shared_creds`). Secrets, when set, still win.

1. **Claude:** Facebook page id + Instagram account id: list them with the shared token (`me/accounts`; Instagram id from the portfolio).
2. **Claude:** district → `districts/districts.json` `<key>.instagram = {"api": "unified", "user_id": "<id>"}`; Kovai → `poster/config.json`
   `instagram.user_id`. Facebook page id → `poster/config.json` `facebook.page_ids.<key>`. Commit.
3. **Claude:** switch on: district → `poster/config.json` `district_powercut.live` (+ `news_live` for all news, + `comments_live` for comment
   replies e-mailed to the owner - the token needs `instagram_manage_comments` + `pages_read_engagement`). Commit; **owner pushes**.
4. **Owner:** place tags - fill the Facebook place-page ids in `districts/locations.json` (city + areas; check each on facebook.com/<id>).
   Empty id = no tag. After the first post: `location tag: …` in the log, or the id in `districts/state/<key>/locations_refused.json`.

## 5. Check before going live

1. One sample reel (Claude, local, test mode) → owner approves.
2. First real post: open the Facebook post while logged out (the app must be in **Live** mode or strangers can't see it).

## Status (14 Nov 2026)

| Page | Facebook | Instagram | Portfolio + bot | Tokens | Live |
|---|---|---|---|---|---|
| Chennai Minnal | 61596474243510 ✅ | chennaiminnal ✅ (17841452418440882) | ✅ | ✅ | ✅ power cuts + all news |
| Kovai Minnal | 61596710992967 ✅ | kovai_minnal ✅ (17841410844667843), name pending (owner, phone) | ✅ | ✅ shared token (FB page 1475639385631396) | after push |
| Madurai | dropped | maduraiminnal suspended | – | – | – |
| Salem Minnal (power cuts only, 19 Nov) | 1415768578293777 ✅ | salem_minnal ✅ (17841453291685225) | ✅ salem-bot, app Salem Pages | ✅ own token + own Apps Script | after salem_live.sh |
