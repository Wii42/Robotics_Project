from enum import Enum

from challenge.robot.track_follower import RobotPosition

class TrackSide(Enum):
    LEFT = 0
    RIGHT = 1
    UNKNOWN = 2

class DetermineSide:
    """
    The DetermineSide class is responsible for determining which side of the track
    the robot is on based on sensor readings and the robot's position.
    """

    def __init__(self, grey_max_value: int, grey_min_value: int, steps_to_determine_side: int):
        """
        Initialize the DetermineSide class with parameters for detecting the track side.

        :param grey_max_value: The maximum value for an area to be considered grey.
        :param grey_min_value: The minimum value for an area to be considered grey.
        :param steps_to_determine_side: The number of readings to consider when determining the side.
        """
        self.grey_max_value = grey_max_value
        self.grey_min_value = grey_min_value
        self.readings: list[TrackSide] = []  # List of all readings indicating the robot's side.
        self.steps_to_determine_side = steps_to_determine_side
        self.certainty_of_last_guess = None

    def in_grey(self, value: int) -> bool:
        """
        Check if a given value falls within the grey range.

        :param value: The value to check.
        :return: True if the value is within the grey range, False otherwise.
        """
        # Return True if the value is between the grey_min_value and grey_max_value.
        return self.grey_min_value <= value <= self.grey_max_value

    def in_white(self, value: int) -> bool:
        """
        Check if a given value is greater than the grey maximum, indicating white.

        :param value: The value to check.
        :return: True if the value is greater than the grey maximum, False otherwise.
        """
        # Return True if the value is greater than the grey_max_value.
        return value > self.grey_max_value

    def __determine_side(self, gs: list[int], position: RobotPosition) -> TrackSide:
        """
        Determine the side of the track based on sensor readings and the robot's position.

        :param gs: A list of sensor readings.
        :param position: The current position of the robot (LEFT, RIGHT, or MIDDLE).
        :return: The detected side (LEFT, RIGHT, or UNKNOWN).
        """
        # Check the robot's position and determine the side based on sensor readings.
        if position == RobotPosition.IS_LEFT:
            # If the robot is on the left and the first sensor detects white, it's on the LEFT side.
            if self.in_white(gs[0]):
                return TrackSide.LEFT
            # If the first sensor detects grey, it's on the RIGHT side.
            elif self.in_grey(gs[0]):
                return TrackSide.RIGHT
        elif position == RobotPosition.IS_RIGHT or position == RobotPosition.IS_MIDDLE:
            # If the robot is on the right or middle and the last sensor detects white, it's on the RIGHT side.
            if self.in_white(gs[2]):
                return TrackSide.RIGHT
            # If the last sensor detects grey, it's on the LEFT side.
            elif self.in_grey(gs[2]):
                return TrackSide.LEFT
        # If no conditions are met, return UNKNOWN.
        return TrackSide.UNKNOWN

    def read_colors(self, gs: list[int]) -> list[str]:
        """
        Convert sensor readings into color labels (white, grey, or black).

        :param gs: A list of sensor readings.
        :return: A list of color labels corresponding to the sensor readings.
        """
        # Initialize an empty list to store color labels.
        l = []
        for g in gs:
            # Check if the reading corresponds to white, grey, or black and append the label.
            if self.in_white(g):
                l.append("white")
            elif self.in_grey(g):
                l.append("grey")
            else:
                l.append("black")
        return l

    def determine_side(self, gs: list[int], position: RobotPosition, invert_side: bool = False):
        """
        Determine the side of the track and store the result in the readings list.

        :param gs: A list of sensor readings.
        :param position: The current position of the robot (LEFT, RIGHT, or MIDDLE).
        :param invert_side: If True, invert the side determination logic.
        """
        # If invert_side is True, reverse the sensor readings.
        if invert_side:
            gs = gs[::-1]  # reverse the list
        v = self.__determine_side(gs, position)
        # If invert_side is True, invert the determined side.
        if invert_side:
            if v == TrackSide.LEFT:
                v = TrackSide.RIGHT
            elif v == TrackSide.RIGHT:
                v = TrackSide.LEFT
        # Append the determined side to the readings list.
        self.readings.append(v)

    def get_probable_side(self) -> TrackSide:
        """
        Determine the most probable side of the track based on recent readings.

        :return: The most probable side (LEFT, RIGHT, or UNKNOWN) based on the readings.
                 If there are no readings or the sides are equally detected, return UNKNOWN.
        """
        # If there are no readings, return UNKNOWN.
        if len(self.readings) == 0:
            values = [TrackSide.UNKNOWN]
        else:
            # Use the last 'steps_to_determine_side' readings or all readings if fewer exist.
            values = self.readings[-self.steps_to_determine_side:] if self.steps_to_determine_side < len(self.readings) else self.readings

        # Count the occurrences of LEFT and RIGHT in the readings.
        left = values.count(TrackSide.LEFT)
        right = values.count(TrackSide.RIGHT)

        # Determine the most probable side based on the counts.
        if left == right:
            dominant = left
            minority = right
            result = TrackSide.UNKNOWN
        elif left > right:
            dominant = left
            minority = right
            result =  TrackSide.LEFT
        else:
            dominant = right
            minority = left
            result = TrackSide.RIGHT

        self.certainty_of_last_guess = self.certainty_of_guess(dominant, minority, len(values))

        return result



    def certainty_of_guess(self, dominant_side: int, minority_side: int, total_values: int) -> float:
        """
        Calculate the certainty of the guess based on the number of readings.
        :param dominant_side: The number of readings for the dominant side, e.g. the side guessed where the robot is.
        :param minority_side: The number of readings for the minority side.
        :param total_values: The total number of readings, including the UNKNOWN readings.
        :return: The certainty of the guess as a float between 0 and 1.
        """
        return (dominant_side - minority_side) / total_values







