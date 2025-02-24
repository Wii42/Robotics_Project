# Basic lover implementation
from unifr_api_epuck import wrapper

MY_IP = '192.168.2.206'  # change robot number
robot = wrapper.get_robot(MY_IP)

NORM_SPEED = 1.5
MAX_PROX = 250

robot.init_sensors()
robot.calibrate_prox()

#infinite loop
while robot.go_on():
    prox_values = robot.get_calibrate_prox()
    prox = (prox_values[0] + prox_values[7])/2
    ds = (NORM_SPEED * prox) / MAX_PROX
    speed = NORM_SPEED - ds
    robot.set_speed(speed)
    
robot.clean_up()
