# New Minnal page – checklist (Instagram + Facebook + posting)

Follow it top to bottom for every new page (Chennai and Kovai were done this way on 13–14 Nov 2026).
**Owner** = only the owner can do it (account creation, passwords, codes, legal "Accept"). **Claude** = done in Chrome / code.
Update this file whenever a step changes.

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
| Salem | dropped | salemminnal (owner deleting) | – | – | – |
