"""
BengaluruTrafficAI - Lightweight Demo Backend
Simulates real AI outputs for free-tier deployment (Render 512MB).
Full YOLOv8 version runs locally: python backend/app.py
"""
import os
import random
import math
import time
from datetime import datetime, timezone
from collections import deque
from flask import Flask, jsonify, request
from flask_cors import CORS

from junction_config import get_junction_config, validate_coordinates

try:
    from backend.security import global_rate_limiter, sanitize_text, sanitize_integer
    from backend.logger_service import audit_logger
    from backend.telemetry_service import build_telemetry_summary
except ImportError:
    from security import global_rate_limiter, sanitize_text, sanitize_integer
    from logger_service import audit_logger
    from telemetry_service import build_telemetry_summary

app = Flask(__name__)
CORS(app)

@app.before_request
def enforce_rate_limits():
    """Protect API endpoints against excessive request bursts."""
    if request.method == "OPTIONS":
        return None
    client_ip = request.remote_addr or "127.0.0.1"
    allowed, status = global_rate_limiter.is_allowed(client_ip)
    if not allowed:
        return jsonify({
            "status": "error",
            "message": "Too many requests. Rate limit exceeded.",
            "retry_after_seconds": status.get("retry_after_seconds", 60)
        }), 429

# ── Simulation Config ────────────────────────────────────────────────
LANES = ["North", "South", "East", "West"]
JUNCTIONS = "Silk Board, Bengaluru"

# Internal sim state
_start_time = time.time()
_tracked_total = 0
_violations = {"red_light": 0, "wrong_side": 0, "speeding": 0, "no_helmet": 0}
_last_emergency = None
_violation_history = deque(maxlen=250)
_violation_seq = 1000

def _seed_violation_history():
    """Seed buffer with initial violation log entries."""
    global _violation_seq
    sample_types = [
        ("red_light", "Red Light Jumping", "North", "Motorcycle", 1000, 0.94),
        ("speeding", "Overspeeding (>60 km/h)", "East", "Car", 1000, 0.91),
        ("no_helmet", "Riding Without Helmet", "South", "Motorcycle", 500, 0.96),
        ("wrong_side", "Wrong-Way Driving", "West", "Auto Rickshaw", 1500, 0.88),
    ]
    for v_type, label, lane, veh, fine, conf in sample_types:
        _violation_seq += 1
        _violations[v_type] += 1
        _violation_history.appendleft({
            "id": f"BLR-{datetime.now().strftime('%Y%m%d')}-{_violation_seq:04d}",
            "category": v_type,
            "label": label,
            "lane": lane,
            "vehicle_type": veh,
            "confidence": conf,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_taken": "E-CHALLAN_QUEUED",
            "fine_amount_inr": fine,
        })

_seed_violation_history()

def _time_factor():
    """Simulate rush hour patterns based on current hour."""
    hour = datetime.now().hour
    # Morning rush 8-10, Evening rush 17-20
    if 8 <= hour <= 10 or 17 <= hour <= 20:
        return random.uniform(0.75, 1.0)   # High traffic
    elif 12 <= hour <= 14:
        return random.uniform(0.45, 0.65)  # Moderate
    elif 0 <= hour <= 5:
        return random.uniform(0.05, 0.2)   # Night — low
    else:
        return random.uniform(0.3, 0.6)    # Normal

def _generate_lane_counts():
    """Return realistic per-lane vehicle counts."""
    factor = _time_factor()
    base = {
        "North": random.randint(int(5 * factor), int(25 * factor)),
        "South": random.randint(int(3 * factor), int(20 * factor)),
        "East":  random.randint(int(4 * factor), int(22 * factor)),
        "West":  random.randint(int(2 * factor), int(18 * factor)),
    }
    return base

def _get_congestion(total):
    if total is None:
        return "UNAVAILABLE"
    try:
        tot = float(total)
        if tot < 0 or math.isnan(tot) or math.isinf(tot):
            return "UNAVAILABLE"
        if tot < 20:
            return "Low"
        elif tot < 45:
            return "Medium"
        return "High"
    except (ValueError, TypeError):
        return "UNAVAILABLE"

def _get_signal_plan(lane_counts, emergency_lane=None):
    counts = lane_counts if isinstance(lane_counts, dict) and lane_counts else {l: 0 for l in LANES}
    total = sum(counts.values()) or 1
    MIN_GREEN, MAX_GREEN = 10, 60
    green_times = {}
    for lane, count in counts.items():
        proportion = count / total
        green_times[lane] = round(MIN_GREEN + proportion * (MAX_GREEN - MIN_GREEN), 1)

    is_override = bool(emergency_lane and emergency_lane in counts)
    priority = emergency_lane if is_override else (max(counts, key=counts.get) if counts else "North")
    if is_override:
        green_times[emergency_lane] = float(MAX_GREEN)

    return {
        "green_times": green_times,
        "priority_lane": priority,
        "cycle_time": round(sum(green_times.values()), 1),
        "emergency_override": is_override,
        "emergency_lane": emergency_lane if is_override else None,
    }

def _maybe_log_violation():
    """Probabilistically add violations to simulate live detection and history."""
    global _violation_seq
    factor = _time_factor()
    events = [
        ("red_light", 0.03 * factor, "Red Light Jumping", 1000, 0.95),
        ("wrong_side", 0.015 * factor, "Wrong-Way Driving", 1500, 0.91),
        ("speeding", 0.04 * factor, "Overspeeding (>60 km/h)", 1000, 0.89),
        ("no_helmet", 0.02 * factor, "Riding Without Helmet", 500, 0.96),
    ]
    for v_type, prob, label, fine, conf in events:
        if random.random() < prob:
            _violations[v_type] += 1
            _violation_seq += 1
            lane = random.choice(LANES)
            veh = random.choice(["Motorcycle", "Car", "Auto Rickshaw", "Bus"])
            rec = {
                "id": f"BLR-{datetime.now().strftime('%Y%m%d')}-{_violation_seq:04d}",
                "category": v_type,
                "label": label,
                "lane": lane,
                "vehicle_type": veh,
                "confidence": round(conf + random.uniform(-0.04, 0.03), 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action_taken": "E-CHALLAN_QUEUED",
                "fine_amount_inr": fine,
            }
            _violation_history.appendleft(rec)
            audit_logger.log_event("AUDIT", "VIOLATION_RECORDED", {"id": rec["id"], "category": v_type, "lane": lane})

# ── API Routes ────────────────────────────────────────────────────────

@app.route('/api/status', methods=['GET'])
def get_status():
    global _tracked_total
    _maybe_log_violation()

    lane_counts = _generate_lane_counts()
    total = sum(lane_counts.values())
    _tracked_total += random.randint(1, 3)

    active_lane = _last_emergency or max(lane_counts, key=lane_counts.get)
    congestion = _get_congestion(total)
    signal_plan = _get_signal_plan(lane_counts, _last_emergency)
    total_violations = sum(_violations.values())

    return jsonify({
        "status": "online",
        "junction": JUNCTIONS,
        "active_lane": active_lane,
        "congestion_level": congestion,
        "congestion_provenance": "synthetic_demo_rule",
        "is_synthetic_congestion_model": True,
        "vehicle_counts": lane_counts,
        "total_vehicles": total,
        "tracked_vehicles": _tracked_total,
        "violations": total_violations,
        "signal_plan": signal_plan,
        "mode": "demo"
    })

@app.route('/api/lanes', methods=['GET'])
def get_lanes():
    return jsonify(_generate_lane_counts())

@app.route('/api/signal', methods=['GET'])
def get_signal():
    counts = _generate_lane_counts()
    return jsonify(_get_signal_plan(counts, _last_emergency))

@app.route('/api/violations', methods=['GET'])
def get_violations():
    return jsonify({
        "total_violations": sum(_violations.values()),
        "red_light":   _violations["red_light"],
        "wrong_side":  _violations["wrong_side"],
        "speeding":    _violations["speeding"],
        "no_helmet":   _violations["no_helmet"]
    })

@app.route('/api/violations/history', methods=['GET'])
def get_violation_history():
    _maybe_log_violation()
    category = sanitize_text(request.args.get('category'), max_length=32)
    limit = sanitize_integer(request.args.get('limit', 20), min_val=1, max_val=100, default=20)
    offset = sanitize_integer(request.args.get('offset', 0), min_val=0, max_val=10000, default=0)

    records = list(_violation_history)
    if category:
        records = [r for r in records if r["category"].lower() == category.lower()]

    total_matching = len(records)
    paged = records[offset : offset + limit]

    return jsonify({
        "status": "success",
        "total_matching": total_matching,
        "limit": limit,
        "offset": offset,
        "records": paged,
        "available_categories": list(_violations.keys())
    })

@app.route('/api/simulate_emergency', methods=['POST'])
def simulate_emergency():
    global _last_emergency
    data = request.json or {}
    raw_lane = data.get('lane')
    lane = sanitize_text(raw_lane, max_length=16) if raw_lane else None
    if lane in LANES:
        _last_emergency = lane
        audit_logger.log_event("WARNING", "EMERGENCY_OVERRIDE_ACTIVATED", {"lane": lane})
        return jsonify({"status": "success", "message": f"Emergency vehicle simulated in {lane} lane."})
    else:
        _last_emergency = None
        audit_logger.log_event("INFO", "EMERGENCY_OVERRIDE_CLEARED", {})
        return jsonify({"status": "success", "message": "Emergency override cleared."})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "mode": "demo", "uptime_seconds": int(time.time() - _start_time)})

@app.route('/api/telemetry/summary', methods=['GET'])
def get_telemetry_summary():
    _maybe_log_violation()
    counts = _generate_lane_counts()
    junction = get_junction_config()
    congestion = _get_congestion(sum(counts.values()))
    summary = build_telemetry_summary(
        junction_config=junction,
        vehicle_counts=counts,
        tracked_total=_tracked_total,
        violations_summary=_violations,
        congestion_level=congestion,
        emergency_lane=_last_emergency,
        mode="demo"
    )
    return jsonify(summary)

@app.route('/api/driver_advice', methods=['GET'])
def get_driver_advice():
    # 1. Configurable Junction Identity & Coordinate Validation
    junction = get_junction_config()
    junction_name = junction["name"]
    junction_lat = junction["latitude"]
    junction_lon = junction["longitude"]
    junction_config_error = junction["configuration_error"]

    lane_counts = _generate_lane_counts()
    total = sum(lane_counts.values()) if isinstance(lane_counts, dict) else None
    signal_plan = _get_signal_plan(lane_counts, _last_emergency) if isinstance(lane_counts, dict) else {}
    congestion = _get_congestion(total) if total is not None else "UNAVAILABLE"

    # 2. Strict Corridor Validation (North, South, East, West case-insensitive)
    raw_corridor = request.args.get('corridor')

    if raw_corridor is not None and raw_corridor.strip() != "":
        clean_corridor = raw_corridor.strip()
        if len(clean_corridor) > 32:
            return jsonify({
                "status": "error",
                "message": "Corridor parameter exceeds maximum allowed length of 32 characters."
            }), 400
        matched = [c for c in LANES if c.lower() == clean_corridor.lower()]
        if not matched:
            return jsonify({
                "status": "error",
                "message": f"Invalid corridor '{clean_corridor}'. Must be one of: {', '.join(LANES)}."
            }), 400
        corridor = matched[0]
    else:
        corridor = _last_emergency or (max(lane_counts, key=lane_counts.get) if lane_counts else "North")

    # 3. GPS Coordinates Validation & Distance
    lat_param = request.args.get('lat')
    lon_param = request.args.get('lon')
    distance_km, distance_status = validate_coordinates(lat_param, lon_param, junction_lat, junction_lon)

    # 4. Extract metrics cleanly without silent zero substitution
    corridor_count = lane_counts.get(corridor) if isinstance(lane_counts, dict) and corridor in lane_counts else None
    green_times = signal_plan.get("green_times") if isinstance(signal_plan, dict) else {}
    corridor_green = green_times.get(corridor) if isinstance(green_times, dict) and corridor in green_times else None
    cycle_time = signal_plan.get("cycle_time") if isinstance(signal_plan, dict) else None

    return jsonify({
        "status": "success",
        "data_source": "demo_sim",
        "feed_description": "Render Free-Tier Simulation (Demonstration Data)",
        "junction": {
            "name": junction_name,
            "latitude": junction_lat,
            "longitude": junction_lon,
            "is_configurable": True,
            "configuration_error": junction_config_error
        },
        "approach": {
            "corridor": corridor,
            "visible_vehicle_count": corridor_count,
            "total_junction_vehicles": total,
            "assigned_green_time_sec": corridor_green,
            "cycle_time_sec": cycle_time,
            "congestion_level": congestion,
            "congestion_provenance": "synthetic_demo_rule"
        },
        "distance_telemetry": {
            "calculation_method": "Haversine Geodesic (Straight-Line)",
            "straight_line_distance_km": distance_km,
            "status": distance_status,
            "disclaimer": "Straight-line aerial distance only. Actual road driving distance will be longer due to road topology and flyover ramps."
        },
        "delay_telemetry": {
            "delay_status": "ESTIMATE_UNAVAILABLE",
            "estimated_delay_mins": None,
            "reason": "Queue clearance delay cannot be accurately calculated without upstream queue length and continuous arrival rates outside camera FOV."
        },
        "safety_guidelines": [
            f"Approaching {corridor} corridor. Maintain safe braking distance in stop-and-go queue.",
            "Merge early and avoid sudden lane switching near junction approach ramps."
        ],
        "corridor_status": {
            "monitored_corridors": LANES,
            "unmonitored_routes": "DATA_UNAVAILABLE"
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚦 BengaluruTrafficAI Demo Backend starting...")
    print(f"   Mode: DEMO (simulated AI outputs)")
    print(f"   Port: {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
