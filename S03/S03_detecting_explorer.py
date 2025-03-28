from unifr_api_epuck import wrapper
import sys, signal
import numpy as np


def detect_objects(robot) -> list[str]:
    img = np.array(robot.get_camera())
    detections = robot.get_detection(img)

    if len(detections) > 0:
        object_labels = [object.label for object in detections]
        object_labels.sort()
        return object_labels
    else:
        return []


def compare_configurations_and_set_leds(robot, last_detections):
    if robot.has_receive_msg():
        msg = robot.receive_msg()
        print("received message: " + msg)
        if msg == str(last_detections):
            if last_detections == []:
                robot.enable_led(0)
            else:
                robot.enable_all_led()
        else:
            robot.disable_all_led()


def explorer_behavior(robot):
    # get IR sensor values
    prox = robot.get_calibrate_prox()
    # behaviours: compute speed according to prox values and current state
    prox_left = (4 * prox[7] + 2 * prox[6] + prox[5]) / 7
    prox_right = (4 * prox[0] + 2 * prox[1] + prox[2]) / 7
    ds_left = (NORM_SPEED * prox_left) / MAX_PROX
    ds_right = (NORM_SPEED * prox_right) / MAX_PROX
    speed_left = NORM_SPEED - ds_right
    speed_right = NORM_SPEED - ds_left
    # set speed
    robot.set_speed(speed_left, speed_right)


if __name__ == "__main__":
    """
    if arguments in the command line --> IRL
    no arguemnts --> use Webots
    """
    ip_addr = None
    if len(sys.argv) == 2:
        ip_addr = sys.argv[1]

    robot = wrapper.get_robot(ip_addr)

    # initialize client communication (server needs to be started)
    robot.init_client_communication()


    def handler(signum, frame):
        robot.clean_up()


    signal.signal(signal.SIGINT, handler)

    NORM_SPEED = 1.2
    MAX_PROX = 250

    robot.init_sensors()
    robot.calibrate_prox()
    robot.initiate_model()

    robot.init_camera("img")

    stepcounter = 0
    n = 10

    last_detections = []

    while robot.go_on():

        if stepcounter % n == 0:
            robot.init_camera()
        if stepcounter % n == 1:
            last_detections = detect_objects(robot)
            robot.send_msg(str(last_detections))

        compare_configurations_and_set_leds(robot, last_detections)
        stepcounter += 1
        explorer_behavior(robot)

    robot.clean_up()
