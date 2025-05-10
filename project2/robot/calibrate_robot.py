import json
import sys, signal

from unifr_api_epuck import wrapper

from project2.robot.beacon_detector import BeaconDetector
from project2.coordinator import coordinator
from project2.robot.grey_area import GreyArea
from project2.robot.odometry import Odometry
from project2.robot.robot_controller import GREY_MIN, LINE_MAX
from project2.robot.step_counter import StepCounter
from project2.robot.track_follower import TrackFollower

def calibrate_robot(robot_id: str, msg: str):
    #with open("calibrate.json", "r") as f:
    #    string = f.read()
    #    calibration_dict = json.loads(string)
    with open("calibrate.json", "a") as f:
        f.write(f"{robot_id}: {msg}\n")
        f.flush()
        f.close()

def main(robot_ip: str, norm_speed: float = 1):
    robot = wrapper.get_robot(robot_ip)

    def handler(signum, frame):
        robot.clean_up()

    signal.signal(signal.SIGINT, handler)

    robot.init_ground()

    step_counter: StepCounter = StepCounter()

    grey_area: GreyArea = GreyArea(norm_speed)
    detector: BeaconDetector = BeaconDetector(norm_speed, grey_area, GREY_MIN, LINE_MAX, coordinator.BEACONS,
                                              step_counter)
    track_follower: TrackFollower = TrackFollower(robot, norm_speed, LINE_MAX)
    odometry: Odometry = Odometry(robot, step_counter)

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()


        odometry.odometry(track_follower.current_speed[0], track_follower.current_speed[1])

        detector.receive_ground(gs)

        if detector.new_beacon_found():
            if odometry.position_from_beacon.from_beacon is not None:
                calibrate_robot(robot.id, f"[{odometry.position_from_beacon.from_beacon.name}->{detector.last_beacon.name}] {odometry.position_from_beacon.distance}")
            odometry.sync_with_beacon(detector.last_beacon)

        if not track_follower.follow_track(gs):
            break

        step_counter.step()

    robot.clean_up()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        ip = '192.168.2.205'
    main(ip)
