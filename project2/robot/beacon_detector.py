

from project2.core.beacon import Beacon
from project2.robot.grey_area import GreyArea


class BeaconDetector:
    """
    Detects beacons on the track.
    """
    def __init__(self, grey_area: GreyArea, grey_min_value: int,
                 grey_max_value: int, beacons: dict[int, Beacon]):
        """
        BeaconDetector constructor.
        :param grey_area: GreyArea object to define a gray area.
        :param grey_min_value: the minimum value of the ground to be considered grey.
        :param grey_max_value: the maximum value of the ground to be considered grey.
        :param beacons: a dictionary of the beacons on the track,
        where the key is the number of grey ares of the beacon
        and the value is the Beacon object.
        """
        self.grey_length: int = 0 # length of the grey area the robot is currently in
        self.grey_distance: int = 0 # distance from the last grey area
        self.grey_area_count: int = 0 # number of grey areas the robot has passed in the current possible beacon
        self.__new_beacon_event: bool = False # if a new beacon was found
        self.last_beacon: Beacon | None = None # the last beacon that was detected

        self.grey_area: GreyArea = grey_area
        self.grey_min_value: int = grey_min_value
        self.grey_max_value: int = grey_max_value
        self.beacons: dict[int, Beacon] = beacons

    def reset(self):
        """
        Reset the detector to its initial state.
        :return: None
        """
        self.grey_length = 0
        self.grey_distance = 0
        self.grey_area_count = 0

    def receive_ground(self, gs: list[int]):
        """
        Receive the ground sensor values and check if the robot is in a grey area.
        :param gs: list of the ground sensor values.
        :return: None
        """
        # print(gs)
        if any([self.in_grey(x) for x in gs]):
            self.handle_on_grey()
        else:
            self.handle_off_grey()

        self.check_for_beacon_detection()

    def check_for_beacon_detection(self):
        """
        Check if the robot is in a grey area and if it has passed enough grey areas to detect a beacon.
        :return:
        """
        if self.grey_distance >= self.grey_area.grey_distance_max():
            # print(f"grey areas: {self.grey_area_count}")
            detected_beacon: Beacon = self.beacons.get(self.grey_area_count)
            if detected_beacon is not None:
                self.__new_beacon_event = True
                self.last_beacon = detected_beacon
            self.reset()

    def handle_off_grey(self):
        """
        Handle the case when the robot is not in a grey area.
        :return:
        """
        if self.grey_length > 0:
            if self.grey_length >= self.grey_area.grey_min_length():
                print(f"grey length: {self.grey_length}")
                self.grey_area_count += 1
            self.grey_length = 0
        if self.grey_area_count > 0:
            self.grey_distance += 1

    def handle_on_grey(self):
        """
        Handle the case when the robot is in a grey area.
        :return:
        """
        # print("grey")
        self.grey_length += 1
        self.grey_distance = 0

    def in_grey(self, value: int) -> bool:
        """
        Check if the value is in the grey area.
        :param value: value of one of the ground sensors.
        :return: bool: True if the value is in the grey area, False otherwise.
        """
        return self.grey_min_value <= value <= self.grey_max_value

    def new_beacon_found(self) -> bool:
        """Return true if a new beacon was found. Not idempotent, so it should be called only once per event.
        :return: bool: True if a new beacon was found, False otherwise."""
        has_event = self.__new_beacon_event
        self.__new_beacon_event = False
        return has_event
