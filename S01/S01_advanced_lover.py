# Basic lover implementation
from unifr_api_epuck import wrapper

MY_IP = '192.168.2.206'  # change robot number

NORM_SPEED = 1.5
MAX_PROX = 250

WEIGHT_FRONT = 1
WEIGHT_FRONT_SIDE = 2
WEIGHT_SIDE = 3
WEIGHT_BACK = 4
WEIGHT_SUM = WEIGHT_FRONT + WEIGHT_FRONT_SIDE + WEIGHT_SIDE + WEIGHT_BACK

def control_wheel(prox, speed):
    ds = (speed * prox) / MAX_PROX
    return speed - ds

def move_lover(prox_values, speed):
    prox_l = (prox_values[7] * WEIGHT_FRONT + prox_values[6] * WEIGHT_FRONT_SIDE + prox_values[5] * WEIGHT_SUM +
              prox_values[4] * WEIGHT_BACK) / WEIGHT_SUM
    prox_r = (prox_values[0] * WEIGHT_FRONT + prox_values[1] * WEIGHT_FRONT_SIDE + prox_values[2] * WEIGHT_SIDE +
              prox_values[3] * WEIGHT_BACK) / WEIGHT_BACK

    return control_wheel(prox_l, speed), control_wheel(prox_r, speed)

def main():
    robot = wrapper.get_robot(MY_IP)
    robot.init_sensors()
    robot.calibrate_prox()

    # infinite loop
    while robot.go_on():
        prox_values = robot.get_calibrate_prox()

        speed_left, speed_right = move_lover(prox_values, NORM_SPEED)

        robot.set_speed(speed_left, speed_right)

    robot.clean_up()

if __name__ == '__main__':
    main()
