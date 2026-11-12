"""
tracker_manager.py
------------------
Lightweight IoU-based multi-object tracker for vehicle tracking.

Uses intersection-over-union (IoU) matching to associate detections
across frames and assigns persistent track IDs to each vehicle.
"""


class Track:
    """Represents a single tracked vehicle across video frames."""

    def __init__(self, track_id: int, bbox: list, label: str):
        """
        Args:
            track_id (int): Unique identifier for this track.
            bbox (list): Bounding box in [x1, y1, x2, y2] format.
            label (str): Vehicle class label (e.g. 'Car', 'Motorcycle').
        """
        self.track_id = track_id
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.label = label
        self.hits = 1   # number of successful matches
        self.age = 1    # frames since last successful match

    def is_confirmed(self) -> bool:
        """Return True if the track has been matched at least once."""
        return self.hits >= 1

    def to_ltrb(self) -> list:
        """Return the bounding box in [left, top, right, bottom] format."""
        return self.bbox


class Tracker:
    """IoU-based greedy multi-object tracker."""

    def __init__(self, max_lost: int = 10, iou_threshold: float = 0.2):
        """
        Args:
            max_lost (int): Frames to keep a track alive without a match.
            iou_threshold (float): Minimum IoU to consider a detection
                as a match for an existing track.
        """
        if max_lost < 0:
            raise ValueError("max_lost must be non-negative")
        if not (0.0 <= iou_threshold <= 1.0):
            raise ValueError("iou_threshold must be between 0.0 and 1.0")
        self.max_lost = max_lost
        self.iou_threshold = iou_threshold
        self.next_id = 1
        self.tracks: list[Track] = []

    def update_tracks(self, detections: list, frame=None) -> list:
        """
        Match detections to existing tracks and return updated track list.

        Args:
            detections (list): List of (bbox_xywh, confidence, label) tuples
                where bbox_xywh is [x, y, w, h].
            frame: Optional video frame (unused, reserved for future use).

        Returns:
            list[Track]: All currently active tracks.
        """
        # Convert valid detections from [x, y, w, h] → [x1, y1, x2, y2]
        det_bboxes = []
        det_labels = []
        for bbox_xywh, conf, label in (detections or []):
            x, y, w, h = bbox_xywh
            if w <= 0 or h <= 0:
                continue
            det_bboxes.append([x, y, x + w, y + h])
            det_labels.append(label)

        updated_tracks = []
        matched_det_indices = set()

        # Greedily match existing tracks to the best-IoU detection
        for track in self.tracks:
            track.age += 1
            best_iou = 0
            best_det_idx = -1

            for idx, det_bbox in enumerate(det_bboxes):
                if idx in matched_det_indices:
                    continue
                iou = self.calculate_iou(track.bbox, det_bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_det_idx = idx

            if best_iou > self.iou_threshold:
                track.bbox = det_bboxes[best_det_idx]
                track.hits += 1
                track.age = 0  # reset lost-frame counter
                matched_det_indices.add(best_det_idx)
                updated_tracks.append(track)
            else:
                # Retain the track until max_lost frames have elapsed
                if track.age <= self.max_lost:
                    updated_tracks.append(track)

        # Spawn new tracks for unmatched detections
        for idx, det_bbox in enumerate(det_bboxes):
            if idx not in matched_det_indices:
                new_track = Track(self.next_id, det_bbox, det_labels[idx])
                self.next_id += 1
                updated_tracks.append(new_track)

        self.tracks = updated_tracks
        return self.tracks

    @staticmethod
    def _box_area(box: list) -> float:
        """Compute non-negative area for a [x1, y1, x2, y2] bounding box."""
        return max(0.0, float(box[2]) - float(box[0])) * max(0.0, float(box[3]) - float(box[1]))

    def calculate_iou(self, boxA: list, boxB: list) -> float:
        """
        Compute Intersection over Union (IoU) for two bounding boxes.

        Args:
            boxA (list): [x1, y1, x2, y2]
            boxB (list): [x1, y1, x2, y2]

        Returns:
            float: IoU score in [0, 1].
        """
        x_left   = max(boxA[0], boxB[0])
        y_top    = max(boxA[1], boxB[1])
        x_right  = min(boxA[2], boxB[2])
        y_bottom = min(boxA[3], boxB[3])

        inter_area = max(0.0, float(x_right) - float(x_left)) * max(0.0, float(y_bottom) - float(y_top))
        if inter_area == 0.0:
            return 0.0

        area_a = self._box_area(boxA)
        area_b = self._box_area(boxB)
        union_area = area_a + area_b - inter_area

        if union_area <= 0.0:
            return 0.0
        return inter_area / union_area


# Module-level singleton used across the application
tracker = Tracker()
