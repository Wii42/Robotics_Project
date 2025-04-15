from unifr_api_epuck import wrapper
from beacon_detector import BeaconDetector

MY_IP: str = '192.168.2.207'

NORM_SPEED: float = 1
GREY_MIN_LENGTH: float = 10 / NORM_SPEED  # how long the robot should be in the grey area
GREY_DISTANCE_MAX: float = 2 * GREY_MIN_LENGTH  # how far apart the grey areas can be for it to count as one beacon

LINE_MAX: int = 750  # to determine if the sensor is on the line

GREY_MIN: int = 450  # to determine if the sensor is on the grey area


def on_line(value: int) -> bool:
    return value < LINE_MAX


def binary_approach(gs: list[int]) -> tuple[float, float] | None:
    black_list: list[bool] = [on_line(v) for v in gs]
    # print(black_list)
    match black_list:
        case [True, True, False]:  # is right
            # print(" is right")
            return 1, 2
        case [False, True, True]:  # is right
            # print(" is left")
            return 2, 1
        case [True, True, True]:  # middle
            # print('middle')
            return 2, 2
        case [True, False, False]:  # far right
            # print(" is far right")
            return -2, 2
        case [False, False, True]:  # far left
            # print(" is far left")
            return 2, -2
        case [True, False, True]:  # path splits
            # print("path splits, going hard left")
            return -2, 2
        case [False, True, False]:  # middle
            # print('middle')
            return 2, 2
        case _:  # else
            print("ERROR")
            return None


def main():
    robot = wrapper.get_robot(MY_IP)

    robot.init_ground()

    detector = BeaconDetector(robot_norm_speed=NORM_SPEED, grey_min_length=GREY_MIN_LENGTH,
                              grey_distance_max=GREY_DISTANCE_MAX, grey_min_value=GREY_MIN, grey_max_value=LINE_MAX)

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()

        detector.receive_ground(gs)

        r = binary_approach(gs)
        if r is not None:
            robot.set_speed(r[0] * NORM_SPEED, r[1] * NORM_SPEED)
        else:
            break

    robot.clean_up()


if __name__ == '__main__':
    main()
