import unittest
import sys
import os

# Ensure repo root is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.signal_service import calculate_green_time, get_priority_lane, get_signal_plan, MIN_GREEN, MAX_GREEN, BASE_GREEN
from backend.congestion_predictor import (
    predict_congestion,
    get_congestion_details,
    CONGESTION_PROVENANCE,
    IS_SYNTHETIC_MODEL,
)
from ai.violation_detector import check_red_light_violation, get_violations, STOP_LINE_Y
from ai.wrong_side_detector import update_track, check_wrong_side, get_wrong_side_violations
from ai.helmet_detector import check_helmet_violation, get_helmet_violations
from ai.speed_estimator import (
    check_speed_violation,
    calculate_speed,
    update_speed,
    get_speed_violations,
    SPEED_LIMIT_KMPH,
    MAX_PLAUSIBLE_SPEED_KMPH,
    MAX_TRACK_AGE_SECONDS,
)


class TestSignalService(unittest.TestCase):
    """Test adaptive signal calculations and emergency overrides."""

    def test_zero_vehicle_counts_all_lanes_receive_base_green(self):
        counts = {"North": 0, "South": 0, "East": 0, "West": 0}
        times = calculate_green_time(counts)
        for lane, seconds in times.items():
            self.assertEqual(seconds, BASE_GREEN)

    def test_proportional_allocation_bounds(self):
        counts = {"North": 30, "South": 10, "East": 5, "West": 5}
        plan = get_signal_plan(counts)
        # Busiest lane should have the most green time
        self.assertEqual(plan["priority_lane"], "North")
        for lane, seconds in plan["green_times"].items():
            self.assertGreaterEqual(seconds, MIN_GREEN)
            self.assertLessEqual(seconds, MAX_GREEN)
        # Cycle time is properly rounded float
        self.assertIsInstance(plan["cycle_time"], (float, int))
        self.assertEqual(plan["cycle_time"], round(sum(plan["green_times"].values()), 1))

    def test_emergency_override_allocates_max_green(self):
        counts = {"North": 5, "South": 30, "East": 5, "West": 5}
        plan = get_signal_plan(counts, emergency_lanes=["North"])
        self.assertEqual(plan["priority_lane"], "North")
        self.assertEqual(plan["green_times"]["North"], MAX_GREEN)
        self.assertTrue(plan["emergency_override"])
        self.assertEqual(plan["emergency_lane"], "North")

    def test_standard_plan_has_no_emergency_override(self):
        counts = {"North": 30, "South": 10, "East": 5, "West": 5}
        plan = get_signal_plan(counts)
        self.assertFalse(plan["emergency_override"])
        self.assertIsNone(plan["emergency_lane"])

    def test_empty_vehicle_counts_graceful_fallback(self):
        plan = get_signal_plan({})
        self.assertIn("green_times", plan)
        self.assertGreaterEqual(plan["cycle_time"], BASE_GREEN)
        self.assertFalse(plan["emergency_override"])
        self.assertIn(plan["priority_lane"], ("North", "South", "East", "West"))

    def test_none_vehicle_counts_graceful_fallback(self):
        plan = get_signal_plan(None)
        self.assertIn("green_times", plan)
        self.assertGreaterEqual(plan["cycle_time"], BASE_GREEN)
        self.assertFalse(plan["emergency_override"])

    def test_negative_vehicle_counts_clamped(self):
        counts = {"North": -25, "South": 20, "East": 0, "West": 0}
        times = calculate_green_time(counts)
        for lane, seconds in times.items():
            self.assertGreaterEqual(seconds, MIN_GREEN)
            self.assertLessEqual(seconds, MAX_GREEN)

    def test_emergency_string_lane_normalized(self):
        counts = {"North": 10, "South": 10, "East": 10, "West": 10}
        plan = get_signal_plan(counts, emergency_lanes=" South ")
        self.assertTrue(plan["emergency_override"])
        self.assertEqual(plan["emergency_lane"], "South")
        self.assertEqual(plan["priority_lane"], "South")
        self.assertEqual(plan["green_times"]["South"], MAX_GREEN)


class TestCongestionPredictor(unittest.TestCase):
    """Test Random Forest congestion classification bands, boundaries, and transparency."""

    def test_low_congestion(self):
        result = predict_congestion(hour=3, total_vehicles=5, active_lane_count=2)
        self.assertEqual(result, "Low")

    def test_low_boundary_transitions(self):
        self.assertEqual(predict_congestion(hour=12, total_vehicles=0, active_lane_count=0), "Low")
        self.assertEqual(predict_congestion(hour=12, total_vehicles=14, active_lane_count=5), "Low")

    def test_medium_boundary_transitions(self):
        self.assertEqual(predict_congestion(hour=12, total_vehicles=15, active_lane_count=6), "Medium")
        self.assertEqual(predict_congestion(hour=12, total_vehicles=34, active_lane_count=13), "Medium")

    def test_high_congestion(self):
        result = predict_congestion(hour=18, total_vehicles=80, active_lane_count=35)
        self.assertEqual(result, "High")
        self.assertEqual(predict_congestion(hour=12, total_vehicles=35, active_lane_count=14), "High")

    def test_missing_and_none_inputs_handled_safely(self):
        self.assertEqual(predict_congestion(total_vehicles=None), "UNAVAILABLE")
        self.assertEqual(predict_congestion(hour=None, total_vehicles=None, active_lane_count=None), "UNAVAILABLE")

    def test_malformed_and_negative_inputs_handled_safely(self):
        self.assertEqual(predict_congestion(total_vehicles=-5), "UNAVAILABLE")
        self.assertEqual(predict_congestion(total_vehicles=float("nan")), "UNAVAILABLE")
        self.assertEqual(predict_congestion(total_vehicles=float("inf")), "UNAVAILABLE")
        self.assertEqual(predict_congestion(total_vehicles="not_a_number"), "UNAVAILABLE")

    def test_default_optional_parameters_compatible(self):
        # hour and active_lane_count omitted or None safely default
        self.assertEqual(predict_congestion(total_vehicles=10), "Low")
        self.assertEqual(predict_congestion(total_vehicles=25), "Medium")
        self.assertEqual(predict_congestion(total_vehicles=50), "High")

    def test_provenance_and_synthetic_identification(self):
        details = get_congestion_details(total_vehicles=20)
        self.assertEqual(details["congestion_level"], "Medium")
        self.assertEqual(details["provenance"], CONGESTION_PROVENANCE)
        self.assertTrue(details["is_synthetic_model"])
        self.assertIn("synthetic", details["disclaimer"].lower())
        self.assertIsNone(details["confidence"])


class TestViolationDeduplication(unittest.TestCase):
    """Test that detection modules avoid spamming duplicate records for the same vehicle."""

    def test_red_light_violation_deduplication(self):
        box_crossing = (100, STOP_LINE_Y - 10, 150, STOP_LINE_Y + 20)
        track_id = 9991

        # First crossing frame triggers violation
        is_viol1, v1 = check_red_light_violation(box_crossing, signal_state="RED", track_id=track_id)
        self.assertTrue(is_viol1)
        self.assertIsNotNone(v1)

        # Subsequent frames for the same track_id must be deduplicated
        is_viol2, v2 = check_red_light_violation(box_crossing, signal_state="RED", track_id=track_id)
        self.assertFalse(is_viol2)
        self.assertIsNone(v2)

    def test_wrong_side_violation_deduplication(self):
        track_id = 8881
        # Left lane moving upward (negative movement = wrong side)
        for cy in range(200, 100, -10):
            update_track(track_id, 200, cy)

        is_viol1, v1 = check_wrong_side(track_id, 200, 100, frame_w=1280, frame_h=720)
        self.assertTrue(is_viol1)
        self.assertIsNotNone(v1)

        # Subsequent check for same track_id must be deduplicated
        is_viol2, v2 = check_wrong_side(track_id, 200, 90, frame_w=1280, frame_h=720)
        self.assertFalse(is_viol2)
        self.assertIsNone(v2)

    def test_helmet_violation_deduplication(self):
        # track_id divisible by 7 simulates violation
        track_id = 707
        box = (100, 100, 150, 200)

        is_viol1, v1 = check_helmet_violation(box, "Motorcycle", track_id=track_id)
        self.assertTrue(is_viol1)
        self.assertIsNotNone(v1)

        # Subsequent check for same track_id must be deduplicated
        is_viol2, v2 = check_helmet_violation(box, "Motorcycle", track_id=track_id)
        self.assertFalse(is_viol2)
        self.assertIsNone(v2)


class TestSpeedEstimator(unittest.TestCase):
    """Test velocity estimation, monotonic time handling, interval safety, and glitch protection."""

    def test_null_track_id_safe(self):
        is_speeding, viol, speed = check_speed_violation(None, 100, 100)
        self.assertFalse(is_speeding)
        self.assertIsNone(viol)
        self.assertEqual(speed, 0.0)
        self.assertEqual(calculate_speed(None), 0.0)

    def test_zero_elapsed_time_returns_zero(self):
        track_id = 1001
        update_speed(track_id, 100, 100, timestamp=10.0)
        update_speed(track_id, 200, 200, timestamp=10.0)
        speed = calculate_speed(track_id)
        self.assertEqual(speed, 0.0)

    def test_negative_elapsed_time_returns_zero(self):
        track_id = 1002
        update_speed(track_id, 100, 100, timestamp=15.0)
        update_speed(track_id, 200, 200, timestamp=10.0)
        speed = calculate_speed(track_id)
        self.assertEqual(speed, 0.0)

    def test_stale_tracking_gap_resets(self):
        track_id = 1003
        update_speed(track_id, 100, 100, timestamp=0.0)
        # Tracking gap exceeding MAX_TRACK_AGE_SECONDS
        update_speed(track_id, 200, 200, timestamp=MAX_TRACK_AGE_SECONDS + 1.0)
        speed = calculate_speed(track_id)
        self.assertEqual(speed, 0.0)

    def test_extreme_speed_spike_capped(self):
        track_id = 1004
        update_speed(track_id, 0, 0, timestamp=0.0)
        # Unrealistic pixel displacement over 0.01s (5000 pixels)
        update_speed(track_id, 3000, 4000, timestamp=0.01)
        speed = calculate_speed(track_id)
        self.assertLessEqual(speed, MAX_PLAUSIBLE_SPEED_KMPH)

    def test_speeding_deduplication_and_estimate_type(self):
        track_id = 1005
        # Move 100 pixels in 0.1s: dist = 100 * 0.05 = 5m / 0.1s = 50 m/s = 180 km/h (> 40 km/h)
        is_sp1, v1, s1 = check_speed_violation(track_id, 100, 100, timestamp=1.0)
        is_sp1, v1, s1 = check_speed_violation(track_id, 200, 100, timestamp=1.1)
        self.assertTrue(is_sp1)
        self.assertIsNotNone(v1)
        self.assertEqual(v1["speed_type"], "estimated_uncalibrated")

        # Subsequent check for same track_id must deduplicate
        is_sp2, v2, s2 = check_speed_violation(track_id, 300, 100, timestamp=1.2)
        self.assertTrue(is_sp2)
        # Violation logged previously; must not append duplicate to speed_violations
        self.assertEqual(
            sum(1 for v in get_speed_violations() if v.get("track_id") == track_id),
            1
        )


if __name__ == "__main__":
    unittest.main()
