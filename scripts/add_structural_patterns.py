"""Structural patch — adds victim-perspective + money-without-$ +
distress + universal-money patterns suggested by the structural audit
(D:\\nahual prompt, Apr 25 2026).

Idempotent: skips patterns already present by exact match.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KW = ROOT / "backend" / "classifier" / "keywords"

# CAPA B-1 — Captación, perspectiva víctima.
PHASE1 = [
    ("me ofrecieron dinero",                0.6,  "oferta_recibida", "víctima reporta oferta económica"),
    ("me ofrecieron trabajo",               0.55, "oferta_recibida", "víctima reporta oferta de empleo"),
    ("me ofrecieron chamba",                0.55, "oferta_recibida", "víctima reporta oferta informal"),
    ("me ofrecieron jale",                  0.7,  "oferta_recibida", "víctima reporta oferta jerga cartel"),
    ("me ofrecen dinero",                   0.6,  "oferta_recibida", "víctima reporta oferta presente"),
    ("me ofrecen pesos",                    0.65, "oferta_recibida", "víctima reporta cantidad MX"),
    ("me dijeron que gano",                 0.55, "oferta_recibida", "promesa salarial recibida"),
    ("me dijeron que puedo ganar",          0.55, "oferta_recibida", "promesa salarial recibida"),
    ("me dijeron que voy a ganar",          0.55, "oferta_recibida", "promesa salarial recibida"),
    ("alguien me ofrecio",                  0.5,  "oferta_recibida", "actor desconocido"),
    ("un desconocido me contacto",          0.5,  "perfilamiento",   "primer contacto sospechoso"),
    ("un desconocido me escribio",          0.5,  "perfilamiento",   "primer contacto sospechoso"),
    ("me escribio alguien que no conozco",  0.5,  "perfilamiento",   "primer contacto sospechoso"),
    ("me mandaron mensaje ofreciendo",      0.55, "oferta_recibida", "oferta no solicitada"),
    ("me invitaron a un jale",              0.7,  "oferta_recibida", "invitación jerga cartel"),
    ("me invitaron a chambear",             0.55, "oferta_recibida", "invitación informal"),
    ("me invitaron a trabajar con ellos",   0.6,  "oferta_recibida", "invitación a colectivo desconocido"),
    ("me prometieron dinero",               0.6,  "oferta_recibida", "promesa económica"),
    ("me prometieron pago",                 0.55, "oferta_recibida", "promesa salarial"),
    ("me prometieron lana",                 0.65, "oferta_recibida", "promesa jerga MX"),
    ("vi un anuncio de trabajo",            0.4,  "fronts_falsos",   "anuncio sospechoso (genérico)"),
    ("vi un anuncio de dinero facil",       0.7,  "fronts_falsos",   "anuncio dinero fácil"),
    ("me contactaron por tiktok",           0.5,  "red_social_dm",   "primer contacto en TikTok"),
    ("me contactaron por instagram",        0.5,  "red_social_dm",   "primer contacto en IG"),
    ("me contactaron por discord",          0.55, "red_social_dm",   "primer contacto en Discord"),
    ("me contactaron por roblox",           0.6,  "red_social_dm",   "primer contacto en Roblox"),
    ("me agregaron de la nada",             0.4,  "perfilamiento",   "amistad/contacto no solicitado"),
    ("un tipo en tiktok me ofrecio",        0.65, "red_social_dm",   "actor + plataforma + oferta"),
    ("un cuate de internet me ofrecio",     0.55, "red_social_dm",   "actor desconocido en internet"),
    # CAPA D — Universal money patterns (regex, no $).
    (r"\d{4,6}\s*(pesos|varos|bolas|lucas)\s*(semanal|diario|al d[ií]a|a la semana|por semana|al mes|mensuales?)", 0.7, "oferta_economica", "dinero+frecuencia explícita", True),
    (r"\d{1,3}000\s*(pesos|varos)?\s*(semanal|a la semana|al mes|diario)", 0.7, "oferta_economica", "miles redondos + frecuencia", True),
    (r"(ganas?|ganar[ai]?s?|haces?)\s*\d{4,6}", 0.5, "oferta_economica", "verbo ganar + cantidad", True),
    (r"(te |les? )(pago|pagamos|damos|ofrecemos?)\s*\d{3,6}", 0.65, "oferta_economica", "verbo pago + cantidad", True),
    (r"te\s*(doy|damos)\s*\d+\s*(pesos|varos|bolas)", 0.65, "oferta_economica", "te doy/damos + cantidad", True),
]

PHASE2 = [
    ("me pidieron mi escuela",                 0.65, "perfilamiento", "pedido datos escolares"),
    ("me pidieron mis datos",                  0.6,  "perfilamiento", "pedido PII genérico"),
    ("me pidieron mi nombre completo",         0.55, "perfilamiento", "pedido nombre completo"),
    ("me pidieron donde vivo",                 0.7,  "perfilamiento", "pedido domicilio"),
    ("me pidieron mi direccion",               0.75, "perfilamiento", "pedido dirección"),
    ("me pidieron que me pasara a telegram",   0.65, "aislamiento_canal", "cambio canal recibido"),
    ("me pidieron que cambiara a signal",      0.65, "aislamiento_canal", "cambio canal recibido"),
    ("me pidieron que fuera a discord",        0.6,  "aislamiento_canal", "cambio canal recibido"),
    ("me dijeron que era un secreto",          0.6,  "aislamiento_secreto", "secrecía recibida"),
    ("me dijeron que era confidencial",        0.55, "aislamiento_secreto", "secrecía recibida"),
    ("me dijeron que era entre nosotros",      0.55, "aislamiento_secreto", "secrecía recibida"),
    ("me preguntaron si necesito dinero",      0.5,  "perfilamiento", "sondeo necesidad económica"),
    ("me preguntaron si ando corto",           0.5,  "perfilamiento", "sondeo necesidad económica"),
    ("me preguntaron si mis papas tienen",     0.55, "perfilamiento", "sondeo familia económica"),
    ("me presionaron para responder",          0.5,  "presion_temporal", "presión temporal"),
    ("me presionaron para decidir rapido",     0.55, "presion_temporal", "presión decisión rápida"),
    ("insistieron mucho",                      0.3,  "presion_temporal", "presión múltiple"),
    ("no me dejaban en paz",                   0.4,  "presion_temporal", "presión sostenida"),
]

# CAPA B-3 — Coerción victim + distress.
PHASE3 = [
    ("me amenazaron de muerte",            0.95, "amenaza_recibida", "amenaza de muerte recibida"),
    ("me amenazaron con matarme",          0.95, "amenaza_recibida", "amenaza con matar recibida"),
    ("me amenazaron con hacerme dano",     0.9,  "amenaza_recibida", "amenaza daño físico recibida"),
    ("si no respondo me van a",             0.85, "amenaza_condicional_recibida", "condicional + amenaza"),
    ("si no contesto me van a",             0.85, "amenaza_condicional_recibida", "condicional + amenaza"),
    ("si no voy me van a",                  0.85, "amenaza_condicional_recibida", "condicional + amenaza"),
    ("si no pago me van a",                 0.85, "amenaza_condicional_recibida", "condicional + amenaza"),
    ("si no hago lo que dicen me",          0.85, "amenaza_condicional_recibida", "condicional + amenaza"),
    ("me tienen amenazado",                 0.85, "amenaza_recibida", "estado amenaza activa"),
    ("me tienen presionado",                0.7,  "amenaza_recibida", "estado presión activa"),
    ("me tienen vigilado",                  0.85, "vigilancia_recibida", "vigilancia activa"),
    ("me estan siguiendo",                  0.75, "vigilancia_recibida", "vigilancia activa"),
    ("me estan vigilando",                  0.8,  "vigilancia_recibida", "vigilancia activa"),
    ("me estan acosando",                   0.7,  "acoso_recibido", "acoso activo"),
    ("me dijeron que ya saben demasiado",   0.85, "amenaza_silencio_recibida", "amenaza por conocimiento"),
    ("me dijeron que no hay vuelta",        0.85, "coercion_no_salida", "coerción no escape"),
    ("me dijeron que no hay salida",        0.85, "coercion_no_salida", "coerción no escape"),
    ("siento que estoy en peligro",         0.6,  "distress_anticipacion", "anticipación amenaza"),
    ("me obligaron a",                      0.8,  "coercion_obligacion", "obligación recibida"),
    ("no me dejan salir",                   0.8,  "privacion_libertad_recibida", "imposibilidad salir"),
    ("no me dejan irme",                    0.8,  "privacion_libertad_recibida", "imposibilidad irse"),
    ("no me dejan escapar",                 0.85, "privacion_libertad_recibida", "imposibilidad escapar"),
    # CAPA E — Distress / SOS
    ("tengo mucho miedo",                   0.6,  "distress_miedo", "estado de miedo"),
    ("tengo miedo de que me hagan algo",    0.7,  "distress_anticipacion", "miedo daño anticipado"),
    ("tengo miedo de que me pase algo",     0.7,  "distress_anticipacion", "miedo daño anticipado"),
    ("estoy asustado",                      0.55, "distress_miedo", "estado de miedo"),
    ("estoy asustada",                      0.55, "distress_miedo", "estado de miedo"),
    ("estoy aterrado",                      0.6,  "distress_miedo", "estado de pánico"),
    ("estoy aterrada",                      0.6,  "distress_miedo", "estado de pánico"),
    ("creo que me van a hacer algo",        0.65, "distress_anticipacion", "anticipación daño"),
    ("creo que van a hacerme algo",         0.65, "distress_anticipacion", "anticipación daño"),
    ("necesito ayuda urgente",              0.55, "distress_urgencia", "petición ayuda urgente"),
    ("necesito ayuda ya",                   0.55, "distress_urgencia", "petición ayuda inmediata"),
    ("necesito ayuda ahora",                0.55, "distress_urgencia", "petición ayuda inmediata"),
    ("no puedo dormir del miedo",           0.5,  "distress_impacto", "impacto fisiológico"),
    ("no puedo comer del miedo",            0.5,  "distress_impacto", "impacto fisiológico"),
    ("no puedo salir del miedo",            0.5,  "distress_impacto", "impacto agorafobia"),
    ("me siento atrapado",                  0.6,  "distress_aislamiento", "sensación atrapamiento"),
    ("me siento atrapada",                  0.6,  "distress_aislamiento", "sensación atrapamiento"),
    ("alguien me dijo que me iban a desaparecer", 0.95, "amenaza_recibida", "amenaza desaparición recibida"),
]

PHASE4 = [
    ("me obligaron a hacer",        0.8,  "coercion_obligacion_op", "obligación operativa"),
    ("me obligaron a llevar",       0.85, "coercion_obligacion_op", "obligación trasladar (paquete)"),
    ("me obligaron a transportar",  0.9,  "coercion_obligacion_op", "obligación transportar"),
    ("me obligaron a vender",       0.9,  "coercion_obligacion_op", "obligación venta (probable droga)"),
    ("me obligaron a entregar",     0.85, "coercion_obligacion_op", "obligación entrega"),
    ("me pidieron que reclutara",   0.85, "reclutamiento_op",       "reclutamiento de pares"),
    ("me pidieron que trajera amigos", 0.85, "reclutamiento_op",    "traer pares al cartel"),
    ("me pidieron que convenciera a", 0.8, "reclutamiento_op",      "convencer pares"),
    ("me estan extorsionando",      0.9,  "extorsion_recibida",     "extorsión activa"),
    ("me estan chantajeando",       0.9,  "extorsion_recibida",     "chantaje activo"),
    ("me piden dinero o van a",     0.95, "sextorsion_chantaje",    "extorsión con condicional"),
    ("me piden fotos o van a",      0.95, "sextorsion_chantaje",    "sextorsión con condicional"),
    ("me piden nudes o van a",      0.95, "sextorsion_chantaje",    "sextorsión con condicional"),
    ("me sacaron fotos sin permiso",0.95, "csam_sin_consent",       "CSAM sin consentimiento"),
    ("me sacaron videos sin permiso",0.95,"csam_sin_consent",       "CSAM sin consentimiento"),
    ("me hicieron fotos con ia",    0.85, "csam_deepfake",          "deepfake CSAM"),
    ("me hicieron videos con ia",   0.85, "csam_deepfake",          "deepfake CSAM"),
    ("me piden que deposite",       0.7,  "extorsion_recibida",     "petición depósito"),
    ("me piden que transfiera",     0.7,  "extorsion_recibida",     "petición transferencia"),
    ("me estan cobrando",           0.5,  "extorsion_recibida",     "cobro irregular"),
]


def patch(phase_num: int, fname: str, new_patterns: list) -> tuple[int, int]:
    path = KW / fname
    data = json.loads(path.read_text(encoding="utf-8"))
    patterns = data["patterns"]
    existing = {p["pattern"].lower() for p in patterns}
    next_id = max(int(p["id"].split("_")[1]) for p in patterns) + 1
    added = 0
    for spec in new_patterns:
        # Allow optional 5th element = is_regex flag.
        if len(spec) == 5:
            pat, weight, cat, expl, is_regex = spec
        else:
            pat, weight, cat, expl = spec
            is_regex = False
        if pat.lower() in existing:
            continue
        patterns.append({
            "id": f"f{phase_num}_{next_id:03d}",
            "pattern": pat,
            "weight": weight,
            "regex": is_regex,
            "category": cat,
            "explanation": expl,
            "source": "structural_audit_2026_04_25",
            "type": "victim_or_distress_or_money",
            "signal_base": weight,
            "confidence": "alta",
            "_source_origin": "structural_audit",
        })
        next_id += 1
        added += 1
    data["patterns"] = patterns
    data["updated_at"] = "2026-04-25T15:45:00Z"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return added, len(patterns)


if __name__ == "__main__":
    a1, t1 = patch(1, "phase1_captacion.json", PHASE1)
    a2, t2 = patch(2, "phase2_enganche.json", PHASE2)
    a3, t3 = patch(3, "phase3_coercion.json", PHASE3)
    a4, t4 = patch(4, "phase4_explotacion.json", PHASE4)
    print(f"Phase1: +{a1} (total {t1})")
    print(f"Phase2: +{a2} (total {t2})")
    print(f"Phase3: +{a3} (total {t3})")
    print(f"Phase4: +{a4} (total {t4})")
    print(f"GRAND: +{a1 + a2 + a3 + a4}")
