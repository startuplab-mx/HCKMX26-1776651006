"""
backend/legal/framework.py

Mapeo programático del marco jurídico mexicano al sistema de detección
de Nahual. Cada fase y categoría tiene artículos de ley, penas,
autoridades competentes, y números de contacto asociados.

Consumido por:
- backend/reports/pdf_generator.py → secciones legales dinámicas en el PDF
- backend/main.py → campo `legal` en /analyze y /alert responses
- bot/handlers/flowController.js → mensajes con autoridades + acciones reales
- panel/index.html → vista de detalle por alerta

El módulo es la fuente única de verdad jurídica del sistema. Cuando una
ley cambia (reformas), se actualiza aquí y todo el stack queda alineado.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class LegalArticle:
    """Un artículo de ley específico."""
    law_name: str             # "Código Penal Federal"
    law_abbreviation: str     # "CPF"
    article: str              # "Art. 209 Quáter"
    title: str                # "Reclutamiento Ilícito"
    summary: str              # Descripción breve
    penalty: str | None = None        # "9-18 años de prisión"
    source_url: str = ""


@dataclass(frozen=True)
class Authority:
    """Autoridad competente para denuncia o emergencia."""
    name: str                 # "Policía Cibernética"
    phone: str                # "088"
    hours: str                # "24/7"
    jurisdiction: str         # "Federal"
    description: str


@dataclass
class LegalContext:
    """Contexto legal completo para un tipo de detección.

    `urgency_level`:
        - "inmediata"   → riesgo PELIGRO, requiere acción ya
        - "prioritaria" → señales de enganche o coerción incipiente
        - "preventiva"  → captación temprana, riesgo bajo
    """
    articles: list[LegalArticle] = field(default_factory=list)
    authorities: list[Authority] = field(default_factory=list)
    victim_rights: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    urgency_level: Literal["inmediata", "prioritaria", "preventiva"] = "preventiva"


# ═══════════════════════════════════════════════════════════════════
# ARTÍCULOS DE LEY
# ═══════════════════════════════════════════════════════════════════

ARTICLES: dict[str, LegalArticle] = {
    "cpeum_16": LegalArticle(
        law_name="Constitución Política de los Estados Unidos Mexicanos",
        law_abbreviation="CPEUM",
        article="Art. 16, párrafos 12-13",
        title="Inviolabilidad de las Comunicaciones Privadas",
        summary=(
            "Las comunicaciones privadas son inviolables. La ley sanciona "
            "penalmente cualquier acto que atente contra su libertad y privacía, "
            "excepto cuando sean aportadas voluntariamente por alguno de los "
            "particulares que participen en ellas."
        ),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf",
    ),
    "cpeum_4": LegalArticle(
        law_name="Constitución Política de los Estados Unidos Mexicanos",
        law_abbreviation="CPEUM",
        article="Art. 4, párrafo 9",
        title="Interés Superior de la Niñez",
        summary=(
            "En todas las decisiones y actuaciones del Estado se velará y cumplirá "
            "con el principio del interés superior de la niñez, garantizando de "
            "manera plena sus derechos."
        ),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf",
    ),
    "lgdnna_47_vii": LegalArticle(
        law_name="Ley General de los Derechos de Niñas, Niños y Adolescentes",
        law_abbreviation="LGDNNA",
        article="Art. 47, fracción VII",
        title="Protección contra Reclutamiento Criminal",
        summary=(
            "Las autoridades deben tomar medidas para prevenir la incitación o "
            "coacción a menores para que participen en la comisión de delitos o "
            "en asociaciones delictuosas."
        ),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LGDNNA.pdf",
    ),
    "lgdnna_48": LegalArticle(
        law_name="Ley General de los Derechos de Niñas, Niños y Adolescentes",
        law_abbreviation="LGDNNA",
        article="Art. 48",
        title="Medidas de Protección Especial",
        summary=(
            "Las autoridades deben adoptar medidas especiales de protección para "
            "NNA víctimas de delitos, incluyendo asistencia jurídica y psicológica."
        ),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LGDNNA.pdf",
    ),
    "cpf_209quater": LegalArticle(
        law_name="Código Penal Federal",
        law_abbreviation="CPF",
        article="Art. 209 Quáter",
        title="Reclutamiento Ilícito de Menores",
        summary=(
            "Comete el delito de reclutamiento ilícito quien enliste, reclute u "
            "obligue a participar directa o indirectamente en hostilidades o "
            "acciones armadas a menores de 18 años."
        ),
        penalty="9 a 18 años de prisión + 1,000 a 2,500 días de multa",
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/CPF.pdf",
    ),
    "cpf_199octies": LegalArticle(
        law_name="Código Penal Federal",
        law_abbreviation="CPF",
        article="Art. 199 Octies",
        title="Violación a la Intimidad Sexual (Ley Olimpia)",
        summary=(
            "Comete delito quien divulgue, comparta o publique imágenes, videos "
            "o audios de contenido íntimo sexual sin consentimiento. Incluye "
            "quien los elabore sin autorización."
        ),
        penalty="3 a 6 años de prisión + 500 a 1,000 UMA de multa",
        source_url="https://mexico.justia.com/federales/codigos/codigo-penal-federal/libro-segundo/titulo-septimo-bis/capitulo-ii/",
    ),
    "cpf_199nonies": LegalArticle(
        law_name="Código Penal Federal",
        law_abbreviation="CPF",
        article="Art. 199 Nonies",
        title="Falsificación de Imágenes (Deepfakes)",
        summary=(
            "Se imponen las mismas penas cuando las imágenes, videos o audios no "
            "correspondan con la persona señalada (cubre deepfakes y material "
            "generado con IA)."
        ),
        penalty="3 a 6 años de prisión",
        source_url="https://mexico.justia.com/federales/codigos/codigo-penal-federal/libro-segundo/titulo-septimo-bis/capitulo-ii/",
    ),
    "cpf_199decies": LegalArticle(
        law_name="Código Penal Federal",
        law_abbreviation="CPF",
        article="Art. 199 Decies",
        title="Agravantes de Violación a la Intimidad Sexual",
        summary=(
            "La pena se aumenta hasta en una mitad cuando: sea cometido por "
            "persona con relación sentimental, servidor público, contra quien "
            "no pueda comprender el hecho, con fines lucrativos, o cuando la "
            "víctima atente contra su vida como consecuencia."
        ),
        penalty="4.5 a 9 años de prisión (con agravante)",
        source_url="https://mexico.justia.com/federales/codigos/codigo-penal-federal/libro-segundo/titulo-septimo-bis/capitulo-ii/",
    ),
    "lgamvlv_20quater": LegalArticle(
        law_name="Ley General de Acceso de las Mujeres a una Vida Libre de Violencia",
        law_abbreviation="LGAMVLV",
        article="Art. 20 Quáter",
        title="Violencia Digital",
        summary=(
            "Acciones en las que se expongan, distribuyan o compartan imágenes, "
            "audios o videos de contenido íntimo sexual sin consentimiento, "
            "causando daño psicológico, emocional o sexual."
        ),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LGAMVLV.pdf",
    ),
    "lfpdppp_5": LegalArticle(
        law_name="Ley Federal de Protección de Datos Personales en Posesión de los Particulares",
        law_abbreviation="LFPDPPP",
        article="Arts. 5-8",
        title="Principios de Protección de Datos",
        summary=(
            "Todo tratamiento de datos personales debe observar los principios "
            "de licitud, finalidad, lealtad, consentimiento, calidad, "
            "proporcionalidad, información y responsabilidad."
        ),
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPDPPP.pdf",
    ),
    "lgpsedmtp_10": LegalArticle(
        law_name="Ley General para Prevenir y Sancionar los Delitos en Materia de Trata de Personas",
        law_abbreviation="LGPSEDMTP",
        article="Art. 10",
        title="Explotación: Utilización de Menores en Actividades Delictivas",
        summary=(
            "Define como forma de explotación la utilización de personas menores "
            "de 18 años en actividades delictivas."
        ),
        penalty="Variable según modalidad",
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/LGPSEDMTP.pdf",
    ),
    "cpf_282": LegalArticle(
        law_name="Código Penal Federal",
        law_abbreviation="CPF",
        article="Art. 282",
        title="Amenazas",
        summary=(
            "Se aplicará sanción a quien amenace a otro con causarle un mal en "
            "su persona, bienes, honor o derechos."
        ),
        penalty="6 meses a 2 años de prisión (amenaza simple); más con agravantes",
        source_url="https://www.diputados.gob.mx/LeyesBiblio/pdf/CPF.pdf",
    ),
}


# ═══════════════════════════════════════════════════════════════════
# AUTORIDADES COMPETENTES
# ═══════════════════════════════════════════════════════════════════

AUTHORITIES: dict[str, Authority] = {
    "policia_cibernetica": Authority(
        name="Policía Cibernética",
        phone="088",
        hours="24 horas, 7 días",
        jurisdiction="Federal",
        description=(
            "Atención a delitos cibernéticos, riesgos digitales, sextorsión, "
            "reclutamiento en línea"
        ),
    ),
    "fiscalia": Authority(
        name="Fiscalía General de la República / Fiscalía Estatal",
        phone="Fiscalía local según estado",
        hours="Horario laboral (urgencias 24/7)",
        jurisdiction="Federal / Estatal",
        description=(
            "Investigación y persecución de delitos. Presentar denuncia formal."
        ),
    ),
    "fevimtra": Authority(
        name="Fiscalía Especial para Delitos de Violencia contra las Mujeres y Trata de Personas (FEVIMTRA)",
        phone="800-00-854-00",
        hours="24 horas",
        jurisdiction="Federal",
        description="Trata de personas, explotación sexual, reclutamiento forzado",
    ),
    "dif": Authority(
        name="Sistema Nacional para el Desarrollo Integral de la Familia (DIF)",
        phone="DIF local según estado",
        hours="Horario laboral",
        jurisdiction="Estatal / Municipal",
        description="Protección de menores en situación de riesgo",
    ),
    "sipinna": Authority(
        name="Sistema Nacional de Protección Integral de Niñas, Niños y Adolescentes",
        phone="sipinna.gob.mx",
        hours="N/A (coordinación institucional)",
        jurisdiction="Federal",
        description="Coordinación de políticas de protección de NNA",
    ),
    "linea_vida": Authority(
        name="Línea de la Vida",
        phone="800-911-2000",
        hours="24 horas, 7 días",
        jurisdiction="Federal",
        description=(
            "Crisis emocional, ideación suicida, apoyo psicológico inmediato"
        ),
    ),
    "comision_busqueda": Authority(
        name="Comisión Nacional de Búsqueda de Personas",
        phone="800-800-2835",
        hours="24 horas",
        jurisdiction="Federal",
        description="Reportar desaparición de personas, incluidos menores",
    ),
}


# ═══════════════════════════════════════════════════════════════════
# MAPEO: FASE / CATEGORÍA → CONTEXTO LEGAL
# ═══════════════════════════════════════════════════════════════════

# Categorías Phase 4 que activan los artículos de Ley Olimpia (sextorsión).
SEXTORSION_CATEGORIES = {
    "sextorsion",
    "solicitud_material",
    "demanda_financiera",
    "material_intimo",
}

# Categorías Phase 4 que activan trata + búsqueda de personas.
EXPLOTACION_OPERATIVA_CATEGORIES = {
    "actividad_ilicita",
    "reclutamiento_secundario",
    "instruccion_operativa",
    "explotacion",  # categoría general que el clasificador emite cuando phase4 matchea
}


def _phase_key(phase: str | None) -> str:
    """Normalize the phase name. Accepts 'captacion' / 'phase1' indistinctly."""
    if not phase:
        return ""
    p = phase.strip().lower()
    return {
        "phase1": "captacion",
        "phase2": "enganche",
        "phase3": "coercion",
        "phase4": "explotacion",
    }.get(p, p)


def get_legal_context(
    phase: str | None,
    categories: list[str] | None,
    risk_level: str,
) -> LegalContext:
    """Build the full legal context for a detection.

    Always includes the constitutional + privacy baseline (CPEUM 4 & 16,
    LGDNNA 47-VII, LFPDPPP 5-8). Adds phase- and category-specific
    articles, authorities, recommended actions, and victim rights.
    """
    cats = set(categories or [])
    p = _phase_key(phase)

    articles: list[LegalArticle] = []
    authorities: list[Authority] = []
    victim_rights: list[str] = []
    recommended_actions: list[str] = []
    urgency: Literal["inmediata", "prioritaria", "preventiva"] = "preventiva"

    # ── Baseline constitucional y de protección a NNA ──
    articles.append(ARTICLES["cpeum_4"])
    articles.append(ARTICLES["lgdnna_47_vii"])

    # ── Por fase ──
    if p == "captacion":
        articles += [ARTICLES["cpf_209quater"], ARTICLES["lgpsedmtp_10"]]
        authorities += [AUTHORITIES["policia_cibernetica"]]
        recommended_actions += [
            "No responder al mensaje sospechoso",
            "No compartir datos personales (ubicación, escuela, nombre completo)",
            "No mover la conversación a otra plataforma",
            "Informar a un adulto de confianza",
            "Conservar capturas de pantalla como evidencia",
        ]
        urgency = "preventiva"

    elif p == "enganche":
        articles += [ARTICLES["cpf_209quater"], ARTICLES["lgpsedmtp_10"]]
        authorities += [
            AUTHORITIES["policia_cibernetica"],
            AUTHORITIES["dif"],
        ]
        recommended_actions += [
            "No compartir ubicación, dirección ni datos de la escuela",
            "No aceptar invitaciones a cambiar de plataforma de comunicación",
            "Bloquear al contacto sospechoso",
            "Reportar la cuenta en la plataforma donde ocurrió",
            "Informar inmediatamente a un adulto de confianza",
        ]
        urgency = "prioritaria"

    elif p == "coercion":
        articles += [
            ARTICLES["cpf_209quater"],
            ARTICLES["cpf_282"],
            ARTICLES["lgdnna_48"],
            ARTICLES["lgpsedmtp_10"],
        ]
        authorities += [
            AUTHORITIES["policia_cibernetica"],
            AUTHORITIES["fiscalia"],
            AUTHORITIES["linea_vida"],
        ]
        recommended_actions += [
            "NO responder al mensaje amenazante",
            "NO borrar la conversación — es evidencia",
            "Llamar al 088 (Policía Cibernética) de inmediato",
            "Informar a un adulto de confianza",
            "Si hay amenaza de violencia física: llamar al 911",
            "Considerar presentar denuncia formal ante la Fiscalía",
        ]
        victim_rights += [
            "Derecho a recibir protección especial como menor víctima (Art. 48 LGDNNA)",
            "Derecho a no ser revictimizado en el proceso de denuncia",
            "Derecho a asistencia jurídica y psicológica gratuita",
            "Derecho a que se preserve su identidad en todo momento",
        ]
        urgency = "inmediata"

    elif p == "explotacion":
        articles += [
            ARTICLES["cpf_209quater"],
            ARTICLES["lgpsedmtp_10"],
            ARTICLES["lgdnna_48"],
        ]
        authorities += [
            AUTHORITIES["policia_cibernetica"],
            AUTHORITIES["fiscalia"],
            AUTHORITIES["fevimtra"],
            AUTHORITIES["linea_vida"],
        ]
        # Sextorsión / Ley Olimpia
        if cats & SEXTORSION_CATEGORIES:
            articles += [
                ARTICLES["cpf_199octies"],
                ARTICLES["cpf_199nonies"],
                ARTICLES["cpf_199decies"],
                ARTICLES["lgamvlv_20quater"],
            ]
            recommended_actions += [
                "NO pagar ninguna cantidad de dinero",
                "NO enviar más imágenes o videos",
                "NO borrar las conversaciones ni eliminar las cuentas",
                "Tomar capturas de pantalla de TODO",
                "Llamar al 088 (Policía Cibernética) de inmediato",
                "Considerar contactar a FEVIMTRA (800-00-854-00)",
            ]
        # Explotación operativa / actividad ilícita
        if cats & EXPLOTACION_OPERATIVA_CATEGORIES:
            articles += [ARTICLES["lgpsedmtp_10"]]
            authorities += [AUTHORITIES["comision_busqueda"]]
            recommended_actions += [
                "NO acudir a ningún punto de encuentro",
                "NO realizar ninguna actividad que le pidan",
                "Llamar al 911 si hay riesgo inmediato",
                "Informar a un adulto de confianza DE INMEDIATO",
                "Presentar denuncia ante la Fiscalía",
            ]
        victim_rights += [
            "Derecho a protección integral como víctima de trata (Art. 10 LGPSEDMTP)",
            "Derecho a no ser criminalizado por actos cometidos bajo coacción",
            "Derecho a atención médica y psicológica de emergencia",
            "Derecho a medidas de protección urgentes",
            "Derecho a la reparación integral del daño",
        ]
        urgency = "inmediata"

    # ── Cumplimiento de privacidad (siempre incluir) ──
    articles += [ARTICLES["cpeum_16"], ARTICLES["lfpdppp_5"]]

    # ── Deduplicación preservando orden ──
    seen_articles: set[str] = set()
    unique_articles: list[LegalArticle] = []
    for a in articles:
        key = f"{a.law_abbreviation}_{a.article}"
        if key not in seen_articles:
            seen_articles.add(key)
            unique_articles.append(a)

    seen_authorities: set[str] = set()
    unique_authorities: list[Authority] = []
    for au in authorities:
        if au.name not in seen_authorities:
            seen_authorities.add(au.name)
            unique_authorities.append(au)

    seen_actions: set[str] = set()
    unique_actions: list[str] = []
    for ac in recommended_actions:
        if ac not in seen_actions:
            seen_actions.add(ac)
            unique_actions.append(ac)

    seen_rights: set[str] = set()
    unique_rights: list[str] = []
    for r in victim_rights:
        if r not in seen_rights:
            seen_rights.add(r)
            unique_rights.append(r)

    return LegalContext(
        articles=unique_articles,
        authorities=unique_authorities,
        victim_rights=unique_rights,
        recommended_actions=unique_actions,
        urgency_level=urgency,
    )


# ═══════════════════════════════════════════════════════════════════
# DISCLAIMERS / TEXTOS DE CONSENTIMIENTO
# ═══════════════════════════════════════════════════════════════════


def get_privacy_disclaimer() -> str:
    """Disclaimer de privacidad para incluir en reportes y API responses."""
    return (
        "Este reporte fue generado por Nahual, sistema de detección de "
        "reclutamiento criminal digital. Nahual no almacena el contenido de "
        "los mensajes analizados (Art. 16 CPEUM). Solo se procesan datos "
        "aportados voluntariamente por el usuario. El sistema cumple con los "
        "principios de la LFPDPPP (Arts. 5-8): licitud, finalidad, lealtad, "
        "consentimiento, calidad, proporcionalidad, información y "
        "responsabilidad. El tratamiento de datos de menores se rige por el "
        "principio de interés superior de la niñez (Art. 4 CPEUM, Art. 2 LGDNNA)."
    )


def get_consent_text() -> str:
    """Texto de consentimiento para contribución anónima de datos."""
    return (
        "Al compartir estos datos de forma anónima, autorizas el tratamiento "
        "de la siguiente información exclusivamente con fines de investigación "
        "sobre reclutamiento criminal digital: nivel de riesgo detectado, "
        "fase, plataforma de origen, y categorías de patrones identificados. "
        "NO se almacena el contenido del mensaje, tu número de teléfono, ni "
        "ningún dato que permita identificarte. Esta autorización es conforme "
        "a los Arts. 5 y 7 de la LFPDPPP y puede ser revocada en cualquier "
        "momento. Los datos anonimizados son irreversibles: no es posible "
        "vincularlos a tu identidad."
    )


# ═══════════════════════════════════════════════════════════════════
# Serialización para API responses
# ═══════════════════════════════════════════════════════════════════


def serialize_context(ctx: LegalContext) -> dict:
    """JSON-friendly view of LegalContext for /alert and /analyze responses."""
    return {
        "urgency": ctx.urgency_level,
        "articles": [
            {
                "law": a.law_abbreviation,
                "law_name": a.law_name,
                "article": a.article,
                "title": a.title,
                "summary": a.summary,
                "penalty": a.penalty,
                "source_url": a.source_url,
            }
            for a in ctx.articles
        ],
        "authorities": [
            {
                "name": au.name,
                "phone": au.phone,
                "hours": au.hours,
                "jurisdiction": au.jurisdiction,
                "description": au.description,
            }
            for au in ctx.authorities
        ],
        "recommended_actions": ctx.recommended_actions,
        "victim_rights": ctx.victim_rights,
    }
