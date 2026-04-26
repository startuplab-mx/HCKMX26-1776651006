"""Bootstrap el modelo Bayesiano con los 870+ patrones del dataset.

Run:
    python scripts/bootstrap_bayesian.py

Lee los 4 phaseN_*.json + emojis_narco.json + research siblings + una
lista curada de frases inocuas (clase "seguro") y entrena el modelo
incrementalmente. Persiste a backend/classifier/bayesian_model.json.

Idempotente: ejecutar dos veces no afecta — el modelo solo crece, las
distribuciones de probabilidad se ajustan al doble. Para empezar de cero,
borra `backend/classifier/bayesian_model.json` antes de correr.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from classifier.bayesian import NaiveBayesClassifier  # noqa: E402

KW_DIR = ROOT / "backend" / "classifier" / "keywords"

PHASE_FILES = {
    "phase1_captacion":   "captacion",
    "phase2_enganche":    "enganche",
    "phase3_coercion":    "coercion",
    "phase4_explotacion": "explotacion",
}

# Frases inocuas que el bot puede recibir y NO son señal. Cubren:
# - saludos, conversación adolescente normal, escuela, videojuegos,
#   familia, comida, transporte, deporte, series.
SAFE_PHRASES = [
    "hola que onda",
    "hola buenas tardes",
    "como estas",
    "estoy bien gracias",
    "estoy aburrido",
    "voy a la escuela",
    "tengo mucha tarea",
    "me reprobaron en mate",
    "saque buena nota en historia",
    "el examen estuvo facil",
    "la clase de ingles me aburre",
    "me toca clase de educacion fisica",
    "voy a estudiar para el final",
    "mi hermana me molesta",
    "mi mama no me deja salir",
    "mi papa esta enojado",
    "vamos a comer pizza",
    "tengo hambre vamos por tacos",
    "quiero un cafe con mi novia",
    "vienes al cumple el sabado",
    "vamos al cine este finde",
    "vamos a la fiesta del sabado",
    "que peli vamos a ver",
    "vi la nueva pelicula de marvel",
    "vi el capitulo de narcos en netflix",
    "estoy viendo stranger things",
    "me ganaron en free fire",
    "me toca jugar fortnite con mis primos",
    "subi de rango en valorant",
    "vamos a jugar minecraft",
    "estoy en la final del torneo de fifa",
    "el equipo perdio anoche",
    "ganamos el partido",
    "voy a ir al gym",
    "estoy entrenando para el maraton",
    "me duele la espalda del entrenamiento",
    "me voy a dormir ya estoy cansado",
    "no puedo dormir por la tarea",
    "tengo cita con el dentista",
    "mi perro esta enfermo",
    "vamos a la playa el fin",
    "voy al concierto de bad bunny",
    "que onda con tu novia",
    "te paso la tarea por whatsapp",
    "feliz cumpleanos amigo",
    "feliz navidad familia",
    "gracias por la ayuda",
    "te quiero mucho",
    "como te fue en el partido",
    "estoy trabajando en mi proyecto de ciencias",
    # Casual money / spending — distinguir de extorsión.
    "me sacaron 500 pesos del monedero",
    "me robaron la cartera ayer",
    "me cobraron 200 pesos por el envio",
    "tengo que pagar la luz",
    "me debe 100 pesos mi amigo",
    "compre un cafe de 50 pesos",
    "le pague la pizza a mi novia",
    "me regalaron un pastel",
    "le voy a comprar un regalo a mi mama",
    "ayer fui al super con mi papa",
    "tengo que ahorrar para los tenis",
    "cuanto cuesta el helado",
    "que caro esta el cine ahora",
    "me prestaron 200 pesos en la cooperativa",
    "me cobraron de mas en la tienda",
    # Emocional/ adolescente normal
    "estoy triste pero ya se me pasara",
    "me peleé con mi mejor amigo",
    "no puedo dormir tengo insomnio",
    "extrano a mi abuela",
    "me siento solo a veces",
    # Más videojuegos / streaming
    "voy a stream en twitch",
    "subi un video a youtube",
    "no me gusta el nuevo update de fortnite",
    "ya termine el pase de batalla",
    "me dieron item raro en el dungeon",
]


def main() -> None:
    # Empieza de cero (idempotencia explícita): borra el modelo si existe
    # y arranca con counters limpios.
    model_path = ROOT / "backend" / "classifier" / "bayesian_model.json"
    if model_path.exists():
        print(f"[reset] removing existing model at {model_path}")
        model_path.unlink()

    bayes = NaiveBayesClassifier(model_path=model_path)

    # 1. Train with main phase patterns.
    grand_total = 0
    for stem, label in PHASE_FILES.items():
        path = KW_DIR / f"{stem}.json"
        if not path.exists():
            print(f"[warn] missing {path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        patterns = data.get("patterns") or data.get("keywords") or []
        added_main = 0
        examples: list[tuple[str, str]] = []
        for p in patterns:
            # We want the surface form, not the regex-form. Skip patterns
            # marked as regex (they're regex sources, not real text).
            if p.get("regex"):
                continue
            text = p.get("pattern") or p.get("signal_base") or ""
            if not text or len(text) < 3:
                continue
            examples.append((text, label))
        added_main = bayes.train_many(examples)
        print(f"[main]   {stem:24s} → {label:12s}: trained {added_main} patterns")
        grand_total += added_main

        # 2. Optional research sibling (etl_dataset_to_keywords output).
        research = KW_DIR / f"{stem}_research.json"
        if research.exists():
            rdata = json.loads(research.read_text(encoding="utf-8"))
            r_examples: list[tuple[str, str]] = []
            for p in rdata.get("patterns", []):
                if p.get("regex"):
                    continue
                text = p.get("pattern") or ""
                if text and len(text) >= 3:
                    r_examples.append((text, label))
            added_res = bayes.train_many(r_examples)
            print(f"[research] {stem}_research.json    → {label:12s}: trained {added_res}")
            grand_total += added_res

    # 3. Train safe phrases.
    safe_added = bayes.train_many([(p, "seguro") for p in SAFE_PHRASES])
    print(f"[safe]   {len(SAFE_PHRASES)} phrases     → seguro      : trained {safe_added}")
    grand_total += safe_added

    # 4. Force final save and report.
    bayes.save()
    stats = bayes.get_stats()
    print()
    print("=" * 60)
    print("BOOTSTRAP COMPLETE")
    print(f"  Total training examples: {stats['total_training_examples']}")
    print(f"  Vocabulary size:         {stats['vocabulary_size']}")
    print(f"  Class distribution:")
    for cls, n in stats["class_distribution"].items():
        print(f"     {cls:12s} {n:5d}")
    print(f"  Model persisted to:      {stats['model_path']}")
    print("=" * 60)
    print()
    # Sanity-check predictions
    samples = [
        ("hola que onda", "seguro"),
        ("te voy a matar", "coercion"),
        ("te pago 15 mil semanales como halcon", "captacion"),
        ("manda fotos o las publico en tu escuela", "explotacion"),
        ("pasate a telegram y no le digas a nadie", "enganche"),
    ]
    print("SANITY CHECK (heuristic-free Bayesian prediction):")
    for text, expected in samples:
        r = bayes.predict(text)
        cls = r.get("predicted_class") or "—"
        conf = r.get("confidence") or 0.0
        score = r.get("risk_score")
        score_str = f"{score:.2f}" if score is not None else "—"
        flag = "OK" if cls == expected else "??"
        print(f"  [{flag}] expected={expected:12s} got={cls:12s} conf={conf:.2f} score={score_str}  '{text}'")


if __name__ == "__main__":
    main()
