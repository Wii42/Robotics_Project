from unifr_api_epuck import wrapper
from beacon_detector import BeaconDetector
from beacon import Beacon
from track_follower import TrackFollower
import queue

MY_IP: str = '192.168.2.208'

NORM_SPEED: float = 1
GREY_MIN_LENGTH: float = 10 / NORM_SPEED  # how long the robot should be in the grey area
GREY_DISTANCE_MAX: float = 2 * GREY_MIN_LENGTH  # how far apart the grey areas can be for it to count as one beacon

LINE_MAX: int = 750  # to determine if the sensor is on the line

GREY_MIN: int = 450  # to determine if the sensor is on the grey area

beacons: dict[int, Beacon] = {1: Beacon("beacon1", 450, 540),
                              2: Beacon("beacon2", 500, 60),
                              }
def send_pos(state_queue: queue.Queue, robot_position: list[float]):
    if state_queue is not None:
        state_queue.put({"robot_position": robot_position.copy()})

def mock_move(robot_position: list[float]):
    robot_position[0] += 1
    robot_position[1] += 0.5

def main(state_queue: queue.Queue = None):
    robot = wrapper.get_robot(MY_IP)
    robot.init_ground()

    detector: BeaconDetector = BeaconDetector(NORM_SPEED, GREY_MIN_LENGTH,
                                              GREY_DISTANCE_MAX, GREY_MIN, LINE_MAX, beacons)
    track_follower: TrackFollower = TrackFollower(robot, NORM_SPEED, LINE_MAX)

    robot_position: list[float] = [50, 50]

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()

        mock_move(robot_position)
        send_pos(state_queue, robot_position)

        detector.receive_ground(gs)


        if detector.new_beacon_found():
            print(f"found beacon: {detector.last_beacon.name}")
            robot_position = [detector.last_beacon.x, detector.last_beacon.y]
            send_pos(state_queue, robot_position)

        if not track_follower.follow_track():
            break

    robot.clean_up()


if __name__ == '__main__':
    main()
