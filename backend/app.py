import sys
import os
import cv2
import threading
from datetime import datetime

from flask import Flask, jsonify
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
from db_logger import log_violation, log_traffic_stats
from congestion_predictor import predict_congestion
from tracker_manager import tracker
from lane_manager import get_lane

app = Flask(__name__)
CORS(app)

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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )