import json
import os
import sys, signal

from unifr_api_epuck import wrapper

from project2.core.beacon import Beacon
from project2.robot.beacon_detector import BeaconDetector
from project2.coordinator import coordinator
from project2.robot.grey_area import GreyArea
from project2.robot.obstacle_avoider import ObstacleAvoider
from project2.robot.odometry import Odometry
from project2.core.position_on_track import PositionOnTrack
from project2.robot.sensor_memory import SensorMemory
from project2.robot.step_counter import StepCounter
from project2.robot.track_follower import TrackFollower

LINE_MAX: int = 750  # to determine if the sensor is on the line

GREY_MIN: int = 500  # to determine if the sensor is on the grey area


class RobotController:
    """
    RobotController class to control the robot's behavior and handle communication with the coordinator.

    This class acts as the main interface for robot control. It initializes the robot connection
    and manages different modules such as obstacle avoidance, track following, and odometry.

    Attributes:
        norm_speed (float): The robot's default movement speed. Defaults to 1.
        robot: The robot instance obtained from the wrapper using the provided IP address.
        step_counter (StepCounter | None): Optional module for counting movement steps.
        proximity_memory (SensorMemory | None): Optional module for storing proximity sensor data.
        grey_area (GreyArea | None): Optional module for handling grey area detection and logic.
        obstacle_avoider (ObstacleAvoider | None): Optional module for avoiding detected obstacles.
        beacon_detector (BeaconDetector | None): Optional module for detecting beacons.
        track_follower (TrackFollower | None): Optional module for following predefined tracks.
        odometry (Odometry | None): Optional module for tracking the robot's position and orientation.
    """

    def __init__(self, robot_ip: str, norm_speed: float = 1):
        """
        RobotController constructor.
        :param robot_ip: IP address of the robot.
        :param norm_speed: The robot's default movement speed. Defaults to 1.
        """
        self.norm_speed = norm_speed
        self.robot = wrapper.get_robot(robot_ip)

        self.step_counter: StepCounter | None = None
        self.proximity_memory: SensorMemory | None = None
        self.grey_area: GreyArea | None = None
        self.obstacle_avoider: ObstacleAvoider | None = None
        self.beacon_detector: BeaconDetector | None = None
        self.track_follower: TrackFollower | None = None
        self.odometry: Odometry | None = None

        # Set up signal handler for graceful shutdown
        def handler(signum, frame):
            self.robot.clean_up()

        signal.signal(signal.SIGINT, handler)

    def run(self):
        """
        Main loop for the robot controller.
        :return: None
        """
        self.init_track_follower_odometry()
        self.odometry.calibrate_robot()

        self.robot.calibrate_prox()
        self.robot.init_client_communication()

        self.proximity_memory: SensorMemory = SensorMemory(5)
        self.obstacle_avoider: ObstacleAvoider = ObstacleAvoider(40, 100)

        while self.robot.go_on():
            gs: list[int] = self.robot.get_ground()
            self.read_proximity_sensors()

            self.handle_incoming_messages()
            self.odometry.odometry(*self.track_follower.current_speed)

            self.beacon_detector.receive_ground(gs)
            self.check_for_beacons()

            self.notify_coordinator_of_position()

            self.adjust_speed_to_possible_obstacle()

            if not self.track_follower.follow_track(gs):
                break

            self.step_counter.step()

        self.robot.clean_up()

    def calibrate_robot(self):
        """
        Calibrate the robot by following the track and detecting beacons.
        :return: None
        """
        self.init_track_follower_odometry()
        print("calibrating robot")
        while self.robot.go_on():
            gs: list[int] = self.robot.get_ground()

            self.odometry.odometry(*self.track_follower.current_speed)

            self.beacon_detector.receive_ground(gs)
            self.check_for_beacons(save_to_file=True)

            if not self.track_follower.follow_track(gs):
                break

            self.step_counter.step()

        self.robot.clean_up()

    def init_track_follower_odometry(self):
        """
        Initializes the track follower and odometry modules.
        :return: None
        """
        self.robot.init_ground()
        self.step_counter: StepCounter = StepCounter()
        self.grey_area: GreyArea = GreyArea(self.norm_speed)
        self.beacon_detector: BeaconDetector = BeaconDetector(self.norm_speed, self.grey_area, GREY_MIN, LINE_MAX,
                                                              coordinator.BEACONS,
                                                              self.step_counter)
        self.track_follower: TrackFollower = TrackFollower(self.robot, self.norm_speed, LINE_MAX)
        self.odometry: Odometry = Odometry(self.robot, self.step_counter)

    def adjust_speed_to_possible_obstacle(self):
        """
        Adjusts the robot's speed based on the proximity sensor data, so it stops in front of an obstacle.
        :return: None
        """
        self.track_follower.obstacle_speed_factor = self.obstacle_avoider.calc_speed(
            self.proximity_memory.get_average())

    def notify_coordinator_of_position(self):
        """
        Periodically notify the coordinator of the robot's probable position and orientation.
        :return: None
        """
        if self.step_counter.get_steps() % 20 == 0:
            self.send_pos([self.odometry.x, self.odometry.y], self.odometry.position_from_beacon)

    def send_pos(self, robot_position: list[float], position_on_track: PositionOnTrack):
        """
        Send the robot's position and orientation to the coordinator.
        :param robot_position: The robot's position in the form of [x, y].
        :param position_on_track: The robot's position on the track as a PositionOnTrack object.
        :return: None
        """
        self.robot.ClientCommunication.send_msg_to(coordinator.COORDINATOR_ID,
                                                   {"robot_id": self.robot.id, "robot_position": robot_position.copy(),
                                                    "position_on_track": position_on_track.to_dict()})

    def check_for_beacons(self, save_to_file: bool = False):
        """
        Check if a new beacon has been detected.
        :param save_to_file: If True, save the calibration data to a file.
        :return: None
        """
        if self.beacon_detector.new_beacon_found():
            print(f"[{self.robot.id.split('_')[-1]}] found beacon: {self.beacon_detector.last_beacon.name}")
            if save_to_file:
                self.save_calibration(self.odometry)
            self.odometry.sync_with_beacon(self.beacon_detector.last_beacon)

    def save_calibration(self, odometry: Odometry):
        """
        Save the calibration data to a file.
        :param odometry: The odometry object containing the robot's position and orientation.
        :return: None
        """

        position_from_beacon = odometry.position_from_beacon
        if position_from_beacon.from_beacon is not None:
            if self.beacon_detector.last_beacon == position_from_beacon.from_beacon.next_beacon[0]:
                distance_between_beacons = position_from_beacon.from_beacon.next_beacon[1]
                distance_correction_factor = distance_between_beacons / position_from_beacon.distance
                previous_beacon_theta = position_from_beacon.from_beacon.orientation
                theta_correction_factor = (
                                                  self.beacon_detector.last_beacon.orientation - previous_beacon_theta) / (
                                                      odometry.theta - previous_beacon_theta)
                save_calibration_to_file(self.robot.id,
                                         odometry.position_from_beacon.from_beacon,
                                         self.beacon_detector.last_beacon,
                                         distance_correction_factor, theta_correction_factor)

    def read_proximity_sensors(self):
        """
        Read the proximity sensors and update the sensor memory.
        :return: None
        """
        self.proximity_memory.update_memory(self.robot.get_calibrate_prox())

    def handle_incoming_messages(self):
        """
        Handle incoming messages from the coordinator and update the robot's speed factor accordingly.
        :return: None
        """
        while self.robot.has_receive_msg():
            msg = self.robot.receive_msg()
            if msg.get("speed_factor"):
                speed_factor = msg.get("speed_factor")
                print(f"[{self.robot.id.split('_')[-1]}] received speed factor: {speed_factor}")
                self.track_follower.speed_factor = speed_factor


def save_calibration_to_file(robot_id: str, from_beacon: Beacon, to_beacon: Beacon, distance_correction_factor: float,
                             theta_correction_factor: float):
    calibration_file = "calibrate.json"
    if os.path.exists(calibration_file):
        with open("calibrate.json", "r") as f:
            string = f.read()
            calibration_dict = json.loads(string)
    else:
        calibration_dict = {}
    calibration_dict[robot_id] = {"from": from_beacon.name, "to": to_beacon.name,
                                  "distance_correction_factor": distance_correction_factor,
                                  "theta_correction_factor": theta_correction_factor}
    with open("calibrate.json", "w") as f:
        f.write(json.dumps(calibration_dict))
        f.flush()
        f.close()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        ip = '192.168.2.207'
    RobotController(ip).run()
