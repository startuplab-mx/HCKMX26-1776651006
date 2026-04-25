#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix fase column to be uniform: Fase1, Fase2, Fase3, Fase4."""
import csv, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, 'dataset_expansion_results.csv')

rows = []
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    for row in reader:
        # Normalize fase column
        fase = row['fase'].strip()
        if fase in ('1', '2', '3', '4'):
            fase = f'Fase{fase}'
        row['fase'] = fase
        rows.append(row)

with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

# Count
from collections import Counter
fc = Counter(r['fase'] for r in rows)
print(f"Fixed {len(rows)} rows. Distribution: {dict(fc)}")
