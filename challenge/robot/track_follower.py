"""
track_follower.py

Implements the logic for following a track using ground sensors for the ePuck robot.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

from enum import Enum


class RobotPosition(Enum):
    IS_LEFT = 0
    IS_RIGHT = 1
    IS_MIDDLE = 2
    ERROR = 3
    UNKNOWN = 4

class TrackFollower:
    """
    The TrackFollower class provides methods to follow a track using ground sensor values.
    It supports different approaches for interpreting sensor data and adjusts the robot's
    speed and direction accordingly.
    """
    def __init__(self, robot, norm_speed: float, line_max_value: int):
        """
        Initialize the TrackFollower.

        Args:
            robot: The robot instance to control.
            norm_speed (float): The robot's normal speed.
            line_max_value (int): The maximum sensor value considered as being on the line.
        """
        self.robot = robot
        self.norm_speed = norm_speed
        self.current_speed = [0, 0]
        self.position: RobotPosition = RobotPosition.UNKNOWN
        self.speed_factor: float = 1.0
        self.obstacle_speed_factor: float = 1
        self.line_max_value = line_max_value # the max brightness value for the line

    def on_line(self, value: int) -> bool:
        """
        Determine if a sensor value indicates the robot is on the line.

        Args:
            value (int): The ground sensor value.

        Returns:
            bool: True if the value is below the line_max_value, False otherwise.
        """
        return value < self.line_max_value

    def binary_approach(self, gs: list[int]) -> tuple[float, float] | None:
        """
        Try to follow the track staying in the middle of the line using a binary approach, e.g. the values of the ground
         sensor are classified into either on the track or not on the track.

        Args:
            gs (list[int]): List of ground sensor values.

        Returns:
            tuple[float, float] | None: (left_speed_factor, right_speed_factor) or None if error.
        """
        black_list: list[bool] = [self.on_line(v) for v in gs]
        match black_list:
            case [True, True, False]:  # is right
                self.position = RobotPosition.IS_RIGHT
                return 1, 2
            case [False, True, True]:  # is left
                self.position = RobotPosition.IS_LEFT
                return 2, 1
            case [True, True, True]:  # middle
                self.position = RobotPosition.IS_MIDDLE
                return 2, 2
            case [True, False, False]:  # far right
                self.position = RobotPosition.IS_RIGHT
                return -2, 2
            case [False, False, True]:  # far left
                self.position = RobotPosition.IS_LEFT
                return 2, -2
            case [True, False, True]:  # path splits
                self.position = RobotPosition.UNKNOWN
                return -2, 2
            case [False, True, False]:  # middle
                self.position = RobotPosition.IS_MIDDLE
                return 2, 2
            case _:  # else
                self.position = RobotPosition.ERROR
                print(f"ERROR: black_list = {black_list}")
                return None

    def two_sensors_approach(self, gs: list[int]) -> tuple[float, float] | None:
        """
        Try to follow the track with only two sensors on the line and one sensor off the line,
        which results in following one edge of the line.

        Args:
            gs (list[int]): List of ground sensor values.

        Returns:
            tuple[float, float] | None: (left_speed_factor, right_speed_factor) or None if error.
        """
        black_list: list[bool] = [self.on_line(v) for v in gs]
        match black_list:
            case [False, False, False]:  # 0: no black
                self.position = RobotPosition.UNKNOWN
                print("WARNING, no black")
                return -1, 1
            case [False, False, True]:  # 1: extremely far left
                self.position = RobotPosition.IS_LEFT
                return 1, -1
            case [False, True, False]:  # 2: ERROR
                self.position = RobotPosition.UNKNOWN
                print("WARNING, 010")
                return 0.5, 0.5
            case [False, True, True]:  # 3: far left
                self.position = RobotPosition.IS_LEFT
                return 1, -1
            case [True, False, False]:  # 4: right
                self.position = RobotPosition.IS_RIGHT
                return 0, 1
            case [True, False, True]:  # 5: ERROR
                self.position = RobotPosition.UNKNOWN
                print("WARNING, 101")
                return 1, 1 # handle as middle
            case [True, True, False]:  # 6: middle
                self.position = RobotPosition.IS_MIDDLE
                return 1, 1
            case [True, True, True]:  # 7: left
                self.position = RobotPosition.IS_LEFT
                return 1, 0
            case _:  # else
                print("ERROR: should not be possible")
                self.position = RobotPosition.ERROR
                return None

    def follow_track(self, gs: list[int], use_two_sensors_approach: bool = False, invert_side: bool = False) -> bool:
        """
        Follow the track by adjusting the robot's speed based on ground sensor readings.

        Args:
            gs (list[int]): List of ground sensor values.
            use_two_sensors_approach (bool): If True, use the two-sensor approach. Otherwise, use binary approach.
            invert_side (bool): If True, reverse the sensor order and swap speeds (for mirrored tracks).

        Returns:
            bool: True if a valid track-following action was taken, False otherwise.
        """
        if invert_side:
            gs.reverse()
        if use_two_sensors_approach:
            r = self.two_sensors_approach(gs)
        else:
            r = self.binary_approach(gs)
        if r is not None:
            if invert_side:
                r = r[::-1] # swap left and right
            speed_factor = min(self.speed_factor, self.obstacle_speed_factor)
            base_speed = self.norm_speed * speed_factor
            speed_left = r[0] * base_speed
            speed_right = r[1] * base_speed
            self.robot.set_speed(speed_left, speed_right)
            self.current_speed = [speed_left, speed_right]

        return r is not None