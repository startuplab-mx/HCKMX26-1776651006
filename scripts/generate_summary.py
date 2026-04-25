#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""NAHUAL — Generate final expansion summary report."""
import csv, json, os
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'dataset_expansion_results.csv')
LOG_PATH = os.path.join(SCRIPT_DIR, 'dataset_expansion_log.txt')

rows = []
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

total_new = len(rows)
grand_total = 374 + total_new

# Distribution by phase
fase_count = Counter()
for r in rows:
    fase_count[r['fase']] += 1

# Distribution by source
fuente_count = Counter()
for r in rows:
    fuente_count[r['fuente']] += 1

# Distribution by confidence
conf_count = Counter()
for r in rows:
    conf_count[r['confiabilidad']] += 1

# Distribution by type
tipo_count = Counter()
for r in rows:
    tipo_count[r['tipo']] += 1

# Top 10 highest weight patterns
sorted_by_weight = sorted(rows, key=lambda x: float(x['peso']), reverse=True)
top10 = sorted_by_weight[:10]

# Build report
lines = []
lines.append("=" * 70)
lines.append("NAHUAL — RESUMEN FINAL DE EXPANSIÓN DE DATASET")
lines.append("Agente Nocturno de Ampliación de Dataset")
lines.append(f"Fecha: 2026-04-25")
lines.append("=" * 70)
lines.append("")
lines.append(f"DATASET ORIGINAL:     374 patrones")
lines.append(f"PATRONES NUEVOS:      {total_new}")
lines.append(f"TOTAL FINAL:          {grand_total}")
lines.append(f"META:                 1000")
lines.append(f"EXCEDENTE:            +{grand_total - 1000}")
lines.append("")

lines.append("-" * 70)
lines.append("DISTRIBUCIÓN POR FASE")
lines.append("-" * 70)
for fase in sorted(fase_count.keys()):
    orig = {'Fase1': 100, 'Fase2': 90, 'Fase3': 84, 'Fase4': 100}.get(fase, 0)
    new = fase_count[fase]
    lines.append(f"  {fase:20s}  Original: {orig:4d}  Nuevos: {new:4d}  Total: {orig+new:4d}")
lines.append(f"  {'TOTAL':20s}  Original: {374:4d}  Nuevos: {total_new:4d}  Total: {grand_total:4d}")
lines.append("")

lines.append("-" * 70)
lines.append("DISTRIBUCIÓN POR CONFIABILIDAD")
lines.append("-" * 70)
for conf in ['alta', 'media', 'baja']:
    c = conf_count.get(conf, 0)
    pct = (c / total_new * 100) if total_new > 0 else 0
    lines.append(f"  {conf:10s}  {c:4d} patrones  ({pct:.1f}%)")
lines.append("")

lines.append("-" * 70)
lines.append("DISTRIBUCIÓN POR TIPO")
lines.append("-" * 70)
for tipo, count in tipo_count.most_common():
    pct = (count / total_new * 100) if total_new > 0 else 0
    lines.append(f"  {tipo:15s}  {count:4d} patrones  ({pct:.1f}%)")
lines.append("")

lines.append("-" * 70)
lines.append("DISTRIBUCIÓN POR FUENTE (Top 15)")
lines.append("-" * 70)
for fuente, count in fuente_count.most_common(15):
    lines.append(f"  {fuente:45s}  {count:4d}")
lines.append(f"  ... y {len(fuente_count) - 15} fuentes adicionales" if len(fuente_count) > 15 else "")
lines.append("")

lines.append("-" * 70)
lines.append("TOP 10 PATRONES DE MAYOR PESO/RELEVANCIA")
lines.append("-" * 70)
for i, p in enumerate(top10, 1):
    lines.append(f"  {i:2d}. [{p['peso']}] {p['fase']} | {p['señal_base']}")
    lines.append(f"      Intención: {p['intención']}")
    lines.append(f"      Fuente: {p['fuente']} | Confiabilidad: {p['confiabilidad']}")
    lines.append("")

lines.append("-" * 70)
lines.append("BRECHAS IDENTIFICADAS")
lines.append("-" * 70)
lines.append("""
  1. FASE 3 (Coerción) sigue siendo la fase con menos patrones relativos.
     Se recomienda buscar más testimonios judiciales de víctimas sobre
     tácticas de control y amenaza.

  2. Fuentes judiciales directas (expedientes, sentencias) son escasas.
     La mayoría de patrones provienen de fuentes periodísticas y derivadas.
     Se recomienda acceder a bases de datos del poder judicial.

  3. Patrones de plataformas emergentes (BeReal, Threads, BlueSky) no
     están representados. Los carteles migran rápido a nuevas plataformas.

  4. Variantes regionales (dialecto, jerga local) están subrepresentadas.
     Patrones de Guerrero, Michoacán, Tamaulipas y Chiapas necesitan
     más especificidad lingüística.

  5. Patrones de audio/voz (notas de voz en WhatsApp, mensajes de voz
     en Telegram) no están cubiertos ya que el dataset es textual.

  6. Patrones en lenguas indígenas (náhuatl, maya, mixteco) utilizados
     en regiones con alta presencia de reclutamiento forzado no están
     representados.

  7. Indicadores de reclutamiento de menores migrantes centroamericanos
     en tránsito por México tienen poca representación.

  8. Patrones de deepfake y manipulación de imagen/video con IA para
     sextorsión y amenazas son un vector emergente poco documentado.
""")

lines.append("-" * 70)
lines.append("METODOLOGÍA")
lines.append("-" * 70)
lines.append("""
  - 7 lotes (batches) de expansión ejecutados secuencialmente
  - Deduplicación contra 374 señales originales + acumulado entre lotes
  - Búsqueda web en 4 rondas: periodísticas, académicas, ciberseguridad, testimonios
  - Fuentes consultadas: CSIS, Infobae, Milenio, CNN, ADN40, REDIM, UNICEF,
    LatinTimes, Publimetro, INAI, CNDH, OECD, Vanguardia, El Español,
    Prensa Libre, Animal Político, Proceso, Vice, UNODC, FinCEN, AFP,
    Xataka, WeLiveSecurity, Derecho de la Red, y más de 30 fuentes adicionales
  - Clasificación de confiabilidad: alta (judicial/periodística verificada),
    media (documentada pero indirecta), baja (derivada/sintética)
  - IDs secuenciales por fase: f1_xxx, f2_xxx, f3_xxx, f4_xxx
""")

lines.append("=" * 70)
lines.append("FIN DEL REPORTE")
lines.append("=" * 70)

report = "\n".join(lines)

with open(LOG_PATH, 'w', encoding='utf-8') as f:
    f.write(report)

print(report)
