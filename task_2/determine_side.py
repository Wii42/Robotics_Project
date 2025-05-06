from enum import Enum

from project2.track_follower import RobotPosition

class TrackSide(Enum):
    LEFT = 0
    RIGHT = 1
    UNKNOWN = 2

class DetermineSide:

    def __init__(self, grey_max_value: int, grey_min_value: int):
        self.grey_max_value = grey_max_value
        self.grey_min_value = grey_min_value
        self.readings: list[TrackSide] = []

    def in_grey(self, value: int) -> bool:
        return self.grey_min_value <= value <= self.grey_max_value

    def in_white(self, value: int) -> bool:
        return value > self.grey_max_value

    def determine_side(self, gs: list[int], position: RobotPosition):
        print(self.a(gs))
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

    def a(self, gs):
        l = []
        for g in gs:
            if self.in_white(g):
                l.append("white")
            elif self.in_grey(g):
                l.append("grey")
            else:
                l.append("black")
        return l

    def det_side(self, gs: list[int], position: RobotPosition, invert_side: bool = False):
        if invert_side:
            gs = gs[::-1]  # reverse the list
        v = self.determine_side(gs, position)
        if invert_side:
            if v == TrackSide.LEFT:
                v = TrackSide.RIGHT
            elif v == TrackSide.RIGHT:
                v = TrackSide.LEFT
        self.readings.append(v)

    def get_probable_side(self, last_n: int = 10):

        if len(self.readings) == 0:
            values = [TrackSide.UNKNOWN]
        else:

            values =  self.readings[-last_n:] if last_n < len(self.readings) else self.readings
        print(values)
        left = values.count(TrackSide.LEFT)
        right = values.count(TrackSide.RIGHT)

        if left == right:
            return TrackSide.UNKNOWN
        elif left > right:
            return TrackSide.LEFT
        else:
            return TrackSide.RIGHT






