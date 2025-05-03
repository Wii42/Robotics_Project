class TrackFollower:

    def __init__(self, robot, norm_speed: float, line_max_value: int):
        self.robot = robot
        self.norm_speed = norm_speed
        self.current_speed = [0, 0]

        self.line_max_value = line_max_value

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

    def follow_track(self) -> bool:
        gs: list[int] = self.robot.get_ground()

        r = self.binary_approach(gs)
        if r is not None:
            speed_left = r[0] * self.norm_speed
            speed_right = r[1] * self.norm_speed
            self.robot.set_speed(speed_left, speed_right)
            self.current_speed = [speed_left, speed_right]

        return r is not None