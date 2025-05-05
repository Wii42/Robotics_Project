import math

from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck
from time import perf_counter_ns

from project2.beacon import Beacon
from project2.step_counter import StepCounter


def wheel_distance(angular_speed: float, wheel_radius: float, time_delta: float) -> float:
    """
    :param angular_speed: in rad/s
    :param wheel_radius: in m
    :param time_delta: in s
    :return: distance in m
    """
    return angular_speed * wheel_radius * time_delta

theta_correction_factor: dict[str, float] = {"207": 0.782608696} # correction factor for the theta angle
# expected angle 90, receceived 115, so 90/115 = 0.782608696
# collected with robot 207, 211 does not need correction

class Odometry:
    def __init__(self, robot: WifiEpuck, step_counter: StepCounter):
        self.robot: WifiEpuck = robot
        self.theta: float = 0  # orientation in radians
        self.x: float = 0 # in m
        self.y: float = 0 # in m
        self.last_time_ns: float = 0
        self.distance_left: float = 0
        self.distance_right: float = 0
        self.step_counter: StepCounter = step_counter
        self.position_on_track = None
        self.calibrated_by_beacon: bool = False

    def odometry(self, speed_left: float, speed_right: float):
        wheel_diameter: float = 0.041  # in m, source https://www.gctronic.com/doc/index.php/e-puck2
        distance_between_wheels: float = 0.053  # in m

        wheel_radius: float = wheel_diameter / 2

        time_ns: float = perf_counter_ns()
        time_delta = time_ns - self.last_time_ns
        self.last_time_ns = time_ns
        distance_left: float = wheel_distance(speed_left, wheel_radius, time_delta/ 1e9)
        distance_right: float = wheel_distance(speed_right, wheel_radius, time_delta/ 1e9)

        distance: float = (distance_right + distance_left) / 2
        # calculate the change in position
        delta_theta: float = ((distance_left - distance_right) / distance_between_wheels) * self.theta_correction()
        delta_x: float = distance*math.cos(self.theta + (delta_theta/2))
        delta_y: float = distance*math.sin(self.theta + (delta_theta/2))

        self.theta += delta_theta
        self.x += delta_x*1500
        self.y += delta_y*1500

        self.distance_left += distance_left
        self.distance_right += distance_right

        if self.calibrated_by_beacon:
            self.position_on_track+= distance


    def theta_correction(self) -> float:
        robot_name = self.robot_name()
        return theta_correction_factor.get(robot_name, 1)

    def robot_name(self):
        return self.robot.id.split("_")[-1]

    def total_distance(self) -> float:
        return (self.distance_right + self.distance_left) / 2


    def print_position(self):
        # Print the current position and orientation
        print(
            f"[{self.robot_name()}] Current Position: ({self.x:.2f}, {self.y:.2f}), Orientation: {math.degrees(self.theta):.2f} degrees, distance: {self.total_distance():.2f} m")

    def sync_with_beacon(self, beacon: Beacon):
        self.x = beacon.x
        self.y = beacon.y
        self.theta = beacon.orientation
        self.calibrated_by_beacon = True
        if self.position_on_track is None :
            self.position_on_track = beacon.position_on_track


class OdometryReading:
    def __init__(self, step:int, x: float, y: float, theta: float, timestamp: int):
        self.step: int = step
        self.x: float = x
        self.y: float = y
        self.theta: float = theta
        self.timestamp: float = timestamp