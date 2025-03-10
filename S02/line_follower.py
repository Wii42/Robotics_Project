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
            return 2,1
        case [True, True, True]:  # middle
            print('middle')
            return 2,2
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

def calc_speed(value: int):
    return -(value - 900) / 300

def continuous_approach(gs: list[int]) -> tuple[float, float] | None:
    left = calc_speed(gs[LEFT_SENSOR])
    right = calc_speed(gs[RIGHT_SENSOR])

    print(right, left)

    if left > 0 or right > 0:
        return left*NORM_SPEED, right*NORM_SPEED
    print("ERROR")
    return None

def main():
    robot = wrapper.get_robot(MY_IP)

    robot.init_ground()

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()
        print(gs)

        r = binary_approach(gs)
        if r is not None:
            robot.set_speed(r[0], r[1])
        else:
            break


    robot.clean_up()

if __name__ == '__main__':
    main()
