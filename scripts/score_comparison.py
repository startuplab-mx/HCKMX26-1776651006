"""Score comparison: heurístico-only vs heurístico+bayesiano (sin LLM)
en los 20 test cases del structural audit.

Usa /analyze con use_llm=false para aislar el efecto de la capa
bayesiana. La diferencia entre `score_h` (sin Bayes) y `score_hb`
(con Bayes) muestra cuánto aportó el modelo entrenado.
"""
import requests
import json
import time

API = "http://159.223.187.6/analyze"
BAYES_PRED = "http://159.223.187.6/bayesian/predict"

TESTS = [
    (1,  'Me ofrecieron 15,000 pesos a la semana si voy al rancho', ['ATENCION', 'PELIGRO']),
    (2,  'me van a matar', ['PELIGRO']),
    (3,  'Me dijeron que si no respondo me van a matar', ['PELIGRO']),
    (4,  'Un tipo en TikTok me ofreció jale', ['ATENCION', 'PELIGRO']),
    (5,  'me pidieron q me pasara a telegram y q no dijera nada', ['ATENCION', 'PELIGRO']),
    (6,  'me ofresieron 15 mil x semana', ['ATENCION', 'PELIGRO']),
    (7,  'me tienen amenazado, tengo mucho miedo', ['PELIGRO']),
    (8,  'me estan extorsionando con mis fotos', ['PELIGRO']),
    (9,  'me obligaron a llevar algo al punto', ['PELIGRO']),
    (10, 'vienes al cumple el sabado', ['SEGURO']),
    (11, 'estoy trabajando ahorita', ['SEGURO']),
    (12, 'vi el capitulo de narcos en netflix anoche', ['SEGURO']),
    (13, 'me sacaron 500 pesos del monedero', ['SEGURO']),
    (14, 'te pago $15,000 semanales como guardia de seguridad', ['ATENCION', 'PELIGRO']),
    (15, 'ya sabes demasiado, te vamos a buscar', ['PELIGRO']),
    (16, 'pasate a telegram, no le digas a nadie', ['ATENCION', 'PELIGRO']),
    (17, 'mandame fotos o las publico en tu escuela', ['PELIGRO']),
    (18, 'un desconocido me agrego y me ofrecio dinero por hacer algo facil', ['ATENCION', 'PELIGRO']),
    (19, 'me presionaron mucho para responder rapido y dar mis datos', ['ATENCION', 'PELIGRO']),
    (20, 'alguien me dijo que me iban a desaparecer si no coopore', ['PELIGRO']),
]

print("=" * 110)
print(f"  {'#':3s} {'TEXTO':50s} | {'WITHOUT LLM':25s} | {'BAYES PURE':18s} | DELTA")
print("=" * 110)
ok = 0
def post_with_retry(url, json_body, max_attempts=5):
    for attempt in range(max_attempts):
        r = requests.post(url, json=json_body, timeout=10)
        if r.status_code == 429:
            time.sleep(5 + attempt * 5)
            continue
        return r
    return r

for n, txt, expected in TESTS:
    time.sleep(4)  # stay below 20/min rate limit
    # /analyze without LLM
    r = post_with_retry(API, {"text": txt, "use_llm": False}).json()
    level = r["risk_level"]
    score = r["risk_score"]
    bayes = r.get("bayesian")
    bayes_score = bayes.get("risk_score") if bayes else None
    bayes_class = bayes.get("predicted_class") if bayes else None

    # Pure bayesian for comparison
    bp = post_with_retry(BAYES_PRED, {"text": txt}).json()
    bp_score = bp.get("risk_score")
    bp_class = bp.get("predicted_class")

    passed = level in expected
    ok += passed
    flag = "OK" if passed else "FAIL"
    bayes_str = f"B={bayes_score:.2f}" if bayes_score is not None else "B=---"
    pure_str = f"{bp_class or '---':12s} {bp_score:.2f}" if bp_score is not None else "insufficient"
    short = (txt[:48] + '..') if len(txt) > 50 else txt
    print(f"  {n:3d} {short:50s} | [{flag}] {level:8s} {score:.2f} {bayes_str:8s} | {pure_str:18s} | exp: {'|'.join(expected)}")
print("=" * 110)
print(f"  RESULTADO: {ok}/{len(TESTS)} ({100*ok//len(TESTS)}%) sin LLM")
print()
print("Nota: el 'B=' es el score que el bayesiano contribuyó al merge final.")
print("'BAYES PURE' es la predicción aislada (ignorando heurístico/LLM).")
