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

MY_IP = '192.168.2.214'
LINE_MAX_VALUE: int = 500

STEPS_TO_DETERMINE_SIDE: int = 20

OBJECT_DETECTIONS_DIR = "./object_detections"


class KartState(Enum):
    LINE_FOLLOWING_AND_ALIGNMENT = (0, lambda mario_kart: mario_kart.line_following_and_alignment())
    CHANGE_LANE_TO_LEFT = (1, lambda mario_kart: mario_kart.change_lane_to_left())
    CHANGE_LANE_TO_RIGHT = (2, lambda mario_kart: mario_kart.change_lane_to_right())

    def __init__(self, value, function):
        self.value: int = value
        self.function = function

    def do(self, mario_kart: 'MarioKart'):
        return self.function(mario_kart)


class MarioKart:

    def __init__(self, robot_ip: str, norm_speed: float = 3):
        self.robot_ip: str = robot_ip
        self.norm_speed: float = norm_speed
        self.robot: WifiEpuck | None = None  # init later
        self.counter: StepCounter = StepCounter()
        self.line_follower: TrackFollower | None = None  # dependent on robot
        self.ground_sensor_memory: SensorMemory = SensorMemory(3)
        self.determine_side: DetermineSide = DetermineSide(750, LINE_MAX_VALUE, STEPS_TO_DETERMINE_SIDE)
        self.line_alignment: LineAlignment = LineAlignment()
        self.check_side_necessary: bool = True
        self.current_state: KartState = KartState.LINE_FOLLOWING_AND_ALIGNMENT
        self.step_of_last_detection = 0
        self.detected_lines = 0

    def init_robot(self):
        self.robot = wrapper.get_robot(MY_IP)
        try:
            os.mkdir(OBJECT_DETECTIONS_DIR)
        except OSError as error:
            print(error)
        self.robot.init_ground()

        self.robot.initiate_model()

        self.robot.init_sensors()
        self.robot.calibrate_prox()

    def init_line_follower(self):
        """
        Initialize the line follower with the robot and the max for the ground be considered black.
        Should only be called after the robot is initialized by self.init_robot().
        :return:
        """
        self.line_follower: TrackFollower = TrackFollower(self.robot, self.norm_speed, LINE_MAX_VALUE)

    def line_following_and_alignment(self):

        if self.counter.get_steps() > STEPS_TO_DETERMINE_SIDE and self.check_side_necessary:
            self.line_alignment.check_line_alignment(self.determine_side.get_probable_side())
            check_side_necessary = False

        # print(gs)
        # print(gs)
        # robot.set_speed(5,5)
        if not self.line_follower.follow_track(self.ground_sensor_memory.get_average(), use_two_sensors_approach=True,
                                               invert_side=self.line_alignment.get_follow_left_side()):
            return False
        self.determine_side.determine_side(self.ground_sensor_memory.get_average(), self.line_follower.position,
                                           invert_side=self.line_alignment.get_follow_left_side())
        # print(determine_side.get_probable_side())
        # print()
        self.current_state = self.change_lanes_detection()
        return True

    def change_lanes_detection(self):

        if self.counter.get_steps() % 50 == 0:
            self.robot.init_camera(dir)

        curr_block = None
        if self.counter.get_steps() % 50 == 1:
            curr_block = utils.block_detector(self.robot, 30, 20)
            self.robot.disable_camera()
        if curr_block is not None:
            currSide = self.determine_side.get_probable_side()

            if (currSide == TrackSide.LEFT) and (curr_block == "Green Block"):
                self.step_of_last_detection = self.counter.get_steps()
                return 2
            if (currSide == TrackSide.RIGHT) and (curr_block == "Red Block"):
                self.step_of_last_detection = self.counter.get_steps()
                return 1
        return 0

    def change_lane_to_right(self):

        self.robot.set_speed(self.norm_speed * 1.2, self.norm_speed * 0.9)
        if self.line_detection():
            self.current_state = KartState.LINE_FOLLOWING_AND_ALIGNMENT
        return True

    def change_lane_to_left(self):

        self.robot.set_speed(self.norm_speed * 0.9, self.norm_speed * 1.2)
        if self.line_detection():
            self.current_state = KartState.LINE_FOLLOWING_AND_ALIGNMENT
        return True

    def line_detection(self):

        if self.counter.get_steps() - self.step_of_last_detection > 200:
            detections = self.ground_sensor_memory.get_average()
            temp = 0
            for detec in detections:
                if detec < LINE_MAX_VALUE:
                    self.detected_lines += 1
            if self.detected_lines > 10:
                detected_lines = 0
                return True
            return False
        return None

    ####################################################################################################

    def detect_epucks(self):
        prox_values = self.robot.get_calibrate_prox()
        av_front_prox = (prox_values[6] * 2 + prox_values[7] + prox_values[0] + prox_values[1] * 2) / 4

        if av_front_prox > 100:
            return True
        return False

    def detect_end(self):

        distance = self.robot.get_tof()
        if distance <= 50:
            return True
        return False

    def run(self):
        no_error = True

        while self.robot.go_on() and no_error:
            gs: list[int] = self.robot.get_ground()
            self.ground_sensor_memory.update_memory(gs)
            no_error = self.current_state.do(self)

            self.counter.step()

        self.robot.clean_up()


if __name__ == "__main__":
    MarioKart(MY_IP, norm_speed=3).run()
