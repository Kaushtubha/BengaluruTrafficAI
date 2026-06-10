from datetime import datetime

# Simulated helmet violations list
helmet_violations = []

def check_helmet_violation(box, vehicle_type, track_id=None):
    """
    Simulate helmet / no-helmet detection for motorcycle riders.
    Returns: (is_violation, violation_dict)
    """
    if vehicle_type == "Motorcycle":
        # Simulate ~15% violation rate deterministically using track_id
        if track_id and track_id % 7 == 0:
            violation = {
                "type": "No Helmet",
                "track_id": track_id,
                "position": {"x1": box[0], "y1": box[1], "x2": box[2], "y2": box[3]},
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            # Avoid duplications
            recent_ids = [v["track_id"] for v in helmet_violations[-10:]]
            if track_id not in recent_ids:
                helmet_violations.append(violation)
                print(f"🪖 No Helmet! Motorcycle rider #{track_id} at {violation['timestamp']}")
            return True, violation

    return False, None

def get_helmet_violations():
    return helmet_violations

def get_helmet_violation_count():
    return len(helmet_violations)
