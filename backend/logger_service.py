"""
logger_service.py — Structured Event Logging and Traffic Audit Service.

Provides thread-safe in-memory structured event auditing with RFC-3339 UTC
timestamps, severity classifications, and query filters. Used across
signal preemption, violation detection, and junction telemetry.
"""

from collections import deque
from datetime import datetime, timezone
import json
import logging
import threading
from typing import Any, Dict, List, Optional

# Standard Python logger
_py_logger = logging.getLogger("BengaluruTrafficAI")
if not _py_logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    _py_logger.addHandler(_handler)
    _py_logger.setLevel(logging.INFO)


class TrafficAuditLogger:
    """
    Thread-safe audit logger storing structured events in an in-memory ring buffer
    with search and filtering capabilities.
    """

    VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "AUDIT"}

    def __init__(self, max_records: int = 500):
        self._buffer: deque = deque(maxlen=max_records)
        self._lock = threading.Lock()

    def log_event(
        self,
        level: str,
        event_type: str,
        details: Dict[str, Any],
        junction_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record a structured audit entry.

        Args:
            level: Severity level (INFO, WARNING, ERROR, CRITICAL, AUDIT)
            event_type: Category identifier (e.g., 'EMERGENCY_OVERRIDE', 'SIGNAL_CYCLE')
            details: Contextual payload dictionary
            junction_id: Optional junction code (e.g., 'silk_board', 'tin_factory')

        Returns:
            Dict representing the logged entry.
        """
        norm_level = level.upper().strip() if level else "INFO"
        if norm_level not in self.VALID_LEVELS:
            norm_level = "INFO"

        timestamp = datetime.now(timezone.utc).isoformat()

        entry = {
            "timestamp": timestamp,
            "level": norm_level,
            "event_type": event_type.strip(),
            "junction_id": junction_id or "system",
            "details": details or {},
        }

        with self._lock:
            self._buffer.append(entry)

        # Output to console logger
        msg = f"[{entry['junction_id']}] {entry['event_type']}: {json.dumps(entry['details'])}"
        if norm_level in ("ERROR", "CRITICAL"):
            _py_logger.error(msg)
        elif norm_level == "WARNING":
            _py_logger.warning(msg)
        else:
            _py_logger.info(msg)

        return entry

    def get_recent_logs(
        self,
        limit: int = 50,
        level: Optional[str] = None,
        event_type: Optional[str] = None,
        junction_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query audit entries with optional criteria.
        """
        norm_level = level.upper().strip() if level else None
        norm_type = event_type.strip().lower() if event_type else None
        norm_junction = junction_id.strip().lower() if junction_id else None

        with self._lock:
            records = list(self._buffer)

        # Filter newest first
        records.reverse()

        filtered: List[Dict[str, Any]] = []
        for r in records:
            if norm_level and r["level"] != norm_level:
                continue
            if norm_type and r["event_type"].lower() != norm_type:
                continue
            if norm_junction and r["junction_id"].lower() != norm_junction:
                continue

            filtered.append(r)
            if len(filtered) >= limit:
                break

        return filtered

    def clear(self) -> None:
        """Clear the in-memory buffer."""
        with self._lock:
            self._buffer.clear()

    def count(self) -> int:
        """Return total number of retained log entries."""
        with self._lock:
            return len(self._buffer)


# Global singleton instance for application-wide logging
audit_logger = TrafficAuditLogger(max_records=500)
