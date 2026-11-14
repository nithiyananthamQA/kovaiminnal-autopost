"""Which Instagram API Kovai Minnal talks to (14 Nov). ONE rule for every script that calls Instagram: poster/post.py and all that go
through post.ig / post.ig_account (comments.py, insights.py, ig_comments.py, ig_probe.py, story catch-up, research_free/collect.py),
and rasipalan/rasi_daily.py.

  poster/config.json  "instagram": {"api": "unified", "user_id": ""}
    user_id empty  -> Instagram login, exactly as before: graph.instagram.com, the account is "me"
                      (token IGAA..., the bridge refreshes it every Sunday)
    user_id filled -> Meta Unified login (system user, token EAA..., never expires): graph.facebook.com/v24.0 and this Instagram
                      account id. There "me" is the system user, never the page, so "me" is never asked on that host.
The token itself stays in the Apps Script bridge (Script property IG_TOKEN_COIMBATORE); nothing secret is in this file or config.json.
District pages set the same three values from districts/districts.json (districts/pipeline.py)."""
import os

LOGIN_HOST = "https://graph.instagram.com"      # Instagram API with Instagram login
UNIFIED_HOST = "https://graph.facebook.com"     # Instagram API with Facebook / Unified login (system-user token)
UNIFIED_VER = "v24.0"


def settings(config, env=None):
    """-> (host, version, Instagram account id) from config.json's "instagram" block; IG_API_VERSION / IG_USER_ID from the environment
    keep working as before on the Instagram-login host."""
    env = os.environ if env is None else env
    ver = env.get("IG_API_VERSION", "")
    ig = (config or {}).get("instagram") or {}
    uid = str(ig.get("user_id") or "").strip()
    if ig.get("api") == "unified" and uid:
        return UNIFIED_HOST, ver or UNIFIED_VER, uid
    return LOGIN_HOST, ver, env.get("IG_USER_ID", "")


def me_allowed(host):
    """'me' names the Instagram account only on the Instagram-login host"""
    return host.rstrip("/") == LOGIN_HOST


def shared_token(config, own_bridge_url="", env=None, get=None, page=""):
    """owner 14 Nov: "use the same account for Chennai and Kovai". ONE minnal-bot token (system user, never expires) serves every
    page; it is kept once, in the Minnal bridge (DISTRICT_BRIDGE_URL, Script property IG_TOKEN_<shared_token_page>).
    A page whose own bridge has no token (Kovai: no IG_TOKEN_COIMBATORE; a new district without IG_TOKEN_<KEY>) reads it from there.
    -> token, or "" (nothing secret logged)."""
    env = os.environ if env is None else env
    src = str(((config or {}).get("instagram") or {}).get("shared_token_page") or "").strip()
    url, key = env.get("DISTRICT_BRIDGE_URL", "").strip(), env.get("DISTRICT_BRIDGE_KEY", "").strip()
    if not (src and url and key) or (url == (own_bridge_url or "").strip() and str(page).lower() == src.lower()):
        return ""       # that very property is the missing one - asking again would not help
    if get is None:
        import requests
        get = requests.get
    for _ in range(3):
        try:
            data = get(url, params={"action": "token", "key": key, "page": src}, timeout=120).json()
            if data.get("ok") and data.get("token"):
                return str(data["token"]).strip()
            return ""
        except Exception:
            continue
    return ""
