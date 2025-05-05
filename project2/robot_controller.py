import math
import sys

from unifr_api_epuck import wrapper
from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck

from beacon_detector import BeaconDetector
from beacon import Beacon
from project2 import coordinator
from project2.coordinator import beacons
from project2.grey_area import GreyArea
from project2.odometry import Odometry
from project2.step_counter import StepCounter
from track_follower import TrackFollower
import queue

LINE_MAX: int = 750  # to determine if the sensor is on the line

GREY_MIN: int = 450  # to determine if the sensor is on the grey area

def send_pos(robot: WifiEpuck, robot_position: list[float], position_on_track: float):
        robot.ClientCommunication.send_msg_to(coordinator.COORDINATOR_ID, {"robot_id": robot.id.split("_")[-1], "robot_position": robot_position.copy(), "position_on_track": position_on_track})

def main(robot_ip: str, norm_speed: float = 1):


    robot = wrapper.get_robot(robot_ip)
    robot.init_ground()
    robot.init_client_communication()

    step_counter: StepCounter = StepCounter()

    grey_area: GreyArea = GreyArea(norm_speed)

    detector: BeaconDetector = BeaconDetector(norm_speed, grey_area, GREY_MIN, LINE_MAX, beacons, step_counter)
    track_follower: TrackFollower = TrackFollower(robot, norm_speed, LINE_MAX)

    odometry: Odometry = Odometry(robot, step_counter)

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()

        odometry.odometry(track_follower.current_speed[0], track_follower.current_speed[1])


        detector.receive_ground(gs)

        odometry.print_position()


        if detector.new_beacon_found():
            print(f"[{robot.id.split('_')[-1]}] found beacon: {detector.last_beacon.name}")
            odometry.sync_with_beacon(detector.last_beacon)

        send_pos(robot, [odometry.x, odometry.y], odometry.position_on_track)



        if not track_follower.follow_track():
            break

        step_counter.step()

    robot.clean_up()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        ip = '192.168.2.207'
    main(ip)
