"""
ETL: build the production keyword JSONs from Marco's real datasets.

Sources merged (in priority order):
  1. scripts/existing_patterns.json — 374 hand-curated rows from the
     polished XLSX. EVERY row is included.
  2. scripts/dataset_expansion_results.csv — overnight expansion. Only
     rows with confiabilidad == 'alta' are included (189 rows). The
     'media' (213) and 'baja' (227) tiers are skipped — they're earned
     in via the auto-tuner (Phase 5).

Output: backend/classifier/keywords/phase{1..4}_captacion|enganche|
coercion|explotacion.json — the main keyword files the classifier
consumes at startup.

Preserved on overwrite: the `whitelist` array of each main JSON. These
were tuned manually to suppress benign matches ("el jale escolar",
"guardia de seguridad de mi escuela", etc.) and must NOT disappear
when we rewrite the patterns.

Run from project root:
    python scripts/etl_dataset.py
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
KEYWORDS_DIR = ROOT / "backend" / "classifier" / "keywords"

EXISTING_JSON = SCRIPT_DIR / "existing_patterns.json"
EXPANSION_CSV = SCRIPT_DIR / "dataset_expansion_results.csv"

PHASE_FILES = {
    1: ("phase1_captacion", "Captación", "Ofertas falsas, narcocultura, glorificación criminal"),
    2: ("phase2_enganche", "Enganche", "Datos personales, cambio de plataforma, confianza falsa"),
    3: ("phase3_coercion", "Coerción", "Amenazas, ultimátums, intimidación"),
    4: ("phase4_explotacion", "Explotación", "Actividades ilícitas, sextorsión, demanda financiera"),
}

# Curated mapping of CSV `intención` (and Marco's `intencion` field) to a
# user-facing Spanish phrase. Bot's "🧠 ¿Por qué?" reads from this.
EXPLANATION_MAP: dict[str, str] = {
    # symbology / identity
    "imposicion": "simbología de organización criminal",
    "imposición": "imposición coercitiva de un rol o tarea",
    "imposición_identidad": "imposición de identidad criminal sobre el menor",
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
    "aspiracional": "glorificación de estilo de vida criminal",
    "aspiracional_digital": "ostentación digital del estilo de vida criminal",
    # incentives
    "incentivo": "incentivo económico sospechoso",
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
    # recruitment
    "reclutamiento": "lenguaje explícito de reclutamiento criminal",
    "reclutamiento_operativo": "reclutamiento para rol operativo del cártel",
    "reclutamiento_menores": "reclutamiento dirigido a menores de edad",
    "reclutamiento_explícito": "convocatoria abierta de reclutamiento",
    "reclutamiento_forzado": "imposición forzada de reclutamiento criminal",
    "reclutamiento_secundario": "instrucción de reclutar a otros menores",
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
    # engagement
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
    # profiling / aislamiento
    "perfilamiento": "recopilación de información personal del menor",
    "perfilamiento_gaming": "perfilamiento durante interacción en videojuego",
    "suplantación_edad": "suplantación de edad para generar confianza",
    "catfishing": "suplantación de identidad para captación",
    "phishing": "intento de phishing (link malicioso)",
    "aislamiento": "intento de aislar de entorno seguro",
    "aislamiento_forzado": "aislamiento forzado, típico de trata o reclutamiento",
    "aislamiento_emocional": "aislamiento emocional contra figuras parentales",
    "aislamiento_psicológico": "aislamiento psicológico para someter a la víctima",
    "aislamiento_digital": "aislamiento digital eliminando red de contactos",
    "aislamiento_gaming": "intento de aislar contacto fuera del videojuego",
    "confianza": "construcción de confianza manipuladora",
    "confianza_falsa": "construcción de confianza manipuladora",
    "vinculo_emocional": "manipulación emocional",
    "manipulación": "manipulación con técnicas de grooming",
    "manipulación_emocional": "manipulación emocional clásica de grooming",
    "minimización": "minimización de la gravedad para reducir tu resistencia",
    "normalización": "discurso para normalizar la actividad criminal",
    "normalización_trata": "normalización del lenguaje propio de la trata",
    "presion_temporal": "presión con urgencia temporal",
    "urgencia": "creación artificial de urgencia",
    "presión": "presión para forzar una decisión rápida",
    "presión_social": "presión social usando al grupo como apalancamiento",
    "presión_masculinidad": "presión basada en estereotipos de masculinidad",
    "presión_comunitaria": "presión usando el barrio o la comunidad",
    "presión_deuda": "presión basada en una deuda inventada",
    "ultimátum": "ultimátum binario (cooperar o consecuencias)",
    "dependencia": "creación artificial de dependencia emocional",
    "culpa": "manipulación por culpa",
    "culpabilización": "culpabilización para mantener el sometimiento",
    "gaslighting": "gaslighting / negación de hechos para confundir",
    "empatía_falsa": "empatía fingida para construir confianza",
    "engaño": "promesa engañosa de salida posterior",
    "complicidad_gradual": "creación gradual de complicidad criminal",
    "desensibilización": "desensibilización progresiva ante la violencia",
    "prueba_lealtad": "exigencia de prueba de lealtad criminal",
    # coerción / amenazas
    "amenaza": "amenaza directa",
    "amenaza_familiar": "amenaza dirigida hacia tus familiares",
    "amenaza_muerte": "amenaza explícita de muerte",
    "amenaza_sextorsión": "amenaza de difusión de material íntimo (sextorsión)",
    "amenaza_deserción": "amenaza ante intento de abandonar el grupo",
    "amenaza_digital": "amenaza por medios digitales",
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
    "intimidación": "intimidación psicológica",
    "extorsión": "extorsión con cobro forzoso",
    "extorsión_financiera": "extorsión financiera con demanda monetaria",
    "extorsión_periódica": "imposición de cuota periódica",
    "chantaje": "chantaje basado en evidencia obtenida",
    "chantaje_video": "chantaje con material de video comprometedor",
    "chantaje_emocional": "chantaje emocional para forzar un acto",
    "control_total": "imposición de control total sobre tus acciones",
    "control_identidad": "imposición de un alias o cambio de identidad",
    "control_financiero": "imposición de control sobre tu dinero",
    "control_dispositivo": "imposición de control sobre tu celular",
    "control_digital": "imposición de control sobre tus cuentas digitales",
    "control_entrenamiento": "reglas de control durante el entrenamiento",
    "control": "imposición de control inmediato sobre tus pertenencias",
    "vigilancia": "vigilancia activa por parte del agresor",
    "vigilancia_digital": "vigilancia digital de tus redes sociales",
    "vigilancia_tech": "instalación de software espía en tu dispositivo",
    "retención": "discurso de retención forzada en el grupo",
    "retención_culpa": "retención apelando a la culpa por actos previos",
    "retención_deuda": "retención apelando a una deuda inventada",
    "retención_legal": "retención con amenaza de implicación legal",
    "servidumbre_deuda": "servidumbre por deuda inducida",
    # explotación / operativo
    "orden_directa": "instrucción operativa directa del cártel",
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
    "operación_droga": "operación de narcotráfico",
    "operación_vigilancia": "asignación de vigilancia (halconeo)",
    "operativo": "indicación operativa del cártel",
    "operativo_digital": "instrucción operativa con marcador digital (pin)",
    "lavado_dinero": "intento de involucrarte en lavado de dinero",
    "evasión_filtro": "intento de evadir filtros con leet speak",
    "evasión_detección": "intento de evadir detección operativa",
    "evasión": "indicación operativa de evadir rastreo",
    "código_droga": "código operativo del narcomenudeo",
    "codigo_narco": "código o jerga del narcotráfico",
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
    "código_vigilancia": "código operativo de vigilancia",
    "transferencia_código": "instrucción de transferencia financiera codificada",
    # sextortion / financial
    "sextorsion": "sextorsión o explotación sexual",
    "financiera": "demanda financiera o extorsión económica",
    "transaccional": "ofrecimiento transaccional por contenido íntimo",
    "red_flag_financiero": "red flag financiero (FinCEN)",
    "narcomarketing": "estrategia de narcomarketing en redes",
    # misc
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
    "instrucción_militar": "instrucción militar paramilitar",
    "punto_encuentro": "imposición de punto de encuentro físico",
    "contacto_inicial_estafa": "contacto inicial con técnica de estafa",
    "contacto_grupo": "invitación a un grupo cerrado",
    "contacto_gaming": "contacto inicial vía videojuego",
    "contacto_digital": "contacto inicial digital (DM)",
    "contacto_inicial": "contacto inicial sin pretexto claro",
    "rol_narcomenudeo": "rol específico del narcomenudeo",
    "salida_traslado": "instrucción de traslado controlado por el agresor",
    "traslado": "indicación de traslado a otro estado para 'capacitación'",
    "grooming": "señal clásica de grooming digital",
    "patron_detectado": "patrón sospechoso detectado",
}


def explanation_for(intencion: object) -> str:
    """Return a human-readable explanation for the why[] field."""
    key = str(intencion or "").strip().lower()
    if key in EXPLANATION_MAP:
        return EXPLANATION_MAP[key]
    if not key:
        return "patrón sospechoso detectado"
    # Fallback: humanize the snake_case category.
    return "señal de " + key.replace("_", " ")


def _read_existing_whitelists() -> dict[int, list[str]]:
    """Pull the current `whitelist` arrays from the production JSONs so
    they survive the overwrite. Whitelists stop benign matches like
    'el jale escolar' and were never in Marco's CSV."""
    out: dict[int, list[str]] = {1: [], 2: [], 3: [], 4: []}
    for fase, (stem, _name, _desc) in PHASE_FILES.items():
        path = KEYWORDS_DIR / f"{stem}.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            wl = data.get("whitelist") or []
            if isinstance(wl, list):
                out[fase] = [str(s) for s in wl]
        except (json.JSONDecodeError, OSError):
            pass
    return out


def _looks_like_regex(signal: str) -> bool:
    if not signal:
        return False
    if any(m in signal for m in ("\\d", "\\s", "\\b", "\\w")):
        return True
    if re.search(r"\([^)]+\|[^)]+\)", signal):
        return True
    if "$X" in signal or "$N" in signal:
        return True
    return False


def _entry(*, fase: int, idx: int, row: dict, source: str, conf: str = "alta") -> dict | None:
    signal = str(
        row.get("señal_base")
        or row.get("signal_base")
        or row.get("pattern")
        or ""
    ).strip()
    if not signal:
        return None
    intencion = (
        row.get("intención")
        or row.get("intencion")
        or row.get("category")
        or ""
    )
    weight_raw = row.get("peso") or row.get("weight") or "0.5"
    try:
        weight = float(weight_raw)
    except (TypeError, ValueError):
        weight = 0.5
    weight = max(0.0, min(weight, 1.0))
    pid = str(row.get("id") or "").strip() or f"f{fase}_{idx:03d}"
    fuente = str(row.get("fuente") or row.get("source") or "Derivado").strip() or "Derivado"
    tipo = str(row.get("tipo") or row.get("type") or "general").strip() or "general"
    return {
        "id": pid,
        "pattern": signal,
        "weight": round(weight, 3),
        "regex": _looks_like_regex(signal),
        "category": str(intencion).strip() or "general",
        "explanation": explanation_for(intencion),
        "source": fuente,
        "type": tipo,
        "signal_base": signal,
        "confidence": conf,
        "_source_origin": source,
    }


def process_existing_patterns() -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {1: [], 2: [], 3: [], 4: []}
    if not EXISTING_JSON.exists():
        return out
    rows = json.loads(EXISTING_JSON.read_text(encoding="utf-8"))
    for row in rows:
        fase_raw = row.get("fase") or row.get("phase") or 0
        if isinstance(fase_raw, str):
            fase = int(fase_raw.replace("Fase", "").strip() or 0)
        else:
            fase = int(fase_raw)
        if fase not in out:
            continue
        e = _entry(fase=fase, idx=len(out[fase]) + 1, row=row, source="existing_patterns.json", conf="alta")
        if e is not None:
            out[fase].append(e)
    return out


def process_expansion_csv(existing_ids: set[str]) -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {1: [], 2: [], 3: [], 4: []}
    if not EXPANSION_CSV.exists():
        return out
    with EXPANSION_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            conf = str(row.get("confiabilidad") or "").strip().lower()
            if conf != "alta":
                continue
            pid = str(row.get("id") or "").strip()
            if pid in existing_ids:
                continue
            fase_raw = row.get("fase") or "0"
            try:
                fase = int(str(fase_raw).replace("Fase", "").strip())
            except ValueError:
                continue
            if fase not in out:
                continue
            e = _entry(fase=fase, idx=len(out[fase]) + 1, row=row, source="dataset_expansion_results.csv", conf="alta")
            if e is not None:
                out[fase].append(e)
    return out


def main() -> int:
    print(f"ETL → {KEYWORDS_DIR}\n")
    KEYWORDS_DIR.mkdir(parents=True, exist_ok=True)

    whitelists = _read_existing_whitelists()
    print(f"Preserved whitelists: {sum(len(v) for v in whitelists.values())} entries")

    existing = process_existing_patterns()
    existing_total = sum(len(v) for v in existing.values())
    print(f"existing_patterns.json:            {existing_total} patterns "
          f"(p1={len(existing[1])} p2={len(existing[2])} p3={len(existing[3])} p4={len(existing[4])})")

    existing_ids = {p["id"] for v in existing.values() for p in v}
    csv_alta = process_expansion_csv(existing_ids)
    csv_total = sum(len(v) for v in csv_alta.values())
    print(f"dataset_expansion_results.csv (alta): {csv_total} patterns "
          f"(p1={len(csv_alta[1])} p2={len(csv_alta[2])} p3={len(csv_alta[3])} p4={len(csv_alta[4])})")

    grand = 0
    for fase, (stem, name, desc) in PHASE_FILES.items():
        merged = existing[fase] + csv_alta[fase]
        # Final dedup pass on (pattern,id).
        seen: set[tuple[str, str]] = set()
        out_patterns: list[dict] = []
        for p in merged:
            key = (p["id"], p["pattern"].lower())
            if key in seen:
                continue
            seen.add(key)
            out_patterns.append(p)

        doc = {
            "phase": stem,
            "phase_name": name,
            "description": desc,
            "total_patterns": len(out_patterns),
            "placeholder": False,
            "last_updated": "2026-04-26",
            "patterns": out_patterns,
            "whitelist": whitelists.get(fase, []),
            "_note": (
                "Generated by scripts/etl_dataset.py from existing_patterns.json + "
                "dataset_expansion_results.csv (alta). Whitelist preserved across "
                "rewrites — edit it manually in this file, not in the ETL."
            ),
        }
        out_path = KEYWORDS_DIR / f"{stem}.json"
        out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  → {out_path.relative_to(ROOT)}: {len(out_patterns)} patterns "
              f"(whitelist preserved: {len(whitelists.get(fase, []))})")
        grand += len(out_patterns)

    print(f"\n[DONE] {grand} patterns written. Restart the backend to load them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
