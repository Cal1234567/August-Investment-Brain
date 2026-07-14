from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
CLIENT_PATH = ROOT / "skills" / "investment-brain" / "scripts" / "brain_api.py"
SPEC = importlib.util.spec_from_file_location("distributed_brain_api", CLIENT_PATH)
assert SPEC and SPEC.loader
CLIENT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLIENT)


class FakeCache:
    def __init__(self):
        self.has_state_changed = True

    def deserialize(self, value):
        self.old = value

    def serialize(self):
        return "serialized-cache"


def fake_msal(app_class):
    return types.SimpleNamespace(
        SerializableTokenCache=FakeCache,
        PublicClientApplication=app_class,
    )


class BrainApiAuthTests(unittest.TestCase):
    def test_static_key_keeps_precedence(self):
        config = {"tenant_id": "t", "client_id": "c", "api_scope": "api://brain/access"}
        with patch.dict(os.environ, {"BRAIN_API_KEY": "local-key"}, clear=True):
            self.assertEqual(CLIENT._credential(config), "local-key")

    def test_incomplete_entra_configuration_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            Path, "home", return_value=Path("C:/tmp/brain-auth-test-home")
        ):
            with self.assertRaisesRegex(RuntimeError, "BRAIN_ENTRA_CLIENT_ID, BRAIN_API_SCOPE"):
                CLIENT._credential({"tenant_id": "tenant"})

    def test_interactive_flow_returns_token_and_updates_cache(self):
        class App:
            def __init__(self, client_id, authority, token_cache):
                self.authority = authority

            def get_accounts(self):
                return []

            def acquire_token_interactive(self, scopes):
                self.scopes = scopes
                return {"access_token": "interactive-token"}

        config = {
            "tenant_id": "tenant",
            "client_id": "client",
            "api_scope": "api://brain/access_as_user",
            "token_cache_file": "C:/tmp/brain-auth-test-cache.json",
        }
        with patch.dict(os.environ, {}, clear=True), patch.object(
            Path, "home", return_value=Path("C:/tmp/brain-auth-test-home")
        ), patch.dict(
            sys.modules, {"msal": fake_msal(App)}
        ), patch.object(CLIENT, "_save_token_cache") as save_cache, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(CLIENT._credential(config), "interactive-token")
        save_cache.assert_called_once()

    def test_guarded_call_blocks_every_route_until_onboarding_is_complete(self):
        with patch.object(
            CLIENT, "_request", return_value={"ok": True, "profile": None}
        ) as request:
            data = CLIENT._guarded_call("pulse", {"days": 7})
        self.assertTrue(data["onboarding_required"])
        self.assertIn("ONBOARDING_REQUIRED", data["text"])
        request.assert_called_once_with("GET", "/me/profile", None)

    def test_guarded_call_runs_requested_route_after_onboarding(self):
        completed = {"ok": True, "profile": {"onboarding_status": "completed"}}
        answer = {"ok": True, "text": "pulse answer"}
        with patch.object(CLIENT, "_request", side_effect=[completed, answer]) as request:
            data = CLIENT._guarded_call("pulse", {"days": 7})
        self.assertEqual(data, answer)
        self.assertEqual(request.call_count, 2)
        request.assert_any_call("GET", "/me/profile", None)
        request.assert_any_call("POST", "/pulse", {"days": 7})


    def test_local_reset_masks_completed_profile_until_onboarding_finishes(self):
        completed = {"ok": True, "profile": {"onboarding_status": "completed"}}
        with patch.object(CLIENT, "_onboarding_reset_pending", return_value=True):
            self.assertFalse(CLIENT._profile_is_complete(completed))
            self.assertIsNone(CLIENT._profile_for_client(completed)["profile"])
            with patch.object(CLIENT, "_request", return_value=completed):
                blocked = CLIENT._guarded_call("pulse", {"days": 7})
            self.assertTrue(blocked["onboarding_required"])
        with patch.object(CLIENT, "_onboarding_reset_pending", return_value=False):
            self.assertTrue(CLIENT._profile_is_complete(completed))

if __name__ == "__main__":
    unittest.main()
