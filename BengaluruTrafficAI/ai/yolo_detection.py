import cv2
from ultralytics import YOLO

class TrafficDetector:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)
        self.target_classes = [2, 3, 5, 7] # car, motorcycle, bus, truck

    def process_frame(self, frame):
        results = self.model(frame, classes=self.target_classes, verbose=False)
        return [{"bbox": map(int, box.xyxy[0]), "conf": float(box.conf[0]), "cls": int(box.cls[0])} for r in results for box in r.boxes]

if __name__ == "__main__":
    print("AI Module Ready.")