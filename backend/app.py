import sys
import os
import cv2
import threading
import math
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(BASE_DIR, 'ai'))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from signal_service import get_signal_plan
from violation_detector import (
    check_red_light_violation,
    get_violation_count
)
from wrong_side_detector import (
    check_wrong_side,
    get_wrong_side_count
)
from speed_estimator import (
    check_speed_violation,
    get_speed_violation_count
)
from helmet_detector import (
    check_helmet_violation,
    get_helmet_violation_count
)
from db_logger import log_violation, log_traffic_stats, get_violations_from_db
from congestion_predictor import predict_congestion
from tracker_manager import tracker
from lane_manager import get_lane
from junction_config import get_junction_config, validate_coordinates
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

model = YOLO(os.path.join(BASE_DIR, "yolov8n.pt"))

VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

tracked_vehicle_ids = set()
simulated_emergency_lane = None

traffic_state = {
    "status": "online",
    "junction": "Silk Board, Bengaluru",
    "active_lane": "North",
    "congestion_level": "Low",
    "congestion_provenance": "heuristic_rule_estimate",
    "is_synthetic_congestion_model": True,

    "vehicle_counts": {
        "North": 0,
        "South": 0,
        "East": 0,
        "West": 0
    },

    "total_vehicles": 0,
    "tracked_vehicles": 0,
    "violations": 0,

    "signal_plan": {
        "green_times": {},
        "priority_lane": "",
        "cycle_time": 0
    }
}


def run_detection():
    video_path = os.path.join(
        BASE_DIR,
        "ai",
        "dataset",
        "sample_traffic.mp4"
    )

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Video could not be opened")
        return

    frame_counter = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        results = model(frame, verbose=False)[0]
        detections = []
        frame_height, frame_width = frame.shape[:2]

        lane_counts = {
            "North": 0,
            "South": 0,
            "East": 0,
            "West": 0
        }

        emergency_lanes = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            if cls_id in VEHICLE_CLASSES and conf > 0.4:
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                detections.append(
                    (
                        [x1, y1, x2 - x1, y2 - y1],
                        conf,
                        VEHICLE_CLASSES[cls_id]
                    )
                )

        tracks = tracker.update_tracks(
            detections,
            frame=frame
        )

        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            tracked_vehicle_ids.add(track_id)

            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            lane = get_lane(center_x, frame_width)
            lane_counts[lane] += 1

            # 1. Red Light jumps
            is_red_violation, red_v = check_red_light_violation(
                (x1, y1, x2, y2),
                signal_state="RED",
                track_id=track_id
            )
            if is_red_violation:
                log_violation(red_v)

            # 2. Wrong side driving checks
            is_wrong, ws_v = check_wrong_side(
                track_id, 
                center_x, 
                center_y, 
                frame_width, 
                frame_height
            )
            if is_wrong:
                log_violation(ws_v)

            # 3. Speed violations checks
            is_speeding, speed_v, speed = check_speed_violation(
                track_id, 
                center_x, 
                center_y
            )
            if is_speeding:
                log_violation(speed_v)

            # 4. Helmet violation checks on motorcycles
            is_helmet_violation, helmet_v = check_helmet_violation(
                (x1, y1, x2, y2),
                track.label,
                track_id=track_id
            )
            if is_helmet_violation:
                log_violation(helmet_v)

            # 5. Emergency priority trigger simulation (e.g. tracks % 22 == 0 represent Ambulances)
            if track_id > 0 and track_id % 22 == 0:
                if lane not in emergency_lanes:
                    emergency_lanes.append(lane)

        # 6. Simulated Emergency Overrides from Frontend
        global simulated_emergency_lane
        if simulated_emergency_lane:
            if simulated_emergency_lane not in emergency_lanes:
                emergency_lanes.append(simulated_emergency_lane)

        # Update stats
        traffic_state["vehicle_counts"] = lane_counts
        traffic_state["total_vehicles"] = sum(lane_counts.values())
        traffic_state["tracked_vehicles"] = len(tracked_vehicle_ids)
        
        # Calculate active lane
        active_lane = max(lane_counts, key=lane_counts.get)
        traffic_state["active_lane"] = active_lane
        active_lane_count = lane_counts[active_lane]

        # 6. Predict Congestion with Random Forest Classifier
        hour = datetime.now().hour
        congestion_level = predict_congestion(
            hour, 
            traffic_state["total_vehicles"], 
            active_lane_count
        )
        traffic_state["congestion_level"] = congestion_level
        traffic_state["congestion_provenance"] = "heuristic_rule_estimate"
        traffic_state["is_synthetic_congestion_model"] = True

        # 7. Calculate Adaptive Signal Plan with Emergency priorities overrides
        traffic_state["signal_plan"] = get_signal_plan(
            lane_counts,
            emergency_lanes=emergency_lanes
        )

        # Calculate combined violations
        traffic_state["violations"] = (
            get_violation_count() + 
            get_speed_violation_count() + 
            get_wrong_side_count() + 
            get_helmet_violation_count()
        )

        # 8. MongoDB log traffic stats every 60 frames (~2s)
        frame_counter += 1
        if frame_counter % 60 == 0:
            log_traffic_stats(lane_counts, congestion_level)

    cap.release()


threading.Thread(
    target=run_detection,
    daemon=True
).start()


@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(traffic_state)


@app.route('/api/lanes', methods=['GET'])
def get_lanes():
    return jsonify(
        traffic_state["vehicle_counts"]
    )


@app.route('/api/signal', methods=['GET'])
def get_signal():
    return jsonify(
        traffic_state["signal_plan"]
    )


@app.route('/api/violations', methods=['GET'])
def get_violations():
    return jsonify({
        "total_violations": traffic_state["violations"],
        "red_light": get_violation_count(),
        "wrong_side": get_wrong_side_count(),
        "speeding": get_speed_violation_count(),
        "no_helmet": get_helmet_violation_count()
    })


@app.route('/api/violations/history', methods=['GET'])
def get_violation_history():
    category = sanitize_text(request.args.get('category'), max_length=32)
    limit = sanitize_integer(request.args.get('limit', 20), min_val=1, max_val=100, default=20)
    offset = sanitize_integer(request.args.get('offset', 0), min_val=0, max_val=10000, default=0)

    db_records = get_violations_from_db(limit=limit, category=category if category else None, offset=offset)

    return jsonify({
        "status": "success",
        "total_matching": len(db_records),
        "limit": limit,
        "offset": offset,
        "records": db_records,
        "available_categories": ["red_light", "wrong_side", "speeding", "no_helmet"]
    })


@app.route('/api/simulate_emergency', methods=['POST'])
def simulate_emergency():
    global simulated_emergency_lane
    from flask import request
    data = request.json or {}
    lane = data.get('lane')
    if lane in ["North", "South", "East", "West"]:
        simulated_emergency_lane = lane
        return jsonify({"status": "success", "message": f"Simulated emergency vehicle in {lane} lane."})
    else:
        simulated_emergency_lane = None
        return jsonify({"status": "success", "message": "Simulated emergency overrides cleared."})


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "mode": "live_cv"})


@app.route('/api/telemetry/summary', methods=['GET'])
def get_telemetry_summary():
    junction = get_junction_config()
    summary = build_telemetry_summary(
        junction_config=junction,
        vehicle_counts=traffic_state.get("vehicle_counts", {}),
        tracked_total=traffic_state.get("tracked_vehicles", 0),
        violations_summary={
            "red_light": get_violation_count(),
            "wrong_side": get_wrong_side_count(),
            "speeding": get_speed_violation_count(),
            "no_helmet": get_helmet_violation_count(),
        },
        congestion_level=traffic_state.get("congestion_level", "Low"),
        emergency_lane=traffic_state.get("emergency_lane"),
        mode="live_cv"
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

    # 2. Strict Corridor Validation (North, South, East, West case-insensitive)
    raw_corridor = request.args.get('corridor')
    valid_corridors = ["North", "South", "East", "West"]

    if raw_corridor is not None and raw_corridor.strip() != "":
        clean_corridor = raw_corridor.strip()
        if len(clean_corridor) > 32:
            return jsonify({
                "status": "error",
                "message": "Corridor parameter exceeds maximum allowed length of 32 characters."
            }), 400
        matched = [c for c in valid_corridors if c.lower() == clean_corridor.lower()]
        if not matched:
            return jsonify({
                "status": "error",
                "message": f"Invalid corridor '{clean_corridor}'. Must be one of: {', '.join(valid_corridors)}."
            }), 400
        corridor = matched[0]
    else:
        active = traffic_state.get("active_lane")
        corridor = active if active in valid_corridors else "North"

    # 3. GPS Coordinates Validation & Distance
    lat_param = request.args.get('lat')
    lon_param = request.args.get('lon')
    distance_km, distance_status = validate_coordinates(lat_param, lon_param, junction_lat, junction_lon)

    # 4. Check Genuine Metric Availability (No silent zero substitution)
    vehicle_counts = traffic_state.get("vehicle_counts")
    corridor_count = vehicle_counts.get(corridor) if isinstance(vehicle_counts, dict) and corridor in vehicle_counts else None

    total_vehicles = traffic_state.get("total_vehicles")
    if not isinstance(total_vehicles, (int, float)):
        total_vehicles = None

    signal_plan = traffic_state.get("signal_plan")
    if isinstance(signal_plan, dict):
        green_times = signal_plan.get("green_times")
        corridor_green = green_times.get(corridor) if isinstance(green_times, dict) and corridor in green_times else None
        cycle_time = signal_plan.get("cycle_time")
        if not isinstance(cycle_time, (int, float)):
            cycle_time = None
    else:
        corridor_green = None
        cycle_time = None

    congestion_level = traffic_state.get("congestion_level")
    if congestion_level not in ["Low", "Medium", "High"]:
        congestion_level = "UNAVAILABLE"

    return jsonify({
        "status": "success",
        "data_source": "live_cv",
        "feed_description": "Local Computer Vision Inference (Sample Video — Generic Urban Roadway)",
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
            "total_junction_vehicles": total_vehicles,
            "assigned_green_time_sec": corridor_green,
            "cycle_time_sec": cycle_time,
            "congestion_level": congestion_level,
            "congestion_provenance": "heuristic_rule_estimate"
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
            "monitored_corridors": valid_corridors,
            "unmonitored_routes": "DATA_UNAVAILABLE"
        }
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )