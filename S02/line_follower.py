from unifr_api_epuck import wrapper

LEFT_SENSOR: int = 0
MIDDLE_SENSOR: int = 1
RIGHT_SENSOR: int = 2
MY_IP: str = '192.168.2.207'

NORM_SPEED: float = 1


def is_black(value: int) -> bool:
    return value < 750


def binary_approach(gs: list[int]) -> tuple[float, float] | None:
    black_list: list[bool] = [is_black(v) for v in gs]
    print(black_list)
    match black_list:
        case [True, True, False]:  # is right
            print(" is right")
            return 1, 2
        case [False, True, True]:  # is right
            print(" is left")
            return 2, 1
        case [True, True, True]:  # middle
            print('middle')
            return 2, 2
        case [True, False, False]:  # far right
            print(" is far right")
            return -2, 2
        case [False, False, True]:  # far left
            print(" is far left")
            return 2, -2
        case [True, False, True]:  # path splits
            print("path splits, going hard left")
            return -2, 2
        case _:  # else
            print("ERROR")
            return None


def two_sensors_approach(gs: list[int]) -> tuple[float, float] | None:
    black_list: list[bool] = [is_black(v) for v in gs]
    print(black_list)
    match black_list:
        case [False, False, False]:  # 0: no black
            print("no black, ERROR")
            return -NORM_SPEED, NORM_SPEED
        case [False, False, True]:  # 1: extremely far left
            print("is extremely far left")
            return NORM_SPEED, -NORM_SPEED
        case [False, True, False]:  # 2: ERROR
            print("ERROR, 010")
            return None
        case [False, True, True]:  # 3: far left
            print(" is far left")
            return NORM_SPEED, -NORM_SPEED
        case [True, False, False]:  # 4: right
            print("is right")
            return 0, NORM_SPEED
        case [True, False, True]:  # 5: ERROR
            print("ERROR, 101")
            return None
        case [True, True, False]:  # 6: middle
            print("middle")
            return NORM_SPEED * 2, NORM_SPEED * 2
        case [True, True, True]:  # 7: left
            print('is left')
            return NORM_SPEED, 0
        case _:  # else
            print("ERROR: should not be possible")
            return None


def main():
    robot = wrapper.get_robot(MY_IP)

    robot.init_ground()

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()
        # print(gs)

        r = two_sensors_approach(gs)
        if r is not None:
            robot.set_speed(r[0], r[1])
        else:
            break

    robot.clean_up()


if __name__ == '__main__':
    main()
