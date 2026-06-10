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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚦 BengaluruTrafficAI Demo Backend starting...")
    print(f"   Mode: DEMO (simulated AI outputs)")
    print(f"   Port: {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
