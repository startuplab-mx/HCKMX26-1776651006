"""
PDF generator using ReportLab. Template-based incident report.

Folio: NAH-2026-XXXX (zero-padded id). The legal sections are now built
dynamically by querying backend.legal.framework.get_legal_context() so
the cited articles, authorities and recommended actions match exactly
what the classifier detected.

NEVER includes the original message text — only the anonymized summary
and SHA-256 hash. Privacy by design.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from legal import get_legal_context, get_privacy_disclaimer

REPORTS_DIR = Path(
    os.getenv(
        "REPORTS_DIR",
        Path(__file__).resolve().parent / "generated",
    )
)

CARBON = colors.HexColor("#2F353A")
COBRE = colors.HexColor("#C16A4C")
GREEN = colors.HexColor("#22C55E")
YELLOW = colors.HexColor("#EAB308")
RED = colors.HexColor("#EF4444")
WHITE = colors.HexColor("#FFFFFF")

LEVEL_COLOR = {"SEGURO": GREEN, "ATENCION": YELLOW, "PELIGRO": RED}
URGENCY_COLOR = {
    "inmediata": RED,
    "prioritaria": YELLOW,
    "preventiva": GREEN,
}
URGENCY_LABEL = {
    "inmediata": "URGENCIA INMEDIATA",
    "prioritaria": "ATENCIÓN PRIORITARIA",
    "preventiva": "ACCIÓN PREVENTIVA",
}

PHASE_LABEL = {
    "captacion": "Fase 1 — Captación",
    "enganche": "Fase 2 — Enganche",
    "coercion": "Fase 3 — Coerción",
    "explotacion": "Fase 4 — Explotación",
    "ninguna": "Sin fase dominante",
}


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            textColor=CARBON,
            fontSize=22,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            textColor=COBRE,
            fontSize=12,
            spaceAfter=18,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            textColor=CARBON,
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.grey,
        ),
    }


def _coerce_categories(raw: Any) -> list[str]:
    """Categories arrive as a list (from the API) or a JSON-encoded string
    (when reading directly from the SQLite alerts row). Normalize both."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(c) for c in raw]
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            return [str(c) for c in data] if isinstance(data, list) else []
        except json.JSONDecodeError:
            return [s.strip() for s in raw.split(",") if s.strip()]
    return []


def generate_report(alert: dict[str, Any], output_dir: Path | str | None = None) -> Path:
    """Generate a PDF incident report. Returns the file path."""
    out_dir = Path(output_dir or REPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    folio = f"NAH-2026-{alert['id']:04d}"
    output_path = out_dir / f"{folio}.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Nahual Incident Report {folio}",
        author="Nahual",
    )

    s = _styles()
    story: list = []

    # Header — avoid emoji glyphs in default Helvetica (ReportLab core fonts
    # don't ship emoji coverage). The brand color stays via the cobre subtitle.
    story.append(Paragraph("NAHUAL", s["title"]))
    story.append(
        Paragraph(
            f"Reporte de incidente · Folio <b>{folio}</b>",
            s["subtitle"],
        )
    )

    # Risk level banner
    level = alert.get("risk_level", "SEGURO")
    color = LEVEL_COLOR.get(level, CARBON)
    banner = Table(
        [[Paragraph(f"<b>NIVEL DE RIESGO: {level}</b>", s["body"])]],
        colWidths=[16 * cm],
    )
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(banner)
    story.append(Spacer(1, 12))

    # Incident metadata
    story.append(Paragraph("Datos del incidente", s["h2"]))
    meta = [
        ["Fecha de registro", alert.get("created_at", "")],
        ["Plataforma", alert.get("platform", "")],
        ["Fuente", alert.get("source", "")],
        ["Risk score", f"{alert.get('risk_score', 0):.2f}"],
        ["Fase dominante", PHASE_LABEL.get(alert.get("phase_detected") or "ninguna", "—")],
        ["Override activado", "Sí (Peligro inminente)" if alert.get("override_triggered") else "No"],
        ["Capa LLM utilizada", "Sí" if alert.get("llm_used") else "No"],
        ["Hash SHA-256 del mensaje", (alert.get("original_text_hash") or "")[:32] + "…"],
    ]
    t = Table(meta, colWidths=[6 * cm, 10 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), CARBON),
                ("TEXTCOLOR", (0, 0), (0, -1), WHITE),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 8))

    # Categories
    cats = _coerce_categories(alert.get("categories"))
    story.append(Paragraph("Categorías detectadas", s["h2"]))
    story.append(
        Paragraph(
            ", ".join(cats) if cats else "Ninguna categoría disparada.",
            s["body"],
        )
    )

    # Summary (anonymized)
    story.append(Paragraph("Resumen anonimizado", s["h2"]))
    story.append(
        Paragraph(
            alert.get("summary") or "Sin resumen disponible.",
            s["body"],
        )
    )
    story.append(
        Paragraph(
            "<i>Por diseño, este reporte no incluye el texto completo del mensaje "
            "analizado. Sólo el hash SHA-256 y un resumen anonimizado.</i>",
            s["small"],
        )
    )

    # ── Build dynamic legal context based on detected phase + categories ──
    legal_ctx = get_legal_context(
        phase=alert.get("phase_detected"),
        categories=cats,
        risk_level=level,
    )

    # Urgency banner
    story.append(Spacer(1, 8))
    urg_color = URGENCY_COLOR.get(legal_ctx.urgency_level, CARBON)
    urg_label = URGENCY_LABEL.get(
        legal_ctx.urgency_level, legal_ctx.urgency_level.upper()
    )
    urg_banner = Table(
        [[Paragraph(f"<b>{urg_label}</b>", s["body"])]],
        colWidths=[16 * cm],
    )
    urg_banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), urg_color),
                ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(urg_banner)

    # Recommended actions (numbered)
    if legal_ctx.recommended_actions:
        story.append(Paragraph("Qué hacer ahora", s["h2"]))
        story.append(
            ListFlowable(
                [
                    ListItem(Paragraph(action, s["body"]), leftIndent=14)
                    for action in legal_ctx.recommended_actions
                ],
                bulletType="1",
                leftIndent=14,
            )
        )

    # Legal articles (dynamic table)
    story.append(Paragraph("Marco legal aplicable", s["h2"]))
    art_rows: list[list[Any]] = [["Ley", "Artículo", "Título", "Pena"]]
    for a in legal_ctx.articles:
        art_rows.append(
            [
                a.law_abbreviation,
                a.article,
                a.title,
                a.penalty or "—",
            ]
        )
    arts_table = Table(art_rows, colWidths=[2.5 * cm, 4 * cm, 6.5 * cm, 3 * cm])
    arts_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), CARBON),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(arts_table)

    # Authorities (dynamic table)
    if legal_ctx.authorities:
        story.append(Paragraph("Autoridades competentes", s["h2"]))
        auth_rows: list[list[Any]] = [["Autoridad", "Contacto", "Horario"]]
        for au in legal_ctx.authorities:
            auth_rows.append([au.name, au.phone, au.hours])
        auth_table = Table(auth_rows, colWidths=[8 * cm, 5 * cm, 3 * cm])
        auth_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COBRE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(auth_table)

    # Victim rights (only when level is PELIGRO and we collected any)
    if level == "PELIGRO" and legal_ctx.victim_rights:
        story.append(Paragraph("Derechos de la víctima", s["h2"]))
        story.append(
            ListFlowable(
                [
                    ListItem(Paragraph(r, s["body"]), leftIndent=14)
                    for r in legal_ctx.victim_rights
                ],
                bulletType="bullet",
                leftIndent=14,
            )
        )

    # Privacy disclaimer
    story.append(Spacer(1, 12))
    story.append(Paragraph("Aviso de privacidad", s["h2"]))
    story.append(Paragraph(get_privacy_disclaimer(), s["small"]))

    story.append(Spacer(1, 10))
    story.append(
        Paragraph(
            "Generado automáticamente por Nahual · Equipo Vanguard · "
            "Hackathon 404: Threat Not Found · Licencia MIT",
            s["small"],
        )
    )

    doc.build(story)
    return output_path
