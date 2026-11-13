#!/usr/bin/env bash
# Kovai Minnal - copies the keys from this project's .env (git-ignored) into the GitHub repository's secrets in one go.
# Fill .env once; values are never printed. A secret that is empty in .env is asked for (hidden; Enter = skip).
#
#   bash tools/set_secrets.sh                      # repository nithiyananthamQA/kovaiminnal-autopost
#   REPO=owner/name bash tools/set_secrets.sh
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=${REPO:-nithiyananthamQA/kovaiminnal-autopost}
NEEDED="BRIDGE_URL BRIDGE_KEY GEMINI_API_KEY GROQ_API_KEY NVIDIA_API_KEY CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID CLOUDINARY_CLOUD CLOUDINARY_PRESET"
OPTIONAL="ANTHROPIC_API_KEY FAL_KEY SARVAM_API_KEY POLLINATIONS_API_KEY TOGETHER_API_KEY DISTRICT_BRIDGE_URL DISTRICT_BRIDGE_KEY"

val_from_env() {      # value of $1 in .env ('' when missing)
  [ -f .env ] || return 0
  sed -n "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*//p" .env | tail -1 | sed "s/^[\"']//; s/[\"']\$//" | tr -d '\r'
}

echo "Secrets for $REPO (values come from .env; nothing is printed)."
for name in $NEEDED $OPTIONAL; do
  v=$(val_from_env "$name")
  if [ -z "$v" ]; then
    case " $OPTIONAL " in *" $name "*) echo "  $name: empty in .env - skipped (optional)"; continue;; esac
    read -rsp "  $name is empty in .env - type it now (hidden, Enter = skip): " v; echo
    v=$(printf '%s' "$v" | sed 's/\x1b\[20[01]~//g' | tr -d '[:space:][:cntrl:]')
    [ -n "$v" ] || { echo "  $name: skipped"; continue; }
  fi
  printf '%s' "$v" | gh secret set "$name" -R "$REPO"
  echo "  $name: set"
done
echo
echo "Set now: $(gh secret list -R "$REPO" --json name -q '[.[].name] | join(", ")')"
echo "Facebook secrets come from: bash tools/meta_fb_token.sh"
