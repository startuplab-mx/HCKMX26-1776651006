"""Test-wide fixtures + env cleanup.

Without this conftest, the project-level .env file (which now ships with
NAHUAL_API_KEY=nahual-hackathon-2026 for the hackathon demo) leaks into the
pytest process. main.py loads .env via dotenv on import, so any test that
does not explicitly override NAHUAL_API_KEY would suddenly see auth turned
on and start receiving 403 from sensitive endpoints.

We clear the auth-related env vars unconditionally before main is imported.
Tests that *want* auth on (test_auth.py) set NAHUAL_API_KEY before the
importlib.reload(main) call, which still wins because dotenv's default
behaviour is to NOT override pre-set env vars.
"""
from __future__ import annotations

import os


# main.py calls load_dotenv() on import, which only overrides env vars that
# are NOT already set. We set them to empty strings explicitly so dotenv
# treats them as "already configured" and skips the .env value.
for _key in (
    "NAHUAL_API_KEY",
    "NAHUAL_WEBHOOK_URLS",
    "NAHUAL_WEBHOOK_SECRET",
    "ANTHROPIC_API_KEY",
    "GROQ_API_KEY",
):
    os.environ[_key] = ""

# Disable rate limit on /feedback for tests (set MAX=0 → unlimited).
# Production keeps the default of 3 per (IP, alert_id) per 10 min.
os.environ["FEEDBACK_RATE_LIMIT_MAX"] = "0"


# Pytest fixture: redirect the Bayesian model file to a per-test tmp path
# so the singleton does NOT inherit the production-bootstrapped model
# (886 docs from scripts/bootstrap_bayesian.py). Without this, integration
# tests that expect a cold model would always fail.
import tempfile
import pytest

@pytest.fixture(autouse=True)
def _isolated_bayesian_model(tmp_path, monkeypatch):
    fresh = tmp_path / "bayesian_iso.json"
    monkeypatch.setenv("BAYESIAN_MODEL_PATH", str(fresh))
    # Reset the singleton so the next get_bayesian() call uses the new path.
    try:
        import sys
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
        from classifier.bayesian import _reset_singleton_for_tests
        _reset_singleton_for_tests()
    except Exception:
        pass
    yield
