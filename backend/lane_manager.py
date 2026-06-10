def get_lane(center_x, frame_width):
    """
    Split the frame width into 4 lanes: North, South, East, West.
    """
    lane_width = frame_width / 4
    if center_x < lane_width:
        return "North"
    elif center_x < lane_width * 2:
        return "South"
    elif center_x < lane_width * 3:
        return "East"
    else:
        return "West"
