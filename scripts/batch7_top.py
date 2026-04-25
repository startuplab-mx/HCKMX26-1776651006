#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NAHUAL — Batch 7: Final 5 patterns to cross 1000."""
import csv, json, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'dataset_expansion_results.csv')
SIGNALS_PATH = os.path.join(SCRIPT_DIR, 'existing_signals.json')
COUNTERS_PATH = os.path.join(SCRIPT_DIR, 'batch6_counters.json')
FINAL_COUNTERS_PATH = os.path.join(SCRIPT_DIR, 'batch7_counters.json')

with open(SIGNALS_PATH, 'r', encoding='utf-8') as f:
    existing = set(json.load(f))
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        existing.add(row['señal_base'].lower().strip())
with open(COUNTERS_PATH, 'r', encoding='utf-8') as f:
    state = json.load(f)
counters = {int(k): int(v) for k, v in state['counters'].items()}
prev_added = state['total_added']

added = 0
skipped = 0
csvfile = open(CSV_PATH, 'a', newline='', encoding='utf-8')
writer = csv.writer(csvfile)

def add(fase, signal, variantes, intencion, fuente, tipo, peso, url='', conf='media'):
    global added, skipped
    key = signal.lower().strip()
    if key in existing:
        skipped += 1
        return
    existing.add(key)
    pid = f'f{fase}_{counters[fase]:03d}'
    counters[fase] += 1
    writer.writerow([pid, f'Fase{fase}', signal, variantes, intencion, fuente, tipo, peso, url, '2026-04-25', conf])
    added += 1

# Pattern 999: Algorithmic targeting via AI
add(1, 'uso de inteligencia artificial para perfilar víctimas menores',
    'IA para seleccionar víctimas|algoritmo de targeting|machine learning reclutamiento',
    'Explotación de herramientas de IA para identificar menores vulnerables',
    'OECD AI 2026', 'táctica', 0.90,
    'https://oecd.ai/en/incidents/2026-02-21-f87d', 'alta')

# Pattern 1000: 60% interaction stat
add(1, '60% de menores interactúa con desconocidos en internet',
    'niños hablan con extraños online|menores contactan desconocidos|interacción riesgosa',
    'Dato estadístico que revela la exposición masiva de menores al riesgo digital',
    'Infobae/Red Grooming Latam 2025', 'dato', 0.85,
    'https://www.infobae.com/tendencias/2025/05/13/el-60-de-los-ninos-y-adolescentes-interactuo-con-desconocidos-en-internet-advirtio-un-estudio-en-america-latina/', 'alta')

# Pattern 1001+: extras
add(2, 'te enseño a usar armas, es para tu protección',
    'aprende a disparar|te entrenamos|es para que te defiendas',
    'Normalización de uso de armas como parte del enganche',
    'derivado', 'frase', 0.85, '', 'media')

add(3, 'ya le avisamos a los de migración que te buscan',
    'estás fichado|te reportamos|la policía te busca',
    'Amenaza falsa de denuncia ante autoridades migratorias',
    'derivado', 'frase', 0.80, '', 'media')

add(4, 'entrégale la mercancía al contacto en la escuela',
    'pasa el producto en la prepa|deja el paquete en el baño|entrega en el recreo',
    'Uso de entorno escolar como punto de distribución de droga',
    'derivado', 'frase', 0.90, '', 'media')

csvfile.close()

final_state = {
    'counters': {str(k): v for k, v in counters.items()},
    'total_added': prev_added + added,
    'grand_total': 374 + prev_added + added
}
with open(FINAL_COUNTERS_PATH, 'w', encoding='utf-8') as f:
    json.dump(final_state, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"BATCH 7 COMPLETE")
print(f"{'='*60}")
print(f"New patterns this batch: {added}")
print(f"Skipped: {skipped}")
print(f"TOTAL NEW PATTERNS: {prev_added + added}")
print(f"ORIGINAL DATASET: 374")
print(f"GRAND TOTAL: {374 + prev_added + added}")
target = 1000
diff = (374 + prev_added + added) - target
if diff >= 0:
    print(f"\n*** META DE {target} ALCANZADA! Excedente: +{diff} ***")
else:
    print(f"\nFaltan: {abs(diff)}")
print(f"{'='*60}")
