"""Pydantic models for API I/O."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AlertStatus = Literal["pending", "reviewed", "dismissed", "escalated"]
SourceType = Literal["text", "audio", "image"]


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    use_llm: bool = True
    session_id: str | None = None
    source_type: Literal["text", "audio", "image"] = "text"


class PhaseScores(BaseModel):
    phase1: float
    phase2: float
    phase3: float
    phase4: float


class AnalyzeResponse(BaseModel):
    risk_score: float
    risk_level: str
    phase_detected: str
    phase_scores: PhaseScores
    categories: list[str]
    pattern_ids: list[str] = Field(default_factory=list)
    override_triggered: bool
    llm_used: bool
    llm_rationale: str | None = None
    text_hash: str
    summary: str


class AlertCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    platform: str = Field(default="whatsapp")
    source: str = Field(default="bot")
    contact_phone: str | None = None
    session_id: str | None = None
    source_type: SourceType = "text"


class Alert(BaseModel):
    id: int
    created_at: str
    platform: str
    source: str
    risk_score: float
    risk_level: str
    phase_detected: str | None
    categories: list[str]
    summary: str | None
    original_text_hash: str | None
    contact_phone: str | None
    report_generated: bool
    report_path: str | None
    llm_used: bool
    override_triggered: bool
    session_id: str | None


class StatsResponse(BaseModel):
    total_alerts: int
    by_level: dict[str, int]
    by_phase: dict[str, int]
    by_platform: dict[str, int]
    by_status: dict[str, int]
    overrides: int
    last_24h: int


class AlertUpdate(BaseModel):
    status: AlertStatus | None = None
    notes: str | None = Field(default=None, max_length=2000)
    reviewer: str | None = Field(default=None, max_length=120)


class EscalationRequest(BaseModel):
    destination: str = Field(
        ..., min_length=1, max_length=120,
        description="Where the case is being escalated (e.g. '088', 'SIPINNA', 'Fiscalía CDMX').",
    )
    reason: str | None = Field(default=None, max_length=500)
    reviewer: str | None = Field(default=None, max_length=120)


class SessionState(BaseModel):
    id: str
    current_step: str
    data: dict[str, object]
    created_at: str
    updated_at: str


class SessionUpsert(BaseModel):
    current_step: str = Field(..., min_length=1, max_length=64)
    data: dict[str, object] | None = None


class TimeseriesBucket(BaseModel):
    bucket: str
    total: int
    by_level: dict[str, int]
    overrides: int
    escalated: int


class AlertAction(BaseModel):
    id: int
    alert_id: int
    action: Literal["status_change", "note", "escalation"]
    reviewer: str | None
    from_value: str | None
    to_value: str | None
    notes: str | None
    created_at: str


class TranscriptionResponse(BaseModel):
    text: str
    source: str  # 'groq_whisper' | 'claude_vision'


class ContributionCreate(BaseModel):
    """Anonymous research metadata. NEVER include text, phone, names, or any
    other PII in this payload — Pydantic forbids unknown fields below.
    """
    model_config = {"extra": "forbid"}

    platform: str = Field(..., min_length=1, max_length=64)
    risk_level: Literal["SEGURO", "ATENCION", "PELIGRO"]
    risk_score: float = Field(..., ge=0.0, le=1.0)
    phase_detected: str | None = Field(default=None, max_length=64)
    categories: list[str] = Field(default_factory=list)
    pattern_ids: list[str] = Field(default_factory=list)
    source_type: SourceType = "text"
    region: str | None = Field(default=None, max_length=80)
    llm_used: bool = False
    override_triggered: bool = False


class ContributionStats(BaseModel):
    total_contributions: int
    by_platform: dict[str, int]
    by_phase: dict[str, int]
    by_level: dict[str, int]
    by_source: dict[str, int]
    by_region: dict[str, int]
    top_patterns: list[dict[str, object]]
