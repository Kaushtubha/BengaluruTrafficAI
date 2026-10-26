import cv2
import time
from collections import defaultdict
from datetime import datetime

# Default heuristic scale: approximate pixel-to-meter ratio for uncalibrated perspective
# Note: Without camera matrix homography, this serves as an uncalibrated relative motion estimate.
PIXEL_TO_METER = 0.05
SPEED_LIMIT_KMPH = 40.0             # Junction advisory speed threshold
MAX_TRACK_AGE_SECONDS = 3.0         # Reset calculation if tracking drops for > 3 seconds
MAX_PLAUSIBLE_SPEED_KMPH = 180.0    # Upper bound to filter out single-frame tracking glitches
MAX_STORED_TRACKS = 250             # Prevent unbounded memory growth over long runs

track_times = defaultdict(list)     # {track_id: [(timestamp, cx, cy), ...]}
speed_violations = []
current_speeds = {}                # {track_id: speed_kmph}


def _prune_stale_tracks(current_time: float):
    """Prune stale tracking records to prevent memory leak."""
    if len(track_times) > MAX_STORED_TRACKS:
        stale_ids = [
            tid for tid, recs in track_times.items()
            if recs and (current_time - recs[-1][0] > MAX_TRACK_AGE_SECONDS)
        ]
        for tid in stale_ids:
            track_times.pop(tid, None)
            current_speeds.pop(tid, None)


def update_speed(track_id, cx, cy, timestamp=None):
    """
    Update position and timestamp for a tracked vehicle.

    Args:
        track_id: Unique identifier for the tracked object.
        cx (float): Center X coordinate.
        cy (float): Center Y coordinate.
        timestamp (float, optional): Monotonic or video frame timestamp in seconds.
            Defaults to time.monotonic() if None.
    """
    if track_id is None:
        return

    now = time.monotonic() if timestamp is None else float(timestamp)
    _prune_stale_tracks(now)

    records = track_times[track_id]
    # If the track was interrupted for longer than MAX_TRACK_AGE_SECONDS or time moved backward, reset
    if records and (now - records[-1][0] > MAX_TRACK_AGE_SECONDS or now < records[-1][0]):
        records.clear()

    records.append((now, float(cx), float(cy)))

    # Maintain a sliding window of recent observations (last 5 records)
    if len(records) > 5:
        records.pop(0)


def calculate_speed(track_id, pixel_scale=PIXEL_TO_METER):
    """
    Calculate estimated speed in km/h based on pixel movement over elapsed time.

    Args:
        track_id: Unique track ID.
        pixel_scale (float): Uncalibrated conversion factor from pixels to meters.

    Returns:
        float: Estimated speed in km/h (rounded to 1 decimal place), or 0.0 if insufficient data.
    """
    if track_id is None or track_id not in track_times:
        return 0.0

    records = track_times[track_id]
    if len(records) < 2:
        return 0.0

    t1, x1, y1 = records[0]
    t2, x2, y2 = records[-1]

    time_diff = t2 - t1  # seconds
    # Guard against zero, negative, or implausibly large time intervals
    if time_diff <= 0.0 or time_diff > MAX_TRACK_AGE_SECONDS:
        return 0.0

    # Euclidean pixel displacement
    pixel_dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    if pixel_dist <= 0.0:
        return 0.0

    # Convert to meters using heuristic scale
    meter_dist = pixel_dist * pixel_scale

    # Speed in m/s then km/h
    speed_ms = meter_dist / time_diff
    speed_kmph = speed_ms * 3.6

    # Cap implausible spikes caused by detection coordinate jitter / ID swaps
    speed_kmph = min(MAX_PLAUSIBLE_SPEED_KMPH, speed_kmph)

    return round(speed_kmph, 1)


def check_speed_violation(track_id, cx, cy, timestamp=None, speed_limit=SPEED_LIMIT_KMPH):
    """
    Check if a tracked vehicle's estimated speed exceeds the junction limit.

    Args:
        track_id: Track ID of the vehicle.
        cx (float): Center X position.
        cy (float): Center Y position.
        timestamp (float, optional): Timestamp in seconds.
        speed_limit (float): Speed threshold in km/h.

    Returns:
        tuple: (is_speeding: bool, violation_dict: Optional[dict], speed: float)
    """
    if track_id is None:
        return False, None, 0.0

    update_speed(track_id, cx, cy, timestamp=timestamp)
    speed = calculate_speed(track_id)
    current_speeds[track_id] = speed

    if speed > speed_limit:
        violation = {
            "type": "Speeding",
            "track_id": track_id,
            "speed": speed,
            "limit": speed_limit,
            "speed_type": "estimated_uncalibrated",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Deduplicate violations for the same vehicle
        existing_ids = {v["track_id"] for v in speed_violations if v.get("track_id") is not None}
        if track_id not in existing_ids:
            speed_violations.append(violation)
            try:
                print(f"🏎️ Speeding! Vehicle #{track_id}: ~{speed} km/h (est) at {violation['timestamp']}")
            except UnicodeEncodeError:
                print(f"[VIOLATION] Speeding: Vehicle #{track_id}: ~{speed} km/h (est) at {violation['timestamp']}")
        return True, violation, speed

    return False, None, speed


def draw_speed_labels(frame, boxes, track_ids):
    """Draw estimated speed on each vehicle bounding box."""
    for box, track_id in zip(boxes, track_ids):
        x1, y1, x2, y2 = map(int, box)
        speed = current_speeds.get(track_id, 0.0)
        color = (0, 0, 255) if speed > SPEED_LIMIT_KMPH else (0, 255, 0)
        cv2.putText(frame, f"~{speed} km/h est",
                    (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame


def get_speed_violations():
    return speed_violations


def get_speed_violation_count():
    return len(speed_violations)