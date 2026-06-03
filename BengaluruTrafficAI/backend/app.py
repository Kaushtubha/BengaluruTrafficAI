from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import threading
import sys
import os

# Fix paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'ai'))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))

from ultralytics import YOLO
from signal_service import get_signal_plan
from violation_detector import check_violation, get_violation_count

app = Flask(__name__)
CORS(app)

model = YOLO(os.path.join(BASE_DIR, "yolov8n.pt"))
VEHICLE_CLASSES = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}

traffic_state = {
    "status": "online",
    "junction": "Silk Board, Bengaluru",
    "active_lane": "North",
    "vehicle_counts": {"North": 0, "South": 0, "East": 0, "West": 0},
    "total_vehicles": 0,
    "violations": 0,
    "signal_plan": {"green_times": {}, "priority_lane": "", "cycle_time": 0}
}

def run_detection():
    video_path = os.path.join(BASE_DIR, "ai", "dataset", "sample_traffic.mp4")
    cap = cv2.VideoCapture(video_path)
    lane_keys = ["North", "South", "East", "West"]
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        results = model(frame, verbose=False)[0]
        count = 0
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if cls_id in VEHICLE_CLASSES and conf > 0.4:
                count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                check_violation((x1, y1, x2, y2), signal_state="RED")
        lane = lane_keys[frame_num % 4]
        traffic_state["vehicle_counts"][lane] = count
        traffic_state["total_vehicles"] = sum(traffic_state["vehicle_counts"].values())
        traffic_state["active_lane"] = max(traffic_state["vehicle_counts"], key=traffic_state["vehicle_counts"].get)
        traffic_state["signal_plan"] = get_signal_plan(traffic_state["vehicle_counts"])
        traffic_state["violations"] = get_violation_count()
        frame_num += 1
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

@app.route('/api/violations', methods=['GET'])
def get_violations():
    return jsonify({"total_violations": traffic_state["violations"]})

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)