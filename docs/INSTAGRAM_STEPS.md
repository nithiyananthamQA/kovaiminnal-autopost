# Instagram steps: Kovai Minnal + Chennai Minnal

You do every step by hand. Claude does not open Instagram.
Copy each grey block exactly. Never paste a token or password into the Claude chat.

If Instagram shows any warning ("automation", "confirm it's you", checkpoint): **stop**, clear it on the phone, tell Claude.

Today (13 Nov) 3 new Instagram accounts were already made and maduraiminnal was suspended.
Making kovaiminnal today = 4th new account in one day. Safer: Part 1 tomorrow. Your call.

---

## Part 1: create kovaiminnal (phone, Instagram app)

1. Profile → tap **s_nithiyanantham_s** at the top → **Add Instagram account** → **Create new account** → use the same login (no e-mail).
   Username:
   ```
   kovaiminnal
   ```
2. Send `brand/profile_1080.png` from the laptop to the phone (WhatsApp to yourself or Google Drive).
   Edit profile → **Change profile picture** → that picture.
3. Edit profile → **Name**:
   ```
   Kovai Minnal | Coimbatore News
   ```
4. Edit profile → **Bio**:
   ```
   ⚡ கோவை செய்திகள் உடனுக்குடன்
   📍 மின்தடை • விபத்து • மழை • வேலை
   🔔 Follow பண்ணுங்க | Coimbatore news
   📩 செய்தி / promotions: DM
   ```
5. Menu (☰) → **Account type and tools** → **Switch to professional account** → **Business**.
   Category:
   ```
   News & media website
   ```
   Show category on profile: **ON**. (Business is required for posting.)
6. Edit profile → **Contact options**. E-mail:
   ```
   kovaiminnalnews@gmail.com
   ```
   City:
   ```
   Coimbatore
   ```
   Show contact info: **ON**. No phone.
7. Account must be **Public**. Post nothing by hand.

Do not link the Facebook page today. Posting works without it.

chennaiminnal: already set up. Do **no** profile edits on it.

---

## Part 2: give the app access (laptop, OLD Facebook profile)

The Meta app "Namenector Social" belongs to your old profile **Nithiyanantham Suriyanarayanan**.
Use a **separate Chrome profile or window** for it. Do not use "Switch account" in Browser 1.

1. Open:
   ```
   https://developers.facebook.com/apps/1023752790742303/roles/roles/
   ```
2. **Add People** → role **Instagram Tester** → username:
   ```
   kovaiminnal
   ```
   → Add. Again with:
   ```
   chennaiminnal
   ```
3. Accept the invite. Phone, Instagram app, switched to that account:
   Settings and activity → **Website permissions** → **Apps and websites** → **Tester invites** → **Accept**.
   Do it for kovaiminnal and for chennaiminnal.

Menu names on Meta change often. If a name does not match, tell Claude what you see.

---

## Part 3: Kovai Instagram token (laptop, OLD Facebook profile)

1. Open:
   ```
   https://developers.facebook.com/apps/1023752790742303/use_cases/
   ```
   → **Manage messaging & content on Instagram** → **API setup with Instagram login**.
2. Permissions must include:
   ```
   instagram_business_basic, instagram_business_content_publish, instagram_business_manage_comments, instagram_business_manage_insights
   ```
3. **Generate access tokens** → **Add account** → Instagram login window → log in as **kovaiminnal** (you type the password) → **Allow**.
4. Next to kovaiminnal → **Generate token** → tick "I understand" → **Copy**.
5. Paste it straight into the Kovai Apps Script:
   script.google.com → project **Kovai Minnal bridge** → **Project Settings** (gear) → **Script properties** → **Add script property**.
   Property:
   ```
   IG_TOKEN_COIMBATORE
   ```
   Value: paste the token → **Save script properties**.
   The script renews it every Sunday by itself.

---

## Part 4: Chennai Instagram token (wait)

Do this only **after** the district Apps Script ("Minnal Power Cut Pages" bridge) exists. It does not exist yet.
Do not generate the token earlier and keep it in a note.

Same as Part 3, but log in as **chennaiminnal**, and paste into the **district** Apps Script. Property:
```
IG_TOKEN_CHENNAI
```

---

## Not Instagram, but needed before anything posts

Claude gives these steps after the Instagram part:

1. GitHub repo (not created yet) + push, every scheduled workflow switched off first.
2. Chennai: new Sheet "Minnal Power Cut Pages Log" (Claude needs its Sheet id) + district Apps Script deployed + `DISTRICT_BRIDGE_URL`.
3. Facebook page tokens for Kovai and Chennai (the new Facebook account needs a role on the app).
4. Test runs on GitHub (nothing posted), then switch on.
