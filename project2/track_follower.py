class TrackFollower:

    def __init__(self, robot, norm_speed: float, line_max_value: int):
        self.robot = robot
        self.norm_speed = norm_speed
        self.current_speed = [0, 0]

        self.line_max_value = line_max_value # the max brightness value for the line

    def on_line(self, value: int) -> bool:
        return value < self.line_max_value

    def binary_approach(self, gs: list[int]) -> tuple[float, float] | None:
        black_list: list[bool] = [self.on_line(v) for v in gs]
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

    def two_sensors_approach(self, gs: list[int]) -> tuple[float, float] | None:
        black_list: list[bool] = [self.on_line(v) for v in gs]
        print(black_list)
        match black_list:
            case [False, False, False]:  # 0: no black
                print("no black, ERROR")
                return -1, 1
            case [False, False, True]:  # 1: extremely far left
                print("is extremely far left")
                return 1, -1
            case [False, True, False]:  # 2: ERROR
                print("WARNING, 010")
                return 0.5, 0.5
            case [False, True, True]:  # 3: far left
                print(" is far left")
                return 1, -1
            case [True, False, False]:  # 4: right
                print("is right")
                return 0, 1
            case [True, False, True]:  # 5: ERROR
                print("WARNING, 101")
                return 1,0 # handle as true,true, true
            case [True, True, False]:  # 6: middle
                print("middle")
                return 1, 1
            case [True, True, True]:  # 7: left
                print('is left')
                return 1, 0
            case _:  # else
                print("ERROR: should not be possible")
                return None

    def follow_track(self, use_two_sensors_approach: bool = False) -> bool:
        gs: list[int] = self.robot.get_ground()
        if use_two_sensors_approach:
            r = self.two_sensors_approach(gs)
        else:
            r = self.binary_approach(gs)
        if r is not None:
            speed_left = r[0] * self.norm_speed
            speed_right = r[1] * self.norm_speed
            self.robot.set_speed(speed_left, speed_right)
            self.current_speed = [speed_left, speed_right]

        return r is not None