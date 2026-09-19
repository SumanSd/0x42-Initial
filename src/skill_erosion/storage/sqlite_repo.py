"""Append-only SQLite trace repository with a derived embedding index.

Canonical attempts live in `attempts`; embeddings are derived state keyed by
versioned attempt key and encoder version, so they can be rebuilt at any time.
"""

import json
import sqlite3
import threading
from pathlib import Path

from skill_erosion.contracts.models import Attempt

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    attempt_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    student_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    payload TEXT NOT NULL,
    PRIMARY KEY (attempt_id, version)
);
CREATE INDEX IF NOT EXISTS idx_attempts_scope ON attempts (student_id, skill_id);
CREATE TABLE IF NOT EXISTS embeddings (
    attempt_key TEXT NOT NULL,
    model_version TEXT NOT NULL,
    vector TEXT NOT NULL,
    PRIMARY KEY (attempt_key, model_version)
);
"""


class SQLiteTraceRepository:
    def __init__(self, path: Path) -> None:
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock, self._conn:
            self._conn.executescript(_SCHEMA)

    @staticmethod
    def _payload(attempt: Attempt) -> str:
        return json.dumps(attempt.__dict__, sort_keys=True)

    def append(self, attempt: Attempt) -> None:
        payload = self._payload(attempt)
        with self._lock, self._conn:
            row = self._conn.execute(
                "SELECT payload FROM attempts WHERE attempt_id=? AND version=?",
                (attempt.attempt_id, attempt.version),
            ).fetchone()
            if row is not None:
                if row["payload"] != payload:
                    raise ValueError(
                        f"Conflicting payload for immutable ({attempt.attempt_id}, v{attempt.version})"
                    )
                return
            self._conn.execute(
                "INSERT INTO attempts VALUES (?,?,?,?,?,?,?)",
                (
                    attempt.attempt_id,
                    attempt.version,
                    attempt.student_id,
                    attempt.skill_id,
                    attempt.checkpoint_id,
                    attempt.timestamp,
                    payload,
                ),
            )

    def history(self, student_id: str, skill_id: str) -> list[Attempt]:
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT a.payload FROM attempts a
                JOIN (
                    SELECT attempt_id, MAX(version) AS v FROM attempts
                    WHERE student_id=? AND skill_id=? GROUP BY attempt_id
                ) latest ON latest.attempt_id=a.attempt_id AND latest.v=a.version
                ORDER BY a.timestamp, a.attempt_id
                """,
                (student_id, skill_id),
            ).fetchall()
        return [Attempt(**json.loads(row["payload"])) for row in rows]

    def get(self, attempt_id: str, version: int) -> Attempt | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT payload FROM attempts WHERE attempt_id=? AND version=?",
                (attempt_id, version),
            ).fetchone()
        return Attempt(**json.loads(row["payload"])) if row else None

    def embedding_keys(self, model_version: str) -> set[str]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT attempt_key FROM embeddings WHERE model_version=?", (model_version,)
            ).fetchall()
        return {row["attempt_key"] for row in rows}

    def upsert_embedding(self, attempt_key: str, model_version: str, vector: list[float]) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO embeddings VALUES (?,?,?)",
                (attempt_key, model_version, json.dumps(vector)),
            )

    def close(self) -> None:
        with self._lock:
            self._conn.close()
