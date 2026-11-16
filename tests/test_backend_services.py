"""
test_backend_services.py — Unit Test Suite for Backend Core Modules and Services.

Tests:
  - Junction Configuration & Haversine Distance
  - Signal Intelligence & MUTCD Clearance Intervals
  - Congestion Predictor Rule-Based Fallback
  - Security Rate Limiter & Sanitization Guards
  - Traffic Audit Logger & Event Queries
  - Telemetry Service (Queue Balance Index & Safety Compliance)
  - System Runtime Diagnostics & Uptime Formatting
"""

import math
import os
import sys
import time
import unittest

# Ensure repo root and backend directory are on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from backend.junction_config import (
    DEFAULT_JUNCTION_LAT,
    DEFAULT_JUNCTION_LON,
    DEFAULT_JUNCTION_NAME,
    calculate_haversine,
    get_junction_config,
    validate_coordinates,
)
from backend.signal_service import (
    ALL_RED_CLEARANCE,
    BASE_GREEN,
    DEFAULT_LANES,
    MAX_GREEN,
    MIN_GREEN,
    YELLOW_CLEARANCE,
    calculate_green_time,
    get_phase_schedule,
    get_priority_lane,
    get_signal_plan,
)
from backend.congestion_predictor import _predict_rule_based, predict_congestion
from backend.security import (
    SlidingWindowRateLimiter,
    sanitize_float,
    sanitize_integer,
    sanitize_lane_counts,
    sanitize_text,
)
from backend.logger_service import TrafficAuditLogger
from backend.telemetry_service import (
    build_telemetry_summary,
    calculate_queue_balance_index,
    calculate_safety_compliance_score,
)
from backend.diagnostics_service import format_uptime, get_system_diagnostics


class TestJunctionConfig(unittest.TestCase):
    """Test junction configuration parsing and GPS geodesics."""

    def test_default_config_values(self):
        config = get_junction_config()
        self.assertEqual(config["name"], DEFAULT_JUNCTION_NAME)
        self.assertAlmostEqual(config["latitude"], DEFAULT_JUNCTION_LAT, places=4)
        self.assertAlmostEqual(config["longitude"], DEFAULT_JUNCTION_LON, places=4)
        self.assertFalse(config["configuration_error"])

    def test_haversine_zero_distance(self):
        dist = calculate_haversine(12.9177, 77.6238, 12.9177, 77.6238)
        self.assertEqual(dist, 0.0)

    def test_haversine_known_distance(self):
        # Distance between Silk Board (12.9177, 77.6238) and Electronic City (12.8452, 77.6602) is ~9-10 km
        dist = calculate_haversine(12.9177, 77.6238, 12.8452, 77.6602)
        self.assertGreater(dist, 8.0)
        self.assertLess(dist, 11.0)

    def test_validate_coordinates(self):
        # Valid coordinates
        dist, status = validate_coordinates("12.9200", "77.6250", 12.9177, 77.6238)
        self.assertEqual(status, "CALCULATED")
        self.assertIsNotNone(dist)
        self.assertGreater(dist, 0.0)

        # Missing coordinates
        dist, status = validate_coordinates(None, None, 12.9177, 77.6238)
        self.assertIsNone(dist)
        self.assertEqual(status, "COORDINATES_NOT_PROVIDED")

        # Invalid out of range latitude
        dist, status = validate_coordinates("95.0", "77.0", 12.9177, 77.6238)
        self.assertIsNone(dist)
        self.assertEqual(status, "COORDINATES_OUT_OF_RANGE")


class TestSignalService(unittest.TestCase):
    """Test adaptive signal planning and clearance intervals."""

    def test_clearance_constants(self):
        self.assertEqual(YELLOW_CLEARANCE, 3.5)
        self.assertEqual(ALL_RED_CLEARANCE, 1.5)
        self.assertEqual(MIN_GREEN, 10)
        self.assertEqual(MAX_GREEN, 60)

    def test_green_time_bounds(self):
        # Empty counts default to BASE_GREEN
        empty_plan = calculate_green_time({})
        for lane, green in empty_plan.items():
            self.assertEqual(green, BASE_GREEN)

        # High count capped at MAX_GREEN, low proportion respects MIN_GREEN
        counts = {"North": 100, "South": 1, "East": 0, "West": 0}
        plan = calculate_green_time(counts)
        self.assertLessEqual(plan["North"], MAX_GREEN)
        self.assertGreaterEqual(plan["South"], MIN_GREEN)

    def test_signal_plan_structure(self):
        counts = {"North": 30, "South": 15, "East": 10, "West": 5}
        plan = get_signal_plan(counts)
        self.assertIn("green_times", plan)
        self.assertIn("priority_lane", plan)
        self.assertEqual(plan["priority_lane"], "North")
        self.assertEqual(plan["yellow_clearance_sec"], 3.5)
        self.assertEqual(plan["all_red_clearance_sec"], 1.5)
        self.assertEqual(plan["total_clearance_overhead_sec"], 20.0)

    def test_phase_schedule_sequencing(self):
        counts = {"North": 20, "South": 10, "East": 5, "West": 5}
        schedule = get_phase_schedule(counts, emergency_lanes=["East"])
        self.assertEqual(len(schedule), 4)
        # Emergency lane should be sequenced first
        self.assertEqual(schedule[0]["lane"], "East")
        self.assertTrue(schedule[0]["is_emergency_priority"])
        # Offsets should be contiguous
        for i in range(1, len(schedule)):
            self.assertAlmostEqual(schedule[i]["start_time_sec"], schedule[i - 1]["end_time_sec"], places=1)


class TestCongestionPredictor(unittest.TestCase):
    """Test congestion fallback and heuristics."""

    def test_rule_based_levels(self):
        self.assertEqual(_predict_rule_based(5), "Low")
        self.assertEqual(_predict_rule_based(25), "Medium")
        self.assertEqual(_predict_rule_based(60), "High")

    def test_predict_congestion_safe_fallback(self):
        level = predict_congestion(hour=14, total_vehicles=18, active_lane_count=8)
        self.assertIn(level, ["Low", "Medium", "High"])


class TestSecurity(unittest.TestCase):
    """Test sliding-window rate limiting and input sanitation."""

    def test_sliding_window_rate_limiter(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10)
        client = "192.168.1.100"

        # First 3 should pass
        for _ in range(3):
            allowed, info = limiter.is_allowed(client)
            self.assertTrue(allowed)

        # 4th should be blocked
        allowed, info = limiter.is_allowed(client)
        self.assertFalse(allowed)
        self.assertGreaterEqual(info["retry_after_seconds"], 1)

    def test_sanitize_text(self):
        clean = sanitize_text("<script>alert('xss')</script>")
        self.assertNotIn("<", clean)
        self.assertNotIn(">", clean)
        self.assertNotIn("'", clean)

    def test_sanitize_integer_and_float(self):
        self.assertEqual(sanitize_integer("42", min_val=0, max_val=100), 42)
        self.assertEqual(sanitize_integer("150", min_val=0, max_val=100), 100)
        self.assertEqual(sanitize_integer("invalid", default=10), 10)
        self.assertEqual(sanitize_float("3.14159"), 3.1416)
        self.assertEqual(sanitize_float("invalid", default=1.5), 1.5)

    def test_sanitize_lane_counts(self):
        raw = {"north": 12, "south": "20", "invalid_lane": 999}
        cleaned = sanitize_lane_counts(raw)
        self.assertIn("North", cleaned)
        self.assertIn("South", cleaned)
        self.assertIn("East", cleaned)
        self.assertIn("West", cleaned)
        self.assertEqual(cleaned["North"], 12)
        self.assertEqual(cleaned["South"], 20)
        self.assertEqual(cleaned["East"], 0)


class TestLoggerService(unittest.TestCase):
    """Test structured traffic audit logging."""

    def setUp(self):
        self.logger = TrafficAuditLogger(max_records=10)

    def test_log_and_retrieve(self):
        self.logger.log_event("WARNING", "QUEUE_SPIKE", {"lane": "North", "count": 45}, junction_id="silk_board")
        self.logger.log_event("INFO", "SIGNAL_CHANGE", {"active": "East"})

        logs = self.logger.get_recent_logs()
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["event_type"], "SIGNAL_CHANGE")  # newest first
        self.assertEqual(logs[1]["level"], "WARNING")

    def test_filter_by_level(self):
        self.logger.log_event("ERROR", "CAMERA_FAIL", {"cam_id": 1})
        self.logger.log_event("INFO", "HEARTBEAT", {})

        errors = self.logger.get_recent_logs(level="ERROR")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["event_type"], "CAMERA_FAIL")


class TestTelemetryService(unittest.TestCase):
    """Test queue balance index and compliance metrics."""

    def test_queue_balance_uniform(self):
        # Completely uniform distribution should give 1.0
        counts = {"North": 20, "South": 20, "East": 20, "West": 20}
        self.assertAlmostEqual(calculate_queue_balance_index(counts), 1.0, places=2)

    def test_queue_balance_bottleneck(self):
        # Extreme bottleneck on one lane
        counts = {"North": 100, "South": 0, "East": 0, "West": 0}
        self.assertLess(calculate_queue_balance_index(counts), 0.5)

    def test_safety_compliance_score(self):
        # 0 violations -> high score
        self.assertEqual(calculate_safety_compliance_score(0, 100), 100.0)
        # Moderate violations -> penalized
        score = calculate_safety_compliance_score(5, 100)
        self.assertLess(score, 100.0)
        self.assertGreaterEqual(score, 50.0)

    def test_build_telemetry_summary(self):
        summary = build_telemetry_summary(
            junction_config={"name": "Tin Factory"},
            vehicle_counts={"North": 15, "South": 10, "East": 5, "West": 5},
            tracked_total=200,
            violations_summary={"red_light": 2},
            congestion_level="Medium",
        )
        self.assertEqual(summary["status"], "success")
        self.assertIn("throughput", summary)
        self.assertIn("traffic_quality", summary)
        self.assertIn("signal_state", summary)
        self.assertEqual(len(summary["signal_state"]["phase_schedule"]), 4)


class TestDiagnosticsService(unittest.TestCase):
    """Test diagnostics and uptime calculations."""

    def test_format_uptime(self):
        self.assertEqual(format_uptime(45), "45s")
        self.assertEqual(format_uptime(125), "2m 5s")
        self.assertEqual(format_uptime(3665), "1h 1m 5s")
        self.assertEqual(format_uptime(90061), "1d 1h 1m 1s")

    def test_diagnostics_report_structure(self):
        report = get_system_diagnostics(time.time() - 60, mode="test", routes=["/api/status"])
        self.assertEqual(report["status"], "healthy")
        self.assertIn("process", report)
        self.assertIn("execution", report)
        self.assertIn("subsystems", report)
        self.assertIn("/api/status", report["api_endpoints"])


if __name__ == "__main__":
    unittest.main()
