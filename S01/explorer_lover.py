from enum import Enum
import time
import random
# Basic lover implementation
from unifr_api_epuck import wrapper

MY_IP = '192.168.2.204'  # change robot number
robot = wrapper.get_robot(MY_IP)

NORM_SPEED = 4
MAX_PROX = 250

WEIGHT_FRONT = 1
WEIGHT_FRONT_SIDE = 2
WEIGHT_SIDE = 3
WEIGHT_BACK = 4
WEIGHT_SUM = WEIGHT_FRONT + WEIGHT_FRONT_SIDE + WEIGHT_SIDE + WEIGHT_BACK

SPEED_0 = 0.1*NORM_SPEED # speed under which the robot is considered stationary

equilibrium_counter = 0


def control_wheel(prox):
    ds = (NORM_SPEED * prox) / MAX_PROX
    return NORM_SPEED - ds


def is_equilibrium(prox_values, speed_left, speed_right):
    # print(f'{prox_values[-1]} {prox_values[0]}')
    is_slow = abs(speed_left) < SPEED_0 and abs(speed_right) < SPEED_0

    return is_close(prox_values[0]) and is_close(prox_values[-1]) and is_slow


def is_close(value):
    return value > (MAX_PROX * 2)


class State(Enum):
    LOVER = 0
    EXPLORER_AWAY = 1
    EXPLORER_CHOOSER = 2




def lover_state(prox_values):
    global equilibrium_counter
    prox_l = (prox_values[7] * WEIGHT_FRONT + prox_values[6] * WEIGHT_FRONT_SIDE + prox_values[5] * WEIGHT_SIDE +
                  prox_values[4] * WEIGHT_BACK) / WEIGHT_SUM
    prox_r = (prox_values[0] * WEIGHT_FRONT + prox_values[1] * WEIGHT_FRONT_SIDE + prox_values[2] * WEIGHT_SIDE +
                  prox_values[3] * WEIGHT_BACK) / WEIGHT_SUM

    speed_left = control_wheel(prox_l)
    speed_right = control_wheel(prox_r)

    if is_equilibrium(prox_values, speed_left, speed_right):
        print('equilibrium')
        equilibrium_counter += 1

    robot.set_speed(control_wheel(prox_l), control_wheel(prox_r))
def explorer_away_state(prox_values):
    global state
    if is_further_than_value(prox_values, 50):
        print('chooser')
        state = State.EXPLORER_CHOOSER

    prox_l = (prox_values[7] + prox_values[6]+ prox_values[5] +
              prox_values[4]) / 4
    prox_r = (prox_values[0] + prox_values[1] + prox_values[2] +
              prox_values[3]) / 4

    speed_left = control_wheel(prox_l)
    speed_right = control_wheel(prox_r)
    robot.set_speed(speed_right, speed_left)
    return
 #
 #
 #   if is_further_than_value(prox_values, 50):
 #       print('chooser')
 #       state = State.EXPLORER_CHOOSER
 #       return
 #   #print(prox_values)
 #   front = (prox_values[6]+prox_values[7]+prox_values[0]+prox_values[1])/4
 #   back = (prox_values[2] + prox_values[3] + prox_values[4] + prox_values[5]) / 4
 #   left = (prox_values[7] + prox_values[6] + prox_values[5] + prox_values[4]) / 4
 #   right = (prox_values[0] + prox_values[1] + prox_values[2] + prox_values[3]) / 4
 #   speed_left = (left * 7) / 3000
 #   speed_right = (right * 7) / 3000
 #   if front*5 > back and front > 100:
 #       #print('turn on spot')
 #       if speed_right > speed_left:
 #           speed_left = -NORM_SPEED
 #           speed_right = NORM_SPEED
 #       else:
 #           speed_right = -NORM_SPEED
 #           speed_left = NORM_SPEED
 #   else:
 #       pass
 #       speed_left = NORM_SPEED
 #       speed_right = NORM_SPEED
 #
 #
 #   robot.set_speed(speed_left, speed_right)

def explorer_chooser_state(prox_values):
    global state
    prox_l = (prox_values[7] + prox_values[6] + prox_values[5] +
              prox_values[4]) / 4
    prox_r = (prox_values[0] + prox_values[1] + prox_values[2] +
              prox_values[3]) / 4

    speed_left = control_wheel(prox_l)
    speed_right = control_wheel(prox_r)
    robot.set_speed(speed_right, speed_left)

    if not  is_further_than_value(prox_values, 100):
        random.seed(time.time())
        choice = random.randint(1,100)
        print(choice)
        if choice < 40:
            state = State.LOVER
            print('chose lover')
        else:
            state = State.EXPLORER_AWAY
            print('chose explorer away')





def is_further_than_value(prox_values, value):
    for v in prox_values:
        if v > value:
            return False
    return True

state = State.LOVER

robot.init_sensors()
robot.calibrate_prox()
# infinite loop
print("battery level")
print(robot.get_battery_level())
while robot.go_on():
    prox_values = robot.get_calibrate_prox()
    match state:
        case State.LOVER:
            lover_state(prox_values)
            robot.enable_all_led()
        case State.EXPLORER_AWAY:
            explorer_away_state(prox_values)
            robot.disable_all_led()
        case State.EXPLORER_CHOOSER:
            explorer_chooser_state(prox_values)
            robot.disable_all_led()
    if equilibrium_counter >= 3:
        print('end')
        state = State.EXPLORER_AWAY
        equilibrium_counter = 0

robot.clean_up()
