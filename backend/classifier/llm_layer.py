"""
Layer 2: Claude API for grey-zone disambiguation (risk_score in [0.3, 0.6]).

Hard 5-second timeout. On any failure or timeout, returns None and the caller
falls back to the heuristic result. The system MUST always answer the user, so
this layer is opportunistic.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _extract_json(content: str) -> str:
    """Strip markdown code fences and surrounding text from a model response."""
    stripped = _FENCE.sub("", content).strip()
    # Fall back to the first {...} block if the model added prose around the JSON.
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1]
    return stripped

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Eres un analista forense de mensajes en español mexicano. Tu trabajo es evaluar si un mensaje recibido por un menor en redes sociales muestra señales de RECLUTAMIENTO CRIMINAL DIGITAL.

Las 4 fases del reclutamiento son:
- captacion: ofertas falsas de trabajo, narcocultura aspiracional, contacto inicial
- enganche: aislamiento, secrecía, traslado a canales privados, recolección de datos
- coercion: amenazas, presión, "ya sabes demasiado"
- explotacion: instrucciones operativas, sextorsión, depósitos, reclutamiento secundario

Responde SIEMPRE en JSON válido con esta estructura exacta y NADA más:
{"risk_score": 0.0-1.0, "phase": "captacion|enganche|coercion|explotacion|ninguna", "rationale": "max 200 chars en español"}

Sé conservador: si el mensaje es ambiguo o cotidiano, baja el score. Si hay amenazas explícitas o sextorsión, sube el score. NO inventes contexto."""


class LLMLayer:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        self.timeout = timeout if timeout is not None else float(
            os.getenv("LLM_TIMEOUT_SECONDS", "5")
        )
        self._client = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key) and not self.api_key.startswith("sk-ant-xxxxx")

    def _get_client(self):
        if self._client is None:
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=self.api_key, timeout=self.timeout)
            except ImportError:
                logger.warning("anthropic package not installed; LLM layer disabled")
                return None
        return self._client

    def analyze(self, text: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        client = self._get_client()
        if client is None:
            return None
        try:
            resp = client.messages.create(
                model=self.model,
                max_tokens=300,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text}],
            )
            content = resp.content[0].text if resp.content else ""
            data = json.loads(_extract_json(content))
            score = float(data.get("risk_score", 0.0))
            score = max(0.0, min(1.0, score))
            return {
                "risk_score": score,
                "phase": data.get("phase", "ninguna"),
                "rationale": data.get("rationale", "")[:200],
            }
        except Exception as e:
            logger.warning("LLM layer failed (%s); falling back to heuristic", e)
            return None
