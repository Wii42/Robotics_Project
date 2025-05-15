from enum import Enum

from unifr_api_epuck import wrapper
import os

from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck

from project2.robot.sensor_memory import SensorMemory
from project2.robot.step_counter import StepCounter
from project2.robot.track_follower import TrackFollower
from determine_side import TrackSide
from determine_side import DetermineSide
from line_alignment import LineAlignment
import utils

# Constants for robot configuration
MY_IP = '192.168.2.208'
LINE_MAX_VALUE: int = 500  # Maximum value for the line to be considered black
GREY_MAX_VALUE: int = 750  # Maximum value for an area to be considered grey
STEPS_TO_DETERMINE_SIDE: int = 20  # Number of steps to determine the side
OBJECT_DETECTIONS_DIR = "./object_detections"  # Directory for storing object detection data


class KartState(Enum):
    """
    Enum representing the different states of the MarioKart robot.
    """
    LINE_FOLLOWING_AND_ALIGNMENT = 0
    CHANGE_LANE_TO_LEFT = 1
    CHANGE_LANE_TO_RIGHT = 2


class MarioKart:
    """
    The MarioKart class controls the robot's behavior, including line following,
    lane changing, and obstacle detection.
    """

    def __init__(self, robot_ip: str, norm_speed: float = 3):
        """
        Initialize the MarioKart robot.

        :param robot_ip: The IP address of the robot.
        :param norm_speed: The normal speed of the robot.
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
        self.current_state: KartState = KartState.LINE_FOLLOWING_AND_ALIGNMENT  # Initial state
        self.state_counter = StepCounter()  # Counter for state transitions

    def states(self) -> dict[KartState, object]:
        """
        Map each state to its corresponding function.

        :return: A dictionary mapping KartState to its handler function.
        """
        return {
            KartState.LINE_FOLLOWING_AND_ALIGNMENT: self.line_following_and_alignment,
            KartState.CHANGE_LANE_TO_LEFT: self.change_lane_to_left,
            KartState.CHANGE_LANE_TO_RIGHT: self.change_lane_to_right
        }

    def init_robot(self):
        """
        Initialize the robot, including sensors, ground calibration, and model loading.
        """
        self.robot = wrapper.get_robot(MY_IP)
        try:
            os.mkdir(OBJECT_DETECTIONS_DIR)  # Create directory for object detections
        except OSError as error:
            print(error)
        self.robot.init_ground()  # Initialize ground sensors
        self.robot.initiate_model()  # Load the robot's model
        self.robot.init_sensors()  # Initialize other sensors
        self.robot.calibrate_prox()  # Calibrate proximity sensors

    def init_line_follower(self):
        """
        Initialize the line follower with the robot and the maximum value for the ground
        to be considered black. Should only be called after the robot is initialized.
        """
        self.line_follower: TrackFollower = TrackFollower(self.robot, self.norm_speed, LINE_MAX_VALUE)

    def line_following_and_alignment(self):
        """
        Handle the line following and alignment state. Aligns the robot to the correct
        side of the line and follows the track.
        """
        # Check if side alignment is necessary
        if self.state_counter.get_steps() > STEPS_TO_DETERMINE_SIDE * 2 and self.check_side_necessary:
            self.line_alignment.check_line_alignment(self.determine_side.get_probable_side())
            self.check_side_necessary = False

        # Follow the track using the line follower
        if not self.line_follower.follow_track(
                self.ground_sensor_memory.get_average(),
                use_two_sensors_approach=True,
                invert_side=self.line_alignment.get_follow_left_side()):
            return False

        # Determine the side and update the state
        self.determine_side.determine_side(
            self.ground_sensor_memory.get_average(),
            self.line_follower.position,
            invert_side=self.line_alignment.get_follow_left_side())
        self.set_state(self.change_lanes_detection())
        return True

    def change_lanes_detection(self):
        """
        Detect if a lane change is necessary based on block detection and the current side.

        :return: The next state (either lane change or continue line following).
        """
        # Periodically initialize the camera for object detection
        if self.counter.get_steps() % 50 == 0:
            self.robot.init_camera(OBJECT_DETECTIONS_DIR)

        curr_block = None
        if self.counter.get_steps() % 50 == 1:
            curr_block = utils.block_detector(self.robot, 30, 20)
            self.robot.disable_camera()

        if curr_block is not None:
            curr_side = self.determine_side.get_probable_side()

            # Decide lane change based on detected block and current side
            if curr_side == TrackSide.LEFT and curr_block == "Green Block":
                return KartState.CHANGE_LANE_TO_RIGHT
            if curr_side == TrackSide.RIGHT and curr_block == "Red Block":
                return KartState.CHANGE_LANE_TO_LEFT

        return KartState.LINE_FOLLOWING_AND_ALIGNMENT

    def change_lanes(self, change_to_left: bool):
        """
        Handle the lane-changing process.

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
        if self.line_detection() and self.state_counter.get_steps() > 300 / self.norm_speed:
            self.set_state(KartState.LINE_FOLLOWING_AND_ALIGNMENT)
            self.line_alignment.follow_left_side = not self.line_alignment.follow_left_side
            self.check_side_necessary = True
        return True

    def change_lane_to_right(self):
        """
        Change to the right lane.
        """
        return self.change_lanes(change_to_left=False)

    def change_lane_to_left(self):
        """
        Change to the left lane.
        """
        return self.change_lanes(change_to_left=True)

    def line_detection(self):
        """
        Detect if the robot is on the line based on ground sensor readings.

        :return: True if the line is detected, False otherwise.
        """
        detections: list[int] = self.ground_sensor_memory.get_average()
        is_white = [True for detection in detections if detection > self.determine_side.grey_max_value + 50]
        if any(is_white):
            print("Detected white: ", detections)
            return True
        return False

    def detect_epucks(self):
        """
        Detect nearby ePuck robots using proximity sensors.

        :return: True if another ePuck is detected, False otherwise.
        """
        prox_values = self.robot.get_calibrate_prox()
        av_front_prox = (prox_values[6] * 2 + prox_values[7] + prox_values[0] + prox_values[1] * 2) / 4
        return av_front_prox > 100

    def detect_end(self):
        """
        Detect the end of the track using the time-of-flight sensor.

        :return: True if the end is detected, False otherwise.
        """
        distance = self.robot.get_tof()
        return distance <= 50

    def set_state(self, new_state: KartState):
        """
        Set the robot's state and reset the state counter if the state changes.

        :param new_state: The new state to transition to.
        """
        if new_state != self.current_state:
            self.state_counter.reset()
        self.current_state = new_state

    def run(self):
        """
        Main loop to run the robot. Initializes the robot and handles state transitions.
        """
        self.init_robot()
        self.init_line_follower()

        print("Initialization complete")

        no_error = True
        assert self.robot is not None
        assert self.line_follower is not None
        while self.robot.go_on() and no_error:
            gs: list[int] = self.robot.get_ground()
            self.ground_sensor_memory.update_memory(gs)
            states = self.states()
            no_error = states[self.current_state]()

            self.counter.step()
            self.state_counter.step()

        self.robot.clean_up()


if __name__ == "__main__":
    MarioKart(MY_IP, norm_speed=3).run()
