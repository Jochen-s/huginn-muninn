"""SQLite cache and feedback store with WAL mode."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path


class HuginnDB:
    """SQLite store for verdict caching and user feedback."""

    def __init__(self, db_path: str | Path = "huginn.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS verdicts (
                id INTEGER PRIMARY KEY,
                claim TEXT NOT NULL,
                verdict_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_verdicts_claim ON verdicts(claim);

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY,
                claim TEXT NOT NULL,
                verdict TEXT,
                feedback_type TEXT NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_feedback_claim ON feedback(claim);

            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY,
                claim TEXT NOT NULL,
                analysis_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_analyses_claim ON analyses(claim);

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS session_items (
                id INTEGER PRIMARY KEY,
                session_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                added_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            CREATE INDEX IF NOT EXISTS idx_session_items_session
                ON session_items(session_id);

            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY,
                url TEXT NOT NULL,
                secret TEXT NOT NULL,
                events TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY,
                claim TEXT NOT NULL,
                models_json TEXT NOT NULL,
                method TEXT NOT NULL,
                results_json TEXT NOT NULL,
                comparison_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_comparisons_claim ON comparisons(claim);
        """)
        self._conn.commit()

    def store_verdict(self, claim: str, verdict_data: dict) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO verdicts (claim, verdict_json, created_at) VALUES (?, ?, ?)",
                (claim, json.dumps(verdict_data), datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_cached_verdict(self, claim: str) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT verdict_json FROM verdicts WHERE claim = ? ORDER BY created_at DESC LIMIT 1",
                (claim,),
            ).fetchone()
        if row:
            return json.loads(row["verdict_json"])
        return None

    def get_cached_verdict_with_id(self, claim: str) -> tuple[dict, int] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT id, verdict_json FROM verdicts WHERE claim = ? ORDER BY created_at DESC LIMIT 1",
                (claim,),
            ).fetchone()
        if row:
            return json.loads(row["verdict_json"]), row["id"]
        return None

    def store_feedback(
        self,
        claim: str,
        verdict: str,
        feedback_type: str,
        comment: str | None,
    ):
        with self._lock:
            self._conn.execute(
                "INSERT INTO feedback (claim, verdict, feedback_type, comment, created_at) VALUES (?, ?, ?, ?, ?)",
                (claim, verdict, feedback_type, comment, datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()

    def get_feedback_for_claim(self, claim: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM feedback WHERE claim = ? ORDER BY created_at",
            (claim,),
        ).fetchall()
        return [dict(r) for r in rows]

    def store_analysis(self, claim: str, analysis_data: dict) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO analyses (claim, analysis_json, created_at) VALUES (?, ?, ?)",
                (claim, json.dumps(analysis_data), datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_cached_analysis(self, claim: str) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT analysis_json FROM analyses WHERE claim = ? ORDER BY created_at DESC LIMIT 1",
                (claim,),
            ).fetchone()
        if row:
            return self._normalize_cached_analysis(json.loads(row["analysis_json"]))
        return None

    def get_cached_analysis_with_id(self, claim: str) -> tuple[dict, int] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT id, analysis_json FROM analyses WHERE claim = ? ORDER BY created_at DESC LIMIT 1",
                (claim,),
            ).fetchone()
        if row:
            return (
                self._normalize_cached_analysis(json.loads(row["analysis_json"])),
                row["id"],
            )
        return None

    @staticmethod
    def _normalize_cached_analysis(raw: dict) -> dict:
        """Populate schema defaults on a cache hit so pre-Sprint-2 cached
        analyses return the same shape as fresh runs.

        Codex PR 2 review identified a High-severity blind spot: new Pydantic
        fields (verification_priority on SubClaim, hypothesis_crowding on
        DecomposerOutput, frame_capture_risk on AuditorOutput, etc.) are
        absent on cached analyses that predate the corresponding sprint. API
        and CLI callers then see split output shape: fresh runs carry the
        field, cache hits do not. Running the cached dict through
        AnalysisReport.model_validate().model_dump() forces every Pydantic
        default to populate, so downstream consumers always see the current
        schema regardless of when the entry was cached.

        If the cached dict cannot be validated (schema change, hand-edited
        row, pre-method-2 verdict), fall back to returning the raw dict so
        that the read path degrades gracefully rather than raising. A
        validation failure here is not a pipeline failure; the caller can
        still inspect whatever fields are present. Logging is deliberately
        omitted to keep this read path zero-dependency.
        """
        # Deferred import avoids a module-level cycle between db.py and
        # contracts.py and lets test fixtures stub this method cheaply.
        from huginn_muninn.contracts import AnalysisReport
        from pydantic import ValidationError

        try:
            return AnalysisReport.model_validate(raw).model_dump(mode="json")
        except ValidationError:
            return raw

    def get_recent_verdicts(self, limit: int = 20) -> list[dict]:
        """Return recent verdicts, most recent first."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT claim, verdict_json, created_at FROM verdicts ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"claim": r["claim"], "data": json.loads(r["verdict_json"]), "created_at": r["created_at"]}
            for r in rows
        ]

    def get_recent_analyses(self, limit: int = 20) -> list[dict]:
        """Return recent analyses, most recent first."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT claim, analysis_json, created_at FROM analyses ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"claim": r["claim"], "data": json.loads(r["analysis_json"]), "created_at": r["created_at"]}
            for r in rows
        ]

    # --- Session methods ---

    def create_session(self, name: str) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO sessions (name, created_at) VALUES (?, ?)",
                (name, datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_session(self, session_id: int) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            if not row:
                return None
            session = dict(row)
            items = self._conn.execute(
                "SELECT * FROM session_items WHERE session_id = ? ORDER BY added_at",
                (session_id,),
            ).fetchall()
        session["items"] = [dict(i) for i in items]
        return session

    def list_sessions(self) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def add_session_item(
        self, session_id: int, item_type: str, item_id: int
    ) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO session_items (session_id, item_type, item_id, added_at) VALUES (?, ?, ?, ?)",
                (session_id, item_type, item_id, datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
            return cur.lastrowid

    # --- Webhook methods ---

    def create_webhook(self, url: str, secret: str, events: list[str]) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO webhooks (url, secret, events, active, created_at) VALUES (?, ?, ?, 1, ?)",
                (url, secret, json.dumps(events), datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_webhook(self, webhook_id: int) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM webhooks WHERE id = ?", (webhook_id,)
            ).fetchone()
        if not row:
            return None
        wh = dict(row)
        wh["events"] = json.loads(wh["events"])
        wh["active"] = bool(wh["active"])
        return wh

    def list_webhooks(self) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM webhooks ORDER BY created_at DESC"
            ).fetchall()
        result = []
        for r in rows:
            wh = dict(r)
            wh["events"] = json.loads(wh["events"])
            wh["active"] = bool(wh["active"])
            result.append(wh)
        return result

    def update_webhook(self, webhook_id: int, **kwargs) -> dict | None:
        with self._lock:
            wh = self.get_webhook(webhook_id)
            if not wh:
                return None
            if "active" in kwargs:
                self._conn.execute(
                    "UPDATE webhooks SET active = ? WHERE id = ?",
                    (int(kwargs["active"]), webhook_id),
                )
            if "events" in kwargs:
                self._conn.execute(
                    "UPDATE webhooks SET events = ? WHERE id = ?",
                    (json.dumps(kwargs["events"]), webhook_id),
                )
            self._conn.commit()
        return self.get_webhook(webhook_id)

    def delete_webhook(self, webhook_id: int) -> bool:
        with self._lock:
            cur = self._conn.execute(
                "DELETE FROM webhooks WHERE id = ?", (webhook_id,)
            )
            self._conn.commit()
            return cur.rowcount > 0

    def get_webhooks_for_event(self, event: str) -> list[dict]:
        """Return active webhooks subscribed to the given event."""
        all_hooks = self.list_webhooks()
        return [
            wh for wh in all_hooks
            if wh["active"] and event in wh["events"]
        ]

    def get_verdict_by_id(self, verdict_id: int) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM verdicts WHERE id = ?", (verdict_id,)
            ).fetchone()
        if not row:
            return None
        return {"id": row["id"], "claim": row["claim"], "data": json.loads(row["verdict_json"]), "created_at": row["created_at"]}

    def get_analysis_by_id(self, analysis_id: int) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
            ).fetchone()
        if not row:
            return None
        return {"id": row["id"], "claim": row["claim"], "data": json.loads(row["analysis_json"]), "created_at": row["created_at"]}

    # --- Comparison methods ---

    def store_comparison(
        self, claim: str, models: list[str], method: str,
        results: dict, comparison: dict,
    ) -> int:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO comparisons (claim, models_json, method, results_json, comparison_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (claim, json.dumps(models), method, json.dumps(results), json.dumps(comparison), datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
            return cur.lastrowid

    def get_comparison(self, comparison_id: int) -> dict | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM comparisons WHERE id = ?", (comparison_id,)
            ).fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "claim": row["claim"],
            "models": json.loads(row["models_json"]),
            "method": row["method"],
            "results": json.loads(row["results_json"]),
            "comparison": json.loads(row["comparison_json"]),
            "created_at": row["created_at"],
        }

    def get_recent_comparisons(self, limit: int = 20) -> list[dict]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM comparisons ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "id": r["id"],
                "claim": r["claim"],
                "models": json.loads(r["models_json"]),
                "method": r["method"],
                "comparison": json.loads(r["comparison_json"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
