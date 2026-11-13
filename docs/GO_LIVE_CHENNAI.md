# Chennai Minnal: setup to go live (browser)

You do every step by hand in the browser. Claude does not open Instagram or Facebook.
Copy each grey block exactly. Never paste a token or password into the Claude chat.
Profiles, pictures and bios stay as they are. This is only the setup.

Same `.env`, same AI keys, same Cloudinary, same GitHub repo as Kovai Minnal.
Chennai has its own Sheet + Apps Script ("Minnal bridge"), so Chennai news never goes to the Kovai page.

If Meta shows any warning ("automation", "confirm it's you", checkpoint): **stop** and tell Claude.

| Step | What | Status |
|---|---|---|
| 1 | Chennai Sheet | done 13 Nov |
| 2 | Apps Script "Minnal bridge" + `DISTRICT_BRIDGE_URL` in `.env` | done 13 Nov (Claude tested it) |
| 3 | Instagram token (old app Namenector Social) | next |
| 4 | GitHub | |
| 5 | Facebook token (new app Minnal Pages) | |
| 6 | Test + switch on | |

Why two apps: Meta lets **new** apps (Minnal Pages) use Instagram only through "Unified login", which needs a business
portfolio and a different API. The **old** app Namenector Social still has "API setup with Instagram login", which our code uses.
Facebook pages work fine with the new app.

---

## Step 3: Chennai Instagram token (Incognito window, OLD Facebook account)

1. Press **Ctrl+Shift+N** (Incognito). Log in to facebook.com with your **old** account (the one that owns Namenector Social).
2. Open:
   ```
   https://developers.facebook.com/apps/1023752790742303/use_cases/
   ```
   If it says "No apps yet", you are in the wrong account: log out and try your other old account.
3. **Manage messaging & content on Instagram** → **Customize** → **API setup with Instagram login**.
4. Under **Generate access tokens** → **Add account** → Instagram window → log in as **chennaiminnal** (you type the password) → **Allow**.
5. If it asks you to accept a tester invite first: in the same Incognito window open
   ```
   https://www.instagram.com/accounts/manage_access/
   ```
   tab **Tester Invites** → **Accept**. Then **Add account** again.
6. Next to chennaiminnal → **Generate token** → tick "I understand" → **Copy**.
7. Normal window, Google kovaiminnalnews: open
   ```
   https://script.google.com/home
   ```
   → **Minnal bridge** (not Kovai Minnal bridge) → **Project Settings** (gear, left) → **Script properties** → **Add script property**. Property:
   ```
   IG_TOKEN_CHENNAI
   ```
   Value: paste the token → **Save script properties**. Tell Claude "token saved" (Claude checks it without showing it).

## Step 4: GitHub (terminal in VS Code; Claude never pushes)

Paste one block at a time.

1. Create the repo and push main:
   ```
   cd "/home/nathi/coimbatore insta" && gh repo create nithiyananthamQA/kovaiminnal-autopost --public --source . --remote origin && git push -u origin main
   ```
2. **Right away** switch off every scheduled job:
   ```
   for w in post.yml pick.yml powercut.yml rasipalan.yml comments.yml insights.yml district_powercut.yml; do gh workflow disable "$w" -R nithiyananthamQA/kovaiminnal-autopost; done
   ```
3. Copy the keys from `.env` to GitHub (asks only for empty ones; Enter = skip):
   ```
   bash tools/set_secrets.sh
   ```
4. Let the bot save its state:
   ```
   gh api -X PUT repos/nithiyananthamQA/kovaiminnal-autopost/actions/permissions/workflow -f default_workflow_permissions=write
   ```

## Step 5: Chennai Facebook token (Browser 1, new Facebook account, app Minnal Pages)

1. Open:
   ```
   https://developers.facebook.com/tools/explorer/
   ```
2. Right side: Meta App **Minnal Pages** → User or Page: **Get User Access Token**. Add permissions:
   ```
   pages_show_list, pages_read_engagement, pages_manage_posts
   ```
   → **Generate Access Token** → tick **only Chennai Minnal** → Continue → **Copy** the token.
   (If those permissions are missing: app → Use cases → Add use case → **Manage everything on your Page**.)
3. Terminal:
   ```
   bash tools/meta_fb_token.sh chennai
   ```
   First time it asks the **App secret** (hidden): developers.facebook.com → Minnal Pages → **App settings → Basic** → App secret → **Show** → copy.
   Then it asks the token (hidden). It saves `FB_PAGE_ID_CHENNAI` and `FB_TOKEN_CHENNAI`.

## Step 6: test, then switch on

1. Tests + a free search (nothing posted):
   ```
   gh workflow run tests.yml -R nithiyananthamQA/kovaiminnal-autopost
   ```
   ```
   gh workflow enable district_powercut.yml -R nithiyananthamQA/kovaiminnal-autopost && gh workflow run district_powercut.yml -R nithiyananthamQA/kovaiminnal-autopost -f dry=1 -f districts=chennai
   ```
2. Claude checks the results, switches Chennai on in `poster/config.json` and commits. You push:
   ```
   cd "/home/nathi/coimbatore insta" && git push origin main
   ```
3. From then on the job looks every 30 minutes (5:35 AM - 9:35 PM) and posts each new Chennai power-cut notice by itself.
   A cut that is already over is never posted.

---

Chennai all news (like Kovai): Claude builds it next. Until then Chennai posts power cuts only.
