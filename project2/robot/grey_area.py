"""
grey_area.py

Defines the GreyArea class for handling grey area detection logic for the ePuck robot.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

class GreyArea:
    """
    The GreyArea class provides methods to determine the minimum length
    and maximum distance between grey areas based on the robot's speed.
    This is used to help detect beacons by analyzing how long and how far apart
    the robot travels over grey areas.
    """
    def __init__(self, speed: float):
        """
        Initialize the GreyArea.

        Args:
            speed (float): The speed of the robot in rad/s. Used to calculate
                the time and steps required to cross a grey area.
        """
        self.norm_speed = speed

    def grey_min_length(self) -> float:
        """
        Calculate the minimum number of steps the robot should be in a grey area
        for it to be considered valid.

        Returns:
            float: Minimum steps in the grey area.
        """
        return 20 / self.norm_speed

    def grey_distance_max(self) -> float:
        """
        Calculate the maximum number of steps allowed between grey areas
        for them to be counted as part of the same beacon.

        Returns:
            float: Maximum steps between grey areas.
        """
        return 2 * self.grey_min_length()