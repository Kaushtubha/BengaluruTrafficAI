import cv2

# Red Light Stop Line coordinates (screen pe virtual line)
# Format: (x1, y1, x2, y2) - horizontal line
STOP_LINE_Y = 300  # Video frame mein line ki height
STOP_LINE_X1 = 0
STOP_LINE_X2 = 1280

violations = []

def check_violation(box, signal_state="RED"):
    """
    box: (x1, y1, x2, y2) - vehicle bounding box
    signal_state: RED ya GREEN
    Returns: True agar violation hai
    """
    x1, y1, x2, y2 = box
    vehicle_bottom = y2  # Vehicle ka bottom edge

    # Agar signal RED hai aur vehicle stop line cross kar rahi hai
    if signal_state == "RED" and vehicle_bottom > STOP_LINE_Y:
        violation = {
            "type": "Red Light Jump",
            "position": (x1, y1, x2, y2),
            "line_y": STOP_LINE_Y
        }
        violations.append(violation)
        print(f"🚨 VIOLATION DETECTED! Red Light Jump at position {x1},{y1}")
        return True
    return False

def draw_stop_line(frame, signal_state="RED"):
    """Frame pe stop line draw karo"""
    color = (0, 0, 255) if signal_state == "RED" else (0, 255, 0)
    cv2.line(frame, (STOP_LINE_X1, STOP_LINE_Y), (STOP_LINE_X2, STOP_LINE_Y), color, 3)
    cv2.putText(frame, f"STOP LINE [{signal_state}]", (10, STOP_LINE_Y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return frame

def get_violations():
    return violations

def get_violation_count():
    return len(violations)

# Test
if __name__ == "__main__":
    # Simulate kuch test boxes
    test_boxes = [
        (100, 250, 200, 280),  # Line se upar - no violation
        (300, 290, 400, 320),  # Line cross kar raha - VIOLATION!
        (500, 200, 600, 290),  # Line se upar - no violation
    ]

    print("Testing Violation Detector...")
    for box in test_boxes:
        result = check_violation(box, signal_state="RED")
        print(f"Box {box}: {'VIOLATION!' if result else 'OK'}")

    print(f"\nTotal Violations: {get_violation_count()}")