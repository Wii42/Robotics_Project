from enum import Enum

from typing import Callable

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
from task_2.calibration import normalize_gs

MY_IP = '192.168.2.208'
LINE_MAX_VALUE: int = 600
GREY_MAX_VALUE: int = 800

STEPS_TO_DETERMINE_SIDE: int = 100

OBJECT_DETECTIONS_DIR = "./object_detections"


class KartState(Enum):
    LINE_FOLLOWING_AND_ALIGNMENT = 0
    CHANGE_LANE_TO_LEFT = 1
    CHANGE_LANE_TO_RIGHT = 2


class MarioKart:

    def __init__(self, robot_ip: str, norm_speed: float = 3):
        self.robot_ip: str = robot_ip
        self.norm_speed: float = norm_speed
        self.robot: WifiEpuck | None = None  # init later
        self.counter: StepCounter = StepCounter()
        self.line_follower: TrackFollower | None = None  # dependent on robot
        self.ground_sensor_memory: SensorMemory = SensorMemory(3)
        self.determine_side: DetermineSide = DetermineSide(GREY_MAX_VALUE, LINE_MAX_VALUE, STEPS_TO_DETERMINE_SIDE)
        self.line_alignment: LineAlignment = LineAlignment()
        self.check_side_necessary: bool = True
        self.current_state: KartState = KartState.LINE_FOLLOWING_AND_ALIGNMENT
        # self.detected_lines = 0
        self.state_counter = StepCounter()

    def states(self) -> dict[KartState, Callable]:
        return {KartState.LINE_FOLLOWING_AND_ALIGNMENT: self.line_following_and_alignment,
                KartState.CHANGE_LANE_TO_LEFT: self.change_lane_to_left,
                KartState.CHANGE_LANE_TO_RIGHT: self.change_lane_to_right}

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

        if self.state_counter.get_steps() > STEPS_TO_DETERMINE_SIDE and self.check_side_necessary:
            self.line_alignment.check_line_alignment(self.determine_side.get_probable_side())
            self.check_side_necessary = False
            self.line_follower.line_max_value = GREY_MAX_VALUE

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

        self.set_state(self.change_lanes_detection())
        return True

    def change_lanes_detection(self):
        picture_frequency = 50


        if self.counter.get_steps() % picture_frequency == 0 and self.state_counter.get_steps() > 30:
            self.robot.init_camera(OBJECT_DETECTIONS_DIR)

        curr_block = None
        if self.counter.get_steps() % picture_frequency == 1 and self.state_counter.get_steps() >= STEPS_TO_DETERMINE_SIDE:
            curr_block = utils.block_detector(self.robot, 30, 15)
            self.robot.disable_camera()
        if curr_block is not None:
            currSide = self.determine_side.get_probable_side()
            confidence_level = self.determine_side.certainty_of_last_guess
            print("curr block: ", curr_block, " curr side: ", currSide, " confidence: ", confidence_level)
            if confidence_level >= 0.4:
                if (currSide == TrackSide.LEFT) and (curr_block == "Green Block"):
                    print("change to right")
                    return KartState.CHANGE_LANE_TO_RIGHT
                if (currSide == TrackSide.RIGHT) and (curr_block == "Red Block"):
                    print("change to left")
                    return KartState.CHANGE_LANE_TO_LEFT
        return KartState.LINE_FOLLOWING_AND_ALIGNMENT

    def change_lanes(self, change_to_left: bool):
        if self.state_counter.get_steps() < 100 / self.norm_speed:
            speeds = [self.norm_speed * 2, self.norm_speed * 0.5]
            if change_to_left:
                speeds.reverse()
            self.robot.set_speed(*speeds)
        else:
            self.robot.set_speed(self.norm_speed, self.norm_speed)
        if self.line_detection() and self.state_counter.get_steps() > 300 / self.norm_speed:
            self.set_state(KartState.LINE_FOLLOWING_AND_ALIGNMENT)
            self.line_alignment.follow_left_side = not self.line_alignment.follow_left_side
            self.check_side_necessary = False
        return True

    def change_lane_to_right(self):
        return self.change_lanes(change_to_left=False)

    def change_lane_to_left(self):
        return self.change_lanes(change_to_left=True)

    def line_detection(self):

        detections: list[int] = self.ground_sensor_memory.get_average()
        is_white = [True for detection in detections if detection > self.determine_side.grey_max_value+50]
        if any(is_white):
            #print("detected white: ", detections)
            return True
        ##for detec in detections:
        ##    if detec < LINE_MAX_VALUE:
        ##        self.detected_lines += 1
        ##if self.detected_lines > 10:
        ##    self.detected_lines = 0
        ##    return True
        ##return False
        return False

    ####################################################################################################

    def detect_epucks(self):
        prox_values = self.robot.get_calibrate_prox()
        av_front_prox = (prox_values[6] + prox_values[7]*2 + prox_values[0]*2 + prox_values[1]) / 4

        if av_front_prox > 150:
            return True
        return False

    def detect_end(self):

        distance = self.robot.get_tof()
        if distance <= 50:
            return True
        return False

    def set_state(self, new_state: KartState):
        if new_state != self.current_state:
            self.state_counter.reset()
        self.current_state = new_state

    def run(self):
        self.init_robot()
        self.init_line_follower()

        data = self.init_gsensors_record()

        print("init complete")

        no_error: bool = True
        assert (self.robot is not None)
        assert (self.line_follower is not None)
        while self.robot.go_on() and no_error:
            gs: list[int | float] = self.robot.get_ground()
            gs = normalize_gs(gs, self.robot_ip)
            self.ground_sensor_memory.update_memory(gs)
            #print(self.determine_side.get_probable_side())
            states = self.states()
            no_error = states[self.current_state]()

            if data is not None:
                self.record_gsensors(data, gs)

            if self.detect_end():
                print("detected end")
                break

            if self.detect_epucks():
                print("detected epuck")
                self.robot.set_speed(0, 0)


            self.counter.step()
            self.state_counter.step()

        self.robot.clean_up()

    def init_gsensors_record(self):
        data = open("Gsensors.csv", "w")
        if data is None:
            print('Error opening data file!\n')
            return

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


if __name__ == "__main__":
    MarioKart(MY_IP, norm_speed=3).run()
