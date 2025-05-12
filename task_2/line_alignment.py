from determine_side import TrackSide


class LineAlignment:
    """
    Goal: The roboter should move on the outer edge og the line (so one sensor is in contact with the white ground not the grey for ease of reading the line)
    LineAlignment checks if the robot follows the outer edge periodically and if not cnages the edge to follow.
    """

    def __init__(self, follow_left_side: bool = False):

        """
        :param follow_left_side: if the robot should follow the left side of the line. if False it will follow the right side
        """
        self.follow_left_side = follow_left_side

    def get_follow_left_side(self) -> bool:
        return self.follow_left_side

    def check_line_alignment(self, current_side: TrackSide):
        """
        Check if the robot is following the correct side of the line. If not, change the side to follow.
        :param current_side: The current side of the line the robot is on.
        :return: nothing
        """
        if current_side == TrackSide.LEFT and not self.follow_left_side:
            self.follow_left_side = True
        elif current_side == TrackSide.RIGHT and self.follow_left_side:
            self.follow_left_side = False
