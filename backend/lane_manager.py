import math


LANES = ("North", "South", "East", "West")


def get_lane(center_x, frame_width):
    """Split the frame width into 4 equal lanes: North, South, East, West."""
    if (
        isinstance(frame_width, bool)
        or not isinstance(frame_width, (int, float))
        or not math.isfinite(frame_width)
        or frame_width <= 0
    ):
        raise ValueError("frame_width must be a positive finite number")
    if (
        isinstance(center_x, bool)
        or not isinstance(center_x, (int, float))
        or not math.isfinite(center_x)
    ):
        raise ValueError("center_x must be a finite number")

    lane_width = frame_width / len(LANES)
    for idx, lane in enumerate(LANES[:-1], start=1):
        if center_x < lane_width * idx:
            return lane
    return LANES[-1]
