from flask import Flask, jsonify
from flask_cors import CORS
import cv2
import threading
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)

# Load YOLO model
model = YOLO("yolov8n.pt")

# Vehicle class IDs
VEHICLE_CLASSES = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}

# Global shared state
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
    "total_vehicles": 0
}

def get_active_lane(counts):
    return max(counts, key=counts.get)

def run_detection():
    cap = cv2.VideoCapture("ai/dataset/sample_traffic.mp4")
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
            if cls_id in VEHICLE_CLASSES and float(box.conf[0]) > 0.4:
                count += 1

        # Simulate 4 lane counts from total
        lane = lane_keys[frame_num % 4]
        traffic_state["vehicle_counts"][lane] = count
        traffic_state["total_vehicles"] = sum(traffic_state["vehicle_counts"].values())
        traffic_state["active_lane"] = get_active_lane(traffic_state["vehicle_counts"])
        frame_num += 1

    cap.release()

# Start detection in background thread
detection_thread = threading.Thread(target=run_detection, daemon=True)
detection_thread.start()

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(traffic_state)

@app.route('/api/lanes', methods=['GET'])
def get_lanes():
    return jsonify(traffic_state["vehicle_counts"])

if __name__ == '__main__':
    app.run(port=5000, debug=True, use_reloader=False)