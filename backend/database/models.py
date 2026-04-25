"""Pydantic models for API I/O."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

AlertStatus = Literal["pending", "reviewed", "dismissed", "escalated"]


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=8000)
    use_llm: bool = True


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
