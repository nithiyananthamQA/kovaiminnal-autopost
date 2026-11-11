# District power-cut pages ("<District> Minnal")

37 Instagram + Facebook pages, one per Tamil Nadu district (all except Coimbatore). Each page posts **only power-cut notices of its
own district**, as soon as the paper publishes them. Kovai Minnal (all Coimbatore news) is a separate setup and is never touched.

## The switch

`poster/config.json`:

```json
"district_powercut": {"enabled": false, "disabled": []}
```

- `enabled: false` = the district job stops in its first step; Kovai Minnal runs exactly as before.
- `disabled: ["salem"]` = that district stays off while the others run.

## What is where

| Path | What |
|---|---|
| `districts/districts.json` | the 37 pages: names, handle, Dinamalar page, Tamil follow lines, bios |
| `districts/<key>/logo.png`, `footer.png` | each page's own logo + reel footer (`upload/` = profile picture + Facebook cover, not in git) |
| `districts/pipeline.py` | switches the Kovai Minnal pipeline to one district (own Sheet, own state, own texts) |
| `districts/main.py` | `list`, `find`, `write <key>`, `post <key>`, `verify <key>` |
| `districts/make_bridge.py` | makes `apps_script/Code.districts.gs` (the districts' own bridge) from Kovai's `Code.gs` |
| `districts/state/<key>/` | saved by the GitHub job: cuts found, writer state, Facebook state |
| `.github/workflows/district_powercut.yml` | every 30 min 5:35 AM - 9:35 PM IST: find, then one job per district with a new cut |

## Setup (once, before switching on)

1. New Google Sheet "Minnal Power Cut Pages Log" (same columns as Kovai's, tab `News`) in the kovaiminnalnews Drive.
2. New Apps Script project bound to it: paste `apps_script/Code.districts.gs`, fill SHEET_ID / ROOT_FOLDER_ID / OWNER_EMAIL /
   CLOUD_NAME / UPLOAD_PRESET, script property `BRIDGE_KEY` (a new one), run setup, deploy as web app.
3. GitHub secrets: `DISTRICT_BRIDGE_URL`, `DISTRICT_BRIDGE_KEY` (never Kovai's - the job refuses it).
4. Per page (when its Instagram + Facebook page exist): Apps Script property `IG_TOKEN_<KEY>` (e.g. `IG_TOKEN_SALEM`),
   GitHub secrets `FB_PAGE_ID_<KEY>` and `FB_TOKEN_<KEY>`. A page without them is skipped for that platform.
5. Free test: Actions → district-powercut → Run workflow with `dry = 1` (finds and shows, writes and posts nothing).
6. Switch on: `"enabled": true`, with the districts that are not ready yet in `"disabled"`.

GitHub allows 100 secrets per repository: 37 × 2 Facebook secrets + about 17 others fits.
