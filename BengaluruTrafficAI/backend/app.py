import sys
sys.path.insert(0, '../ai')
from violation_detector import check_red_light_violation, get_violations, get_violation_count
from wrong_side_detector import check_wrong_side, update_track
from speed_estimator import check_speed_violation
from snapshot import save_violation_snapshot
from db_logger import log_violation, log_traffic_stats
from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import threading
from ultralytics import YOLO
from signal_service import get_signal_plan

app = Flask(__name__)
CORS(app)

model = YOLO("yolov8n.pt")
VEHICLE_CLASSES = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}

traffic_state = {
    "status": "online",
    "junction": "Silk Board, Bengaluru",
    "active_lane": "North",
    "violation_count": 0,
    "recent_violations": [],
    "vehicle_counts": {"North": 0, "South": 0, "East": 0, "West": 0},
    "total_vehicles": 0,
    "signal_plan": {"green_times": {}, "priority_lane": "", "cycle_time": 0}
}

def run_detection():
    # Using webcam (0) instead of hardcoded path
    cap = cv2.VideoCapture(0)
    lane_keys = ["North", "South", "East", "West"]
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        results = model(frame, verbose=False)[0]
        count = sum(1 for box in results.boxes
                    if int(box.cls[0]) in VEHICLE_CLASSES and float(box.conf[0]) > 0.4)
        lane = lane_keys[frame_num % 4]
        traffic_state["vehicle_counts"][lane] = count
        traffic_state["total_vehicles"] = sum(traffic_state["vehicle_counts"].values())
        traffic_state["active_lane"] = max(traffic_state["vehicle_counts"], key=traffic_state["vehicle_counts"].get)
        traffic_state["signal_plan"] = get_signal_plan(traffic_state["vehicle_counts"])
        frame_num += 1 
        traffic_state["violation_count"] = get_violation_count()
        traffic_state["recent_violations"] = [
            {"type": v["type"], "timestamp": v["timestamp"]}
            for v in get_violations()[-5:]
        ]
        log_traffic_stats(traffic_state["vehicle_counts"], "MEDIUM")
    cap.release()

threading.Thread(target=run_detection, daemon=True).start()

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(traffic_state)

@app.route('/api/lanes', methods=['GET'])
def get_lanes():
    return jsonify(traffic_state["vehicle_counts"])

@app.route('/api/signal', methods=['GET'])
def get_signal():
    return jsonify(traffic_state["signal_plan"])

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)