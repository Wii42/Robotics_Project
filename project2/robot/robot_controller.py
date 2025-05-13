import json
import os
import sys, signal

from unifr_api_epuck import wrapper
from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck

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
    def __init__(self, robot_ip: str, norm_speed: float = 1):
        self.norm_speed = norm_speed
        self.robot = wrapper.get_robot(robot_ip)

        self.step_counter: StepCounter | None = None
        self.proximity_memory: SensorMemory | None = None
        self.grey_area: GreyArea | None = None
        self.obstacle_avoider: ObstacleAvoider | None = None
        self.beacon_detector: BeaconDetector | None = None
        self.track_follower: TrackFollower | None = None
        self.odometry: Odometry | None = None

        def handler(signum, frame):
            self.robot.clean_up()

        signal.signal(signal.SIGINT, handler)

    def run(self):
        self.init_track_follower_odometry()
        #self.odometry.calibrate_robot()

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
        self.robot.init_ground()
        self.step_counter: StepCounter = StepCounter()
        self.grey_area: GreyArea = GreyArea(self.norm_speed)
        self.beacon_detector: BeaconDetector = BeaconDetector(self.norm_speed, self.grey_area, GREY_MIN, LINE_MAX,
                                                              coordinator.BEACONS,
                                                              self.step_counter)
        self.track_follower: TrackFollower = TrackFollower(self.robot, self.norm_speed, LINE_MAX)
        self.odometry: Odometry = Odometry(self.robot, self.step_counter)

    def adjust_speed_to_possible_obstacle(self):
        self.track_follower.obstacle_speed_factor = self.obstacle_avoider.calc_speed(
            self.proximity_memory.get_average())
        #if self.track_follower.obstacle_speed_factor != 1.0:
        #    print(
        #        f"[{self.robot.id.split('_')[-1]}] obstacle speed factor: {self.track_follower.obstacle_speed_factor}")

    def notify_coordinator_of_position(self):
        if self.step_counter.get_steps() % 20 == 0:
            self.send_pos([self.odometry.x, self.odometry.y], self.odometry.position_from_beacon)

    def send_pos(self, robot_position: list[float], position_on_track: PositionOnTrack):
        self.robot.ClientCommunication.send_msg_to(coordinator.COORDINATOR_ID,
                                                   {"robot_id": self.robot.id, "robot_position": robot_position.copy(),
                                                    "position_on_track": position_on_track.to_dict()})

    def check_for_beacons(self, save_to_file: bool = False):
        if self.beacon_detector.new_beacon_found():
            print(f"[{self.robot.id.split('_')[-1]}] found beacon: {self.beacon_detector.last_beacon.name}")
            if save_to_file:
                self.save_calibration(self.odometry)
            self.odometry.sync_with_beacon(self.beacon_detector.last_beacon)

    def save_calibration(self, odometry: Odometry):

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
        self.proximity_memory.update_memory(self.robot.get_calibrate_prox())

    def handle_incoming_messages(self):
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
