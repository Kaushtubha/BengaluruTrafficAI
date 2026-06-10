import cv2
from collections import defaultdict
from datetime import datetime

# Track vehicle movement history
track_positions = defaultdict(list)
wrong_side_violations = []

# Define expected movement direction per zone
# Vehicles in left half should move downward (South)
# Vehicles in right half should move upward (North)
FRAME_W = 1280
FRAME_H = 720

def update_track(track_id, cx, cy):
    """Store last 10 positions for each vehicle"""
    track_positions[track_id].append((cx, cy))
    if len(track_positions[track_id]) > 10:
        track_positions[track_id].pop(0)

def check_wrong_side(track_id, cx, cy, frame_w=FRAME_W, frame_h=FRAME_H):
    """
    Left lane (x < frame_w//2): vehicles should move downward (cy increasing)
    Right lane (x > frame_w//2): vehicles should move upward (cy decreasing)
    """
    positions = track_positions[track_id]
    if len(positions) < 5:
        return False, None  # Not enough data yet

    # Calculate movement direction
    first_y = positions[0][1]
    last_y = positions[-1][1]
    movement = last_y - first_y  # Positive = moving down, Negative = moving up

    is_left_lane = cx < frame_w // 2
    is_wrong = False

    # Left lane should move down (positive movement)
    if is_left_lane and movement < -20:
        is_wrong = True
    # Right lane should move up (negative movement)
    elif not is_left_lane and movement > 20:
        is_wrong = True

    if is_wrong:
        violation = {
            "type": "Wrong Side Driving",
            "track_id": track_id,
            "position": (cx, cy),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Avoid duplicate violations for same vehicle
        existing_ids = [v["track_id"] for v in wrong_side_violations]
        if track_id not in existing_ids:
            wrong_side_violations.append(violation)
            print(f"⚠️ Wrong Side! Vehicle #{track_id} at {violation['timestamp']}")
        return True, violation

    return False, None

def draw_lane_directions(frame):
    """Draw expected direction arrows on frame"""
    h, w = frame.shape[:2]
    # Left lane - down arrow
    cv2.arrowedLine(frame, (w//4, 50), (w//4, 150), (0, 255, 255), 2)
    cv2.putText(frame, "Expected", (w//4 - 40, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    # Right lane - up arrow
    cv2.arrowedLine(frame, (3*w//4, 150), (3*w//4, 50), (0, 255, 255), 2)
    cv2.putText(frame, "Expected", (3*w//4 - 40, 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
    return frame

def get_wrong_side_violations():
    return wrong_side_violations

def get_wrong_side_count():
    return len(wrong_side_violations)