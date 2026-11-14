"""owner 14 Nov: one minnal-bot token for every page, kept only in the Minnal bridge; Kovai reads it from there."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "poster"))
import ig_api  # noqa: E402

CFG = {"instagram": {"api": "unified", "user_id": "1", "shared_token_page": "chennai"}}
ENV = {"DISTRICT_BRIDGE_URL": "https://minnal", "DISTRICT_BRIDGE_KEY": "k"}


class Resp:
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


class SharedToken(unittest.TestCase):
    def test_reads_shared_page_token(self):
        seen = {}

        def get(url, params=None, timeout=None):
            seen.update(url=url, **params)
            return Resp({"ok": True, "token": "EAAx"})
        self.assertEqual(ig_api.shared_token(CFG, "https://kovai", ENV, get), "EAAx")
        self.assertEqual((seen["url"], seen["page"], seen["action"]), ("https://minnal", "chennai", "token"))

    def test_off_without_config_or_secrets(self):
        get = lambda *a, **k: Resp({"ok": True, "token": "EAAx"})  # noqa: E731
        self.assertEqual(ig_api.shared_token({"instagram": {}}, "https://kovai", ENV, get), "")
        self.assertEqual(ig_api.shared_token(CFG, "https://kovai", {}, get), "")

    def test_new_district_on_the_minnal_bridge(self):
        get = lambda *a, **k: Resp({"ok": True, "token": "EAAx"})  # noqa: E731
        self.assertEqual(ig_api.shared_token(CFG, "https://minnal", ENV, get, page="madurai"), "EAAx")
        self.assertEqual(ig_api.shared_token(CFG, "https://minnal", ENV, get, page="chennai"), "")

    def test_missing_token_gives_empty(self):
        get = lambda *a, **k: Resp({"ok": False, "error": "No Instagram token saved"})  # noqa: E731
        self.assertEqual(ig_api.shared_token(CFG, "https://kovai", ENV, get), "")


if __name__ == "__main__":
    unittest.main()
