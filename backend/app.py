import sys
import os
import cv2
import threading

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

traffic_state = {
    "status": "online",
    "junction": "Silk Board, Bengaluru",
    "active_lane": "North",

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

            lane = get_lane(center_x, frame_width)

            lane_counts[lane] += 1

            check_red_light_violation(
                (x1, y1, x2, y2),
                signal_state="RED",
                track_id=track_id
            )

        traffic_state["vehicle_counts"] = lane_counts

        traffic_state["total_vehicles"] = sum(
            lane_counts.values()
        )

        traffic_state["tracked_vehicles"] = len(
            tracked_vehicle_ids
        )

        traffic_state["active_lane"] = max(
            lane_counts,
            key=lane_counts.get
        )

        traffic_state["signal_plan"] = get_signal_plan(
            lane_counts
        )

        traffic_state["violations"] = get_violation_count()

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
        "total_violations":
        traffic_state["violations"]
    })


if __name__ == '__main__':

    app.run(
        port=5000,
        debug=True,
        use_reloader=False
    )