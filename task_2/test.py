from unifr_api_epuck import wrapper
from step_counter import StepCounter
from track_follower import TrackFollower
from determine_side import DetermineSide
from ground_sensor_memory import GroundSensorMemory
from line_alignment import LineAlignment
import utils
import os
import time

MY_IP = '192.168.2.211'
LINE_MAX_VALUE = 500
STEPS_TO_DETERMINE_SIDE = 20

def main():
    robot = wrapper.get_robot(MY_IP)
    output_dir = "./object_detections"


    counter = StepCounter()
    time.sleep(1)

    while robot.go_on():
        steps = counter.get_steps()
        robot.set_speed(2*1.2, 2*0.9)
        print(steps)

        counter.step()

    robot.clean_up()

if __name__ == "__main__":
    main()
