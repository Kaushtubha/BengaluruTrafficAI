import cv2
from ultralytics import YOLO
import time

# Load YOLOv8 model (downloads automatically first time)
model = YOLO("yolov8n.pt")

# Vehicle class IDs in COCO dataset
VEHICLE_CLASSES = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}

def process_frame(frame):
    results = model(frame, verbose=False)[0]
    vehicle_count = 0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        if cls_id in VEHICLE_CLASSES and conf > 0.4:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = f"{VEHICLE_CLASSES[cls_id]} {conf:.2f}"
            vehicle_count += 1

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show vehicle count on screen
    cv2.putText(frame, f"Vehicles: {vehicle_count}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    return frame, vehicle_count

def run_detection(source=0):
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print("Error: Cannot open video source")
        return

    print("Detection started... Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame, count = process_frame(frame)
        cv2.imshow("BengaluruTrafficAI - Vehicle Detection", processed_frame)
        print(f"Vehicles detected: {count}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Use 0 for webcam, or give video file path
    run_detection(source="ai/dataset/sample_traffic.mp4")