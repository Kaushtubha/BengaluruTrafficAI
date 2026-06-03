import cv2
import numpy as np
from snapshot import save_violation_snapshot, get_all_snapshots

# Create a dummy traffic frame
frame = np.zeros((720, 1280, 3), dtype=np.uint8)

# Draw a fake vehicle (white rectangle)
cv2.rectangle(frame, (100, 100), (300, 300), (255, 255, 255), -1)
cv2.putText(frame, "CAR", (150, 200),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# Save violation snapshot
filename = save_violation_snapshot(
    frame=frame,
    box=(100, 100, 300, 300),
    violation_type="Red_Light_Jump",
    track_id=5
)

print("Snapshot saved:", filename)
print("All snapshots:", get_all_snapshots())