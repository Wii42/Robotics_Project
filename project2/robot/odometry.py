"""
odometry.py

Handles odometry calculations for the ePuck robot, including position and orientation
tracking, calibration, and synchronization with beacons.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

import json
import math
import os

from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck
from time import perf_counter_ns

from project2.core.beacon import Beacon
from project2.core.position_on_track import PositionOnTrack
from project2.robot.step_counter import StepCounter


def wheel_distance(angular_speed: float, wheel_radius: float, time_delta: float) -> float:
    """
    Calculate the distance traveled by a wheel given its angular speed, radius, and time interval.

    Args:
        angular_speed (float): Angular speed in rad/s.
        wheel_radius (float): Wheel radius in meters.
        time_delta (float): Time interval in seconds.

    Returns:
        float: Distance traveled in meters.
    """
    return angular_speed * wheel_radius * time_delta

class Odometry:
    """
    The Odometry class tracks the robot's position (x, y) and orientation (theta)
    using wheel speeds and time intervals. It supports calibration and synchronization
    with beacons for improved accuracy.
    """
    def __init__(self, robot: WifiEpuck, step_counter: StepCounter):
        """
        Initialize the Odometry object.

        Args:
            robot (WifiEpuck): The robot instance.
            step_counter (StepCounter): Step counter for tracking steps.
        """
        self.robot: WifiEpuck = robot
        self.theta: float = 0  # orientation in radians
        self.x: float = 0 # in m
        self.y: float = 0 # in m
        self.last_time_ns: float = 0
        self.distance_left: float = 0
        self.distance_right: float = 0
        self.step_counter: StepCounter = step_counter
        self.position_from_beacon: PositionOnTrack = PositionOnTrack(0)
        self.calibrated_by_beacon: bool = False
        self.distance_correction_factor: float = 1.0
        self.theta_correction_factor: float = 1.0

    def odometry(self, speed_left: float, speed_right: float):
        """
        Update the robot's position and orientation based on wheel speeds.

        Args:
            speed_left (float): Left wheel speed in rad/s.
            speed_right (float): Right wheel speed in rad/s.
        """
        wheel_diameter: float = 0.041  # in m, source https://www.gctronic.com/doc/index.php/e-puck2
        distance_between_wheels: float = 0.053  # in m
        wheel_radius: float = wheel_diameter / 2

        time_ns: float = perf_counter_ns()
        time_delta = time_ns - self.last_time_ns
        self.last_time_ns = time_ns

        # Calculate distance traveled by each wheel
        distance_left: float = wheel_distance(speed_left, wheel_radius, time_delta / 1e9)
        distance_right: float = wheel_distance(speed_right, wheel_radius, time_delta / 1e9)

        # Apply correction factor and compute average distance
        distance: float = ((distance_right + distance_left) / 2) * self.distance_correction_factor

        # Calculate change in orientation
        delta_theta: float = ((distance_left - distance_right) / distance_between_wheels) * self.theta_correction_factor

        # Calculate change in position
        delta_x: float = distance * math.cos(self.theta + (delta_theta / 2))
        delta_y: float = distance * math.sin(self.theta + (delta_theta / 2))

        # Update robot's pose
        self.theta += delta_theta
        self.x += delta_x * 1500  # Scaling factor for simulation
        self.y += delta_y * 1500

        self.distance_left += distance_left
        self.distance_right += distance_right

        # If calibrated by beacon, update distance from beacon
        if self.calibrated_by_beacon:
            self.position_from_beacon.distance += distance

    def calibrate_robot(self):
        """
        Calibrate the robot using values from a calibration file.
        """
        self.read_calibration_file()

    def robot_name(self):
        """
        Get the robot's name from its ID.

        Returns:
            str: Robot name.
        """
        return self.robot.id.split("_")[-1]

    def total_distance(self) -> float:
        """
        Calculate the total distance traveled by the robot.

        Returns:
            float: Total distance in meters.
        """
        return (self.distance_right + self.distance_left) / 2

    def print_position(self):
        """
        Print the current position and orientation of the robot.
        """
        print(
            f"[{self.robot_name()}] Current Position: ({self.x:.2f}, {self.y:.2f}), Orientation: {math.degrees(self.theta):.2f} degrees, distance: {self.total_distance():.2f} m")

    def sync_with_beacon(self, beacon: Beacon):
        """
        Synchronize the robot's position and orientation with a detected beacon.

        Args:
            beacon (Beacon): The detected beacon.
        """
        self.x = beacon.x
        self.y = beacon.y
        self.theta = beacon.orientation
        self.calibrated_by_beacon = True
        self.position_from_beacon.from_beacon = beacon
        self.position_from_beacon.distance = 0

    def read_calibration_file(self):
        """
        Read calibration factors from a JSON file and apply them to the robot.
        """
        calibration_file = "calibrate.json"
        if os.path.exists(calibration_file):
            with open("calibrate.json", "r") as f:
                string = f.read()
                calibration_dict = json.loads(string)
                robot_id = self.robot.id
                if robot_id in calibration_dict:
                    self.distance_correction_factor = calibration_dict[robot_id]["distance_correction_factor"]
                    self.theta_correction_factor = calibration_dict[robot_id]["theta_correction_factor"]
                    print(f"calibration for {robot_id}: {self.distance_correction_factor}, {self.theta_correction_factor}")
                else:
                    print(f"no calibration for {robot_id}")
        else:
            print("no calibration file found")


class OdometryReading:
    """
    Stores a single odometry reading, including step, position, orientation, and timestamp.
    """
    def __init__(self, step: int, x: float, y: float, theta: float, timestamp: int):
        """
        Initialize an OdometryReading.

        Args:
            step (int): Step number.
            x (float): X position.
            y (float): Y position.
            theta (float): Orientation in radians.
            timestamp (int): Timestamp in ns or ms.
        """
        self.step: int = step
        self.x: float = x
        self.y: float = y
        self.theta: float = theta
        self.timestamp: float = timestamp