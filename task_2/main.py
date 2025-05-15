import sys
import os
from enum import Enum

from typing import Callable

from unifr_api_epuck import wrapper
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck

from project2.robot.sensor_memory import SensorMemory
from project2.robot.step_counter import StepCounter
from project2.robot.track_follower import TrackFollower
from determine_side import TrackSide
from determine_side import DetermineSide
from line_alignment import LineAlignment
import utils
from task_2.calibration import normalize_gs

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
        self.current_state: KartState = KartState.WAIT_FOR_START if communicate else KartState.LINE_FOLLOWING_AND_ALIGNMENT # Initial state
        self.state_counter = StepCounter()  # Counter for state transitions
        self.could_be_first: bool = True  # Flag to check if the robot could be the first or if the other robot has already finished
        self.communicate: bool = communicate  # Flag for communication

    def states(self) -> dict[KartState, Callable]:
        return {KartState.LINE_FOLLOWING_AND_ALIGNMENT: self.line_following_and_alignment,
                KartState.CHANGE_LANE_TO_LEFT: self.change_lane_to_left,
                KartState.CHANGE_LANE_TO_RIGHT: self.change_lane_to_right,
                KartState.WAIT_FOR_START: lambda: True,
                KartState.FINISHED: self.on_end_detected,
                }

    def init_robot(self):
        """
        Initialize the robot, including sensors, ground calibration, and model loading.
        """
        self.robot = wrapper.get_robot(self.robot_ip)
        try:
            os.mkdir(OBJECT_DETECTIONS_DIR)  # Create directory for object detections
        except OSError as error:
            print(error)
        self.robot.init_ground()  # Initialize ground sensors
        self.robot.initiate_model()  # Load the robot's model
        self.robot.init_sensors()  # Initialize other sensors
        self.robot.calibrate_prox()  # Calibrate proximity sensors
        if self.communicate:
            self.robot.init_client_communication()

    def init_line_follower(self):
        """
        Initialize the line follower with the robot and the maximum value for the ground
        to be considered black. Should only be called after the robot is initialized.
        """
        self.line_follower: TrackFollower = TrackFollower(self.robot, self.norm_speed, LINE_MAX_VALUE)

    def line_following_and_alignment(self):

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
        # print(determine_side.get_probable_side())
        # print()

        self.set_state(self.change_lanes_detection())
        self.while_moving()

        return True

    def change_lanes_detection(self):
        picture_frequency = 50

        if self.counter.get_steps() % picture_frequency == 0 and self.state_counter.get_steps() > 30:
            self.robot.init_camera(OBJECT_DETECTIONS_DIR)

        curr_block = None
        if self.counter.get_steps() % picture_frequency == 1 and self.state_counter.get_steps() >= STEPS_TO_DETERMINE_SIDE:
            curr_block = utils.block_detector(self.robot, 30, 15)
            self.robot.disable_camera()

        self.set_led_on_detected_block(curr_block)

        if curr_block is not None:
            if  self.line_alignment.follow_left_side :
                currSide = TrackSide.LEFT
            else:
                currSide = TrackSide.RIGHT
            confidence_level = self.determine_side.certainty_of_last_guess
            print("curr block: ", curr_block, " curr side: ", currSide, " confidence: ", confidence_level)
            if confidence_level >= 0:
                if (currSide == TrackSide.LEFT) and (curr_block == "Green Block"):
                    print("change to right")
                    return KartState.CHANGE_LANE_TO_RIGHT
                if (currSide == TrackSide.RIGHT) and (curr_block == "Red Block"):
                    print("change to left")
                    return KartState.CHANGE_LANE_TO_LEFT
        return KartState.LINE_FOLLOWING_AND_ALIGNMENT

    def set_led_on_detected_block(self, curr_block):
        if curr_block is None:
            self.robot.disable_led(3)
        elif curr_block == "Red Block":
            self.robot.enable_led(3, 100, 0, 0)
        elif curr_block == "Green Block":
            self.robot.enable_led(3, 0, 100, 0)

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

    def line_detection(self):
        """
        Detect if the robot is on the line based on ground sensor readings.

        :return: True if the line is detected, False otherwise.
        """
        detections: list[int] = self.ground_sensor_memory.get_average()
        is_white = [True for detection in detections if detection > self.determine_side.grey_max_value + 50]
        if any(is_white):
            # print("detected white: ", detections)
            return True
        return False

    ####################################################################################################

    def detect_epucks(self):
        """
        Detect nearby ePuck robots using proximity sensors.

        :return: True if another ePuck is detected, False otherwise.
        """
        prox_values = self.robot.get_calibrate_prox()
        av_front_prox = (prox_values[6] + prox_values[7] * 2 + prox_values[0] * 2 + prox_values[1]) / 4

        if av_front_prox > 150:
            self.robot.enable_led(0)
            return True
        else:
            self.robot.disable_led(0)
            return False

    def detect_end(self):
        """
        Detect the end of the track using the time-of-flight sensor.

        :return: True if the end is detected, False otherwise.
        """
        distance = self.robot.get_tof()
        if distance <= 50:
            return True
        return False

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

        print("init complete")

        no_error: bool = True
        assert (self.robot is not None)
        assert (self.line_follower is not None)
        while self.robot.go_on() and no_error:
            gs: list[int | float] = self.robot.get_ground()
            gs = normalize_gs(gs, self.robot_ip)
            self.ground_sensor_memory.update_memory(gs)
            # print(self.determine_side.get_probable_side())
            states = self.states()
            no_error = states[self.current_state]()
            #print(self.current_state)
            if self.communicate:
                self.listen_for_messages()





        self.robot.clean_up()

    def while_moving(self) -> bool:
        if self.detect_end():
            if self.current_state != KartState.FINISHED and self.communicate:
                self.robot.send_msg("goal")
            self.current_state = KartState.FINISHED
            print("detected end")
            return False
        if self.detect_epucks():
            print("detected epuck")
            #self.robot.set_speed(0, 0)
        if self.line_alignment.follow_left_side:  # left side = led 6
            self.robot.enable_led(6)
            self.robot.disable_led(2)
        else:  # right side = led 2
            self.robot.enable_led(2)
            self.robot.disable_led(6)
        self.counter.step()
        self.state_counter.step()
        return True

    def on_end_detected(self):
        print("detected end")
        self.robot.set_speed(0, 0)
        self.robot.enable_led(0)
        self.robot.enable_led(2)
        self.robot.enable_led(4)
        self.robot.enable_led(6)
        self.robot.enable_body_led()
        return True

    def init_gsensors_record(self):
        data = open("Gsensors.csv", "w")
        if data is None:
            print('Error opening data file!\n')
            return None

        # write header in CSV file
        data.write('step,')
        for i in range(self.robot.GROUND_SENSORS_COUNT):
            data.write('gs' + str(i) + ',')
        data.write('\n')
        return data

    def record_gsensors(self, data, gs):
        # write a line of data
        data.write(str(self.counter.get_steps()) + ',')
        for v in gs:
            data.write(str(v) + ',')
        data.write('\n')

    def listen_for_messages(self):
        while self.robot.has_receive_msg():
            msg = self.robot.receive_msg()
            print(msg)
            if self.current_state == KartState.WAIT_FOR_START:
                if msg == "start":
                    self.current_state = KartState.LINE_FOLLOWING_AND_ALIGNMENT
            elif not self.current_state == KartState.FINISHED:
                if msg == "goal":
                    self.could_be_first = False



if __name__ == "__main__":
    print(len(sys.argv))
    if len(sys.argv) == 2:
        ip = sys.argv[1]
        print("ip: ", ip)
    else:
        ip = MY_IP
    MarioKart(ip, norm_speed=3, communicate=False).run()
