import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional


def project_root() -> Path:
    # app/data/db.py -> data -> app -> PROJECT_ROOT
    return Path(__file__).resolve().parents[2]


DB_PATH = project_root() / "outputs" / "db" / "app.db"


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self._create_tables()
        self._migrate()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                bottle_id INTEGER,
                message TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def _migrate(self):
        cur = self.conn.cursor()
        cur.execute("PRAGMA table_info(events)")
        cols = [row[1] for row in cur.fetchall()]
        if "snapshot_path" not in cols:
            try:
                cur.execute("ALTER TABLE events ADD COLUMN snapshot_path TEXT")
                self.conn.commit()
            except Exception:
                pass

    def insert_event(
        self,
        timestamp: str,
        bottle_id: Optional[int],
        message: str,
        snapshot_path: Optional[str] = None
    ):
        cur = self.conn.cursor()
        cur.execute("PRAGMA table_info(events)")
        cols = [row[1] for row in cur.fetchall()]

        if "snapshot_path" in cols:
            cur.execute(
                "INSERT INTO events (timestamp, bottle_id, message, snapshot_path) VALUES (?, ?, ?, ?)",
                (timestamp, bottle_id, message, snapshot_path)
            )
        else:
            cur.execute(
                "INSERT INTO events (timestamp, bottle_id, message) VALUES (?, ?, ?)",
                (timestamp, bottle_id, message)
            )
        self.conn.commit()

    def fetch_events(self, limit: int = 1000) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("PRAGMA table_info(events)")
        cols = [row[1] for row in cur.fetchall()]

        if "snapshot_path" in cols:
            cur.execute("""
                SELECT id, timestamp, bottle_id, message, snapshot_path
                FROM events
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            rows = cur.fetchall()
            return [
                {"id": r[0], "timestamp": r[1], "bottle_id": r[2], "message": r[3], "snapshot_path": r[4]}
                for r in rows
            ]

        cur.execute("""
            SELECT id, timestamp, bottle_id, message
            FROM events
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        return [
            {"id": r[0], "timestamp": r[1], "bottle_id": r[2], "message": r[3], "snapshot_path": ""}
            for r in rows
        ]

    def close(self):
        self.conn.close()