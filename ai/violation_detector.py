import cv2
import numpy as np
from datetime import datetime
import os

# Stop line position
STOP_LINE_Y = 300
STOP_LINE_X1 = 0
STOP_LINE_X2 = 1280

violations = []

def check_red_light_violation(box, signal_state="RED", track_id=None):
    x1, y1, x2, y2 = box
    vehicle_bottom = y2

    if signal_state == "RED" and vehicle_bottom > STOP_LINE_Y:
        violation = {
            "type": "Red Light Jump",
            "track_id": track_id,
            "position": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "line_y": STOP_LINE_Y
        }
        violations.append(violation)
        print(f"🚨 Red Light Violation! Track ID: {track_id} at {violation['timestamp']}")
        return True, violation
    return False, None

def draw_stop_line(frame, signal_state="RED"):
    color = (0, 0, 255) if signal_state == "RED" else (0, 255, 0)
    cv2.line(frame, (STOP_LINE_X1, STOP_LINE_Y),
             (STOP_LINE_X2, STOP_LINE_Y), color, 3)
    cv2.putText(frame, f"STOP LINE [{signal_state}]",
                (10, STOP_LINE_Y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return frame

def draw_violation_overlay(frame):
    recent = violations[-3:] if len(violations) >= 3 else violations
    for i, v in enumerate(reversed(recent)):
        text = f"🚨 {v['type']} at {v['timestamp']}"
        cv2.putText(frame, text,
                    (10, frame.shape[0] - 20 - (i * 28)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
    return frame

def get_violations():
    return violations

def get_violation_count():
    return len(violations)