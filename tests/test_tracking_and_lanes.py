"""
Unit tests for geometric lane mapping (backend/lane_manager.py)
and IoU multi-object tracking (backend/tracker_manager.py).
"""

import os
import sys
import unittest

# Ensure repo root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.lane_manager import LANES, get_lane
from backend.tracker_manager import Tracker


class TestLaneManager(unittest.TestCase):
    """Tests for frame-width lane division and input boundary checks."""

    def test_lane_quadrants_and_exact_boundaries(self):
        frame_width = 1280
        cases = [
            (0, "North"),
            (319.9, "North"),
            (320, "South"),
            (639.9, "South"),
            (640, "East"),
            (959.9, "East"),
            (960, "West"),
            (1280, "West"),
        ]
        for center_x, expected_lane in cases:
            with self.subTest(center_x=center_x):
                self.assertEqual(get_lane(center_x, frame_width), expected_lane)

    def test_out_of_frame_coordinates_clamp_to_outer_lanes(self):
        self.assertEqual(get_lane(-15, 1000), LANES[0])
        self.assertEqual(get_lane(1250, 1000), LANES[-1])

    def test_invalid_inputs_raise_value_error(self):
        invalid_cases = [
            (100, 0),
            (100, -640),
            (100, float("nan")),
            (100, float("inf")),
            (float("nan"), 1280),
            (float("-inf"), 1280),
            (True, 1280),
            (100, True),
        ]
        for center_x, frame_width in invalid_cases:
            with self.subTest(center_x=center_x, frame_width=frame_width):
                with self.assertRaises(ValueError):
                    get_lane(center_x, frame_width)


class TestTrackerManager(unittest.TestCase):
    """Tests for IoU calculation, track association, and lifecycle pruning."""

    def test_constructor_validates_bounds(self):
        with self.assertRaises(ValueError):
            Tracker(max_lost=-1)
        with self.assertRaises(ValueError):
            Tracker(iou_threshold=-0.1)
        with self.assertRaises(ValueError):
            Tracker(iou_threshold=1.1)

    def test_calculate_iou_cases(self):
        tracker = Tracker()
        self.assertAlmostEqual(tracker.calculate_iou([0, 0, 10, 10], [0, 0, 10, 10]), 1.0)
        self.assertAlmostEqual(tracker.calculate_iou([0, 0, 10, 10], [20, 20, 30, 30]), 0.0)
        # 5x10 overlap inside two 10x10 boxes -> intersection=50, union=150 -> 1/3
        self.assertAlmostEqual(tracker.calculate_iou([0, 0, 10, 10], [5, 0, 15, 10]), 1.0 / 3.0)
        # Degenerate zero-area and inverted boxes must safely return 0.0
        self.assertEqual(tracker.calculate_iou([0, 0, 0, 0], [0, 0, 0, 0]), 0.0)
        self.assertEqual(tracker.calculate_iou([100, 100, 50, 50], [100, 100, 50, 50]), 0.0)

    def test_track_persistence_and_new_spawn(self):
        tracker = Tracker(max_lost=2, iou_threshold=0.2)
        frame1 = tracker.update_tracks([([100, 100, 50, 50], 0.9, "Car")])
        self.assertEqual(len(frame1), 1)
        first_id = frame1[0].track_id
        self.assertTrue(frame1[0].is_confirmed())

        # Slightly shifted box should retain the same track ID and add a new vehicle
        frame2 = tracker.update_tracks([
            ([105, 105, 50, 50], 0.92, "Car"),
            ([400, 200, 40, 80], 0.85, "Motorcycle"),
        ])
        self.assertEqual(len(frame2), 2)
        self.assertEqual(frame2[0].track_id, first_id)
        self.assertEqual(frame2[0].hits, 2)
        self.assertEqual(frame2[0].age, 0)
        self.assertEqual(frame2[0].to_ltrb(), [105, 105, 155, 155])
        self.assertNotEqual(frame2[1].track_id, first_id)

    def test_stale_tracks_expire_after_max_lost(self):
        tracker = Tracker(max_lost=2, iou_threshold=0.2)
        # Initial spawn creates age=1; matching resets age=0
        tracker.update_tracks([([10, 10, 40, 40], 0.9, "Car")])
        tracker.update_tracks([([10, 10, 40, 40], 0.9, "Car")])

        # Miss 1 (age=1 <= 2) -> retained
        self.assertEqual(len(tracker.update_tracks([])), 1)
        # Miss 2 (age=2 <= 2) -> retained
        self.assertEqual(len(tracker.update_tracks([])), 1)
        # Miss 3 (age=3 > 2) -> pruned
        self.assertEqual(len(tracker.update_tracks(None)), 0)

    def test_ignores_non_positive_dimension_detections(self):
        tracker = Tracker()
        tracks = tracker.update_tracks([
            ([10, 10, 0, 20], 0.8, "Car"),
            ([10, 10, 20, -5], 0.8, "Bus"),
            ([50, 50, 30, 30], 0.9, "Truck"),
        ])
        self.assertEqual(len(tracks), 1)
        self.assertEqual(tracks[0].label, "Truck")


if __name__ == "__main__":
    unittest.main()
