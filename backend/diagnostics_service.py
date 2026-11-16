"""
diagnostics_service.py — Backend Process Diagnostics and Runtime Health Inspector.

Gathers process uptime, memory footprint, host platform, subsystem readiness,
and registered route registries for operational monitoring.
"""

from datetime import datetime, timezone
import os
import platform
import sys
import time
from typing import Any, Dict, List, Optional

try:
    from backend.logger_service import audit_logger
except ImportError:
    from logger_service import audit_logger


def format_uptime(seconds: float) -> str:
    """Format elapsed seconds into readable 'Xd Xh Xm Xs' representation."""
    secs = int(seconds)
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, s = divmod(rem, 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{s}s")
    return " ".join(parts)


def get_memory_info() -> Dict[str, Any]:
    """Retrieve process memory consumption if psutil is available, otherwise safe fallback."""
    try:
        import psutil
        proc = psutil.Process(os.getpid())
        mem_info = proc.memory_info()
        return {
            "rss_mb": round(mem_info.rss / (1024 * 1024), 2),
            "vms_mb": round(mem_info.vms / (1024 * 1024), 2),
            "cpu_percent": proc.cpu_percent(interval=None),
            "provider": "psutil",
        }
    except Exception:
        return {
            "rss_mb": None,
            "vms_mb": None,
            "cpu_percent": None,
            "provider": "uninstrumented_fallback",
        }


def get_system_diagnostics(
    start_time: float,
    mode: str = "demo",
    extra_subsystems: Optional[Dict[str, Any]] = None,
    routes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Generate comprehensive runtime diagnostics report.
    """
    now = time.time()
    uptime_sec = max(0.0, now - start_time)

    subsystems = {
        "audit_logger": {
            "status": "operational",
            "buffered_event_count": audit_logger.count(),
        },
        "rate_limiter": {
            "status": "operational",
            "strategy": "sliding_window_in_memory",
        },
    }
    if extra_subsystems:
        subsystems.update(extra_subsystems)

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "process": {
            "pid": os.getpid(),
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "uptime_seconds": int(uptime_sec),
            "uptime_human": format_uptime(uptime_sec),
            "memory": get_memory_info(),
        },
        "execution": {
            "mode": mode,
            "containerized": os.path.exists("/.dockerenv") or bool(os.getenv("RENDER")),
            "cloud_provider": "Render" if os.getenv("RENDER") else "local_workstation",
        },
        "subsystems": subsystems,
        "api_endpoints": routes or [],
    }
