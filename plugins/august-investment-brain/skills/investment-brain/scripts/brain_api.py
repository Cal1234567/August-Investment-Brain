#!/usr/bin/env python3
"""Small cross-platform client for the August Investment Brain REST API."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Windows consoles default to cp1252; Brain responses carry UTF-8 punctuation.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


AUTH_ENV = {
    "tenant_id": "BRAIN_ENTRA_TENANT_ID",
    "client_id": "BRAIN_ENTRA_CLIENT_ID",
    "api_scope": "BRAIN_API_SCOPE",
}


def _config() -> dict:
    path = Path(os.environ.get("BRAIN_CONFIG_FILE", "") or Path.home() / ".august" / "investment-brain" / "config.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _static_key(config: dict) -> str | None:
    value = (os.environ.get("BRAIN_API_KEY") or "").strip()
    if value:
        return value
    configured = str(config.get("api_key_file") or "").strip()
    candidates = ([Path(configured).expanduser()] if configured else []) + [
        Path.home() / ".august" / "investment-brain" / "api-key.txt",
        Path.home() / ".claude" / "secrets" / "brain-api-key.txt",
        Path.home() / ".codex" / "secrets" / "brain-api-key.txt",
    ]
    for path in candidates:
        if path.exists():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
    return None


def _key(config: dict) -> str:
    """Return the legacy/local static credential, preserving the old contract."""
    value = _static_key(config)
    if value:
        return value
    raise RuntimeError("Investment Brain credential not found. Run investment onboarding or ask the August Brain administrator.")


def _entra_settings(config: dict) -> dict[str, str] | None:
    values = {
        key: str(os.environ.get(env_name) or config.get(key) or "").strip()
        for key, env_name in AUTH_ENV.items()
    }
    if not any(values.values()):
        return None
    missing = [AUTH_ENV[key] for key, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            "Investment Brain Entra configuration is incomplete. Set " + ", ".join(missing) + "."
        )
    return values


def _token_cache_path(config: dict) -> Path:
    configured = str(
        os.environ.get("BRAIN_TOKEN_CACHE_FILE")
        or config.get("token_cache_file")
        or ""
    ).strip()
    return (
        Path(configured).expanduser()
        if configured
        else Path.home() / ".august" / "investment-brain" / "msal-token-cache.json"
    )


def _onboarding_reset_path() -> Path:
    configured = str(os.environ.get("BRAIN_ONBOARDING_RESET_FILE") or "").strip()
    return (
        Path(configured).expanduser()
        if configured
        else Path.home() / ".august" / "investment-brain" / "onboarding-reset.pending"
    )


def _onboarding_reset_pending() -> bool:
    return _onboarding_reset_path().exists()


def _set_onboarding_reset() -> Path:
    path = _onboarding_reset_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("pending\n", encoding="utf-8")
    return path


def _clear_onboarding_reset() -> None:
    try:
        _onboarding_reset_path().unlink()
    except FileNotFoundError:
        pass


def _save_token_cache(cache, path: Path) -> None:
    if not getattr(cache, "has_state_changed", False):
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(cache.serialize(), encoding="utf-8")
    try:
        temporary.chmod(0o600)
    except OSError:
        pass
    temporary.replace(path)


def _entra_token(config: dict, settings: dict[str, str]) -> str:
    try:
        import msal
    except ImportError as exc:
        raise RuntimeError(
            "Microsoft Entra sign-in requires MSAL. Re-run the Investment Brain installer "
            "or run: python -m pip install --user 'msal>=1.31,<2'"
        ) from exc

    cache_path = _token_cache_path(config)
    cache = msal.SerializableTokenCache()
    if cache_path.exists():
        try:
            cache.deserialize(cache_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass

    app = msal.PublicClientApplication(
        settings["client_id"], authority=f"https://login.microsoftonline.com/{settings['tenant_id']}",
        token_cache=cache,
    )
    scopes = [settings["api_scope"]]
    result = None
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    if not result or "access_token" not in result:
        result = app.acquire_token_interactive(scopes=scopes)

    _save_token_cache(cache, cache_path)
    token = str((result or {}).get("access_token") or "").strip()
    if not token:
        detail = (result or {}).get("error_description") or (result or {}).get("error") or "no access token returned"
        raise RuntimeError(
            f"Microsoft Entra interactive sign-in failed: {detail}. "
            "Confirm your August account is authorized and try again."
        )
    return token


def _credential(config: dict) -> str:
    static = _static_key(config)
    if static:
        return static
    settings = _entra_settings(config)
    if settings:
        return _entra_token(config, settings)
    raise RuntimeError(
        "Investment Brain credential not found. For hosted access, configure "
        "BRAIN_ENTRA_TENANT_ID, BRAIN_ENTRA_CLIENT_ID, and BRAIN_API_SCOPE; "
        "for local access, use BRAIN_API_KEY or an API key file."
    )


def _request(method: str, path: str, payload: dict | None) -> dict:
    config = _config()
    base = (os.environ.get("BRAIN_API_URL") or config.get("base_url") or "http://127.0.0.1:8787/api").rstrip("/")
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base + path, data=body, method=method,
        headers={"Authorization": f"Bearer {_credential(config)}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:600]
        raise RuntimeError(f"Investment Brain HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Investment Brain is unreachable: {exc.reason}") from exc
    if not data.get("ok", False):
        raise RuntimeError(data.get("error") or "Investment Brain request failed")
    return data


def _payload(raw: str) -> dict:
    value = json.loads(raw or "{}")
    if not isinstance(value, dict):
        raise ValueError("--json must contain a JSON object")
    return value


ONBOARDING_REQUIRED_TEXT = (
    "ONBOARDING_REQUIRED: The authenticated Investment Brain profile is missing or incomplete. "
    "Do not run the requested workflow or show a capability menu. Immediately continue with the "
    "investment-onboarding workflow in this same turn, briefly explain the profile boundary, and "
    "ask the first onboarding question."
)


def _profile_is_complete(data: dict) -> bool:
    if _onboarding_reset_pending():
        return False
    profile = data.get("profile") if isinstance(data, dict) else None
    return isinstance(profile, dict) and profile.get("onboarding_status") == "completed"


def _profile_for_client(data: dict) -> dict:
    if not _onboarding_reset_pending():
        return data
    masked = dict(data)
    masked["profile"] = None
    masked["onboarding_reset"] = True
    masked["text"] = ONBOARDING_REQUIRED_TEXT
    return masked


def _guarded_call(route: str, payload: dict) -> dict:
    """Require onboarding before every shared Brain workflow, regardless of skill entry point."""
    profile = _request("GET", "/me/profile", None)
    if not _profile_is_complete(profile):
        return {
            "ok": True,
            "onboarding_required": True,
            "text": ONBOARDING_REQUIRED_TEXT,
        }
    return _request("POST", "/" + route.lstrip("/"), payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    call = sub.add_parser("call")
    call.add_argument("route")
    call.add_argument("--json", default="{}")
    call.add_argument("--raw", action="store_true")

    profile = sub.add_parser("profile")
    profile.add_argument("action", choices=("get", "onboard", "update", "reset"))
    profile.add_argument("--json", default="{}")

    args = parser.parse_args()
    if args.command == "call":
        data = _guarded_call(args.route, _payload(args.json))
        print(json.dumps(data, ensure_ascii=False, indent=2) if args.raw else data.get("text", ""))
        return 0

    if args.action == "reset":
        _set_onboarding_reset()
        data = {
            "ok": True,
            "onboarding_reset": True,
            "text": "Onboarding reset. The next Investment Brain skill must start onboarding.",
        }
    elif args.action == "get":
        data = _profile_for_client(_request("GET", "/me/profile", None))
    elif args.action == "onboard":
        data = _request("POST", "/me/onboarding", _payload(args.json))
        _clear_onboarding_reset()
    else:
        data = _request("PATCH", "/me/profile", _payload(args.json))
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
