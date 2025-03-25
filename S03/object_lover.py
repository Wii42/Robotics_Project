from unifr_api_epuck import wrapper
import os
import numpy as np
from unifr_api_epuck.epuck.epuck_wifi import Detected

dir = "./object_lover_img"

def object_with_largest_area(detections: list[Detected]):
    if len(detections) == 0:
        return None
    max_area = 0
    max_obj = None
    for obj in detections:
        area = obj.width * obj.height
        if area > max_area:
            max_area = area
            max_obj = obj
    return max_obj

if __name__ == "__main__":
    try:
        os.mkdir(dir)
    except OSError as error:
        print(error)


    """
    if arguments in the command line --> IRL
    no arguemnts --> use Webots
    """
    ip_addr = "192.168.2.205"

    robot = wrapper.get_robot(ip_addr)


    NORM_SPEED = 1.2*3
    MAX_PROX = 92

    robot.init_sensors()
    robot.calibrate_prox()
    robot.initiate_model()

    robot.init_camera(dir)

    stepcounter = 0
    n = 10

    while robot.go_on():
        speed_left = 0
        speed_right = 0
        img = np.array(robot.get_camera())
        detections = robot.get_detection(img)
        robot.save_detection()
        if len(detections) > 0:
            red_blocks =[obj for obj in detections if obj.label == "Red Block"]
            if len(red_blocks) > 0:
                object = object_with_largest_area(red_blocks)
                if object.label == "Red Block":
                    #print(object.label)
                    #print(object.x_center)

                    horizontal_deviation = object.x_center - 80
                    ds = abs(horizontal_deviation) / 80 * NORM_SPEED
                    if horizontal_deviation < 0:
                        speed_left = NORM_SPEED - ds
                        speed_right = NORM_SPEED
                    else:
                        speed_right = NORM_SPEED - ds
                        speed_left = NORM_SPEED

                    print(object.height)

                    ds2 = (NORM_SPEED * object.height) / MAX_PROX

                    speed_left = speed_left - ds2
                    speed_right = speed_right - ds2








            # robot.disable_camera() # BUG !! will be working soon...

        stepcounter += 1

        # get IR sensor values


        #speed_left = NORM_SPEED - ds_left
        #speed_right = NORM_SPEED - ds_right

        # set speed
        robot.set_speed(speed_left, speed_right)

    robot.clean_up()

