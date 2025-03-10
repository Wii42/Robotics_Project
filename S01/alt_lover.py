from enum import Enum
import time
import random
# Basic lover implementation
from unifr_api_epuck import wrapper

from lover import move_lover

MY_IP = '192.168.2.214'  # change robot number
robot = wrapper.get_robot(MY_IP)

NORM_SPEED = 4
MAX_PROX = 250

SPEED_0 = 0.1*NORM_SPEED # speed under which the robot is considered stationary

counter = 0


def control_wheel(prox):
    ds = (NORM_SPEED * prox) / MAX_PROX
    return NORM_SPEED - ds


def is_equilibrium(prox_values, speed_left, speed_right):
    is_slow = abs(speed_left) < SPEED_0 and abs(speed_right) < SPEED_0

    return is_close(prox_values[0]) and is_close(prox_values[-1]) and is_slow


def is_close(value):
    return value > (MAX_PROX * 2)


class State(Enum):
    LOVER = 0
    EXPLORER_AWAY = 1
    EXPLORER_CHOOSER = 2




def lover_state(prox_values):
    global counter
    speed_left, speed_right = move_lover(prox_values, NORM_SPEED)

    if is_equilibrium(prox_values, speed_left, speed_right):
        print('equilibrium')
        counter += 1
    else:
        counter = 0

    robot.set_speed(speed_left, speed_right)


def explorer_move(prox_values):
    prox_l = (prox_values[7] + prox_values[6] + prox_values[5] +
              prox_values[4]) / 4
    prox_r = (prox_values[0] + prox_values[1] + prox_values[2] +
              prox_values[3]) / 4

    speed_left = control_wheel(prox_l)
    speed_right = control_wheel(prox_r)
    robot.set_speed(speed_right, speed_left)

def explorer_away_state(prox_values):
    global counter
    if is_further_than_value(prox_values, 50):
        counter+=1
    else:
        counter = 0
    explorer_move(prox_values)

def explorer_chooser_state(prox_values):
    global counter
    explorer_move(prox_values)

    if not  is_further_than_value(prox_values, 100):
        counter+=1
    else:
        counter = 0
   
   
def explorer_choose_state():
    global state
    random.seed(time.time())
    choice = random.randint(1, 100)
    if choice < 50:
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
            if counter >= 3:
                print('explorer away')
                state = State.EXPLORER_AWAY
                counter = 0
        case State.EXPLORER_AWAY:
            explorer_away_state(prox_values)
            robot.disable_all_led()
            if counter >= 3:
                print('explorer chooser')
                state = State.EXPLORER_CHOOSER
                counter = 0
        case State.EXPLORER_CHOOSER:
            explorer_chooser_state(prox_values)
            robot.enable_led(1)
            robot.enable_led(2)
            if counter >= 3:
                explorer_choose_state()
                counter = 0



robot.clean_up()
