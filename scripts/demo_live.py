"""
scripts/demo_live.py

Live demo for the Nahual pitch. Drives the API through a 5-message
recruitment progression. Press ENTER between steps. Renders progress
bars, "why" reasons, escalation timeline, and override flags directly
in the terminal so the jury sees risk climb in real time.

Pre-req: backend running (uvicorn main:app --port 8000).

Usage:
    python scripts/demo_live.py                  # interactive
    python scripts/demo_live.py --auto           # no ENTER, fixed pauses
    python scripts/demo_live.py --reset-only     # just clear history
"""
from __future__ import annotations

import argparse
import sys
import time

import httpx

API_URL = "http://localhost:8000"
SESSION_ID = "demo_live_session"

DEMO_SEQUENCE: list[dict] = [
    {
        "step": 1,
        "label": "CONTACTO INOCENTE",
        "text": "Hola, qué onda? Vi tu perfil en TikTok",
        "platform": "tiktok",
        "expected": "SEGURO",
    },
    {
        "step": 2,
        "label": "CAPTACIÓN",
        "text": (
            "Oye, no te gustaría ganar $15,000 a la semana? Es trabajo de "
            "guardia de seguridad, fácil, te pago el viaje 🍕"
        ),
        "platform": "tiktok",
        "expected": "ATENCIÓN",
    },
    {
        "step": 3,
        "label": "ENGANCHE",
        "text": (
            "Pásate a telegram, te mandamos un carro. No le digas a nadie, "
            "es entre nosotros. En qué colonia vives?"
        ),
        "platform": "whatsapp",
        "expected": "ATENCIÓN/PELIGRO (escalamiento)",
    },
    {
        "step": 4,
        "label": "COERCIÓN",
        "text": (
            "Ya sabes demasiado compa. Si no vienes, te vamos a buscar. "
            "Sabemos donde vives. Última oportunidad."
        ),
        "platform": "whatsapp",
        "expected": "PELIGRO (Override)",
    },
    {
        "step": 5,
        "label": "EXPLOTACIÓN",
        "text": (
            "Ve al punto mañana a las 6. No traigas celular. Te van a "
            "recoger. Y trae a tus compas, necesitamos más gente."
        ),
        "platform": "whatsapp",
        "expected": "PELIGRO (Override)",
    },
]

C = {
    "SEGURO": "\033[92m",
    "ATENCION": "\033[93m",
    "PELIGRO": "\033[91m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "DIM": "\033[2m",
    "CYAN": "\033[96m",
}


def bar(score: float, width: int = 30) -> str:
    filled = int(round(score * width))
    return "█" * filled + "░" * (width - filled)


def color_for(level: str) -> str:
    return C.get(level, "")


def header() -> None:
    print("\n" + "═" * 64)
    print(f"{C['BOLD']}  🛡️  NAHUAL — DEMO DE DETECCIÓN EN VIVO{C['RESET']}")
    print(f"{C['DIM']}  Reclutamiento criminal progresivo · 5 mensajes{C['RESET']}")
    print(f"{C['DIM']}  Sesión: {SESSION_ID}  ·  API: {API_URL}{C['RESET']}")
    print("═" * 64 + "\n")


def reset_history(client: httpx.Client) -> None:
    try:
        client.delete(f"{API_URL}/risk-history/{SESSION_ID}", timeout=5.0)
    except httpx.HTTPError:
        pass


def render_step(step: dict, result: dict) -> None:
    level = result.get("risk_level", "—")
    score = result.get("risk_score", 0.0)
    phase = result.get("phase_detected") or "—"
    why = result.get("why", []) or []
    escalation = result.get("escalation") or {}
    color = color_for(level)

    print("\n" + "─" * 64)
    print(f"{C['BOLD']}PASO {step['step']}: {step['label']}{C['RESET']}")
    print(f"{C['DIM']}Plataforma: {step['platform']}{C['RESET']}")
    text = step["text"]
    print(f'{C["DIM"]}Mensaje:   "{text[:90]}{"…" if len(text) > 90 else ""}"{C["RESET"]}')
    print(
        f"\n  {color}{bar(score)}  {score * 100:>5.1f}%  {C['BOLD']}{level}{C['RESET']}"
    )
    print(f"  Fase dominante: {phase}")

    if result.get("override_triggered"):
        print(f"  {C['PELIGRO']}⚡ OVERRIDE ESTÁTICO — Fase 3/4 ≥ 0.80{C['RESET']}")
    if result.get("escalation_override"):
        print(
            f"  {C['PELIGRO']}📈 OVERRIDE POR TRAYECTORIA — el riesgo escala{C['RESET']}"
        )

    if why:
        print(f"\n  {C['BOLD']}¿Por qué?{C['RESET']}")
        for line in why[:4]:
            print(f"    → {line}")

    if escalation and escalation.get("trend") not in (None, "insufficient_data"):
        timeline = " → ".join(
            f"{int(round(s * 100))}%" for s in escalation.get("score_history", [])
        )
        if timeline:
            print(
                f"\n  {C['CYAN']}Trayectoria:  {timeline}{C['RESET']}"
            )
        if escalation.get("description"):
            print(f"  {C['DIM']}{escalation['description']}{C['RESET']}")

    legal = result.get("legal") or {}
    auths = legal.get("authorities", [])[:2]
    if auths and level != "SEGURO":
        print(f"\n  {C['BOLD']}Autoridades sugeridas:{C['RESET']}")
        for au in auths:
            print(f"    • {au['name']}: {au['phone']}")


def call_alert(client: httpx.Client, step: dict) -> dict:
    r = client.post(
        f"{API_URL}/alert",
        json={
            "text": step["text"],
            "platform": step["platform"],
            "source": "demo_live",
            "source_type": "text",
            "session_id": SESSION_ID,
        },
        timeout=15.0,
    )
    r.raise_for_status()
    return r.json()


def render_profile(client: httpx.Client) -> None:
    try:
        r = client.get(f"{API_URL}/profile/{SESSION_ID}", timeout=5.0)
        if r.status_code != 200:
            return
        data = r.json()
    except httpx.HTTPError:
        return

    if data.get("status") != "ok":
        return

    profile = data["risk_profile"]
    timeline = " → ".join(
        f"{int(round(s * 100))}%" for s in profile["score_timeline"]
    )
    print("\n" + "═" * 64)
    print(f"{C['BOLD']}  Perfil de riesgo de la sesión{C['RESET']}")
    print(
        f"  Análisis: {data['total_analyses']}  ·  "
        f"avg={profile['average_score']:.2f}  ·  max={profile['max_score']:.2f}"
    )
    print(f"  Tendencia: {profile['trend']}  ·  fase dominante: {profile['dominant_phase']}")
    print(f"  Trayectoria completa: {timeline}")
    print("═" * 64 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--auto", action="store_true", help="Run without ENTER (fixed 3 s pauses)."
    )
    parser.add_argument(
        "--reset-only", action="store_true", help="Just clear the demo's history."
    )
    args = parser.parse_args()

    with httpx.Client() as client:
        if args.reset_only:
            reset_history(client)
            print("history cleared.")
            return

        # Make sure backend is up
        try:
            client.get(f"{API_URL}/health", timeout=2.0).raise_for_status()
        except Exception as e:  # noqa: BLE001
            print(f"❌ Backend no disponible en {API_URL}: {e}")
            sys.exit(1)

        header()
        reset_history(client)

        for step in DEMO_SEQUENCE:
            if args.auto:
                time.sleep(3)
            else:
                input(f"{C['DIM']}[ENTER para enviar paso {step['step']}…]{C['RESET']}")
            try:
                result = call_alert(client, step)
            except httpx.HTTPError as e:
                print(f"  {C['PELIGRO']}error: {e}{C['RESET']}")
                continue
            render_step(step, result)

        render_profile(client)
        print(f"{C['BOLD']}  ✅ DEMO COMPLETA{C['RESET']}\n")


if __name__ == "__main__":
    main()
