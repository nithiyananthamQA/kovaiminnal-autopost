#!/usr/bin/env bash
# Minnal pages - one-time Facebook Page token setup (adapted from the Namenector social bot's meta-token.sh).
# Turns the short-lived user token from Graph API Explorer into a Page token that never expires and saves
#   FB_PAGE_ID_COIMBATORE and FB_TOKEN_COIMBATORE
# as GitHub secrets of THIS repository only (never Namenector's META_* secrets). Nothing secret is printed.
#
#   bash tools/meta_fb_token.sh                       # repository nithiyananthamQA/kovaiminnal-autopost
#   REPO=owner/name bash tools/meta_fb_token.sh       # another repository
#
# Instagram is NOT set here: the Instagram token lives in the Apps Script (Script property IG_TOKEN_COIMBATORE), see docs/SETUP_KOVAI_MINNAL.md.
#   bash tools/meta_fb_token.sh chennai               # a district page: FB_PAGE_ID_CHENNAI / FB_TOKEN_CHENNAI
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=${REPO:-nithiyananthamQA/kovaiminnal-autopost}
DKEY=${1:-}
if [ -z "$DKEY" ] || [ "$DKEY" = "coimbatore" ]; then
  SKEY=COIMBATORE; LABEL="Kovai Minnal"; MATCH='(?i)kovai|கோவை'
else
  EN=$(jq -r --arg k "$DKEY" '.districts[$k].en // empty' districts/districts.json)
  [ -n "$EN" ] || { echo "Unknown district '$DKEY' (see districts/districts.json)."; exit 1; }
  SKEY=$(printf '%s' "$DKEY" | tr '[:lower:]' '[:upper:]'); LABEL="$EN Minnal"; MATCH="(?i)^$EN Minnal"
fi
V=${META_GRAPH_VERSION:-v24.0}
G="https://graph.facebook.com/$V"

# Our own Meta app "Minnal Pages" (made 13 Nov 2026 by the Kovai Minnal Facebook account; no longer Namenector Social).
# Its secret is asked once (hidden) and kept only on this laptop in ~/.config/minnal-pages/meta-app (never in git).
SAVED="$HOME/.config/minnal-pages/meta-app"
if [ -f "$SAVED" ]; then
  # shellcheck source=/dev/null
  . "$SAVED"
  echo "Using the saved Minnal Pages App ID and secret."
else
  read -rp  "App ID [1448178013559937]: " APP_ID
  APP_ID=${APP_ID:-1448178013559937}
  read -rsp "App secret (hidden; App settings -> Basic -> App secret -> Show): " APP_SECRET; echo
  mkdir -p "$(dirname "$SAVED")" && umask 077 && printf 'APP_ID=%q\nAPP_SECRET=%q\n' "$APP_ID" "$(printf '%s' "$APP_SECRET" | tr -d '[:space:][:cntrl:]')" > "$SAVED"
fi
read -rsp "User token from Graph API Explorer (hidden): " SHORT; echo
clean() { printf '%s' "$1" | sed 's/\x1b\[20[01]~//g' | tr -d '[:space:][:cntrl:]'; }
APP_ID=$(clean "$APP_ID"); APP_SECRET=$(clean "$APP_SECRET"); SHORT=$(clean "$SHORT")

api() {
  local out
  out=$(curl -sS -g "$G/$1" 2>/dev/null) || { echo "Could not reach Meta (network error)." >&2; exit 1; }
  if echo "$out" | jq -e '.error' >/dev/null 2>&1; then
    echo "Meta said: $(echo "$out" | jq -r '.error.message')" >&2
    echo "$2" >&2
    exit 1
  fi
  printf '%s' "$out"
}

# a system-user token (Business settings -> System users -> Generate token, "Never") is already long-lived: used as it is
LONG=$(curl -sS -g "$G/oauth/access_token?grant_type=fb_exchange_token&client_id=$APP_ID&client_secret=$APP_SECRET&fb_exchange_token=$SHORT" 2>/dev/null | jq -r '.access_token // empty' 2>/dev/null || true)
if [ -z "$LONG" ]; then LONG=$SHORT; echo "Token used as it is (system-user token)."; fi

echo "Token belongs to: $(api "me?fields=name&access_token=$LONG" "Could not read the token's owner." | jq -r '.name')"
FIELDS='id,name,access_token,instagram_business_account%7Bid,username%7D'
PAGES=$(api "me/accounts?fields=$FIELDS&access_token=$LONG" "Could not list your Pages.")
if [ "$(echo "$PAGES" | jq '.data | length')" -eq 0 ]; then
  BIZ=$(api "me/businesses?fields=name,owned_pages%7B$FIELDS%7D,client_pages%7B$FIELDS%7D&access_token=$LONG" "(Business Pages need business_management; skipped.)") || BIZ='{"data":[]}'
  PAGES=$(echo "$BIZ" | jq '{data: [.data[] | (.owned_pages.data // []) + (.client_pages.data // []) | .[] | select(.access_token)] | unique_by(.id)}')
fi
echo
echo "Your Pages:"
echo "$PAGES" | jq -r '.data[] | "  \(.id)  \(.name)  (Instagram: \(.instagram_business_account.username // "not linked"))"'
COUNT=$(echo "$PAGES" | jq '.data | length')
[ "$COUNT" -gt 0 ] || { echo "No Pages found. Tick the $LABEL Page when Facebook asks, then run this again."; exit 1; }
# pick the page automatically when its name says so; otherwise ask
PAGE_ID=$(echo "$PAGES" | jq -r --arg m "$MATCH" '[.data[] | select(.name | test($m))][0].id // empty')
if [ -z "$PAGE_ID" ]; then read -rp "Page ID of $LABEL: " PAGE_ID; else echo "Using page $PAGE_ID (name matches $LABEL)."; fi
case "$(echo "$PAGES" | jq -r --arg id "$PAGE_ID" '.data[] | select(.id == $id) | .name')" in
  *amenector*|*ame*ector*) echo "That is the Namenector page - stopping (this script is for the Minnal pages only)."; exit 1;;
esac

PAGE_TOKEN=$(echo "$PAGES" | jq -r --arg id "$PAGE_ID" '.data[] | select(.id == $id) | .access_token')
[ -n "$PAGE_TOKEN" ] || { echo "Page $PAGE_ID not found in the list."; exit 1; }

DEBUG=$(api "debug_token?input_token=$PAGE_TOKEN&access_token=$APP_ID%7C$APP_SECRET" "Could not check the Page token.")
EXPIRES=$(echo "$DEBUG" | jq -r '.data.expires_at')
SCOPES=$(echo "$DEBUG" | jq -r '.data.scopes | join(", ")')
echo "Page token expires: $([ "$EXPIRES" = "0" ] && echo never || date -d "@$EXPIRES")"
echo "Permissions: $SCOPES"
for need in pages_show_list pages_read_engagement pages_manage_posts; do
  case ", $SCOPES," in *", $need,"*) ;; *) echo "Missing permission: $need. Add it in Graph API Explorer and run this again."; exit 1;; esac
done

printf '%s' "$PAGE_ID"    | gh secret set "FB_PAGE_ID_$SKEY" -R "$REPO"
printf '%s' "$PAGE_TOKEN" | gh secret set "FB_TOKEN_$SKEY" -R "$REPO"
echo
echo "Saved FB_PAGE_ID_$SKEY and FB_TOKEN_$SKEY to $REPO."
