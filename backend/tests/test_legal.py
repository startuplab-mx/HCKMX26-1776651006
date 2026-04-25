"""Legal framework module: mapping correctness + API integration."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from legal.framework import (  # noqa: E402
    ARTICLES,
    AUTHORITIES,
    get_consent_text,
    get_legal_context,
    get_privacy_disclaimer,
    serialize_context,
)


# ---------------- mapping unit tests ----------------


def test_coercion_returns_amenazas():
    """Coerción debe incluir Art. 282 CPF (Amenazas)."""
    ctx = get_legal_context("coercion", [], "PELIGRO")
    arts = [a.article for a in ctx.articles]
    assert "Art. 282" in arts


def test_sextorsion_returns_ley_olimpia():
    """Sextorsión debe incluir Arts. 199 Octies-Decies + LGAMVLV 20 Quáter."""
    ctx = get_legal_context("explotacion", ["sextorsion"], "PELIGRO")
    arts = [a.article for a in ctx.articles]
    assert "Art. 199 Octies" in arts
    assert "Art. 199 Nonies" in arts
    assert "Art. 199 Decies" in arts
    assert "Art. 20 Quáter" in arts


def test_captacion_returns_reclutamiento():
    """Captación debe incluir el art. de Reclutamiento Forzado (propuesto)."""
    ctx = get_legal_context("captacion", [], "ATENCION")
    arts = [a.article for a in ctx.articles]
    assert any("Sextus" in a for a in arts)
    # Y debe estar etiquetado como propuesto, no como ley vigente.
    matching = [a for a in ctx.articles if "Sextus" in a.article]
    assert all("propuesto" in a.article.lower() for a in matching)


def test_peligro_includes_emergency_contacts():
    """PELIGRO en coerción siempre incluye Policía Cibernética 088."""
    ctx = get_legal_context("coercion", [], "PELIGRO")
    phones = [a.phone for a in ctx.authorities]
    assert "088" in phones


def test_urgency_levels():
    """Verificar niveles de urgencia por fase."""
    assert get_legal_context("captacion", [], "ATENCION").urgency_level == "preventiva"
    assert get_legal_context("enganche", [], "ATENCION").urgency_level == "prioritaria"
    assert get_legal_context("coercion", [], "PELIGRO").urgency_level == "inmediata"
    assert get_legal_context("explotacion", [], "PELIGRO").urgency_level == "inmediata"


def test_always_includes_base_articles():
    """Siempre incluir Art. 4 CPEUM, Art. 47 LGDNNA y Art. 101 Bis 2 LGDNNA."""
    ctx = get_legal_context("captacion", [], "SEGURO")
    pairs = [(a.law_abbreviation, a.article) for a in ctx.articles]
    assert any(law == "CPEUM" and "Art. 4" in art for law, art in pairs)
    assert any(law == "LGDNNA" and "Art. 47" in art for law, art in pairs)
    assert any(law == "LGDNNA" and "101 Bis 2" in art for law, art in pairs)


def test_always_includes_privacy_compliance():
    """Toda respuesta legal debe declarar Art. 16 CPEUM + LFPDPPP."""
    ctx = get_legal_context("captacion", [], "SEGURO")
    pairs = [(a.law_abbreviation, a.article) for a in ctx.articles]
    assert any(law == "CPEUM" and "Art. 16" in art for law, art in pairs)
    assert any(law == "LFPDPPP" for law, _ in pairs)


def test_privacy_disclaimer_mentions_article_16():
    """Disclaimer debe mencionar Art. 16 CPEUM y LFPDPPP."""
    text = get_privacy_disclaimer()
    assert "Art. 16 CPEUM" in text
    assert "LFPDPPP" in text


def test_consent_text_mentions_lfpdppp():
    """Consent text debe citar LFPDPPP y dejar claro que es anónimo."""
    text = get_consent_text()
    assert "LFPDPPP" in text
    assert "anónim" in text.lower()


def test_no_duplicate_articles():
    """get_legal_context no repite artículos cuando varias fases/categorías
    los referencian."""
    ctx = get_legal_context("explotacion", ["sextorsion", "actividad_ilicita"], "PELIGRO")
    keys = [(a.law_abbreviation, a.article) for a in ctx.articles]
    assert len(keys) == len(set(keys))


def test_phase_alias_phaseN_works():
    """Las fases pueden venir como 'phase1' (heuristic) o 'captacion' (pipeline)."""
    via_alias = get_legal_context("phase3", [], "PELIGRO")
    via_canonical = get_legal_context("coercion", [], "PELIGRO")
    via_arts = sorted(a.article for a in via_alias.articles)
    canon_arts = sorted(a.article for a in via_canonical.articles)
    assert via_arts == canon_arts


def test_explotacion_with_actividad_ilicita_adds_busqueda():
    """Si hay categoría operativa, sumar Comisión Nacional de Búsqueda."""
    ctx = get_legal_context("explotacion", ["actividad_ilicita"], "PELIGRO")
    names = [a.name for a in ctx.authorities]
    assert any("Búsqueda" in n for n in names)


def test_peligro_in_coercion_emits_victim_rights():
    """En coerción debe haber al menos un derecho del Art. 48 LGDNNA."""
    ctx = get_legal_context("coercion", [], "PELIGRO")
    assert any("Art. 48 LGDNNA" in r for r in ctx.victim_rights)


def test_serialize_context_returns_jsonable_dict():
    """serialize_context devuelve un dict de tipos primitivos."""
    ctx = get_legal_context("coercion", [], "PELIGRO")
    payload = serialize_context(ctx)
    assert payload["urgency"] == "inmediata"
    assert isinstance(payload["articles"], list)
    assert all("law" in a and "article" in a for a in payload["articles"])
    assert all("name" in au and "phone" in au for au in payload["authorities"])
    assert isinstance(payload["recommended_actions"], list)
    assert isinstance(payload["victim_rights"], list)


def test_articles_dict_has_expected_keys():
    expected = {
        "cpeum_4", "cpeum_16", "lgdnna_47_vii", "lgdnna_48", "lgdnna_101bis2",
        "cpf_209quater", "cpf_199octies", "cpf_199nonies", "cpf_199decies",
        "lgamvlv_20quater", "lfpdppp_5", "lgpsedmtp_10", "cpf_282",
    }
    assert expected.issubset(set(ARTICLES.keys()))


def test_authorities_dict_has_expected_keys():
    expected = {
        "policia_cibernetica", "fiscalia", "fevimtra", "dif",
        "sipinna", "linea_vida", "comision_busqueda",
    }
    assert expected.issubset(set(AUTHORITIES.keys()))


# ---------------- HTTP integration ----------------


def _client(tmp_path: Path):
    os.environ["DATABASE_PATH"] = str(tmp_path / "legal_api.db")
    os.environ["ANTHROPIC_API_KEY"] = ""
    os.environ["GROQ_API_KEY"] = ""
    os.environ["NAHUAL_WEBHOOK_URLS"] = ""
    import importlib

    import database.db as db_module
    import main as main_module
    import webhooks as wh_module

    importlib.reload(wh_module)
    importlib.reload(db_module)
    importlib.reload(main_module)

    from fastapi.testclient import TestClient

    return TestClient(main_module.app)


def test_alert_response_includes_legal_block(tmp_path):
    with _client(tmp_path) as c:
        r = c.post(
            "/alert",
            json={"text": "te voy a matar, sabemos donde vives"},
        )
        body = r.json()
        assert r.status_code == 201
        assert "legal" in body
        assert body["legal"]["urgency"] == "inmediata"
        articles = [a["article"] for a in body["legal"]["articles"]]
        assert "Art. 282" in articles
        assert any(a["phone"] == "088" for a in body["legal"]["authorities"])


def test_analyze_response_includes_legal_block(tmp_path):
    with _client(tmp_path) as c:
        r = c.post(
            "/analyze",
            json={"text": "yo quiero jale, te pago el viaje", "use_llm": False},
        )
        body = r.json()
        assert r.status_code == 200
        assert "legal" in body
        assert "privacy_disclaimer" in body
        assert body["legal"]["urgency"] == "preventiva"


def test_alert_legal_endpoint_recomputes_from_storage(tmp_path):
    with _client(tmp_path) as c:
        aid = c.post(
            "/alert",
            json={"text": "te voy a matar"},
        ).json()["id"]
        r = c.get(f"/alerts/{aid}/legal")
        body = r.json()
        assert r.status_code == 200
        assert body["urgency"] == "inmediata"
        assert any(a["article"] == "Art. 282" for a in body["articles"])


def test_alert_legal_endpoint_404_for_missing(tmp_path):
    with _client(tmp_path) as c:
        r = c.get("/alerts/9999/legal")
        assert r.status_code == 404
