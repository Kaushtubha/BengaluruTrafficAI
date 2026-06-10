class Track:
    def __init__(self, track_id, bbox, label):
        self.track_id = track_id
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.label = label
        self.hits = 1
        self.age = 1

    def is_confirmed(self):
        # A track is confirmed if it has been matched/tracked at least once
        return self.hits >= 1

    def to_ltrb(self):
        return self.bbox

class Tracker:
    def __init__(self, max_lost=10, iou_threshold=0.2):
        self.max_lost = max_lost
        self.iou_threshold = iou_threshold
        self.next_id = 1
        self.tracks = []

    def update_tracks(self, detections, frame=None):
        """
        detections: list of ( [x, y, w, h], confidence, label )
        """
        # Convert detections to [x1, y1, x2, y2] format
        det_bboxes = []
        det_labels = []
        for bbox_xywh, conf, label in detections:
            x, y, w, h = bbox_xywh
            det_bboxes.append([x, y, x + w, y + h])
            det_labels.append(label)

        updated_tracks = []
        matched_det_indices = set()

        # Update existing tracks
        for track in self.tracks:
            track.age += 1
            best_iou = 0
            best_det_idx = -1

            for idx, det_bbox in enumerate(det_bboxes):
                if idx in matched_det_indices:
                    continue
                # Calculate IoU
                iou = self.calculate_iou(track.bbox, det_bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_det_idx = idx

            if best_iou > self.iou_threshold:
                # Update track with matched detection
                track.bbox = det_bboxes[best_det_idx]
                track.hits += 1
                track.age = 0  # Reset age
                matched_det_indices.add(best_det_idx)
                updated_tracks.append(track)
            else:
                # Keep lost track if not too old
                if track.age <= self.max_lost:
                    updated_tracks.append(track)

        # Create new tracks for unmatched detections
        for idx, det_bbox in enumerate(det_bboxes):
            if idx not in matched_det_indices:
                new_track = Track(self.next_id, det_bbox, det_labels[idx])
                self.next_id += 1
                updated_tracks.append(new_track)

        self.tracks = updated_tracks
        return self.tracks

    def calculate_iou(self, boxA, boxB):
        # determine the (x, y)-coordinates of the intersection rectangle
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        # compute the area of intersection rectangle
        interArea = max(0, xB - xA) * max(0, yB - yA)

        # compute the area of both the prediction and ground-truth rectangles
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the intersection area
        unionArea = float(boxAArea + boxBArea - interArea)
        if unionArea == 0:
            return 0
        iou = interArea / unionArea
        return iou

# Global instance
tracker = Tracker()
