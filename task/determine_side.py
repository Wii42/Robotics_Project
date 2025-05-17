"""
determine_side.py

Module for determining which side of the track the robot is on, based on ground sensor readings
and the robot's position. This is useful for autonomous navigation tasks where the robot must
adapt its behavior depending on its lane or side of the track.

Classes:
    TrackSide (Enum): Enum representing possible sides of the track.
    DetermineSide: Class for determining the robot's side using sensor data and position.

Authors:
    Lukas Künzi
    Thirith Yang

Date:
    18th May 2025
"""

from enum import Enum

from challenge.robot.track_follower import RobotPosition

class TrackSide(Enum):
    """
    Enum representing the possible sides of the track.
    """
    LEFT = 0
    RIGHT = 1
    UNKNOWN = 2

class DetermineSide:
    """
    The DetermineSide class is responsible for determining which side of the track
    the robot is on based on sensor readings and the robot's position.

    Attributes:
        grey_max_value (int): Maximum value for a sensor to be considered grey.
        grey_min_value (int): Minimum value for a sensor to be considered grey.
        readings (list[TrackSide]): History of detected sides.
        steps_to_determine_side (int): Number of readings to consider for side determination.
        certainty_of_last_guess (float | None): Certainty of the last side guess.
    """

    def __init__(self, grey_max_value: int, grey_min_value: int, steps_to_determine_side: int):
        """
        Initialize the DetermineSide class with parameters for detecting the track side.

        Args:
            grey_max_value (int): The maximum value for an area to be considered grey.
            grey_min_value (int): The minimum value for an area to be considered grey.
            steps_to_determine_side (int): The number of readings to consider when determining the side.
        """
        self.grey_max_value = grey_max_value
        self.grey_min_value = grey_min_value
        self.readings: list[TrackSide] = []  # List of all readings indicating the robot's side.
        self.steps_to_determine_side = steps_to_determine_side
        self.certainty_of_last_guess = None

    def in_grey(self, value: int) -> bool:
        """
        Check if a given value falls within the grey range.

        Args:
            value (int): The value to check.

        Returns:
            bool: True if the value is within the grey range, False otherwise.
        """
        return self.grey_min_value <= value <= self.grey_max_value

    def in_white(self, value: int) -> bool:
        """
        Check if a given value is greater than the grey maximum, indicating white.

        Args:
            value (int): The value to check.

        Returns:
            bool: True if the value is greater than the grey maximum, False otherwise.
        """
        return value > self.grey_max_value

    def __determine_side(self, gs: list[int], position: RobotPosition) -> TrackSide:
        """
        Determine the side of the track based on sensor readings and the robot's position.

        Args:
            gs (list[int]): A list of sensor readings.
            position (RobotPosition): The current position of the robot (LEFT, RIGHT, or MIDDLE).

        Returns:
            TrackSide: The detected side (LEFT, RIGHT, or UNKNOWN).
        """
        # If robot is on the left, check leftmost sensor for white or grey
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

        Args:
            gs (list[int]): A list of sensor readings.

        Returns:
            list[str]: A list of color labels corresponding to the sensor readings.
        """
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

        Args:
            gs (list[int]): A list of sensor readings.
            position (RobotPosition): The current position of the robot (LEFT, RIGHT, or MIDDLE).
            invert_side (bool, optional): If True, invert the side determination logic.
        """
        # Optionally invert the sensor readings for mirrored logic
        if invert_side:
            gs = gs[::-1]  # reverse the list
        v = self.__determine_side(gs, position)
        # Invert the result if invert_side is True
        if invert_side:
            if v == TrackSide.LEFT:
                v = TrackSide.RIGHT
            elif v == TrackSide.RIGHT:
                v = TrackSide.LEFT
        self.readings.append(v)

    def get_probable_side(self) -> TrackSide:
        """
        Determine the most probable side of the track based on recent readings.

        Returns:
            TrackSide: The most probable side (LEFT, RIGHT, or UNKNOWN) based on the readings.
        """
        # Use the last N readings for decision, or all if not enough
        if len(self.readings) == 0:
            values = [TrackSide.UNKNOWN]
        else:
            values = self.readings[-self.steps_to_determine_side:] if self.steps_to_determine_side < len(self.readings) else self.readings

        left = values.count(TrackSide.LEFT)
        right = values.count(TrackSide.RIGHT)

        # Decide which side is dominant, or UNKNOWN if equal
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

        # Store certainty for external use
        self.certainty_of_last_guess = self.certainty_of_guess(dominant, minority, len(values))

        return result

    def certainty_of_guess(self, dominant_side: int, minority_side: int, total_values: int) -> float:
        """
        Calculate the certainty of the guess based on the number of readings.

        Args:
            dominant_side (int): The number of readings for the dominant side.
            minority_side (int): The number of readings for the minority side.
            total_values (int): The total number of readings, including the UNKNOWN readings.

        Returns:
            float: The certainty of the guess as a float between 0 and 1.
        """
        return (dominant_side - minority_side) / total_values







