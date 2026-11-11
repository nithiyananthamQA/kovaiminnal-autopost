#!/usr/bin/env bash
# One SAMPLE reel made on this laptop exactly the way pick.yml + post.yml make it on GitHub, with this project's .env keys.
# NOTHING is posted: post.py runs with DRY_RUN=1 (render + Cloudinary upload, no Instagram / Facebook).
#   1. pick.py collect + decide   -> today's Coimbatore news, the top PICK_AUTO_TOP (default 1) chosen automatically
#   2. collect.py (MANUAL_URL)    -> writer (Gemini -> Groq), picture (article photo, else Cloudflare), story saved in the Sheet
#   3. post.py check + run        -> the reel (poster/config.json reel_design, v5), uploaded to Cloudinary, test e-mail to the owner
#
#   bash tools/sample_reel.sh                 # uses .venv (made by this script the first time)
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || { echo ".env missing"; exit 1; }
set -a; . ./.env; set +a
unset GH_TOKEN GITHUB_TOKEN GITHUB_OUTPUT GITHUB_EVENT_NAME      # never start GitHub workflows from a local sample

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r poster/requirements.txt edge-tts==7.2.3 googlenewsdecoder==0.2.2 \
    opencv-contrib-python-headless==4.10.0.84 pillow-avif-plugin==1.4.6 pyswisseph==2.10.3.2
  .venv/bin/python -m playwright install chromium
  (cd kit && npm install --no-audit --no-fund --silent)
fi
PY=.venv/bin/python

export CITY_ONLY=0 PICK_AUTO_TOP="${PICK_AUTO_TOP:-1}" PICK_EMAIL=0 PICK_WAIT_MIN=0 PICK_REQUIRE_EMAIL=0 ANTHROPIC_MODEL=claude-haiku-5-5
echo "== 1. pick today's news (top $PICK_AUTO_TOP)"
$PY -u research_free/pick.py collect
$PY -u research_free/pick.py decide
urls=$(tr '\n' ' ' < research_free/results/pick_urls.txt 2>/dev/null || true)
n=$(echo $urls | wc -w)
[ "$n" -gt 0 ] || { echo "no news picked"; exit 0; }

echo "== 2. write $n news + picture + save to the Sheet"
PICK_ONLY=1 COLLECT_MODE=both WRITE_STORIES=1 AUTO_IMAGES=1 WRITE_WORKERS=1 BUDGET_MIN=80 FRESH_DAYS=1 DAILY_CAP=1000 \
  MANUAL_URL="$urls" MAX_STORIES="$n" $PY -u research_free/collect.py
$PY -u research_free/pick.py mark || true

echo "== 3. build the reel (test mode: nothing is posted)"
# the story just written = the newest row of the Sheet (post.py alone would take the OLDEST waiting one, and test runs never mark posted)
SID=$($PY - <<'PY'
import os, requests
r = requests.get(os.environ["BRIDGE_URL"], params={"action": "recent", "key": os.environ["BRIDGE_KEY"]}, timeout=120).json()
rows = [x for x in r.get("rows", []) if x.get("story_id")]
print(rows[-1]["story_id"] if rows else "")
PY
)
echo "story: $SID"
DRY_RUN=1 $PY -u poster/post.py run $SID
echo "== done: out/$SID/${SID}_reel.mp4 (its Cloudinary link is in the log above)"
