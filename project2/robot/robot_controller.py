import sys, signal

from unifr_api_epuck import wrapper
from unifr_api_epuck.epuck.epuck_wifi import WifiEpuck

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

GREY_MIN: int = 450  # to determine if the sensor is on the grey area


def send_pos(robot: WifiEpuck, robot_position: list[float], position_on_track: PositionOnTrack):
    robot.ClientCommunication.send_msg_to(coordinator.COORDINATOR_ID,
                                          {"robot_id": robot.id, "robot_position": robot_position.copy(),
                                           "position_on_track": position_on_track.to_dict()})


def main(robot_ip: str, norm_speed: float = 1):
    robot = wrapper.get_robot(robot_ip)

    def handler(signum, frame):
        robot.clean_up()

    signal.signal(signal.SIGINT, handler)

    robot.init_ground()
    robot.calibrate_prox()
    robot.init_client_communication()

    step_counter: StepCounter = StepCounter()
    proximity_memory: SensorMemory = SensorMemory(5)
    grey_area: GreyArea = GreyArea(norm_speed)
    obstacle_avoider: ObstacleAvoider = ObstacleAvoider(40, 100)
    detector: BeaconDetector = BeaconDetector(norm_speed, grey_area, GREY_MIN, LINE_MAX, coordinator.BEACONS,
                                              step_counter)
    track_follower: TrackFollower = TrackFollower(robot, norm_speed, LINE_MAX)
    odometry: Odometry = Odometry(robot, step_counter)

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()
        proximity_memory.update_memory(robot.get_calibrate_prox())

        while robot.has_receive_msg():
            msg = robot.receive_msg()
            if msg.get("speed_factor"):
                speed_factor = msg.get("speed_factor")
                print(f"[{robot.id.split('_')[-1]}] received speed factor: {speed_factor}")
                track_follower.speed_factor = speed_factor
        odometry.odometry(track_follower.current_speed[0], track_follower.current_speed[1])

        detector.receive_ground(gs)

        # odometry.print_position()

        if detector.new_beacon_found():
            print(f"[{robot.id.split('_')[-1]}] found beacon: {detector.last_beacon.name}")
            odometry.sync_with_beacon(detector.last_beacon)

        if step_counter.get_steps() % 10 == 0:
            send_pos(robot, [odometry.x, odometry.y], odometry.position_from_beacon)

        track_follower.obstacle_speed_factor = obstacle_avoider.calc_speed(proximity_memory.get_average())
        if track_follower.obstacle_speed_factor != 1.0:
            print(f"[{robot.id.split('_')[-1]}] obstacle speed factor: {track_follower.obstacle_speed_factor}")

        if not track_follower.follow_track(gs):
            break

        step_counter.step()

    robot.clean_up()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        ip = '192.168.2.207'
    main(ip)
