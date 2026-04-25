"""
PDF generator using ReportLab. Template-based incident report.

Folio: NAH-2026-XXXX (zero-padded id). The PDF includes incident metadata,
phase analysis, anonymized summary, legal protocols (Art. 47 LGDNNA, Art. 16
CPEUM), and contacts (088, SIPINNA, Línea de la Vida).

NEVER includes the original message text — only the anonymized summary and
SHA-256 hash. Privacy by design.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

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
    cats = alert.get("categories") or []
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

    # Legal protocol
    story.append(Paragraph("Marco legal aplicable", s["h2"]))
    legal = (
        "<b>Art. 47 LGDNNA</b> — Protección contra reclutamiento de menores.<br/>"
        "<b>Art. 16 CPEUM</b> — Inviolabilidad de comunicaciones (Nahual cumple: solo "
        "analiza datos autoinformados por el usuario).<br/>"
        "<b>Código Penal Federal (reforma 2026)</b> — Hasta 18 años de pena por reclutamiento "
        "de menores.<br/>"
        "<b>Ley Olimpia</b> — Aplica en casos de difusión no consentida de material íntimo "
        "(sextorsión).<br/>"
        "<b>LFPDPPP</b> — Protección de datos personales de menores."
    )
    story.append(Paragraph(legal, s["body"]))

    # Contacts
    story.append(Paragraph("Contactos para denuncia y apoyo", s["h2"]))
    contacts = [
        ["Policía Cibernética", "088"],
        ["SIPINNA", "https://sipinna.gob.mx"],
        ["Línea de la Vida (crisis)", "800-911-2000"],
        ["Fiscalía General (local)", "Según estado"],
    ]
    ct = Table(contacts, colWidths=[8 * cm, 8 * cm])
    ct.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), COBRE),
                ("TEXTCOLOR", (0, 0), (0, -1), WHITE),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(ct)

    story.append(Spacer(1, 14))
    story.append(
        Paragraph(
            "Generado automáticamente por Nahual · Equipo Vanguard · "
            "Hackathon 404: Threat Not Found · Licencia MIT",
            s["small"],
        )
    )

    doc.build(story)
    return output_path
