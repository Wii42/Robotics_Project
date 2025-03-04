# Basic lover implementation
from unifr_api_epuck import wrapper

MY_IP = '192.168.2.206'  # change robot number
robot = wrapper.get_robot(MY_IP)

NORM_SPEED = 1.5
MAX_PROX = 250

WEIGHT_FRONT = 1
WEIGHT_FRONT_SIDE = 2
WEIGHT_SIDE = 3
WEIGHT_BACK = 4
WEIGHT_SUM = WEIGHT_FRONT + WEIGHT_FRONT_SIDE + WEIGHT_SIDE + WEIGHT_BACK

def control_wheel(prox):
    ds = (NORM_SPEED * prox) / MAX_PROX
    return NORM_SPEED - ds


robot.init_sensors()
robot.calibrate_prox()

#infinite loop
while robot.go_on():
    prox_values = robot.get_calibrate_prox()
    prox_l = (prox_values[7]*WEIGHT_FRONT + prox_values[6]*WEIGHT_FRONT_SIDE + prox_values[5]*WEIGHT_SUM + prox_values[4]*WEIGHT_BACK) /WEIGHT_SUM
    prox_r = (prox_values[0]*WEIGHT_FRONT + prox_values[1]*WEIGHT_FRONT_SIDE + prox_values[2]*WEIGHT_SIDE + prox_values[3]*WEIGHT_BACK) /WEIGHT_BACK

    robot.set_speed(control_wheel(prox_l), control_wheel(prox_r))
    
robot.clean_up()
