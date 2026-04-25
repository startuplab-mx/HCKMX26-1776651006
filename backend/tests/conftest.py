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
