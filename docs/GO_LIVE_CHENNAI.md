# Chennai Minnal: setup to go live (browser)

You do every step by hand in the browser. Claude does not open Instagram or Facebook.
Copy each grey block exactly. Never paste a token or password into the Claude chat.
Profiles, pictures and bios stay as they are. This is only the setup.

Same `.env`, same AI keys, same Cloudinary and same GitHub repo as Kovai Minnal.
The one new thing is Chennai's own Sheet + Apps Script (its "bridge"), so Chennai rows never mix with Kovai's.

If Meta shows any warning ("automation", "confirm it's you", checkpoint): **stop** and tell Claude.

---

## Step 1: Chennai Sheet (Google, logged in as kovaiminnalnews@gmail.com)

1. Open:
   ```
   https://sheets.new
   ```
2. Click the title "Untitled spreadsheet" and type:
   ```
   Minnal Power Cut Pages Log
   ```
3. Bottom tab "Sheet1": right-click → **Rename**:
   ```
   News
   ```
4. Click cell **A1**, paste this line:
   ```
   story_id,researched,published,headline_ta,headline_en,category,location,importance,verification,source,other_sources,review_page,doc,notion,caption,email_sent,gmail_id,review,post_to,reel,reel_script,slides_spec,post_status,posted_at,spare_link,coimbatore_link,reel_link,notes,batch,prompts,images
   ```
   Then menu **Data → Split text to columns**. Row 1 now fills A to AE.
5. From the address bar, copy the part between `/d/` and `/edit` and send it to Claude in the chat (it is not secret).
   Claude puts it into `apps_script/Code.districts.local.gs`. Wait until Claude says "ready".

## Step 2: Chennai Apps Script (same Google login, after Claude says "ready")

1. Open:
   ```
   https://script.google.com/home/projects/create
   ```
2. Click "Untitled project" and type:
   ```
   Minnal Power Cut Pages bridge
   ```
3. In VS Code open `apps_script/Code.districts.local.gs` → Ctrl+A → Ctrl+C.
   In the Apps Script editor: Ctrl+A → Ctrl+V (replaces the sample) → Ctrl+S.
4. Top bar function list → **runFirst** → **Run** → allow every permission
   (if Google says "unsafe": **Advanced → Go to Minnal Power Cut Pages bridge → Allow**).
5. Function list → **authorizeForms** → **Run** → allow.
6. **Deploy → New deployment** → gear → **Web app** → Execute as: **Me** → Who has access: **Anyone** → **Deploy** → copy the **Web app URL**.
7. In VS Code open `.env`, paste the URL after this text, save:
   ```
   DISTRICT_BRIDGE_URL=
   ```
   Tell Claude "bridge done". Claude tests it.

## Step 3: give chennaiminnal access to the app (OLD Facebook profile)

The Meta app "Namenector Social" belongs to your old profile **Nithiyanantham Suriyanarayanan**.
Use a **separate Chrome profile** for it. Do not use "Switch account" in Browser 1.

1. Open:
   ```
   https://developers.facebook.com/apps/1023752790742303/roles/roles/
   ```
2. **Add People** → role **Instagram Tester** → username:
   ```
   chennaiminnal
   ```
   → **Add**.
3. **Add People** again → role **Developer** → the new Facebook account **Nithiyanantham S**
   (paste its profile link: in Browser 1 click your name, copy the address bar). Needed for the Facebook token in step 7.

## Step 4: accept the invites

1. Browser where **chennaiminnal** is logged in on instagram.com. Open:
   ```
   https://www.instagram.com/accounts/manage_access/
   ```
   Tab **Tester Invites** → **Accept**.
2. Browser 1 (Facebook **Nithiyanantham S**). Open:
   ```
   https://developers.facebook.com/requests/
   ```
   → **Accept**. (If it asks to register as a developer first: do it, then accept.)

## Step 5: Chennai Instagram token (OLD Facebook profile)

1. Open:
   ```
   https://developers.facebook.com/apps/1023752790742303/use_cases/
   ```
   → **Manage messaging & content on Instagram** → **API setup with Instagram login**.
2. Permissions must include:
   ```
   instagram_business_basic, instagram_business_content_publish, instagram_business_manage_comments, instagram_business_manage_insights
   ```
3. **Generate access tokens** → **Add account** → Instagram login window → log in as **chennaiminnal** (you type the password) → **Allow**.
4. Next to chennaiminnal → **Generate token** → tick "I understand" → **Copy**.
5. Chennai Apps Script (step 2) → **Project Settings** (gear, left) → **Script properties** → **Add script property**. Property:
   ```
   IG_TOKEN_CHENNAI
   ```
   Value: paste the token → **Save script properties**. The script renews it every Sunday by itself.

## Step 6: GitHub (terminal in VS Code; Claude never pushes)

Paste one block at a time.

1. Create the repo and push main:
   ```
   cd "/home/nathi/coimbatore insta" && gh repo create nithiyananthamQA/kovaiminnal-autopost --public --source . --remote origin && git push -u origin main
   ```
2. **Right away** switch off every scheduled job (nothing may post before the test):
   ```
   for w in post.yml pick.yml powercut.yml rasipalan.yml comments.yml insights.yml district_powercut.yml; do gh workflow disable "$w" -R nithiyananthamQA/kovaiminnal-autopost; done
   ```
3. Copy the keys from `.env` to GitHub (asks only for empty ones; press Enter to skip):
   ```
   bash tools/set_secrets.sh
   ```
4. Let the bot save its state:
   ```
   gh api -X PUT repos/nithiyananthamQA/kovaiminnal-autopost/actions/permissions/workflow -f default_workflow_permissions=write
   ```

## Step 7: Chennai Facebook token (Browser 1, Facebook Nithiyanantham S)

1. Open:
   ```
   https://developers.facebook.com/tools/explorer/
   ```
2. Right side: Meta App **Namenector Social** → User or Page: **Get User Access Token**.
   Add permissions:
   ```
   pages_show_list, pages_read_engagement, pages_manage_posts
   ```
   → **Generate Access Token** → tick **only Chennai Minnal** → Continue → **Copy** the token.
3. Terminal:
   ```
   bash tools/meta_fb_token.sh chennai
   ```
   Paste the token when it asks (hidden). It saves `FB_PAGE_ID_CHENNAI` and `FB_TOKEN_CHENNAI`.

## Step 8: test (nothing is posted)

```
gh workflow run tests.yml -R nithiyananthamQA/kovaiminnal-autopost
```
```
gh workflow enable district_powercut.yml -R nithiyananthamQA/kovaiminnal-autopost && gh workflow run district_powercut.yml -R nithiyananthamQA/kovaiminnal-autopost -f dry=1 -f districts=chennai
```
Tell Claude "tests started". Claude reads the results.
(The Chennai switch in `poster/config.json` is still off, so the timed runs do nothing.)

## Step 9: switch on

Claude switches Chennai on in `poster/config.json` and commits. You push:
```
cd "/home/nathi/coimbatore insta" && git push origin main
```
First Chennai post: Claude shows it to you. Also open it on Facebook while logged out, to check strangers can see it.

---

Chennai all news (like Kovai): Claude builds it next. Until then Chennai posts power cuts only.
