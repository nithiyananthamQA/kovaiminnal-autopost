# Page setup checklist (Facebook page + Instagram account per district)

One place for how every Minnal page is set up, so each new district is done the same way.

## Account structure (decided 13 Nov 2026)

```
Meta Account  (login: kovaiminnalnews@gmail.com or the owner's phone)
 ├─ Facebook profile  Nithiyanantham S         <- owns every Facebook page
 │   └─ Facebook pages: Kovai Minnal, <District> Minnal ...
 └─ Instagram s_nithiyanantham_s (Business)    <- main Instagram; every page account is created under it
     └─ Instagram page accounts: chennaiminnal, maduraiminnal, salemminnal ...
```

- No new e-mail for any page. Facebook pages need none. Instagram page accounts are made in the phone app from
  s_nithiyanantham_s and share its login.
- The old account (Nathi Anand) is not used. The Kovai Gmail was removed from it.

## Pace (Meta flags fast work on new accounts)

- At most **1 new Facebook page and 1 new Instagram account per day**.
- Edit **one Instagram account per day** at most. Never switch quickly between accounts in the browser.
- Do it slowly, like a person would. Prefer the phone app for Instagram.
- If Meta shows any warning (automation, checkpoint, "confirm it's you"), **stop everything**. The owner clears it
  on the phone, then the accounts rest 24-48 hours.
- 13 Nov: Instagram flagged maduraiminnal after three new accounts were edited in one hour from the browser.

## Facebook page (Claude, in Browser 1, logged in as Nithiyanantham S)

1. facebook.com/pages/create
2. Name: `fb_name` from `districts/districts.json` (e.g. `Chennai Minnal - சென்னை மின்னல்`)
3. Categories: **Media/news company** + **News & media website**
4. Profile picture: `districts/<key>/upload/profile_1080.png`. Cover: `districts/<key>/upload/fb_cover_1640x624.png`
5. WhatsApp step: skip. Invite friends: skip. Marketing e-mails: off. Page notifications: on.
6. Bio (Intro): `fb_intro`. About/description: `fb_about`
7. Contact: e-mail kovaiminnalnews@gmail.com. No phone.
8. Switch back to the profile Nithiyanantham S before creating the next page.
9. Link the Instagram account: page Settings → Linked accounts → Instagram.

## Instagram account

Ready texts per page (username, name, bio within 150, steps): `districts/<key>/upload/instagram_details.txt`
(Kovai: `brand/instagram_details.txt`). Open them in a normal text editor; the terminal shows Tamil as boxes.

Linking Instagram to the Facebook page is **not needed for posting**. Instagram posts go through Instagram login
(graph.instagram.com, token `IG_TOKEN_<KEY>`), and Facebook posts go through the page token. Linking is still
recommended: one dashboard in Meta Business Suite, Instagram shown on the page, and Meta sees a real business.

**Owner, on the phone (no e-mail):** Instagram → Profile → tap s_nithiyanantham_s → Add Instagram account →
Create new account → use the same login → username `<key>minnal` (`handle` in districts.json).

**Then (one account per day):**
1. Profile picture: `districts/<key>/upload/profile_1080.png`
2. Name (searchable, max 30): `<District> Minnal | Power Cut`. Changed in Meta Account → profile → Name
   (only 2 changes per 14 days, so get it right the first time).
3. Bio (max 150; Instagram counts emoji as 2):
   ```
   ⚡ <Tamil district> மின்தடை அறிவிப்புகள் உடனுக்குடன்
   📍 எந்த பகுதி, எந்த நேரம் - முன்கூட்டியே
   🔔 Follow பண்ணுங்க | <District> power cut
   📩 DM for promotions
   ```
   For long names (Tiruvannamalai, Kanniyakumari) shorten line 3, or it goes over 150.
4. Account type: **Business**, category **News & media website**, "Show category on profile" ticked.
5. Contact: e-mail kovaiminnalnews@gmail.com, town/city = the district, "Show contact info" ticked. No phone.
   The Message button (DM) is on by default.
6. Public account. Post nothing by hand; the first post comes from the system.
7. Link to the district's Facebook page.
8. Later: Apps Script property `IG_TOKEN_<KEY>` and GitHub secrets `FB_PAGE_ID_<KEY>` / `FB_TOKEN_<KEY>`
   (see README.md).

## What the reference page has that we should add later

From @coimbatore360_official (followed in spirit, not copied):
- **Story highlights** (his: Raasi palan, Diwali). Add ours once there are stories, e.g. "இன்றைய மின்தடை" and "How to follow".
- **Tamil city name** as his profile name. Ours uses `<District> Minnal | Power Cut` for search. A Tamil line is already in the bio.
- **Regular posting** (258 posts). Our system posts automatically once the pages are switched on.
- His Facebook page has not been checked yet. Compare it when Facebook work resumes.

## Status (13 Nov 2026)

| Page | Facebook page | Instagram | Instagram setup |
|---|---|---|---|
| Kovai Minnal | done (id 61596710992967) | not created yet | - |
| Chennai Minnal | done (id 61596474243510): name, 2 categories, e-mail, city, bio, logo, cover | chennaiminnal | done; link to the Facebook page pending (owner, phone) |
| Madurai Minnal | dropped for now | maduraiminnal **suspended** by Instagram (180 days to appeal); left to expire | - |
| Salem Minnal | dropped for now | salemminnal: owner deleting it | - |

From 13 Nov: the owner does all Instagram work by hand on the phone. Claude does Facebook pages only, one per day.
