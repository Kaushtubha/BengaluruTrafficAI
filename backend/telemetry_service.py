"""
telemetry_service.py — Consolidated Junction Telemetry and Queue Engineering Metrics.

Computes queue balance index, safety compliance scores, lane load distributions,
and aggregates phase schedules for smart junction management.
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional

try:
    from backend.signal_service import get_phase_schedule
except ImportError:
    from signal_service import get_phase_schedule


def calculate_queue_balance_index(vehicle_counts: Dict[str, int]) -> float:
    """
    Calculate queue distribution balance across monitored lanes (0.0 to 1.0).
    A score of 1.0 indicates perfectly uniform vehicle distribution across all approaches.
    0.0 indicates extreme bottlenecking where one lane holds all traffic.
    """
    if not vehicle_counts:
        return 1.0

    counts = [float(v) for v in vehicle_counts.values()]
    n = len(counts)
    if n <= 1:
        return 1.0

    mean_count = sum(counts) / n
    if mean_count <= 0.001:
        return 1.0  # Empty junction is uniformly balanced

    variance = sum((c - mean_count) ** 2 for c in counts) / n
    std_dev = math.sqrt(variance)

    # Normalized coefficient of variation (bounded to [0.0, 1.0])
    cv = std_dev / mean_count
    balance = max(0.0, min(1.0, 1.0 - (cv / math.sqrt(n - 1))))
    return round(balance, 3)


def calculate_safety_compliance_score(total_violations: int, tracked_total: int) -> float:
    """
    Calculate safety compliance index (0.0 to 100.0).
    Penalizes elevated violation rates per 1,000 tracked vehicles.
    """
    if tracked_total <= 0:
        return 98.5

    # Violations per 100 vehicles
    rate = (total_violations / tracked_total) * 100.0
    # Base 100 minus penalty
    score = max(50.0, min(100.0, 100.0 - (rate * 3.5)))
    return round(score, 1)


def build_telemetry_summary(
    junction_config: Dict[str, Any],
    vehicle_counts: Dict[str, int],
    tracked_total: int,
    violations_summary: Dict[str, int],
    congestion_level: str,
    emergency_lane: Optional[str] = None,
    mode: str = "demo",
) -> Dict[str, Any]:
    """
    Build consolidated junction telemetry summary payload.
    """
    counts = vehicle_counts or {"North": 0, "South": 0, "East": 0, "West": 0}
    total_vehicles = sum(counts.values())
    total_violations = sum(violations_summary.values()) if violations_summary else 0

    # Calculate per-lane percentage
    lane_distribution: Dict[str, float] = {}
    for lane, count in counts.items():
        lane_distribution[lane] = round((count / total_vehicles * 100.0), 1) if total_vehicles > 0 else 25.0

    balance_index = calculate_queue_balance_index(counts)
    safety_score = calculate_safety_compliance_score(total_violations, tracked_total)

    # Active phase determination
    active_lane = emergency_lane or (max(counts, key=counts.get) if counts else "North")
    phase_schedule = get_phase_schedule(counts, emergency_lanes=[emergency_lane] if emergency_lane else None)

    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "junction": {
            "name": junction_config.get("name", "Silk Board, Bengaluru"),
            "latitude": junction_config.get("latitude", 12.9177),
            "longitude": junction_config.get("longitude", 77.6238),
            "status": "operational",
        },
        "throughput": {
            "current_frame_vehicles": total_vehicles,
            "cumulative_tracked_vehicles": tracked_total,
            "lane_counts": counts,
            "lane_load_percentage": lane_distribution,
        },
        "traffic_quality": {
            "congestion_level": congestion_level,
            "queue_balance_index": balance_index,
            "balance_status": "optimal" if balance_index >= 0.75 else ("moderate" if balance_index >= 0.5 else "imbalanced"),
            "safety_compliance_score": safety_score,
            "safety_rating": "grade_a" if safety_score >= 90 else ("grade_b" if safety_score >= 75 else "grade_c"),
        },
        "signal_state": {
            "active_lane": active_lane,
            "emergency_preemption_active": bool(emergency_lane),
            "emergency_lane": emergency_lane,
            "phases_in_cycle": len(phase_schedule),
            "phase_schedule": phase_schedule,
        },
    }
