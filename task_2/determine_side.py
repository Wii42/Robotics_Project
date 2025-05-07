from enum import Enum

from project2.track_follower import RobotPosition

class TrackSide(Enum):
    LEFT = 0
    RIGHT = 1
    UNKNOWN = 2

class DetermineSide:

    def __init__(self, grey_max_value: int, grey_min_value: int, steps_to_determine_side: int):
        """
        :param grey_max_value: the max value for an area to be considered grey
        :param grey_min_value: the min value for an area to be considered grey
        :param steps_to_determine_side: how many readings should be considered to determine the side
        """
        self.grey_max_value = grey_max_value
        self.grey_min_value = grey_min_value
        self.readings: list[TrackSide] = [] # list of all reading on which side the robot is
        self.steps_to_determine_side = steps_to_determine_side


    def in_grey(self, value: int) -> bool:
        return self.grey_min_value <= value <= self.grey_max_value

    def in_white(self, value: int) -> bool:
        return value > self.grey_max_value

    def __determine_side(self, gs: list[int], position: RobotPosition):
        if position == RobotPosition.IS_LEFT:
            if self.in_white(gs[0]):
                return TrackSide.LEFT
            elif self.in_grey(gs[0]):
                return TrackSide.RIGHT
        elif position == RobotPosition.IS_RIGHT or position == RobotPosition.IS_MIDDLE:
            if self.in_white(gs[2]):
                return TrackSide.RIGHT
            elif self.in_grey(gs[2]):
                return TrackSide.LEFT
        return TrackSide.UNKNOWN

    def read_colors(self, gs):
        l = []
        for g in gs:
            if self.in_white(g):
                l.append("white")
            elif self.in_grey(g):
                l.append("grey")
            else:
                l.append("black")
        return l

    def determine_side(self, gs: list[int], position: RobotPosition, invert_side: bool = False):
        if invert_side:
            gs = gs[::-1]  # reverse the list
        v = self.__determine_side(gs, position)
        if invert_side:
            if v == TrackSide.LEFT:
                v = TrackSide.RIGHT
            elif v == TrackSide.RIGHT:
                v = TrackSide.LEFT
        self.readings.append(v)

    def get_probable_side(self) -> TrackSide:
        """
        Get the probable side of the line based on the last readings.
        If there are no readings, return UNKNOWN.
        The side which was recorded the most times in this interval will be returned.
        :return: TrackSide.LEFT, TrackSide.RIGHT (or TrackSide.UNKNOWN if there are no readings or no side was detected)
        """
        if len(self.readings) == 0:
            values = [TrackSide.UNKNOWN]
        else:

            values = self.readings[-self.steps_to_determine_side:] if self.steps_to_determine_side < len(self.readings) else self.readings
        #print(values)
        left = values.count(TrackSide.LEFT)
        right = values.count(TrackSide.RIGHT)

        if left == right:
            return TrackSide.UNKNOWN
        elif left > right:
            return TrackSide.LEFT
        else:
            return TrackSide.RIGHT






