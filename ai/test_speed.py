import time
from speed_estimator import update_speed, calculate_speed, check_speed_violation

# Simulate a fast vehicle (speeding)
print("Testing speeding vehicle...")
for i in range(5):
    check_speed_violation(track_id=1, cx=100 + i*50, cy=100 + i*50)
    time.sleep(0.1)

speed = calculate_speed(track_id=1)
print(f"Vehicle #1 speed: {speed} km/h")

# Simulate a slow vehicle (normal)
print("\nTesting normal vehicle...")
for i in range(5):
    check_speed_violation(track_id=2, cx=100 + i*5, cy=100 + i*5)
    time.sleep(0.3)

speed2 = calculate_speed(track_id=2)
print(f"Vehicle #2 speed: {speed2} km/h")