from unifr_api_epuck import wrapper
import os
from project2.robot.step_counter import StepCounter
from project2.robot.track_follower import TrackFollower
from determine_side import TrackSide
from determine_side import DetermineSide
from ground_sensor_memory import GroundSensorMemory
from line_alignment import LineAlignment
import utils
import time

MY_IP = '192.168.2.214'
LINE_MAX_VALUE: int = 500

STEPS_TO_DETERMINE_SIDE: int = 20


def main():
    dir = "./object_detections"
    robot = wrapper.get_robot(MY_IP)
    try:
        os.mkdir(dir)
    except OSError as error:
        print(error)
    robot.init_ground()

    robot.initiate_model()

    robot.init_sensors()
    robot.calibrate_prox()

    counter: StepCounter = StepCounter()

    line_follower: TrackFollower = TrackFollower(robot, 3, LINE_MAX_VALUE)

    sensor_memory: GroundSensorMemory = GroundSensorMemory(3)

    determine_side: DetermineSide = DetermineSide(750, LINE_MAX_VALUE, STEPS_TO_DETERMINE_SIDE)

    line_alignment: LineAlignment = LineAlignment()

    check_side_necessary: bool = True

    ####################################
    no_error = True
    curr_state = 0

    def line_following_and_alignment():

        nonlocal check_side_necessary
        nonlocal curr_state
        if counter.get_steps() > STEPS_TO_DETERMINE_SIDE and check_side_necessary:
            line_alignment.check_line_alignment(determine_side.get_probable_side())
            check_side_necessary = False

        # print(gs)
        # print(gs)
        # robot.set_speed(5,5)
        if not line_follower.follow_track(sensor_memory.get_average(), use_two_sensors_approach=True,
                                          invert_side=line_alignment.get_follow_left_side()):
            return False
        determine_side.determine_side(sensor_memory.get_average(), line_follower.position,
                                      invert_side=line_alignment.get_follow_left_side())
        # print(determine_side.get_probable_side())
        # print()
        curr_state = change_lanes_detection()
        return True

    step_of_last_detection = 0
    stand_speed = 2

    def change_to_line_following():
        nonlocal curr_state
        curr_state = 0

    def change_lane_to_right():

        robot.set_speed(stand_speed * 1.2, stand_speed * 0.9)
        if line_detection():
            change_to_line_following()
        return True

    def change_lane_to_left():

        nonlocal curr_state
        robot.set_speed(stand_speed * 0.9, stand_speed * 1.2)
        if line_detection():
            change_to_line_following()
        return True

    detected_lines = 0

    def line_detection():
        nonlocal detected_lines

        if (counter.get_steps() - step_of_last_detection > 200):
            detections = sensor_memory.get_average()
            temp = 0
            for detec in detections:
                if detec < LINE_MAX_VALUE:
                    detected_lines += 1
            if detected_lines > 10:
                detected_lines = 0
                return True
            return False

    def change_lanes_detection():
        nonlocal step_of_last_detection

        if (counter.get_steps() % 50 == 0):
            robot.init_camera(dir)

        curr_block = None
        if (counter.get_steps() % 50 == 1):
            curr_block = utils.block_detector(robot, 30, 20)
            robot.disable_camera()
        if curr_block != None:
            currSide = determine_side.get_probable_side()

            if (currSide == TrackSide.LEFT) and (curr_block == "Green Block"):
                step_of_last_detection = counter.get_steps()
                return 2
            if (currSide == TrackSide.RIGHT) and (curr_block == "Red Block"):
                step_of_last_detection = counter.get_steps()
                return 1
        return 0

    ####################################################################################################

    def detect_epucks():
        prox_values = robot.get_calibrate_prox()
        av_front_prox = (prox_values[6] * 2 + prox_values[7] + prox_values[0] + prox_values[1] * 2) / 4

        if av_front_prox > 100:
            return True
        return False

    def detect_end():

        distance = robot.get_tof()
        if distance <= 50:
            return True
        return False

    states = {0: line_following_and_alignment,
              1: change_lane_to_left,
              2: change_lane_to_right}

    while robot.go_on() and no_error:
        gs: list[int] = robot.get_ground()
        sensor_memory.update_memory(gs)
        no_error = states[curr_state]()

        counter.step()

    robot.clean_up()


if __name__ == "__main__":
    main()
