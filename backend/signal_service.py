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
YELLOW_CLEARANCE = 3.5   # seconds — standard urban yellow change interval (IRC:93/MUTCD)
ALL_RED_CLEARANCE = 1.5  # seconds — all-red intersection clearance buffer


DEFAULT_LANES = ("North", "South", "East", "West")


def calculate_green_time(vehicle_counts: dict) -> dict:
    """
    Calculate proportional green-light durations for each lane.

    Args:
        vehicle_counts (dict): Mapping of lane name → vehicle count.

    Returns:
        dict: Mapping of lane name → green-light duration in seconds.
    """
    if not vehicle_counts or not isinstance(vehicle_counts, dict):
        return {lane: float(BASE_GREEN) for lane in DEFAULT_LANES}

    # Clean and clamp vehicle counts to non-negative numbers
    cleaned_counts = {}
    for lane, count in vehicle_counts.items():
        try:
            val = float(count)
            cleaned_counts[str(lane)] = max(0.0, val)
        except (ValueError, TypeError):
            cleaned_counts[str(lane)] = 0.0

    total = sum(cleaned_counts.values())
    green_times = {}

    if total == 0:
        # Equal time for all lanes when no vehicles are detected
        for lane in cleaned_counts:
            green_times[lane] = float(BASE_GREEN)
        return green_times

    for lane, count in cleaned_counts.items():
        # Allocate time proportionally to the lane's share of total traffic
        proportion = count / total
        green_time = MIN_GREEN + (proportion * (MAX_GREEN - MIN_GREEN))
        # Ensure duration stays strictly within [MIN_GREEN, MAX_GREEN] bounds
        bounded_time = max(float(MIN_GREEN), min(float(MAX_GREEN), green_time))
        green_times[lane] = round(bounded_time, 1)

    return green_times


def get_priority_lane(vehicle_counts: dict) -> str:
    """Return the lane with the highest vehicle count, defaulting to North if empty."""
    if not vehicle_counts or not isinstance(vehicle_counts, dict):
        return DEFAULT_LANES[0]
    try:
        return max(vehicle_counts, key=lambda k: float(vehicle_counts[k]) if vehicle_counts[k] is not None else 0.0)
    except (ValueError, TypeError):
        return next(iter(vehicle_counts), DEFAULT_LANES[0])


def get_phase_schedule(vehicle_counts: dict, emergency_lanes=None) -> list:
    """
    Generate sequential phase schedule with green, yellow, and all-red clearance intervals.

    Returns:
        list[dict]: Ordered phase sequence with start/end offsets and durations.
    """
    counts = vehicle_counts if isinstance(vehicle_counts, dict) and vehicle_counts else {l: 0 for l in DEFAULT_LANES}
    plan = get_signal_plan(counts, emergency_lanes=emergency_lanes)
    green_times = plan["green_times"]
    emergency_lane = plan.get("emergency_lane")

    # Sequence phases: if emergency override is active, put emergency lane first
    lanes = list(DEFAULT_LANES)
    if emergency_lane and emergency_lane in lanes:
        lanes.remove(emergency_lane)
        lanes.insert(0, emergency_lane)

    schedule = []
    current_time = 0.0

    for lane in lanes:
        green = float(green_times.get(lane, BASE_GREEN))
        yellow = float(YELLOW_CLEARANCE)
        all_red = float(ALL_RED_CLEARANCE)
        phase_total = round(green + yellow + all_red, 1)

        schedule.append({
            "lane": lane,
            "green_sec": green,
            "yellow_sec": yellow,
            "all_red_sec": all_red,
            "phase_duration_sec": phase_total,
            "start_time_sec": round(current_time, 1),
            "end_time_sec": round(current_time + phase_total, 1),
            "is_emergency_priority": bool(emergency_lane and lane.lower() == emergency_lane.lower()),
        })
        current_time += phase_total

    return schedule


def get_signal_plan(vehicle_counts: dict, emergency_lanes=None) -> dict:
    """
    Build a complete signal plan, giving priority to emergency vehicles.

    Args:
        vehicle_counts (dict): Mapping of lane name → vehicle count.
        emergency_lanes (list or str, optional): Lanes containing emergency vehicles.
            The first valid entry receives the maximum green time.

    Returns:
        dict: Signal plan with green_times, priority_lane, cycle_time, emergency_override, and emergency_lane.
    """
    counts = vehicle_counts if isinstance(vehicle_counts, dict) and vehicle_counts else {l: 0 for l in DEFAULT_LANES}
    green_times = calculate_green_time(counts)
    priority = get_priority_lane(counts)
    is_override = False
    active_emergency_lane = None

    # Normalize emergency_lanes if a single string is passed
    if isinstance(emergency_lanes, str):
        emergency_lanes = [emergency_lanes]

    if emergency_lanes and isinstance(emergency_lanes, (list, tuple)):
        for cand in emergency_lanes:
            if cand and isinstance(cand, str) and cand.strip():
                clean_cand = cand.strip()
                # Match existing lane case-insensitively if possible
                matched_lane = None
                for lane in green_times:
                    if lane.lower() == clean_cand.lower():
                        matched_lane = lane
                        break
                active_emergency_lane = matched_lane or clean_cand
                is_override = True
                break

    if is_override and active_emergency_lane:
        priority = active_emergency_lane
        green_times[priority] = float(MAX_GREEN)
        try:
            print(f"🚨 EMERGENCY VEHICLE detected in {priority} lane! Signal plan overridden.")
        except UnicodeEncodeError:
            print(f"[EMERGENCY] Vehicle detected in {priority} lane! Signal plan overridden.")

    green_sum = round(sum(green_times.values()), 1)

    return {
        "green_times": green_times,
        "priority_lane": priority,
        "cycle_time": green_sum,
        "emergency_override": is_override,
        "emergency_lane": active_emergency_lane if is_override else None,
        "yellow_clearance_sec": YELLOW_CLEARANCE,
        "all_red_clearance_sec": ALL_RED_CLEARANCE,
        "total_clearance_overhead_sec": round(len(green_times) * (YELLOW_CLEARANCE + ALL_RED_CLEARANCE), 1),
    }


# Quick smoke-test
if __name__ == "__main__":
    test_counts = {"North": 15, "South": 8, "East": 20, "West": 5}
    plan = get_signal_plan(test_counts)
    print("Vehicle Counts:", test_counts)
    print("Green Times:   ", plan["green_times"])
    print("Priority Lane: ", plan["priority_lane"])
    print("Total Cycle:   ", plan["cycle_time"], "seconds")