from enum import Enum


class RobotPosition(Enum):
    IS_LEFT = 0
    IS_RIGHT = 1
    IS_MIDDLE = 2
    ERROR = 3
    UNKNOWN = 4

class TrackFollower:

    def __init__(self, robot, norm_speed: float, line_max_value: int):
        self.robot = robot
        self.norm_speed = norm_speed
        self.current_speed = [0, 0]
        self.position: RobotPosition = RobotPosition.UNKNOWN
        self.speed_factor: float = 1.0

        self.line_max_value = line_max_value # the max brightness value for the line

    def on_line(self, value: int) -> bool:
        return value < self.line_max_value

    def binary_approach(self, gs: list[int]) -> tuple[float, float] | None:
        black_list: list[bool] = [self.on_line(v) for v in gs]
        # print(black_list)
        match black_list:
            case [True, True, False]:  # is right
                # print(" is right")
                self.position = RobotPosition.IS_RIGHT
                return 1, 2
            case [False, True, True]:  # is right
                self.position = RobotPosition.IS_LEFT
                # print(" is left")
                return 2, 1
            case [True, True, True]:  # middle
                self.position = RobotPosition.IS_MIDDLE
                # print('middle')
                return 2, 2
            case [True, False, False]:  # far right
                self.position = RobotPosition.IS_RIGHT
                # print(" is far right")
                return -2, 2
            case [False, False, True]:  # far left
                self.position = RobotPosition.IS_LEFT
                # print(" is far left")
                return 2, -2
            case [True, False, True]:  # path splits
                self.position = RobotPosition.UNKNOWN
                # print("path splits, going hard left")
                return -2, 2
            case [False, True, False]:  # middle
                self.position = RobotPosition.IS_MIDDLE
                # print('middle')
                return 2, 2
            case _:  # else
                self.position = RobotPosition.ERROR
                print("ERROR")
                return None

    def two_sensors_approach(self, gs: list[int]) -> tuple[float, float] | None:
        black_list: list[bool] = [self.on_line(v) for v in gs]
        #print(black_list)
        match black_list:
            case [False, False, False]:  # 0: no black
                self.position = RobotPosition.UNKNOWN
                print("no black, ERROR")
                return -1, 1
            case [False, False, True]:  # 1: extremely far left
                self.position = RobotPosition.IS_LEFT
                #print("is extremely far left")
                return 1, -1
            case [False, True, False]:  # 2: ERROR
                self.position = RobotPosition.UNKNOWN
                print("WARNING, 010")
                return 0.5, 0.5
            case [False, True, True]:  # 3: far left
                self.position = RobotPosition.IS_LEFT
                #print(" is far left")
                return 1, -1
            case [True, False, False]:  # 4: right
                self.position = RobotPosition.IS_RIGHT
                #print("is right")
                return 0, 1
            case [True, False, True]:  # 5: ERROR
                self.position = RobotPosition.UNKNOWN
                print("WARNING, 101")
                return 1,1 # handle as middle
            case [True, True, False]:  # 6: middle
                #print("middle")
                self.position = RobotPosition.IS_MIDDLE
                return 1, 1
            case [True, True, True]:  # 7: left
                #print('is left')
                self.position = RobotPosition.IS_LEFT
                return 1, 0
            case _:  # else
                print("ERROR: should not be possible")
                self.position = RobotPosition.ERROR
                return None

    def follow_track(self, gs: list[int], use_two_sensors_approach: bool = False, invert_side :bool = False) -> bool:

        if invert_side:
            gs.reverse()
        if use_two_sensors_approach:
            r = self.two_sensors_approach(gs)
        else:
            r = self.binary_approach(gs)
        if r is not None:
            if invert_side:
                r = r[::-1] # swap left and right
            speed_left = r[0] * self.norm_speed* self.speed_factor
            speed_right = r[1] * self.norm_speed* self.speed_factor
            self.robot.set_speed(speed_left, speed_right)
            self.current_speed = [speed_left, speed_right]

        return r is not None