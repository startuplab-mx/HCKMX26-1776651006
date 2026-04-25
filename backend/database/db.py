"""SQLite layer. Single connection per request; thread-safe via check_same_thread=False."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "nahual.db"

ALERT_STATUSES = ("pending", "reviewed", "dismissed", "escalated")
ALERT_ACTION_TYPES = ("status_change", "note", "escalation")

SCHEMA = """
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    platform TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'bot',
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    phase_detected TEXT,
    categories TEXT,
    summary TEXT,
    original_text_hash TEXT,
    contact_phone TEXT,
    report_generated INTEGER DEFAULT 0,
    report_path TEXT,
    llm_used INTEGER DEFAULT 0,
    override_triggered INTEGER DEFAULT 0,
    session_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    notes TEXT,
    reviewer TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    current_step TEXT NOT NULL DEFAULT 'inicio',
    data TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS alert_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    reviewer TEXT,
    from_value TEXT,
    to_value TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
);

-- Anonymous research dataset. Populated only when a user opts in via the
-- bot's ASK_CONTRIBUTE flow. Holds NO PII: no text, no phone, no session id.
CREATE TABLE IF NOT EXISTS contributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    platform TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    risk_score REAL NOT NULL,
    phase_detected TEXT,
    categories TEXT,           -- JSON array of category names
    pattern_ids TEXT,          -- JSON array of pattern IDs that fired
    source_type TEXT NOT NULL DEFAULT 'text',  -- text | audio | image
    region TEXT,               -- Optional state/region (voluntary)
    llm_used INTEGER DEFAULT 0,
    override_triggered INTEGER DEFAULT 0
);

-- Auto-tuning feedback log. Three sources feed it:
--   1. confirm/deny: implicit signals from the bot flow (user provided
--      guardian phone vs explicitly denied the alert)
--   2. llm_discrepancy: pipeline observed a >0.3 gap between heuristic
--      and Claude API scores
--   3. operator_fp/operator_fn: explicit panel actions
-- The PrecisionProcessor reads `processed=0` rows in batches and adjusts
-- per-pattern weight overlays in runtime.
CREATE TABLE IF NOT EXISTS feedback_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    alert_id INTEGER,
    feedback_type TEXT NOT NULL,
    heuristic_score REAL,
    llm_score REAL,
    final_score REAL,
    pattern_ids TEXT,
    text_hash TEXT,
    session_id TEXT,
    processed INTEGER DEFAULT 0
);

-- Per-session risk score history. One row per analysis. Used by
-- classifier/escalation.py to detect when risk is increasing across a
-- conversation, even when individual messages would land in ATENCION.
CREATE TABLE IF NOT EXISTS risk_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    phase_detected TEXT,
    source_type TEXT DEFAULT 'text'
);

CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_risk_level ON alerts(risk_level);
CREATE INDEX IF NOT EXISTS idx_alerts_platform ON alerts(platform);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_session ON alerts(session_id);
CREATE INDEX IF NOT EXISTS idx_actions_alert_id ON alert_actions(alert_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_contrib_platform ON contributions(platform);
CREATE INDEX IF NOT EXISTS idx_contrib_phase ON contributions(phase_detected);
CREATE INDEX IF NOT EXISTS idx_contrib_created_at ON contributions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_risk_history_session ON risk_history(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_feedback_processed ON feedback_log(processed);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback_log(feedback_type);
"""

# Columns added after v1.0 that need ALTER TABLE on pre-existing DBs.
ALERT_COLUMN_MIGRATIONS = (
    ("status", "TEXT NOT NULL DEFAULT 'pending'"),
    ("notes", "TEXT"),
    ("reviewer", "TEXT"),
    ("updated_at", "TEXT"),
    ("pattern_ids", "TEXT"),     # JSON array of matched pattern IDs
    ("source_type", "TEXT NOT NULL DEFAULT 'text'"),  # text | audio | image
)


class _CursorSnapshot:
    """Cursor wrapper that serializes fetches and snapshots metadata.

    `lastrowid` and `rowcount` are read eagerly while the lock is held by
    the producing call to ``execute``. Subsequent ``fetchone``/``fetchall``
    re-acquire the lock so they're safe under FastAPI's threadpool.
    """

    __slots__ = ("_cur", "_lock", "lastrowid", "rowcount")

    def __init__(self, cur: sqlite3.Cursor, lock: threading.RLock) -> None:
        self._cur = cur
        self._lock = lock
        self.lastrowid = cur.lastrowid
        self.rowcount = cur.rowcount

    def fetchone(self) -> sqlite3.Row | None:
        with self._lock:
            return self._cur.fetchone()

    def fetchall(self) -> list[sqlite3.Row]:
        with self._lock:
            return self._cur.fetchall()


class _LockedConn:
    """Thin wrapper around sqlite3.Connection that serializes mutations.

    FastAPI runs sync handlers in a threadpool — sharing one sqlite3
    connection across threads without serialization raises
    ``InterfaceError: bad parameter or other API misuse`` under contention.
    Existing call sites use ``self._conn.execute(...)`` patterns; this
    proxy lets that code stay unchanged while becoming thread-safe.
    """

    def __init__(self, conn: sqlite3.Connection, lock: threading.RLock) -> None:
        self._conn = conn
        self._lock = lock

    def execute(self, sql: str, params: tuple | list = ()) -> _CursorSnapshot:
        with self._lock:
            cur = self._conn.execute(sql, params)
            return _CursorSnapshot(cur, self._lock)

    def executescript(self, sql: str) -> None:
        with self._lock:
            self._conn.executescript(sql)

    def close(self) -> None:
        with self._lock:
            self._conn.close()


class Database:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or os.getenv("DATABASE_PATH", DEFAULT_DB_PATH))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        raw = sqlite3.connect(
            self.path, check_same_thread=False, isolation_level=None
        )
        raw.row_factory = sqlite3.Row
        raw.execute("PRAGMA journal_mode=WAL")
        raw.execute("PRAGMA foreign_keys=ON")
        self._conn = _LockedConn(raw, self._lock)
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(SCHEMA)
        self._migrate_alerts_columns()

    def _migrate_alerts_columns(self) -> None:
        """Additive column migrations for databases created before v1.1."""
        with self._lock:
            existing = {
                row["name"]
                for row in self._conn.execute("PRAGMA table_info(alerts)").fetchall()
            }
            for col, ddl in ALERT_COLUMN_MIGRATIONS:
                if col not in existing:
                    self._conn.execute(f"ALTER TABLE alerts ADD COLUMN {col} {ddl}")
            # Backfill updated_at for rows created before the column existed.
            self._conn.execute(
                "UPDATE alerts SET updated_at = created_at WHERE updated_at IS NULL"
            )

    # ---------------- Alerts ----------------

    def insert_alert(
        self,
        platform: str,
        source: str,
        risk_score: float,
        risk_level: str,
        phase_detected: str | None,
        categories: list[str],
        summary: str | None,
        text_hash: str | None,
        contact_phone: str | None,
        llm_used: bool,
        override_triggered: bool,
        session_id: str | None,
        pattern_ids: list[str] | None = None,
        source_type: str = "text",
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO alerts (
                platform, source, risk_score, risk_level, phase_detected,
                categories, summary, original_text_hash, contact_phone,
                llm_used, override_triggered, session_id, pattern_ids, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                platform,
                source,
                risk_score,
                risk_level,
                phase_detected,
                json.dumps(categories, ensure_ascii=False),
                summary,
                text_hash,
                contact_phone,
                int(llm_used),
                int(override_triggered),
                session_id,
                json.dumps(pattern_ids or [], ensure_ascii=False),
                source_type,
            ),
        )
        return int(cur.lastrowid)

    def seed_insert_alert(
        self,
        *,
        platform: str,
        source: str,
        risk_score: float,
        risk_level: str,
        phase_detected: str | None,
        categories: list[str],
        summary: str | None,
        text_hash: str | None,
        contact_phone: str | None,
        llm_used: bool,
        override_triggered: bool,
        session_id: str | None,
        created_at: str,
        status: str = "pending",
        reviewer: str | None = None,
        notes: str | None = None,
        pattern_ids: list[str] | None = None,
        source_type: str = "text",
    ) -> int:
        """Seed-only insert that allows overriding created_at/status.

        Used by scripts/seed_test_data.py to spread demo data across time so
        the panel chart shows multi-bucket activity. Do NOT call from request
        handlers — the production path is insert_alert().
        """
        if status not in ALERT_STATUSES:
            raise ValueError(f"invalid status {status!r}")
        cur = self._conn.execute(
            """
            INSERT INTO alerts (
                created_at, updated_at, platform, source, risk_score, risk_level,
                phase_detected, categories, summary, original_text_hash,
                contact_phone, llm_used, override_triggered, session_id,
                status, reviewer, notes, pattern_ids, source_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                created_at,
                platform,
                source,
                risk_score,
                risk_level,
                phase_detected,
                json.dumps(categories, ensure_ascii=False),
                summary,
                text_hash,
                contact_phone,
                int(llm_used),
                int(override_triggered),
                session_id,
                status,
                reviewer,
                notes,
                json.dumps(pattern_ids or [], ensure_ascii=False),
                source_type,
            ),
        )
        return int(cur.lastrowid)

    def get_alert(self, alert_id: int) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM alerts WHERE id = ?", (alert_id,)
        ).fetchone()
        return self._row_to_alert(row) if row else None

    def list_alerts(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
        risk_level: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if status:
            clauses.append("status = ?")
            params.append(status)
        if risk_level:
            clauses.append("risk_level = ?")
            params.append(risk_level)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.extend([limit, offset])
        rows = self._conn.execute(
            f"SELECT * FROM alerts {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
        return [self._row_to_alert(r) for r in rows]

    def mark_report_generated(self, alert_id: int, report_path: str) -> None:
        self._conn.execute(
            "UPDATE alerts SET report_generated = 1, report_path = ?, "
            "updated_at = datetime('now') WHERE id = ?",
            (report_path, alert_id),
        )

    # ---------------- Moderation / Triage ----------------

    def update_alert_status(
        self,
        alert_id: int,
        *,
        status: str | None = None,
        notes: str | None = None,
        reviewer: str | None = None,
    ) -> dict[str, Any] | None:
        """Mutate an alert's triage state and write an audit-trail entry.

        Returns the updated alert or None if it doesn't exist. Valid status
        transitions are any of ALERT_STATUSES — the status field is just a
        label, there are no forbidden transitions (a dismissal can be walked
        back by setting to pending).
        """
        if status is not None and status not in ALERT_STATUSES:
            raise ValueError(
                f"invalid status {status!r}; allowed: {ALERT_STATUSES}"
            )
        with self._lock:
            current = self.get_alert(alert_id)
            if current is None:
                return None

            sets: list[str] = ["updated_at = datetime('now')"]
            params: list[Any] = []
            if status is not None and status != current["status"]:
                sets.append("status = ?")
                params.append(status)
                self._log_action(
                    alert_id,
                    action="status_change",
                    reviewer=reviewer,
                    from_value=current["status"],
                    to_value=status,
                    notes=notes,
                )
            if notes is not None and notes != current.get("notes"):
                sets.append("notes = ?")
                params.append(notes)
                if status is None or status == current["status"]:
                    self._log_action(
                        alert_id,
                        action="note",
                        reviewer=reviewer,
                        from_value=None,
                        to_value=None,
                        notes=notes,
                    )
            if reviewer is not None and reviewer != current.get("reviewer"):
                sets.append("reviewer = ?")
                params.append(reviewer)

            params.append(alert_id)
            self._conn.execute(
                f"UPDATE alerts SET {', '.join(sets)} WHERE id = ?",
                params,
            )
            return self.get_alert(alert_id)

    def escalate_alert(
        self,
        alert_id: int,
        *,
        destination: str,
        reason: str | None = None,
        reviewer: str | None = None,
    ) -> dict[str, Any] | None:
        """Mark an alert as escalated and record the destination (e.g. 088, SIPINNA)."""
        with self._lock:
            current = self.get_alert(alert_id)
            if current is None:
                return None
            self._conn.execute(
                "UPDATE alerts SET status = 'escalated', reviewer = COALESCE(?, reviewer), "
                "updated_at = datetime('now') WHERE id = ?",
                (reviewer, alert_id),
            )
            self._log_action(
                alert_id,
                action="escalation",
                reviewer=reviewer,
                from_value=current["status"],
                to_value="escalated",
                notes=f"destination={destination}" + (f" · reason={reason}" if reason else ""),
            )
            return self.get_alert(alert_id)

    def _log_action(
        self,
        alert_id: int,
        *,
        action: str,
        reviewer: str | None,
        from_value: str | None,
        to_value: str | None,
        notes: str | None,
    ) -> None:
        if action not in ALERT_ACTION_TYPES:
            raise ValueError(f"invalid action {action!r}")
        self._conn.execute(
            """
            INSERT INTO alert_actions (alert_id, action, reviewer, from_value, to_value, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (alert_id, action, reviewer, from_value, to_value, notes),
        )

    def list_actions(self, alert_id: int) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM alert_actions WHERE alert_id = ? ORDER BY created_at DESC, id DESC",
            (alert_id,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "alert_id": r["alert_id"],
                "action": r["action"],
                "reviewer": r["reviewer"],
                "from_value": r["from_value"],
                "to_value": r["to_value"],
                "notes": r["notes"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def stats(self) -> dict[str, Any]:
        total = self._conn.execute("SELECT COUNT(*) AS c FROM alerts").fetchone()["c"]

        by_level = {
            r["risk_level"]: r["c"]
            for r in self._conn.execute(
                "SELECT risk_level, COUNT(*) AS c FROM alerts GROUP BY risk_level"
            ).fetchall()
        }
        by_phase = {
            (r["phase_detected"] or "ninguna"): r["c"]
            for r in self._conn.execute(
                "SELECT phase_detected, COUNT(*) AS c FROM alerts GROUP BY phase_detected"
            ).fetchall()
        }
        by_platform = {
            r["platform"]: r["c"]
            for r in self._conn.execute(
                "SELECT platform, COUNT(*) AS c FROM alerts GROUP BY platform"
            ).fetchall()
        }
        overrides = self._conn.execute(
            "SELECT COUNT(*) AS c FROM alerts WHERE override_triggered = 1"
        ).fetchone()["c"]

        by_status = {
            r["status"]: r["c"]
            for r in self._conn.execute(
                "SELECT status, COUNT(*) AS c FROM alerts GROUP BY status"
            ).fetchall()
        }

        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        last_24h = self._conn.execute(
            "SELECT COUNT(*) AS c FROM alerts WHERE created_at >= ?",
            (cutoff,),
        ).fetchone()["c"]

        for level in ("SEGURO", "ATENCION", "PELIGRO"):
            by_level.setdefault(level, 0)
        for st in ALERT_STATUSES:
            by_status.setdefault(st, 0)

        return {
            "total_alerts": total,
            "by_level": by_level,
            "by_phase": by_phase,
            "by_platform": by_platform,
            "by_status": by_status,
            "overrides": overrides,
            "last_24h": last_24h,
        }

    # ---------------- Analytics ----------------

    def timeseries(
        self, interval: str = "hour", hours: int = 24
    ) -> list[dict[str, Any]]:
        """Bucket alerts over time for the panel chart.

        ``interval`` is 'hour' or 'day'. Buckets with zero alerts are not
        emitted — the client fills gaps as needed.

        Bucket key uses SQLite ``strftime`` so the value is stable text:
            'hour' → 'YYYY-MM-DD HH:00'
            'day'  → 'YYYY-MM-DD'
        """
        fmt_by_interval = {
            "hour": "%Y-%m-%d %H:00",
            "day": "%Y-%m-%d",
        }
        fmt = fmt_by_interval.get(interval)
        if fmt is None:
            raise ValueError(f"unsupported interval {interval!r}")
        if hours < 1:
            raise ValueError("hours must be >= 1")

        cutoff = (
            datetime.now(timezone.utc) - timedelta(hours=hours)
        ).strftime("%Y-%m-%d %H:%M:%S")

        rows = self._conn.execute(
            """
            SELECT
                strftime(?, created_at) AS bucket,
                COUNT(*)                                                       AS total,
                SUM(CASE WHEN risk_level = 'PELIGRO'  THEN 1 ELSE 0 END)       AS peligro,
                SUM(CASE WHEN risk_level = 'ATENCION' THEN 1 ELSE 0 END)       AS atencion,
                SUM(CASE WHEN risk_level = 'SEGURO'   THEN 1 ELSE 0 END)       AS seguro,
                SUM(CASE WHEN override_triggered = 1   THEN 1 ELSE 0 END)      AS overrides,
                SUM(CASE WHEN status = 'escalated'     THEN 1 ELSE 0 END)      AS escalated
            FROM alerts
            WHERE created_at >= ?
            GROUP BY bucket
            ORDER BY bucket ASC
            """,
            (fmt, cutoff),
        ).fetchall()
        return [
            {
                "bucket": r["bucket"],
                "total": r["total"],
                "by_level": {
                    "PELIGRO": r["peligro"] or 0,
                    "ATENCION": r["atencion"] or 0,
                    "SEGURO": r["seguro"] or 0,
                },
                "overrides": r["overrides"] or 0,
                "escalated": r["escalated"] or 0,
            }
            for r in rows
        ]

    # ---------------- Sessions ----------------

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "current_step": row["current_step"],
            "data": json.loads(row["data"]) if row["data"] else {},
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def upsert_session(
        self, session_id: str, current_step: str, data: dict[str, Any] | None = None
    ) -> None:
        payload = json.dumps(data or {}, ensure_ascii=False)
        self._conn.execute(
            """
            INSERT INTO sessions (id, current_step, data, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
            ON CONFLICT(id) DO UPDATE SET
                current_step = excluded.current_step,
                data = excluded.data,
                updated_at = datetime('now')
            """,
            (session_id, current_step, payload),
        )

    def delete_session(self, session_id: str) -> None:
        self._conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

    # ---------------- Risk history (Phase 4 — escalation tracking) ----------------

    def save_risk_history(
        self,
        *,
        session_id: str,
        risk_score: float,
        risk_level: str,
        phase_detected: str | None,
        source_type: str = "text",
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO risk_history (
                session_id, risk_score, risk_level, phase_detected, source_type
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, risk_score, risk_level, phase_detected, source_type),
        )
        return int(cur.lastrowid)

    def get_risk_history(
        self, session_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Chronological history (oldest → newest) for the escalation detector."""
        rows = self._conn.execute(
            """
            SELECT id, session_id, timestamp, risk_score, risk_level,
                   phase_detected, source_type
            FROM risk_history
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (session_id, limit),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "timestamp": r["timestamp"],
                "risk_score": r["risk_score"],
                "risk_level": r["risk_level"],
                "phase_detected": r["phase_detected"],
                "source_type": r["source_type"],
            }
            for r in rows
        ]

    def get_alerts_by_session(self, session_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM alerts WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ).fetchall()
        return [self._row_to_alert(r) for r in rows]

    def clear_risk_history(self, session_id: str) -> None:
        """Reset history for a session — used by demo_live.py to start clean."""
        self._conn.execute(
            "DELETE FROM risk_history WHERE session_id = ?", (session_id,)
        )

    # ---------------- Precision feedback (auto-tuning) ----------------

    def save_feedback(
        self,
        *,
        feedback_type: str,
        alert_id: int | None = None,
        heuristic_score: float | None = None,
        llm_score: float | None = None,
        final_score: float | None = None,
        pattern_ids: list[str] | None = None,
        text_hash: str | None = None,
        session_id: str | None = None,
    ) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO feedback_log (
                alert_id, feedback_type, heuristic_score, llm_score, final_score,
                pattern_ids, text_hash, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                alert_id,
                feedback_type,
                heuristic_score,
                llm_score,
                final_score,
                json.dumps(pattern_ids or [], ensure_ascii=False),
                text_hash,
                session_id,
            ),
        )
        return int(cur.lastrowid)

    def get_unprocessed_feedback(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM feedback_log WHERE processed = 0 ORDER BY created_at ASC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "created_at": r["created_at"],
                "alert_id": r["alert_id"],
                "feedback_type": r["feedback_type"],
                "heuristic_score": r["heuristic_score"],
                "llm_score": r["llm_score"],
                "final_score": r["final_score"],
                "pattern_ids": json.loads(r["pattern_ids"] or "[]"),
                "text_hash": r["text_hash"],
                "session_id": r["session_id"],
                "processed": r["processed"],
            }
            for r in rows
        ]

    def mark_feedback_processed(self, feedback_ids: list[int]) -> None:
        if not feedback_ids:
            return
        with self._lock:
            placeholders = ",".join("?" * len(feedback_ids))
            self._conn.execute(
                f"UPDATE feedback_log SET processed = 1 WHERE id IN ({placeholders})",
                feedback_ids,
            )

    def feedback_stats(self) -> dict[str, Any]:
        with self._lock:
            total = self._conn.execute(
                "SELECT COUNT(*) AS c FROM feedback_log"
            ).fetchone()["c"]
            pending = self._conn.execute(
                "SELECT COUNT(*) AS c FROM feedback_log WHERE processed = 0"
            ).fetchone()["c"]
            by_type = {
                r["feedback_type"]: r["c"]
                for r in self._conn.execute(
                    "SELECT feedback_type, COUNT(*) AS c FROM feedback_log GROUP BY feedback_type"
                ).fetchall()
            }
        return {"total": total, "pending": pending, "by_type": by_type}

    def close(self) -> None:
        self._conn.close()

    # ---------------- helpers ----------------

    @staticmethod
    def _row_to_alert(row: sqlite3.Row) -> dict[str, Any]:
        keys = row.keys()
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"] if "updated_at" in keys else row["created_at"],
            "platform": row["platform"],
            "source": row["source"],
            "risk_score": row["risk_score"],
            "risk_level": row["risk_level"],
            "phase_detected": row["phase_detected"],
            "categories": json.loads(row["categories"] or "[]"),
            "summary": row["summary"],
            "original_text_hash": row["original_text_hash"],
            "contact_phone": row["contact_phone"],
            "report_generated": bool(row["report_generated"]),
            "report_path": row["report_path"],
            "llm_used": bool(row["llm_used"]),
            "override_triggered": bool(row["override_triggered"]),
            "session_id": row["session_id"],
            "status": row["status"] if "status" in keys else "pending",
            "notes": row["notes"] if "notes" in keys else None,
            "reviewer": row["reviewer"] if "reviewer" in keys else None,
            "pattern_ids": (
                json.loads(row["pattern_ids"] or "[]")
                if "pattern_ids" in keys and row["pattern_ids"]
                else []
            ),
            "source_type": row["source_type"] if "source_type" in keys else "text",
        }

    # ---------------- Contributions (anonymous research) ----------------

    def insert_contribution(
        self,
        *,
        platform: str,
        risk_level: str,
        risk_score: float,
        phase_detected: str | None,
        categories: list[str],
        pattern_ids: list[str],
        source_type: str = "text",
        region: str | None = None,
        llm_used: bool = False,
        override_triggered: bool = False,
    ) -> int:
        """Persist anonymous research metadata. NO PII allowed.

        Validators (defense-in-depth): the caller controls all fields, but
        we still cap region length and reject suspicious payloads. The
        endpoint layer re-validates with Pydantic.
        """
        if region is not None and len(region) > 80:
            raise ValueError("region too long")
        cur = self._conn.execute(
            """
            INSERT INTO contributions (
                platform, risk_level, risk_score, phase_detected,
                categories, pattern_ids, source_type, region,
                llm_used, override_triggered
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                platform,
                risk_level,
                risk_score,
                phase_detected,
                json.dumps(categories, ensure_ascii=False),
                json.dumps(pattern_ids, ensure_ascii=False),
                source_type,
                region,
                int(llm_used),
                int(override_triggered),
            ),
        )
        return int(cur.lastrowid)

    def contribution_stats(self) -> dict[str, Any]:
        """Aggregate stats for the public /contributions/stats endpoint."""
        with self._lock:
            total = self._conn.execute(
                "SELECT COUNT(*) AS c FROM contributions"
            ).fetchone()["c"]
            by_platform = {
                r["platform"]: r["c"]
                for r in self._conn.execute(
                    "SELECT platform, COUNT(*) AS c FROM contributions GROUP BY platform"
                ).fetchall()
            }
            by_phase = {
                (r["phase_detected"] or "ninguna"): r["c"]
                for r in self._conn.execute(
                    "SELECT phase_detected, COUNT(*) AS c FROM contributions "
                    "GROUP BY phase_detected"
                ).fetchall()
            }
            by_level = {
                r["risk_level"]: r["c"]
                for r in self._conn.execute(
                    "SELECT risk_level, COUNT(*) AS c FROM contributions GROUP BY risk_level"
                ).fetchall()
            }
            by_source = {
                r["source_type"]: r["c"]
                for r in self._conn.execute(
                    "SELECT source_type, COUNT(*) AS c FROM contributions GROUP BY source_type"
                ).fetchall()
            }
            by_region = {
                (r["region"] or "no especificada"): r["c"]
                for r in self._conn.execute(
                    "SELECT region, COUNT(*) AS c FROM contributions GROUP BY region"
                ).fetchall()
            }
            top_patterns = [
                {"pattern_id": r["pid"], "count": r["c"]}
                for r in self._conn.execute(
                    """
                    SELECT json_each.value AS pid, COUNT(*) AS c
                    FROM contributions, json_each(contributions.pattern_ids)
                    GROUP BY pid
                    ORDER BY c DESC
                    LIMIT 10
                    """
                ).fetchall()
            ]
        for level in ("SEGURO", "ATENCION", "PELIGRO"):
            by_level.setdefault(level, 0)
        for st in ("text", "audio", "image"):
            by_source.setdefault(st, 0)
        return {
            "total_contributions": total,
            "by_platform": by_platform,
            "by_phase": by_phase,
            "by_level": by_level,
            "by_source": by_source,
            "by_region": by_region,
            "top_patterns": top_patterns,
        }


_db_singleton: Database | None = None


def get_db() -> Database:
    global _db_singleton
    if _db_singleton is None:
        _db_singleton = Database()
    return _db_singleton
