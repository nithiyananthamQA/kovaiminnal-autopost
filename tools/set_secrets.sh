#!/usr/bin/env bash
# Kovai Minnal - asks for each GitHub secret (typed hidden, never printed or saved) and stores it in the repository.
# Press Enter on an empty line to skip a secret (optional ones can stay empty).
#
#   bash tools/set_secrets.sh                      # repository nithiyananthamQA/kovaiminnal-autopost
#   REPO=owner/name bash tools/set_secrets.sh
set -euo pipefail
REPO=${REPO:-nithiyananthamQA/kovaiminnal-autopost}
echo "Secrets for $REPO (Enter = skip)."
NEEDED="BRIDGE_URL BRIDGE_KEY GEMINI_API_KEY GROQ_API_KEY NVIDIA_API_KEY CLOUDFLARE_API_TOKEN CLOUDFLARE_ACCOUNT_ID CLOUDINARY_CLOUD CLOUDINARY_PRESET"
OPTIONAL="SARVAM_API_KEY POLLINATIONS_API_KEY TOGETHER_API_KEY FAL_KEY"
have=$(gh secret list -R "$REPO" --json name -q '.[].name' 2>/dev/null || true)
for name in $NEEDED $OPTIONAL; do
  tag="needed"; case " $OPTIONAL " in *" $name "*) tag="optional";; esac
  case " $(echo $have) " in *" $name "*) state="(already set - Enter keeps it)";; *) state="";; esac
  read -rsp "$name [$tag] $state: " v; echo
  v=$(printf '%s' "$v" | sed 's/\x1b\[20[01]~//g' | tr -d '[:space:][:cntrl:]')
  [ -n "$v" ] || continue
  printf '%s' "$v" | gh secret set "$name" -R "$REPO"
done
echo
echo "Set now: $(gh secret list -R "$REPO" --json name -q '[.[].name] | join(", ")')"
echo "Facebook secrets come from: bash tools/meta_fb_token.sh"
