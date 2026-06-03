import cv2
import time
from collections import defaultdict
from datetime import datetime

# Real world calibration
# Assume 1 pixel = 0.05 meters (adjust based on camera height)
PIXEL_TO_METER = 0.05
SPEED_LIMIT_KMPH = 40  # Speed limit for the junction

track_times = defaultdict(list)   # {track_id: [(time, cx, cy), ...]}
speed_violations = []
current_speeds = {}  # {track_id: speed_kmph}

def update_speed(track_id, cx, cy):
    """Update position and time for track"""
    now = time.time()
    track_times[track_id].append((now, cx, cy))

    # Keep only last 5 records
    if len(track_times[track_id]) > 5:
        track_times[track_id].pop(0)

def calculate_speed(track_id):
    """Calculate speed in km/h"""
    records = track_times[track_id]
    if len(records) < 2:
        return 0

    t1, x1, y1 = records[0]
    t2, x2, y2 = records[-1]

    time_diff = t2 - t1  # seconds
    if time_diff == 0:
        return 0

    # Pixel distance
    pixel_dist = ((x2-x1)**2 + (y2-y1)**2) ** 0.5

    # Convert to meters
    meter_dist = pixel_dist * PIXEL_TO_METER

    # Speed in m/s then km/h
    speed_ms = meter_dist / time_diff
    speed_kmph = speed_ms * 3.6

    return round(speed_kmph, 1)

def check_speed_violation(track_id, cx, cy):
    """Check if vehicle exceeds speed limit"""
    update_speed(track_id, cx, cy)
    speed = calculate_speed(track_id)
    current_speeds[track_id] = speed

    if speed > SPEED_LIMIT_KMPH:
        violation = {
            "type": "Speeding",
            "track_id": track_id,
            "speed": speed,
            "limit": SPEED_LIMIT_KMPH,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Avoid flooding with same vehicle
        recent_ids = [v["track_id"] for v in speed_violations[-10:]]
        if track_id not in recent_ids:
            speed_violations.append(violation)
            print(f"🏎️ Speeding! Vehicle #{track_id}: {speed} km/h at {violation['timestamp']}")
        return True, violation, speed

    return False, None, speed

def draw_speed_labels(frame, boxes, track_ids):
    """Draw speed on each vehicle"""
    for box, track_id in zip(boxes, track_ids):
        x1, y1, x2, y2 = map(int, box)
        speed = current_speeds.get(track_id, 0)
        color = (0, 0, 255) if speed > SPEED_LIMIT_KMPH else (0, 255, 0)
        cv2.putText(frame, f"{speed} km/h",
                    (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

def get_speed_violations():
    return speed_violations

def get_speed_violation_count():
    return len(speed_violations)