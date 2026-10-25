"""
BengaluruTrafficAI - Lightweight Demo Backend
Simulates real AI outputs for free-tier deployment (Render 512MB).
Full YOLOv8 version runs locally: python backend/app.py
"""
import os
import random
import math
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Simulation Config ────────────────────────────────────────────────
LANES = ["North", "South", "East", "West"]
JUNCTIONS = "Silk Board, Bengaluru"

# Internal sim state
_start_time = time.time()
_tracked_total = 0
_violations = {"red_light": 0, "wrong_side": 0, "speeding": 0, "no_helmet": 0}
_last_emergency = None

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
    if total < 20:
        return "Low"
    elif total < 45:
        return "Medium"
    return "High"

def _get_signal_plan(lane_counts, emergency_lane=None):
    total = sum(lane_counts.values()) or 1
    MIN_GREEN, MAX_GREEN = 10, 60
    green_times = {}
    for lane, count in lane_counts.items():
        proportion = count / total
        green_times[lane] = round(MIN_GREEN + proportion * (MAX_GREEN - MIN_GREEN), 1)

    priority = emergency_lane or max(lane_counts, key=lane_counts.get)
    if emergency_lane:
        green_times[emergency_lane] = MAX_GREEN

    return {
        "green_times": green_times,
        "priority_lane": priority,
        "cycle_time": round(sum(green_times.values()), 1)
    }

def _maybe_log_violation():
    """Probabilistically add violations to simulate live detection."""
    factor = _time_factor()
    if random.random() < 0.03 * factor:
        _violations["red_light"] += 1
    if random.random() < 0.015 * factor:
        _violations["wrong_side"] += 1
    if random.random() < 0.04 * factor:
        _violations["speeding"] += 1
    if random.random() < 0.02 * factor:
        _violations["no_helmet"] += 1

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

@app.route('/api/simulate_emergency', methods=['POST'])
def simulate_emergency():
    global _last_emergency
    data = request.json or {}
    lane = data.get('lane')
    if lane in LANES:
        _last_emergency = lane
        return jsonify({"status": "success", "message": f"Emergency vehicle simulated in {lane} lane."})
    else:
        _last_emergency = None
        return jsonify({"status": "success", "message": "Emergency override cleared."})

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "mode": "demo", "uptime_seconds": int(time.time() - _start_time)})

def _calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


@app.route('/api/driver_advice', methods=['GET'])
def get_driver_advice():
    # 1. Configurable Junction Identity & Coordinate Validation
    junction_name = os.environ.get("JUNCTION_NAME", JUNCTIONS)
    junction_lat_env = os.environ.get("JUNCTION_LAT")
    junction_lon_env = os.environ.get("JUNCTION_LON")

    junction_config_error = None
    if junction_lat_env is not None or junction_lon_env is not None:
        try:
            j_lat_str = str(junction_lat_env).strip()
            j_lon_str = str(junction_lon_env).strip()
            if len(j_lat_str) > 32 or len(j_lon_str) > 32:
                junction_config_error = "Configured junction coordinates exceed maximum allowed length of 32 characters"
                junction_lat, junction_lon = None, None
            else:
                j_lat = float(j_lat_str)
                j_lon = float(j_lon_str)
                if math.isnan(j_lat) or math.isnan(j_lon) or math.isinf(j_lat) or math.isinf(j_lon):
                    junction_config_error = "Configured junction coordinates have invalid numeric format"
                    junction_lat, junction_lon = None, None
                elif not (-90.0 <= j_lat <= 90.0 and -180.0 <= j_lon <= 180.0):
                    junction_config_error = f"Configured junction coordinates out of range (-90..90, -180..180): lat={j_lat}, lon={j_lon}"
                    junction_lat, junction_lon = None, None
                else:
                    junction_lat, junction_lon = j_lat, j_lon
        except (ValueError, TypeError):
            junction_config_error = "Configured junction coordinates have invalid numeric format"
            junction_lat, junction_lon = None, None
    else:
        junction_lat, junction_lon = 12.9176, 77.6238

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
    distance_km = None

    if lat_param is not None and lon_param is None:
        distance_status = "INCOMPLETE_COORDINATES_MISSING_LON"
    elif lat_param is None and lon_param is not None:
        distance_status = "INCOMPLETE_COORDINATES_MISSING_LAT"
    elif lat_param is not None and lon_param is not None:
        lat_str = str(lat_param).strip()
        lon_str = str(lon_param).strip()
        if len(lat_str) > 32 or len(lon_str) > 32:
            distance_status = "INVALID_COORDINATE_FORMAT"
        else:
            try:
                driver_lat = float(lat_str)
                driver_lon = float(lon_str)
                if math.isnan(driver_lat) or math.isnan(driver_lon) or math.isinf(driver_lat) or math.isinf(driver_lon):
                    distance_status = "INVALID_COORDINATE_FORMAT"
                elif not (-90.0 <= driver_lat <= 90.0 and -180.0 <= driver_lon <= 180.0):
                    distance_status = "COORDINATES_OUT_OF_RANGE"
                elif junction_lat is None or junction_lon is None:
                    distance_status = "JUNCTION_COORDINATES_CONFIG_ERROR"
                else:
                    distance_km = _calculate_haversine(driver_lat, driver_lon, junction_lat, junction_lon)
                    distance_status = "CALCULATED"
            except (ValueError, TypeError):
                distance_status = "INVALID_COORDINATE_FORMAT"
    else:
        distance_status = "COORDINATES_NOT_PROVIDED"

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
            "congestion_level": congestion
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
