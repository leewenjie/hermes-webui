#!/usr/bin/env python3
"""Check Hermes WebUI readiness for the real Hermes home Azure-backed setup.

This script is intentionally small and read-only. It verifies:
- /health responds with status=ok
- /api/onboarding/status reports provider_ready/chat_ready

It does not write state, open a browser, or print secrets.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def _fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as response:  # nosec B310 - localhost/manual operator URL
        return json.load(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check real-home Hermes WebUI Azure readiness")
    parser.add_argument("--port", type=int, default=8792, help="WebUI port to probe (default: 8792)")
    args = parser.parse_args()

    base = f"http://127.0.0.1:{args.port}"

    try:
        health = _fetch_json(f"{base}/health")
    except urllib.error.URLError as exc:
        print(json.dumps({"ok": False, "stage": "health", "error": str(exc)}))
        return 1

    try:
        onboarding = _fetch_json(f"{base}/api/onboarding/status")
    except urllib.error.HTTPError as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "stage": "onboarding",
                    "status": exc.code,
                    "error": exc.reason,
                }
            )
        )
        return 1
    except urllib.error.URLError as exc:
        print(json.dumps({"ok": False, "stage": "onboarding", "error": str(exc)}))
        return 1

    system = onboarding.get("system") or {}
    summary = {
        "ok": True,
        "health": {
            "status": health.get("status"),
            "active_streams": health.get("active_streams"),
            "active_runs": health.get("active_runs"),
        },
        "onboarding": {
            "completed": onboarding.get("completed"),
            "provider_configured": system.get("provider_configured"),
            "provider_ready": system.get("provider_ready"),
            "chat_ready": system.get("chat_ready"),
            "setup_state": system.get("setup_state"),
            "current_provider": system.get("current_provider"),
            "current_model": system.get("current_model"),
            "current_base_url": system.get("current_base_url"),
        },
    }
    print(json.dumps(summary, indent=2))
    return 0 if health.get("status") == "ok" and system.get("chat_ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
