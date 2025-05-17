"""
main.py

MarioKart e-puck Robot Control Script

This script implements the main control logic for an autonomous e-puck robot designed for a MarioKart-inspired robotics project.
It manages the robot's state machine, including line following, lane changing, obstacle and block detection, and end-of-track detection.
The MarioKart class encapsulates all robot behaviors and state transitions, providing a robust framework for autonomous navigation and interaction with the environment.

Modules & Classes:
------------------
- KartState (Enum): Represents the different operational states of the robot.
- MarioKart: Main class for controlling the robot's behavior and state transitions.

Key Features:
-------------
- Line following and alignment using ground sensors.
- Lane changing based on detected colored blocks.
- Obstacle and e-puck detection using proximity sensors.
- End-of-track detection using camera and time-of-flight sensors.
- Communication support for multi-robot coordination.

Usage:
------
Run this script as the main entry point. Optionally, provide the robot's IP address as a command-line argument.

Example:
    python main.py 192.168.2.210

Authors:
--------
- Lukas Künzi
- Thirith Yang

Date:
------
18th May 2025
"""

import sys
from enum import Enum

from typing import Callable

from unifr_api_epuck import wrapper
import numpy as np
import os

import led_indicators as led

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck, ColorDetected

from challenge.robot.sensor_memory import SensorMemory
from challenge.robot.step_counter import StepCounter
from challenge.robot.track_follower import TrackFollower
from determine_side import DetermineSide
from line_alignment import LineAlignment
import utils
from calibration import normalize_gs

# Constants for robot configuration
MY_IP = '192.168.2.210'
LINE_MAX_VALUE: int = 600
GREY_MAX_VALUE: int = 800

STEPS_TO_DETERMINE_SIDE: int = 100

OBJECT_DETECTIONS_DIR = "./object_detections"


class KartState(Enum):
    """
    Enum representing the different states of the MarioKart robot.
    """
    LINE_FOLLOWING_AND_ALIGNMENT = 0
    CHANGE_LANE_TO_LEFT = 1
    CHANGE_LANE_TO_RIGHT = 2
    WAIT_FOR_START = 3
    FINISHED = 4
    MAYBE_END = 5


def create_dir_for_detections():
    try:
        os.mkdir(OBJECT_DETECTIONS_DIR)  # Create directory for object detections
    except OSError as error:
        print(error)


class MarioKart:
    """
    The MarioKart class controls the robot's behavior, including line following,
    lane changing, and obstacle detection.
    """

    def __init__(self, robot_ip: str, norm_speed: float = 3, communicate: bool = True):
        """
        Initialize the MarioKart robot.

        :param robot_ip: The IP address of the robot.
        :param norm_speed: The normal speed of the robot.
        :param communicate: Enable communication with race manager and other robots.
        """
        self.robot_ip: str = robot_ip
        self.norm_speed: float = norm_speed
        self.robot: WifiEpuck | None = None  # Robot instance (initialized later)
        self.counter: StepCounter = StepCounter()  # Step counter for general tracking
        self.line_follower: TrackFollower | None = None  # Line follower instance
        self.ground_sensor_memory: SensorMemory = SensorMemory(3)  # Memory for ground sensor readings
        self.determine_side: DetermineSide = DetermineSide(GREY_MAX_VALUE, LINE_MAX_VALUE, STEPS_TO_DETERMINE_SIDE)
        self.line_alignment: LineAlignment = LineAlignment()  # Line alignment logic
        self.check_side_necessary: bool = True  # Flag to check if side alignment is needed
        self.current_state: KartState = KartState.WAIT_FOR_START if communicate else KartState.LINE_FOLLOWING_AND_ALIGNMENT  # Initial state
        self.old_state: KartState | None = None  # Previous state (used for state transitions)
        self.state_counter = StepCounter()  # Counter for state transitions
        self.could_be_first: bool = True  # Flag to check if the robot could be the first or if the other robot has already finished
        self.communicate: bool = communicate  # Flag for communication

    def states(self) -> dict[KartState, Callable]:
        """
        Returns a dictionary mapping each KartState to its corresponding handler function.
        """
        return {KartState.LINE_FOLLOWING_AND_ALIGNMENT: self.line_following_and_alignment,
                KartState.CHANGE_LANE_TO_LEFT: self.change_lane_to_left,
                KartState.CHANGE_LANE_TO_RIGHT: self.change_lane_to_right,
                KartState.WAIT_FOR_START: lambda: True,
                KartState.FINISHED: self.on_end_detected,
                KartState.MAYBE_END: self.maybe_end,
                }

    def init_robot(self):
        """
        Initialize the robot, including sensors, ground calibration, and model loading.
        """
        self.robot = wrapper.get_robot(self.robot_ip)
        create_dir_for_detections()
        self.robot.init_ground()  # Initialize ground sensors
        self.robot.initiate_model()  # Load the robot's model
        self.robot.init_sensors()  # Initialize other sensors
        self.robot.calibrate_prox()  # Calibrate proximity sensors
        if self.communicate:
            self.robot.init_client_communication()
            print("client communication initialized")

    def init_line_follower(self):
        """
        Initialize the line follower with the robot and the maximum value for the ground
        to be considered black. Should only be called after the robot is initialized.
        """
        self.line_follower: TrackFollower = TrackFollower(self.robot, self.norm_speed, LINE_MAX_VALUE)

    #######################################################################
    # State behaviours

    def line_following_and_alignment(self):
        """
        Handles the main line following and alignment logic.
        Adjusts alignment if necessary and follows the track using the line follower.
        """

        if self.state_counter.get_steps() > STEPS_TO_DETERMINE_SIDE and self.check_side_necessary:
            self.line_alignment.check_line_alignment(self.determine_side.get_probable_side())
            self.check_side_necessary = False
            self.line_follower.line_max_value = GREY_MAX_VALUE

        # Follow the track using the line follower
        if not self.line_follower.follow_track(
                self.ground_sensor_memory.get_average(),
                use_two_sensors_approach=True,
                invert_side=self.line_alignment.get_follow_left_side()):
            return False
        self.determine_side.determine_side(self.ground_sensor_memory.get_average(), self.line_follower.position,
                                           invert_side=self.line_alignment.get_follow_left_side())

        self.set_state(self.change_lanes_detection())
        self.while_moving()

        return True

    def change_lanes_detection(self):
        """
        Detects if a lane change is necessary based on block detection.
        Returns the next state depending on detected block color and current alignment.
        """
        picture_frequency = 50

        if self.counter.get_steps() % picture_frequency == 0 and self.state_counter.get_steps() > 30:
            self.robot.init_camera(OBJECT_DETECTIONS_DIR)

        curr_block = None
        if self.counter.get_steps() % picture_frequency == 1 and self.state_counter.get_steps() >= STEPS_TO_DETERMINE_SIDE:
            curr_block = utils.detect_block(self.robot, 30, 15)
            self.robot.disable_camera()

        led.set_led_on_block(self.robot, curr_block)

        if curr_block is not None:
            is_left: bool = self.line_alignment.follow_left_side

            if is_left and (curr_block == "Green Block"):
                print("change to right")
                return KartState.CHANGE_LANE_TO_RIGHT
            if not is_left and (curr_block == "Red Block"):
                print("change to left")
                return KartState.CHANGE_LANE_TO_LEFT
        return self.current_state

    def change_lanes(self, change_to_left: bool):
        """
        Handle the lane-changing process.
        This method adjusts the robot's speed and checks for line detection to complete the lane change.

        Turns the robot to the left or right lane based on the provided parameter, then drives straight until the other line is detected.
        :param change_to_left: True if changing to the left lane, False otherwise.
        :return: True if the lane change is complete.
        """

        # Adjust speed for lane change
        if self.state_counter.get_steps() < 100 / self.norm_speed:
            speeds = [self.norm_speed * 2, self.norm_speed * 0.5]
            if change_to_left:
                speeds.reverse()
            self.robot.set_speed(*speeds)
        else:
            self.robot.set_speed(self.norm_speed, self.norm_speed)

        # Detect the line to complete the lane change
        has_line_detected = self.line_detection(self.ground_sensor_memory.get_average())
        if has_line_detected and self.state_counter.get_steps() > 300 / self.norm_speed:
            self.set_state(KartState.LINE_FOLLOWING_AND_ALIGNMENT)
            self.line_alignment.follow_left_side = not self.line_alignment.follow_left_side
            self.check_side_necessary = False
        return True

    def change_lane_to_right(self):
        """
        Change to the right lane.
        """
        self.change_lanes(change_to_left=False)
        self.while_moving()
        return True

    def change_lane_to_left(self):
        """
        Change to the left lane.
        """
        self.change_lanes(change_to_left=True)
        self.while_moving()
        return True

    def line_detection(self, gs: list[int]) -> bool:
        """
        Detect the other line using the ground sensors.
        The other line is considered detected if at least one sensor detects the white ground on the other side of the line.

        :return: True if the line is detected, False otherwise.
        """

        is_white = [True for sensor in gs if sensor > self.determine_side.grey_max_value + 50]
        return any(is_white)

    def maybe_end(self):
        """
        Check if the robot is at the end of the track using camera and color detection.

        :return: True if the end is detected, False otherwise.
        """

        if self.state_counter.get_steps() == 0:
            self.robot.init_camera(OBJECT_DETECTIONS_DIR)
            return False
        elif self.state_counter.get_steps() >= 1:
            img = np.array(self.robot.get_camera())
            detections: list[ColorDetected] = self.robot.get_colordetection(img, saveimg=True, savemasks=True)
            sum_area = 0
            for detection in detections:
                print(detection.label, detection.area)
                sum_area += detection.area

            print("sum_area: ", sum_area)

            if 1000 > sum_area:
                if self.current_state != KartState.FINISHED and self.communicate:
                    self.robot.send_msg("goal")
                self.set_state(KartState.FINISHED)
            else:
                self.robot.disable_camera()
                self.set_state(self.old_state)
        return True

    ####################################################################################################

    def detect_epucks(self):
        """
        Detect nearby ePuck robots using proximity sensors.

        :return: True if another ePuck is detected, False otherwise.
        """
        prox_values = self.robot.get_calibrate_prox()
        av_front_prox = (prox_values[6] + prox_values[7] * 2 + prox_values[0] * 2 + prox_values[1]) / 4

        detect_epuck: bool = av_front_prox > 150

        led.set_led_on_epuck(self.robot, detect_epuck)
        return detect_epuck

    def detect_end(self):
        """
        Detect the end of the track using the time-of-flight sensor.

        :return: True if the end is detected, False otherwise.
        """
        distance = self.robot.get_tof()
        print("distance: ", distance)

        if distance <= 50:
            self.set_state(KartState.MAYBE_END)

            return False
        return False

    def set_state(self, new_state: KartState):
        """
        Set the robot's state and reset the state counter if the state changes.

        :param new_state: The new state to transition to.
        """
        if new_state != self.current_state:
            self.state_counter.reset()
            self.old_state = self.current_state
        self.current_state = new_state

    def run(self):
        """
        Main loop to run the robot. Initializes the robot and handles state transitions.
        """
        self.init_robot()
        self.init_line_follower()

        print("init complete")

        no_error: bool = True
        assert (self.robot is not None)
        assert (self.line_follower is not None)
        while self.robot.go_on() and no_error:
            gs: list[int | float] = self.robot.get_ground()
            gs = normalize_gs(gs, self.robot_ip)
            self.ground_sensor_memory.update_memory(gs)
            states = self.states()
            no_error = states[self.current_state]()
            if self.communicate:
                self.listen_for_messages()

        self.robot.clean_up()

    def while_moving(self) -> bool:
        """
        Called while the robot is moving. Handles end detection, ePuck detection, LED updates, and step counting.
        """

        self.detect_end()
        if self.detect_epucks():
            self.robot.set_speed(0, 0)
        led.set_led_on_side(self.robot, self.line_alignment.follow_left_side)
        self.counter.step()
        self.state_counter.step()
        return True

    def on_end_detected(self):
        """
        Called when the end of the track is detected. Stops the robot and activates goal LEDs.
        """
        print("detected end")
        self.robot.set_speed(0, 0)
        led.set_leds_on_goal(self.robot)
        return True

    def listen_for_messages(self):
        """
        Listen for incoming messages from other robots or the race manager and handle state transitions accordingly.
        """
        while self.robot.has_receive_msg():
            msg = self.robot.receive_msg()
            print(msg)
            if self.current_state == KartState.WAIT_FOR_START:
                if msg == "start":
                    self.set_state(KartState.LINE_FOLLOWING_AND_ALIGNMENT)
            elif not self.current_state == KartState.FINISHED:
                if msg == "goal":
                    self.could_be_first = False


if __name__ == "__main__":
    # Entry point for running the MarioKart robot.
    print(len(sys.argv))
    if len(sys.argv) == 2:
        ip = sys.argv[1]
        print("ip: ", ip)
    else:
        ip = MY_IP
    MarioKart(ip, norm_speed=3, communicate=False).run()
