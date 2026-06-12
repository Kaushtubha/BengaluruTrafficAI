"""
signal_service.py
-----------------
Adaptive Traffic Signal Timing Algorithm.

Calculates green-light durations for each lane proportionally to
vehicle counts, with support for emergency-vehicle priority overrides.
"""

MIN_GREEN = 10   # seconds — minimum green time for any lane
MAX_GREEN = 60   # seconds — maximum green time for any lane
BASE_GREEN = 20  # seconds — default green time when no vehicles are detected


def calculate_green_time(vehicle_counts: dict) -> dict:
    """
    Calculate proportional green-light durations for each lane.

    Args:
        vehicle_counts (dict): Mapping of lane name → vehicle count.

    Returns:
        dict: Mapping of lane name → green-light duration in seconds.
    """
    total = sum(vehicle_counts.values())
    green_times = {}

    if total == 0:
        # Equal time for all lanes when no vehicles are detected
        for lane in vehicle_counts:
            green_times[lane] = BASE_GREEN
        return green_times

    for lane, count in vehicle_counts.items():
        # Allocate time proportionally to the lane's share of total traffic
        proportion = count / total
        green_time = MIN_GREEN + (proportion * (MAX_GREEN - MIN_GREEN))
        green_times[lane] = round(green_time, 1)

    return green_times


def get_priority_lane(vehicle_counts: dict) -> str:
    """Return the lane with the highest vehicle count."""
    return max(vehicle_counts, key=vehicle_counts.get)


def get_signal_plan(vehicle_counts: dict, emergency_lanes: list = None) -> dict:
    """
    Build a complete signal plan, giving priority to emergency vehicles.

    Args:
        vehicle_counts (dict): Mapping of lane name → vehicle count.
        emergency_lanes (list, optional): Lanes containing emergency vehicles.
            The first entry receives the maximum green time.

    Returns:
        dict: Signal plan with green_times, priority_lane, and cycle_time.
    """
    green_times = calculate_green_time(vehicle_counts)
    priority = get_priority_lane(vehicle_counts)

    if emergency_lanes:
        # Emergency lane gets priority override
        priority = emergency_lanes[0]
        green_times[priority] = MAX_GREEN
        print(f"🚨 EMERGENCY VEHICLE detected in {priority} lane! Signal plan overridden.")

    return {
        "green_times": green_times,
        "priority_lane": priority,
        "cycle_time": sum(green_times.values()),
    }


# Quick smoke-test
if __name__ == "__main__":
    test_counts = {"North": 15, "South": 8, "East": 20, "West": 5}
    plan = get_signal_plan(test_counts)
    print("Vehicle Counts:", test_counts)
    print("Green Times:   ", plan["green_times"])
    print("Priority Lane: ", plan["priority_lane"])
    print("Total Cycle:   ", plan["cycle_time"], "seconds")