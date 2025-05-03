from enum import Enum

from beacon import Beacon
from project2.step_counter import StepCounter

class BeaconDetector:

    def __init__(self, robot_norm_speed: float, grey_min_length: float, grey_distance_max: float, grey_min_value: int,
                 grey_max_value: int, beacons: dict[int, Beacon], step_counter: StepCounter):
        self.grey_length: int = 0
        self.grey_distance: int = 0
        self.grey_area_count: int = 0
        self.__new_beacon_event: bool = False
        self.last_beacon: Beacon | None = None
        self.last_beacon_start: int | None = None # last step when the grey area started
        self.last_beacon_end: int | None = None # last step when the grey area ended

        self.robot_norm_speed: float = robot_norm_speed
        self.grey_min_length: float = grey_min_length
        self.grey_distance_max: float = grey_distance_max
        self.grey_min_value: int = grey_min_value
        self.grey_max_value: int = grey_max_value
        self.beacons: dict[int, Beacon] = beacons
        self.step_counter: StepCounter = step_counter

    def reset(self):
        self.grey_length = 0
        self.grey_distance = 0
        self.grey_area_count = 0

    def receive_ground(self, gs: list[int]):
        # print(gs)
        if any([self.in_grey(x) for x in gs]):
            self.handle_on_grey()
        else:
            self.handle_off_grey()

        self.check_for_beacon_detection()

    def check_for_beacon_detection(self):
        if self.grey_distance >= self.grey_distance_max:
            # print(f"grey areas: {self.grey_area_count}")
            detected_beacon: Beacon = self.beacons.get(self.grey_area_count)
            if detected_beacon is not None:
                self.__new_beacon_event = True
                self.last_beacon = detected_beacon
            self.reset()

    def handle_off_grey(self):
        if self.grey_length > 0:
            if self.grey_length >= self.grey_min_length:
                print(f"grey length: {self.grey_length}")
                self.grey_area_count += 1
            self.grey_length = 0
        if self.grey_area_count > 0:
            self.grey_distance += 1

    def handle_on_grey(self):
        # print("grey")
        self.grey_length += 1
        self.grey_distance = 0
        self.last_beacon_start = self.step_counter.get_steps()

    def in_grey(self, value: int) -> bool:
        return self.grey_min_value <= value <= self.grey_max_value

    """Return if a new beacon was found. Not idempotent, so it should be called only once per event."""

    def new_beacon_found(self) -> bool:
        has_event = self.__new_beacon_event
        self.__new_beacon_event = False
        return has_event
