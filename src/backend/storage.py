# src/backend/storage.py
"""SQLite-backed persistent storage for SysWatch metrics and incidents."""

import sqlite3
import json
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
import sys
import os

# Allow running as module directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.logger import get_logger
from utils.config import AppConfig

logger = get_logger("storage")


def _get_db_path() -> Path:
    return AppConfig.get_data_dir() / "syswatch.db"


class Storage:
    """Thread-safe SQLite storage manager."""

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or _get_db_path()
        self._local = threading.local()
        self._lock = threading.Lock()
        self._init_db()
        logger.info(f"Storage initialized at {self._db_path}")

    def _conn(self) -> sqlite3.Connection:
        """Return a thread-local database connection."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                str(self._db_path), check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
        return self._local.conn

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        conn = self._conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS services (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'unknown',
                cpu_usage REAL DEFAULT 0,
                memory_usage REAL DEFAULT 0,
                uptime_seconds INTEGER DEFAULT 0,
                last_seen TEXT,
                metadata TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS metrics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                cpu REAL,
                memory REAL,
                latency REAL,
                requests REAL,
                disk_read REAL DEFAULT 0,
                disk_write REAL DEFAULT 0,
                net_in REAL DEFAULT 0,
                net_out REAL DEFAULT 0
            );
            CREATE INDEX IF NOT EXISTS idx_metrics_service_time
                ON metrics_history(service_id, timestamp);

            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                service TEXT NOT NULL,
                severity TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                details TEXT DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_incidents_time
                ON incidents(timestamp);
        """)
        conn.commit()

    # -------------------------------------------------------------------------
    # Service management
    # -------------------------------------------------------------------------

    def upsert_service(self, service: Dict[str, Any]) -> None:
        conn = self._conn()
        conn.execute("""
            INSERT INTO services (id, name, status, cpu_usage, memory_usage,
                                  uptime_seconds, last_seen, metadata)
            VALUES (:id, :name, :status, :cpu_usage, :memory_usage,
                    :uptime_seconds, :last_seen, :metadata)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name, status=excluded.status,
                cpu_usage=excluded.cpu_usage, memory_usage=excluded.memory_usage,
                uptime_seconds=excluded.uptime_seconds,
                last_seen=excluded.last_seen, metadata=excluded.metadata
        """, {
            "id": service["id"],
            "name": service["name"],
            "status": service.get("status", "unknown"),
            "cpu_usage": service.get("cpu_usage", 0),
            "memory_usage": service.get("memory_usage", 0),
            "uptime_seconds": service.get("uptime_seconds", 0),
            "last_seen": datetime.utcnow().isoformat(),
            "metadata": json.dumps(service.get("metadata", {})),
        })
        conn.commit()

    def get_services(self) -> List[Dict]:
        rows = self._conn().execute(
            "SELECT * FROM services ORDER BY name"
        ).fetchall()
        return [dict(r) for r in rows]

    # -------------------------------------------------------------------------
    # Metrics
    # -------------------------------------------------------------------------

    def save_metrics(self, service_id: str, metrics: Dict[str, float]) -> None:
        conn = self._conn()
        conn.execute("""
            INSERT INTO metrics_history
                (service_id, timestamp, cpu, memory, latency, requests,
                 disk_read, disk_write, net_in, net_out)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            service_id,
            datetime.utcnow().isoformat(),
            metrics.get("cpu", 0),
            metrics.get("memory", 0),
            metrics.get("latency", 0),
            metrics.get("requests", 0),
            metrics.get("disk_read", 0),
            metrics.get("disk_write", 0),
            metrics.get("net_in", 0),
            metrics.get("net_out", 0),
        ))
        conn.commit()

    def get_metrics_history(
        self,
        service_id: str,
        limit: int = 300,
        since_hours: float = 1.0,
    ) -> List[Dict]:
        since = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat()
        rows = self._conn().execute("""
            SELECT * FROM metrics_history
            WHERE service_id = ? AND timestamp > ?
            ORDER BY timestamp DESC LIMIT ?
        """, (service_id, since, limit)).fetchall()
        return [dict(r) for r in reversed(rows)]

    # -------------------------------------------------------------------------
    # Incidents
    # -------------------------------------------------------------------------

    def save_incident(self, incident: Dict[str, Any]) -> int:
        conn = self._conn()
        cursor = conn.execute("""
            INSERT INTO incidents
                (timestamp, service, severity, type, description, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            incident.get("timestamp", datetime.utcnow().isoformat()),
            incident["service"],
            incident["severity"],
            incident["type"],
            incident["description"],
            incident.get("status", "active"),
            json.dumps(incident.get("details", {})),
        ))
        conn.commit()
        logger.info(f"Saved incident: {incident['type']} on {incident['service']}")
        return cursor.lastrowid

    def get_incidents(
        self,
        limit: int = 100,
        severity: Optional[str] = None,
        since_hours: float = 24.0,
    ) -> List[Dict]:
        since = (datetime.utcnow() - timedelta(hours=since_hours)).isoformat()
        if severity and severity.lower() != "all":
            rows = self._conn().execute("""
                SELECT * FROM incidents
                WHERE timestamp > ? AND severity = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (since, severity.lower(), limit)).fetchall()
        else:
            rows = self._conn().execute("""
                SELECT * FROM incidents WHERE timestamp > ?
                ORDER BY timestamp DESC LIMIT ?
            """, (since, limit)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["details"] = json.loads(d.get("details") or "{}")
            result.append(d)
        return result

    def update_incident_status(self, incident_id: int, status: str) -> None:
        conn = self._conn()
        conn.execute(
            "UPDATE incidents SET status = ? WHERE id = ?", (status, incident_id)
        )
        conn.commit()

    def clear_incidents(self) -> None:
        conn = self._conn()
        conn.execute("DELETE FROM incidents")
        conn.commit()

    # -------------------------------------------------------------------------
    # Maintenance
    # -------------------------------------------------------------------------

    def clear_old_data(self, retention_hours: float = 24.0) -> None:
        """Delete metrics older than retention window."""
        cutoff = (datetime.utcnow() - timedelta(hours=retention_hours)).isoformat()
        conn = self._conn()
        conn.execute(
            "DELETE FROM metrics_history WHERE timestamp < ?", (cutoff,)
        )
        conn.commit()
        logger.debug(f"Cleared metrics older than {retention_hours}h")

    def close(self) -> None:
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
