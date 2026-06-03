import cv2
import os
from datetime import datetime

# Create snapshots folder
SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def save_snapshot(frame, violation_type, track_id=None):
    """
    Save a cropped snapshot of violation
    Returns: filename of saved snapshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    track_str = f"_id{track_id}" if track_id else ""
    filename = f"{violation_type.replace(' ', '_')}{track_str}_{timestamp}.jpg"
    filepath = os.path.join(SNAPSHOT_DIR, filename)

    cv2.imwrite(filepath, frame)
    print(f"📸 Snapshot saved: {filepath}")
    return filename

def save_violation_snapshot(frame, box, violation_type, track_id=None):
    """
    Crop vehicle region and save with red border
    """
    x1, y1, x2, y2 = map(int, box)
    h, w = frame.shape[:2]

    # Add padding around vehicle
    pad = 20
    x1 = max(0, x1 - pad)
    y1 = max(0, y1 - pad)
    x2 = min(w, x2 + pad)
    y2 = min(h, y2 + pad)

    # Crop vehicle region
    crop = frame[y1:y2, x1:x2].copy()

    # Draw red border on crop
    cv2.rectangle(crop, (0, 0), (crop.shape[1]-1, crop.shape[0]-1),
                  (0, 0, 255), 3)

    # Add violation text on crop
    cv2.putText(crop, violation_type, (5, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return save_snapshot(crop, violation_type, track_id)

def get_all_snapshots():
    """Return list of all snapshot filenames"""
    if not os.path.exists(SNAPSHOT_DIR):
        return []
    return os.listdir(SNAPSHOT_DIR)
