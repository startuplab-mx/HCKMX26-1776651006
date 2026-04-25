"""
Seed the database with realistic demo alerts spread across the last 72 hours.

Variety in timestamps + statuses so the panel chart and triage view both
display rich data on first paint.

Usage (from project root):
    python scripts/seed_test_data.py
"""
from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from classifier import Pipeline
from classifier.heuristic import HeuristicClassifier
from classifier.llm_layer import LLMLayer
from database import get_db


class _OfflineLLM(LLMLayer):
    @property
    def enabled(self) -> bool:
        return False


# (text, platform, source, hours_ago, status, reviewer)
SAMPLES = [
    ("hola, mañana hay examen de bio",                                     "whatsapp",  "bot",       70, "pending",   None),
    ("yo quiero jale, $15,000 semanales 🍕",                                "whatsapp",  "bot",       62, "reviewed",  "marco"),
    ("trabajo de guardia de seguridad, te pago el viaje",                  "instagram", "extension", 55, "pending",   None),
    ("vienes al cumple el sábado en casa de juan",                          "whatsapp",  "bot",       50, "dismissed", "marco"),
    ("pásate a telegram, no le digas a nadie",                              "whatsapp",  "bot",       42, "reviewed",  "marco"),
    ("envía tu ubicación, confía en mí",                                    "discord",   "extension", 38, "pending",   None),
    ("ya sabes demasiado, te vamos a buscar",                               "whatsapp",  "bot",       30, "escalated", "marco"),
    ("necesito gente, dinero rápido, trabajo fácil 💰",                     "whatsapp",  "bot",       26, "pending",   None),
    ("recoge esto en el punto, no traigas celular",                         "discord",   "extension", 22, "pending",   None),
    ("trae a tus compas para el jale, $15,000 semanales 🍕",                "instagram", "extension", 18, "pending",   None),
    ("si intentas escapar te descuartizo, sabemos dónde vives",             "whatsapp",  "bot",       12, "escalated", "marco"),
    ("manda nudes o las fotos van a tu escuela. deposita $500 spei",        "instagram", "extension",  8, "escalated", "marco"),
    ("hola tengo una duda de la tarea",                                     "whatsapp",  "bot",        5, "dismissed", "marco"),
    ("pásate a privado, peleas con la familia, yo te cuido",                "instagram", "extension",  3, "pending",   None),
    ("ve al punto a las 11pm, te van a recoger",                            "discord",   "extension",  1, "pending",   None),
]


def main() -> None:
    random.seed(42)  # deterministic spread for reproducible demos
    pipeline = Pipeline(heuristic=HeuristicClassifier(), llm=_OfflineLLM())
    db = get_db()
    now = datetime.now(timezone.utc)

    print(f"📦 Seeding into {db.path} ({len(SAMPLES)} alerts spread across 72 h)...")

    for i, (text, platform, source, hours_ago, status, reviewer) in enumerate(SAMPLES, start=1):
        r = pipeline.classify(text, use_llm=False)
        # Add a small jitter (±20 min) so buckets don't overlap perfectly.
        jitter = timedelta(minutes=random.randint(-20, 20))
        ts = (now - timedelta(hours=hours_ago) + jitter).strftime("%Y-%m-%d %H:%M:%S")
        alert_id = db.seed_insert_alert(
            platform=platform,
            source=source,
            risk_score=r["risk_score"],
            risk_level=r["risk_level"],
            phase_detected=r["phase_detected"],
            categories=r["categories"],
            summary=r["summary"],
            text_hash=r["text_hash"],
            contact_phone=None,
            llm_used=False,
            override_triggered=r["override_triggered"],
            session_id=f"demo-session-{i}",
            created_at=ts,
            status=status,
            reviewer=reviewer,
            pattern_ids=r.get("pattern_ids", []),
            source_type="text",
        )
        print(
            f"  [{alert_id:>3}] {ts} · {r['risk_level']:<8} score={r['risk_score']:.2f} "
            f"phase={(r['phase_detected'] or '-'):<12} status={status:<10} {platform}"
        )

    stats = db.stats()
    print("\n✅ Done. Stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
