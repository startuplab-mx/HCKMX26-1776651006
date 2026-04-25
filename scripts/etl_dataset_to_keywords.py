"""
ETL: dataset_expansion_results.csv → backend/classifier/keywords/phase{1..4}_research.json

Why a separate file per phase?  The placeholder JSONs (phaseN_captacion etc.)
are the ones the team has been editing manually with explicit `explanation`
fields. We don't want to clobber them. The heuristic loader reads BOTH the
main file and the optional `_research.json` sibling, concatenating the
patterns. Whitelist stays only in the main file.

Filtering policy
----------------
We only ship `confiabilidad: alta` rows to production by default. The 213
`media` rows are emitted to a `*_research_media.json` sibling that the
loader skips by default — the auto-tuner will earn them in over time.
The 227 `baja` rows are not emitted at all (they're synthetic / derivado).

Run from the project root:
    python scripts/etl_dataset_to_keywords.py            # alta only (default)
    python scripts/etl_dataset_to_keywords.py --include-media

Reads:  scripts/dataset_expansion_results.csv
Writes: backend/classifier/keywords/phase{1..4}_research.json
        (and *_research_media.json with --include-media)
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "scripts" / "dataset_expansion_results.csv"
KEYWORDS_DIR = ROOT / "backend" / "classifier" / "keywords"

# Map CSV `fase` → output filename stem (matches PHASE_FILES in heuristic.py).
PHASE_FILE_STEM = {
    "Fase1": "phase1",
    "Fase2": "phase2",
    "Fase3": "phase3",
    "Fase4": "phase4",
}


# Curated mapping of CSV `intención` → human-readable explanation. For
# anything unmapped we fall back to a generated default. The point is the
# pipeline's `why[]` field — the bot's "🧠 ¿Por qué?" lines should read
# naturally in Spanish.
INTENCION_TEXT: dict[str, str] = {
    # Threats / coerción
    "amenaza_familiar": "amenaza dirigida hacia tus familiares",
    "amenaza_muerte": "amenaza explícita de muerte",
    "amenaza_sextorsión": "amenaza de difusión de material íntimo (sextorsión)",
    "amenaza_deserción": "amenaza ante intento de abandonar el grupo",
    "amenaza_digital": "amenaza de difusión de contenido digital privado",
    "amenaza_difusión": "amenaza de difusión masiva de contenido íntimo",
    "amenaza_doxxing": "amenaza de revelar tu identidad o ubicación pública",
    "amenaza_persecución": "amenaza de búsqueda y persecución",
    "amenaza_ubicación": "amenaza basada en conocer tu ubicación",
    "amenaza_silencio": "amenaza para imponer el silencio sobre lo ocurrido",
    "amenaza_existencial": "ultimátum de muerte o sometimiento",
    "amenaza_implícita": "amenaza velada con referencia a víctimas previas",
    "amenaza_evasiva": "amenaza con técnica de evasión de filtros (leet)",
    "amenaza_emoji": "amenaza codificada con emojis violentos",
    "amenaza_IA": "amenaza con material generado por IA (deepfake)",
    "amenaza_deepfake": "amenaza con material falso generado con IA",
    "amenaza_social": "amenaza de exposición social ante terceros",
    "amenaza_comunitaria": "amenaza de exposición ante tu comunidad inmediata",
    "amenaza_suplantación": "amenaza de crear perfiles falsos con tu identidad",
    "amenaza_exposición": "amenaza de exposición ante grupos rivales",
    "amenaza_desaparición": "amenaza de desaparición forzada",
    "amenaza_WhatsApp": "amenaza explícita por WhatsApp",
    "extorsión": "extorsión con cobro forzoso",
    "extorsión_financiera": "extorsión financiera con demanda monetaria",
    "extorsión_periódica": "imposición de cuota periódica",
    "chantaje": "chantaje basado en evidencia obtenida",
    "chantaje_video": "chantaje con material de video comprometedor",
    "chantaje_emocional": "chantaje emocional para forzar un acto",
    # Recruitment / captación
    "reclutamiento": "lenguaje explícito de reclutamiento criminal",
    "reclutamiento_operativo": "reclutamiento para rol operativo del cártel",
    "reclutamiento_menores": "reclutamiento dirigido a menores de edad",
    "reclutamiento_explícito": "convocatoria abierta de reclutamiento",
    "reclutamiento_forzado": "imposición forzada de reclutamiento criminal",
    "reclutamiento_secundario": "presión para que el menor reclute a más menores",
    "reclutamiento_edad_temprana": "reclutamiento dirigido a edad temprana",
    "reclutamiento_directo": "reclutamiento dirigido directo al menor",
    "reclutamiento_cascada": "presión para que el menor reclute a otros (cascada)",
    "reclutamiento_live": "reclutamiento durante transmisión en vivo",
    "reclutamiento_local": "reclutamiento dirigido a la zona del menor",
    "reclutamiento_organizado": "reclutamiento con citas y reuniones organizadas",
    "reclutamiento_escolar": "reclutamiento en entornos escolares",
    "reclutamiento_regional": "reclutamiento con énfasis regional",
    "reclutamiento_digital": "reclutamiento canalizado por redes digitales",
    "auto_reclutamiento": "expresión de auto-reclutamiento al cártel",
    # Identity / propaganda
    "identidad_criminal": "símbolo de identidad criminal organizada",
    "identidad_cartel": "referencia codificada a un cártel específico",
    "propaganda": "elemento de narcopropaganda",
    "narcopropaganda": "propaganda visual o textual de actividad criminal",
    "narcopropaganda_gaming": "propaganda criminal dentro de plataformas de videojuego",
    "narcocultura": "señal de narcocultura aspiracional",
    "lealtad": "discurso de lealtad al cártel",
    "jerarquía": "referencia a jerarquía interna del cártel",
    "territorialidad": "discurso de control territorial criminal",
    "espiritualidad_criminal": "espiritualidad asociada al narco",
    # Incentives
    "incentivo": "ofrecimiento de incentivo material para captar",
    "incentivo_económico": "oferta económica desproporcionada",
    "incentivo_familiar": "incentivo dirigido a beneficio familiar del menor",
    "incentivo_estudiantes": "incentivo dirigido a estudiantes",
    "incentivo_mujeres": "incentivo dirigido a mujeres en situación vulnerable",
    "incentivo_material": "ofrecimiento de bienes materiales (carro, ropa, arma)",
    "incentivo_visual": "ostentación visual del estilo de vida criminal",
    "incentivo_protección": "ofrecimiento de protección como incentivo",
    "incentivo_jerárquico": "promesa de ascenso rápido en la jerarquía",
    "incentivo_gaming": "ofrecimiento de bienes virtuales en videojuegos",
    "incentivo_social": "ofrecimiento de pertenencia social como anzuelo",
    "incentivo_migración": "incentivo ligado a migración o cruce fronterizo",
    "oferta_falsa": "oferta laboral señuelo del crimen organizado",
    "oferta_falsa_trata": "oferta laboral señuelo asociada a trata de personas",
    # Engagement / enganche
    "enganche": "intento de mover la conversación a un punto de captación",
    "enganche_laboral": "enganche disfrazado como proceso laboral",
    "enganche_sentimental": "enganche con discurso sentimental o de pareja",
    "enganche_grupo": "invitación a un grupo cerrado",
    "enganche_deuda": "creación de deuda como gancho de retención",
    "enganche_temporal": "engaño con promesa de ayuda temporal",
    "enganche_social": "invitación a evento o círculo social cerrado",
    "enganche_vivienda": "ofrecimiento de vivienda como gancho",
    "enganche_trata": "técnica de enganche típica de trata de personas",
    "enganche_presencial": "invitación a un encuentro presencial",
    # Profiling / perfilamiento
    "perfilamiento": "perfilamiento del menor para identificar vulnerabilidades",
    "perfilamiento_gaming": "perfilamiento durante interacción en videojuego",
    "suplantación_edad": "suplantación de edad para generar confianza",
    "catfishing": "perfil falso (catfishing) en redes sociales",
    "phishing": "intento de phishing (link malicioso)",
    # Isolation / aislamiento
    "aislamiento": "intento de aislar al menor de su red de apoyo",
    "aislamiento_forzado": "aislamiento forzado, típico de trata o reclutamiento",
    "aislamiento_emocional": "aislamiento emocional contra figuras parentales",
    "aislamiento_psicológico": "aislamiento psicológico para someter a la víctima",
    "aislamiento_digital": "aislamiento digital eliminando red de contactos",
    "aislamiento_gaming": "intento de aislar contacto fuera del videojuego",
    # Control / manipulación
    "control_total": "imposición de control total sobre tus acciones",
    "control_identidad": "imposición de un alias o cambio de identidad",
    "control_financiero": "imposición de control sobre tu dinero",
    "control_dispositivo": "imposición de control sobre tu celular",
    "control_digital": "imposición de control sobre tus cuentas digitales",
    "control_entrenamiento": "reglas de control durante el entrenamiento",
    "vigilancia": "vigilancia activa por parte del agresor",
    "vigilancia_digital": "vigilancia digital de tus redes sociales",
    "vigilancia_tech": "instalación de software espía en tu dispositivo",
    "manipulación": "manipulación con técnicas de grooming",
    "manipulación_emocional": "manipulación emocional clásica de grooming",
    "minimización": "minimización de la gravedad para reducir tu resistencia",
    "normalización": "discurso para normalizar la actividad criminal",
    "normalización_trata": "normalización del lenguaje propio de la trata",
    "imposición": "imposición coercitiva de un rol o tarea",
    "imposición_identidad": "imposición de identidad criminal sobre el menor",
    "presión": "presión para forzar una decisión rápida",
    "presión_social": "presión social usando al grupo como apalancamiento",
    "presión_masculinidad": "presión basada en estereotipos de masculinidad",
    "presión_comunitaria": "presión usando el barrio o la comunidad",
    "presión_deuda": "presión basada en una deuda inventada",
    "ultimátum": "ultimátum binario (cooperar o consecuencias)",
    "dependencia": "creación artificial de dependencia emocional",
    "culpabilización": "culpabilización para mantener el sometimiento",
    "gaslighting": "gaslighting / negación de hechos para confundir",
    "empatía_falsa": "empatía fingida para construir confianza",
    "engaño": "promesa engañosa de salida posterior",
    "complicidad_gradual": "creación gradual de complicidad criminal",
    "desensibilización": "desensibilización progresiva ante la violencia",
    "prueba_lealtad": "exigencia de prueba de lealtad criminal",
    "retención": "discurso de retención forzada en el grupo",
    "retención_culpa": "retención apelando a la culpa por actos previos",
    "retención_deuda": "retención apelando a una deuda inventada",
    "retención_legal": "retención con amenaza de implicación legal",
    "servidumbre_deuda": "servidumbre por deuda inducida",
    # Operational
    "orden_directa": "orden operativa directa del cártel",
    "orden_violenta": "orden de cometer un acto violento",
    "orden_armamento": "orden de manejar armas o equipo",
    "orden_extorsión": "orden de cobrar extorsión",
    "orden_inteligencia": "orden de realizar tareas de inteligencia",
    "orden_logística": "orden de tareas logísticas del cártel",
    "orden_encubrimiento": "orden de encubrir un delito",
    "orden_menor": "orden operativa de bajo riesgo (paso de prueba)",
    "orden_operativa": "orden operativa de campo",
    "orden_producción": "orden de producir mercancía ilícita",
    "orden_transporte": "orden de transportar paquetes ilícitos",
    "orden_vigilancia": "orden de vigilancia (halconeo)",
    "orden_comunicación": "orden de transmitir un mensaje del cártel",
    "orden_financiera": "orden de manejar el dinero del cártel",
    "orden_extorsión": "orden de cobrar extorsión",
    "lavado_dinero": "intento de involucrarte en lavado de dinero",
    "evasión_filtro": "intento de evadir filtros con leet speak",
    "evasión_detección": "intento de evadir detección operativa",
    "evasión": "indicación operativa de evadir rastreo",
    "código_droga": "código operativo asociado a tipo de droga",
    "código_arma": "jerga criminal asociada a armamento",
    "código_cantidad": "código operativo de cantidad o dosis",
    "código_alerta": "código operativo de alerta a fuerzas del orden",
    "código_operativo": "código operativo del cártel",
    "código_seguridad": "código de seguridad para evadir adultos",
    "código_numerico": "código numérico predatorio",
    "código_vehículo": "código operativo asociado a vehículos",
    "código_temporal": "código operativo basado en tiempo",
    "código_problema": "código operativo de problema en operación",
    "código_cita": "código operativo para concertar cita",
    "código_completado": "código operativo de transacción completada",
    "código_confirmación": "código operativo de confirmación",
    "código_faltante": "código operativo de faltante u objeto no encontrado",
    "código_retorno": "código operativo de retorno o regreso",
    "código_seguimiento": "código operativo de seguimiento o rastreo",
    "código_silencio": "código de silencio criminal",
    "código_territorial": "código asociado a control territorial",
    "código_emoji_predador": "emoji codificado por agresores sexuales (AFP)",
    "código_comunicación": "código operativo de comunicación interna",
    "código_droga": "código operativo del narcomenudeo",
    "transferencia_código": "instrucción de transferencia financiera codificada",
    "código_vigilancia": "código operativo de vigilancia",
    # Misc
    "explotación": "explotación operativa o sexual del menor",
    "escalamiento": "escalamiento gradual hacia conducta de mayor riesgo",
    "escalamiento_gradual": "escalamiento gradual de tareas de complicidad",
    "escalamiento_sexual": "escalamiento hacia contenido sexual",
    "escalamiento_presencial": "escalamiento del contacto digital al presencial",
    "tráfico_migrantes": "ofrecimiento ligado a tráfico de migrantes",
    "captación_migrantes": "captación dirigida a personas migrantes",
    "captación_vulnerables": "captación dirigida a personas en vulnerabilidad",
    "captación_inicial": "captación inicial mediante regalos u obsequios",
    "captación_ESCI": "captación con fines de explotación sexual comercial",
    "ciberbullying": "ciberbullying con potencial de derivar a coerción",
    "predatorio": "señal predatoria documentada (AFP)",
    "estadística": "dato estadístico citado en el patrón",
    "dato": "dato cuantitativo citado en el patrón",
    "monetización_reclutamiento": "intento de monetizar el reclutamiento en vivo",
    "comunicación_criminal": "comunicación criminal pública (narcomanta)",
    "eufemismo": "eufemismo del lenguaje criminal",
    "eufemismo_violencia": "eufemismo para encubrir un acto violento",
    "desconfianza_institucional": "discurso de desconfianza institucional",
    "desvalorización_educación": "desvalorización del valor de la educación",
    "presentación_jerárquica": "presentación al líder del grupo",
    "pertenencia": "construcción artificial de sentido de pertenencia",
    "inclusión_falsa": "discurso falso de inclusión universal",
    "migración_plataforma": "intento de mover la conversación a app cifrada",
    "anonimización": "intento de imponer anonimato (alias, cuenta nueva)",
    "urgencia": "creación artificial de urgencia",
    "transaccional": "ofrecimiento transaccional por contenido íntimo",
    "red_flag_financiero": "red flag financiero (FinCEN)",
    "instrucción_militar": "instrucción militar paramilitar",
    "punto_encuentro": "imposición de punto de encuentro físico",
    "control": "imposición de control inmediato sobre tus pertenencias",
    "contacto_inicial_estafa": "contacto inicial con técnica de estafa",
    "contacto_grupo": "invitación a un grupo cerrado",
    "contacto_gaming": "contacto inicial vía videojuego",
    "contacto_digital": "contacto inicial digital (DM)",
    "contacto_inicial": "contacto inicial sin pretexto claro",
    "rol_narcomenudeo": "rol específico del narcomenudeo",
    "operativo_digital": "instrucción operativa con marcador digital (pin)",
    "operativo": "indicación operativa del cártel",
    "aspiracional": "discurso aspiracional de la vida criminal",
    "aspiracional_digital": "ostentación digital del estilo de vida criminal",
    "confianza": "construcción artificial de confianza",
    "grooming": "señal clásica de grooming digital",
    "salida_traslado": "instrucción de traslado controlado por el agresor",
    "traslado": "indicación de traslado a otro estado para 'capacitación'",
    "punto_encuentro": "fijación de punto de encuentro presencial",
    "narcomarketing": "estrategia de narcomarketing en redes",
}


def explanation_for(intencion: str, fuente: str) -> str:
    """Return a human-readable explanation for the why[] field."""
    if intencion in INTENCION_TEXT:
        return INTENCION_TEXT[intencion]
    # Fallback: humanize the snake_case category.
    return "señal de " + intencion.replace("_", " ").lower()


def looks_like_regex(signal: str) -> bool:
    """Best-effort detection: does the CSV's `señal_base` use regex syntax?

    Most rows are literal phrases. A few have parenthesised alternations
    or character classes ("$X,000 semanales"). When in doubt we default
    to literal — the heuristic re-escapes literals, so false negatives
    are safer than false positives.
    """
    if not signal:
        return False
    # Common regex meta sequences.
    if any(m in signal for m in ("\\d", "\\s", "\\b", "\\w")):
        return True
    if re.search(r"\([a-zA-ZñáéíóúüÑÁÉÍÓÚÜ ]+\|[a-zA-ZñáéíóúüÑÁÉÍÓÚÜ ]+\)", signal):
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-media",
        action="store_true",
        help="Also emit *_research_media.json (213 rows of medium confidence).",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=CSV_PATH,
        help="Path to dataset_expansion_results.csv (default: scripts/...)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=KEYWORDS_DIR,
        help="Where to write phaseN_research.json (default: backend/classifier/keywords/)",
    )
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"❌ CSV not found: {args.csv}")
        return 1
    args.out_dir.mkdir(parents=True, exist_ok=True)

    by_phase_alta: dict[str, list[dict]] = defaultdict(list)
    by_phase_media: dict[str, list[dict]] = defaultdict(list)
    counts = Counter()

    with args.csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fase = (row.get("fase") or "").strip()
            stem = PHASE_FILE_STEM.get(fase)
            if not stem:
                continue
            try:
                weight = float(row["peso"])
            except (KeyError, ValueError):
                continue
            confiabilidad = (row.get("confiabilidad") or "").strip().lower()
            counts[confiabilidad] += 1

            entry = {
                "id": (row.get("id") or "").strip(),
                "pattern": (row.get("señal_base") or "").strip(),
                "weight": round(max(0.0, min(weight, 1.0)), 3),
                "source": (row.get("fuente") or "").strip(),
                "regex": looks_like_regex(row.get("señal_base") or ""),
                "explanation": explanation_for(
                    (row.get("intención") or "").strip(),
                    (row.get("fuente") or "").strip(),
                ),
                "url": (row.get("url_fuente") or "").strip() or None,
            }
            # Drop empty patterns / dupes against the in-memory bucket.
            if not entry["pattern"]:
                continue

            if confiabilidad == "alta":
                by_phase_alta[stem].append(entry)
            elif confiabilidad == "media":
                by_phase_media[stem].append(entry)
            # baja → discarded; auto-tuner will earn them in.

    def write_bucket(bucket: dict[str, list[dict]], suffix: str, label: str) -> int:
        total = 0
        for stem in ("phase1", "phase2", "phase3", "phase4"):
            entries = bucket.get(stem, [])
            phase_name = {
                "phase1": "captacion",
                "phase2": "enganche",
                "phase3": "coercion",
                "phase4": "explotacion",
            }[stem]
            doc = {
                "phase": phase_name,
                "phase_name": phase_name.capitalize(),
                "description": (
                    f"Patrones {label} importados desde "
                    "dataset_expansion_results.csv (Marco · expansión nocturna)."
                ),
                "_note": (
                    "ETL-generated. Edits must go through "
                    "scripts/etl_dataset_to_keywords.py to stay reproducible."
                ),
                "patterns": entries,
                "whitelist": [],
            }
            out = args.out_dir / f"{stem}_research{suffix}.json"
            out.write_text(
                json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"  → {out.relative_to(ROOT)}: {len(entries)} patterns")
            total += len(entries)
        return total

    print("Source counts:")
    for k, v in counts.most_common():
        print(f"  {k:8s}  {v}")
    print()

    print("Writing alta tier:")
    alta_total = write_bucket(by_phase_alta, "", "de alta confiabilidad")
    print(f"  total alta: {alta_total}")

    if args.include_media:
        print("\nWriting media tier:")
        media_total = write_bucket(by_phase_media, "_media", "de confiabilidad media")
        print(f"  total media: {media_total}")
    else:
        print("\n(skipping media tier — pass --include-media to emit it too)")

    print("\n✅ ETL done. Restart the backend to pick up the new patterns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
