"""
beacon_detector.py

Detects beacons on the track for the ePuck robot.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

from project2.core.beacon import Beacon
from project2.robot.grey_area import GreyArea


class BeaconDetector:
    """
    The BeaconDetector class is responsible for detecting beacons on the track
    by analyzing the ground sensor values of the robot. It keeps track of the
    number and length of grey areas passed, and determines when a beacon is detected
    based on predefined beacon patterns.
    """

    def __init__(self, grey_area: GreyArea, grey_min_value: int,
                 grey_max_value: int, beacons: dict[int, Beacon]):
        """
        Initialize the BeaconDetector.

        Args:
            grey_area (GreyArea): GreyArea object to define a gray area.
            grey_min_value (int): Minimum value of the ground to be considered grey.
            grey_max_value (int): Maximum value of the ground to be considered grey.
            beacons (dict[int, Beacon]): Dictionary of beacons on the track,
                where the key is the number of grey areas of the beacon
                and the value is the Beacon object.
        """
        self.grey_length: int = 0  # Length of the grey area the robot is currently in
        self.grey_distance: int = 0  # Distance from the last grey area
        self.grey_area_count: int = 0  # Number of grey areas passed in the current possible beacon
        self.__new_beacon_event: bool = False  # True if a new beacon was found
        self.last_beacon: Beacon | None = None  # The last beacon that was detected

        self.grey_area: GreyArea = grey_area
        self.grey_min_value: int = grey_min_value
        self.grey_max_value: int = grey_max_value
        self.beacons: dict[int, Beacon] = beacons

    def reset(self):
        """
        Reset the detector to its initial state.
        Resets the grey area length, distance, and area count.
        """
        self.grey_length = 0
        self.grey_distance = 0
        self.grey_area_count = 0

    def receive_ground(self, gs: list[int]):
        """
        Receive the ground sensor values and check if the robot is in a grey area.
        Updates the detector state based on the sensor readings.

        Args:
            gs (list[int]): List of the ground sensor values.
        """
        # Check if any ground sensor is in the grey area
        if any([self.in_grey(x) for x in gs]):
            self.handle_on_grey()
        else:
            self.handle_off_grey()

        # After updating state, check if a beacon has been detected
        self.check_for_beacon_detection()

    def check_for_beacon_detection(self):
        """
        Check if the robot has passed enough grey areas to detect a beacon.
        If a beacon is detected, set the event flag and store the beacon.
        """
        # If the distance since the last grey area exceeds the threshold, check for beacon
        if self.grey_distance >= self.grey_area.grey_distance_max():
            detected_beacon: Beacon = self.beacons.get(self.grey_area_count)
            if detected_beacon is not None:
                self.__new_beacon_event = True
                self.last_beacon = detected_beacon
            self.reset()

    def handle_off_grey(self):
        """
        Handle the case when the robot is not in a grey area.
        Increments the grey area count if a valid grey area was just left,
        and increases the distance from the last grey area.
        """
        # If the robot just left a grey area, check if it was long enough to count
        if self.grey_length > 0:
            if self.grey_length >= self.grey_area.grey_min_length():
                print(f"grey length: {self.grey_length}")
                self.grey_area_count += 1
            self.grey_length = 0
        # If any grey areas have been counted, increment the distance since last
        if self.grey_area_count > 0:
            self.grey_distance += 1

    def handle_on_grey(self):
        """
        Handle the case when the robot is in a grey area.
        Increments the current grey area length and resets the distance from the last grey area.
        """
        self.grey_length += 1
        self.grey_distance = 0

    def in_grey(self, value: int) -> bool:
        """
        Check if the value is in the grey area.

        Args:
            value (int): Value of one of the ground sensors.

        Returns:
            bool: True if the value is in the grey area, False otherwise.
        """
        return self.grey_min_value <= value <= self.grey_max_value

    def new_beacon_found(self) -> bool:
        """
        Return True if a new beacon was found.
        Not idempotent, so it should be called only once per event.

        Returns:
            bool: True if a new beacon was found, False otherwise.
        """
        has_event = self.__new_beacon_event
        self.__new_beacon_event = False
        return has_event
