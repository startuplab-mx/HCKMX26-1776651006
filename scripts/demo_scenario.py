"""
Drive the live API through a 3-step demo scenario.

Pre-req: backend running (uvicorn main:app --reload --port 8000).
Usage:
    python scripts/demo_scenario.py
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

API = "http://localhost:8000"

SCENARIO = [
    ("Mensaje cotidiano", "hola, vienes al cumple el sábado?"),
    ("Captación + emoji narco", "yo quiero jale, te pago el viaje, $15,000 semanales 🍕"),
    ("Coerción explícita (override)", "si intentas escapar te descuartizo, sabemos dónde vives"),
]


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{API}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main() -> int:
    try:
        with urllib.request.urlopen(f"{API}/health", timeout=2) as r:
            json.loads(r.read())
    except urllib.error.URLError:
        print(f"❌ Backend no responde en {API}. Levántalo con: uvicorn main:app --reload")
        return 1

    print("🛡️  NAHUAL — DEMO SCENARIO\n")
    for label, text in SCENARIO:
        print(f"▸ {label}")
        print(f"  texto: {text}")
        result = post("/analyze", {"text": text, "use_llm": False})
        print(
            f"  → risk={result['risk_score']:.2f} "
            f"level={result['risk_level']} "
            f"phase={result['phase_detected']} "
            f"override={result['override_triggered']}"
        )
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
