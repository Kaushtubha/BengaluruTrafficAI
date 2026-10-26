"""
Unit and regression tests for Driver Assistance Telemetry (/api/driver_advice)
and legacy API contracts across both backend modes (demo_sim and live_cv).

Uses Python's standard library `unittest` module. No external test packages required.
"""

import os
import sys
import unittest

# Ensure backend directory is in Python module search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    import flask
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False


@unittest.skipUnless(HAS_FLASK, "Flask is required for backend API client integration tests")
class TestDriverAdviceDemo(unittest.TestCase):
    """Tests for backend/app_demo.py (Render free-tier simulation mode)."""

    @classmethod
    def setUpClass(cls):
        from app_demo import app
        cls.app = app
        cls.client = app.test_client()

    def test_default_corridor(self):
        res = self.client.get('/api/driver_advice')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("data_source"), "demo_sim")
        self.assertIn(data["approach"]["corridor"], ["North", "South", "East", "West"])

    def test_valid_corridors_case_insensitive(self):
        for corridor in ["North", "South", "East", "West", "north", "south", "EAST", "wEsT"]:
            res = self.client.get(f'/api/driver_advice?corridor={corridor}')
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["approach"]["corridor"].lower(), corridor.lower())

    def test_invalid_corridor_rejected(self):
        res = self.client.get('/api/driver_advice?corridor=UptownExpress')
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertEqual(data.get("status"), "error")
        self.assertIn("Invalid corridor", data.get("message", ""))

    def test_missing_coordinates(self):
        res = self.client.get('/api/driver_advice?corridor=North')
        self.assertEqual(res.status_code, 200)
        telemetry = res.get_json()["distance_telemetry"]
        self.assertIsNone(telemetry["straight_line_distance_km"])
        self.assertEqual(telemetry["status"], "COORDINATES_NOT_PROVIDED")

    def test_partial_coordinates(self):
        # Missing lon
        res_lat = self.client.get('/api/driver_advice?corridor=North&lat=12.9352')
        self.assertEqual(res_lat.get_json()["distance_telemetry"]["status"], "INCOMPLETE_COORDINATES_MISSING_LON")
        self.assertIsNone(res_lat.get_json()["distance_telemetry"]["straight_line_distance_km"])

        # Missing lat
        res_lon = self.client.get('/api/driver_advice?corridor=North&lon=77.6245')
        self.assertEqual(res_lon.get_json()["distance_telemetry"]["status"], "INCOMPLETE_COORDINATES_MISSING_LAT")
        self.assertIsNone(res_lon.get_json()["distance_telemetry"]["straight_line_distance_km"])

    def test_malformed_coordinates(self):
        res = self.client.get('/api/driver_advice?corridor=North&lat=abc&lon=def')
        self.assertEqual(res.status_code, 200)
        telemetry = res.get_json()["distance_telemetry"]
        self.assertIsNone(telemetry["straight_line_distance_km"])
        self.assertEqual(telemetry["status"], "INVALID_COORDINATE_FORMAT")

    def test_out_of_range_coordinates(self):
        res = self.client.get('/api/driver_advice?corridor=North&lat=120.0&lon=77.6245')
        self.assertEqual(res.status_code, 200)
        telemetry = res.get_json()["distance_telemetry"]
        self.assertIsNone(telemetry["straight_line_distance_km"])
        self.assertEqual(telemetry["status"], "COORDINATES_OUT_OF_RANGE")

    def test_nan_and_inf_coordinates_guarded(self):
        for bad_val in ["nan", "inf", "-inf"]:
            res = self.client.get(f'/api/driver_advice?corridor=North&lat={bad_val}&lon=77.6245')
            self.assertEqual(res.status_code, 200)
            telemetry = res.get_json()["distance_telemetry"]
            self.assertIsNone(telemetry["straight_line_distance_km"])
            self.assertEqual(telemetry["status"], "INVALID_COORDINATE_FORMAT")

    def test_corridor_length_limit(self):
        oversized = "A" * 35
        res = self.client.get(f'/api/driver_advice?corridor={oversized}')
        self.assertEqual(res.status_code, 400)
        self.assertIn("exceeds maximum allowed length", res.get_json().get("message", ""))

    def test_whitespace_padded_coordinates(self):
        res = self.client.get('/api/driver_advice?corridor=North&lat=%2012.9352%20&lon=%2077.6245%20')
        self.assertEqual(res.status_code, 200)
        telemetry = res.get_json()["distance_telemetry"]
        self.assertEqual(telemetry["status"], "CALCULATED")
        self.assertIsInstance(telemetry["straight_line_distance_km"], float)

    def test_valid_gps_calculation(self):
        res = self.client.get('/api/driver_advice?corridor=North&lat=12.9352&lon=77.6245')
        self.assertEqual(res.status_code, 200)
        telemetry = res.get_json()["distance_telemetry"]
        self.assertEqual(telemetry["status"], "CALCULATED")
        dist = telemetry["straight_line_distance_km"]
        self.assertIsInstance(dist, float)
        self.assertGreater(dist, 0.0)
        self.assertIn("Straight-line aerial distance", telemetry["disclaimer"])

    def test_delay_transparency(self):
        res = self.client.get('/api/driver_advice?corridor=North')
        delay = res.get_json()["delay_telemetry"]
        self.assertEqual(delay["delay_status"], "ESTIMATE_UNAVAILABLE")
        self.assertIsNone(delay["estimated_delay_mins"])
        self.assertIn("Queue clearance delay cannot be accurately calculated", delay["reason"])

    def test_route_transparency(self):
        res = self.client.get('/api/driver_advice?corridor=North')
        corridor_status = res.get_json()["corridor_status"]
        self.assertEqual(corridor_status["unmonitored_routes"], "DATA_UNAVAILABLE")

    def test_legacy_api_compatibility(self):
        for endpoint in ['/api/status', '/api/lanes', '/api/signal', '/api/violations', '/api/health']:
            res = self.client.get(endpoint)
            self.assertEqual(res.status_code, 200, f"Endpoint {endpoint} failed")


@unittest.skipUnless(HAS_FLASK, "Flask is required for backend API client integration tests")
class TestDriverAdviceLiveCV(unittest.TestCase):
    """Tests for backend/app.py (Local Computer Vision mode)."""

    @classmethod
    def setUpClass(cls):
        from app import app
        cls.app = app
        cls.client = app.test_client()

    def test_live_cv_provenance(self):
        res = self.client.get('/api/driver_advice')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("data_source"), "live_cv")
        self.assertIn("Local Computer Vision Inference", data.get("feed_description", ""))

    def test_valid_corridor_live_cv(self):
        res = self.client.get('/api/driver_advice?corridor=South')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["approach"]["corridor"], "South")

    def test_invalid_corridor_live_cv(self):
        res = self.client.get('/api/driver_advice?corridor=NonExistentLane')
        self.assertEqual(res.status_code, 400)

    def test_gps_calculation_live_cv(self):
        res = self.client.get('/api/driver_advice?corridor=East&lat=12.9116&lon=77.6389')
        self.assertEqual(res.status_code, 200)
        telemetry = res.get_json()["distance_telemetry"]
        self.assertEqual(telemetry["status"], "CALCULATED")
        self.assertIsInstance(telemetry["straight_line_distance_km"], float)

    def test_legacy_endpoints_live_cv(self):
        for endpoint in ['/api/status', '/api/lanes', '/api/signal', '/api/violations', '/api/health']:
            res = self.client.get(endpoint)
            self.assertEqual(res.status_code, 200, f"Live CV endpoint {endpoint} failed")


@unittest.skipUnless(HAS_FLASK, "Flask is required for backend API client integration tests")
class TestJunctionEnvironmentConfig(unittest.TestCase):
    """Tests for configurable junction environment variables."""

    @classmethod
    def setUpClass(cls):
        from app_demo import app
        cls.client = app.test_client()

    def test_out_of_range_junction_coords(self):
        os.environ["JUNCTION_LAT"] = "999.0"
        os.environ["JUNCTION_LON"] = "77.6238"
        try:
            res = self.client.get('/api/driver_advice?corridor=North&lat=12.93&lon=77.62')
            data = res.get_json()
            self.assertIsNotNone(data["junction"]["configuration_error"])
            self.assertEqual(data["distance_telemetry"]["status"], "JUNCTION_COORDINATES_CONFIG_ERROR")
        finally:
            del os.environ["JUNCTION_LAT"]
            del os.environ["JUNCTION_LON"]

    def test_malformed_junction_coords(self):
        os.environ["JUNCTION_LAT"] = "not_a_number"
        os.environ["JUNCTION_LON"] = "77.6238"
        try:
            res = self.client.get('/api/driver_advice?corridor=North&lat=12.93&lon=77.62')
            data = res.get_json()
            self.assertIn("invalid numeric format", data["junction"]["configuration_error"])
            self.assertEqual(data["distance_telemetry"]["status"], "JUNCTION_COORDINATES_CONFIG_ERROR")
        finally:
            del os.environ["JUNCTION_LAT"]
            del os.environ["JUNCTION_LON"]


if __name__ == '__main__':
    unittest.main()
