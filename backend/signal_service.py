# Adaptive Traffic Signal Timing Algorithm
# Member 2 ka kaam - Signal Optimization

MIN_GREEN = 10   # seconds
MAX_GREEN = 60   # seconds
BASE_GREEN = 20  # seconds

def calculate_green_time(vehicle_counts: dict) -> dict:
    """
    Input: vehicle counts for 4 lanes
    Output: green light duration for each lane
    """
    total = sum(vehicle_counts.values())
    green_times = {}

    if total == 0:
        # Equal time agar koi vehicle nahi
        for lane in vehicle_counts:
            green_times[lane] = BASE_GREEN
        return green_times

    for lane, count in vehicle_counts.items():
        # Proportion ke hisaab se time calculate karo
        proportion = count / total
        green_time = MIN_GREEN + (proportion * (MAX_GREEN - MIN_GREEN))
        green_times[lane] = round(green_time, 1)

    return green_times

def get_priority_lane(vehicle_counts: dict) -> str:
    """Sabse zyada vehicles wali lane ko priority do"""
    return max(vehicle_counts, key=vehicle_counts.get)

def get_signal_plan(vehicle_counts: dict, emergency_lanes: list = None) -> dict:
    """Complete signal plan banao, priority to emergency vehicles"""
    green_times = calculate_green_time(vehicle_counts)
    priority = get_priority_lane(vehicle_counts)

    if emergency_lanes:
        # Emergency lane gets priority override
        priority = emergency_lanes[0]
        # Give priority lane max green time (60 seconds)
        green_times[priority] = MAX_GREEN
        # Log override
        print(f"🚨 EMERGENCY VEHICLE detected in {priority} lane! Signal plan overriden.")

    return {
        "green_times": green_times,
        "priority_lane": priority,
        "cycle_time": sum(green_times.values())
    }

# Test
if __name__ == "__main__":
    test_counts = {"North": 15, "South": 8, "East": 20, "West": 5}
    plan = get_signal_plan(test_counts)
    print("Vehicle Counts:", test_counts)
    print("Green Times:", plan["green_times"])
    print("Priority Lane:", plan["priority_lane"])
    print("Total Cycle:", plan["cycle_time"], "seconds")