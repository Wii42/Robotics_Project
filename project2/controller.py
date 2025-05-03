import math

from unifr_api_epuck import wrapper
from beacon_detector import BeaconDetector
from beacon import Beacon
from project2.odometry import Odometry
from project2.step_counter import StepCounter
from track_follower import TrackFollower
import queue

MY_IP: str = '192.168.2.211'

NORM_SPEED: float = 1
GREY_MIN_LENGTH: float = 10 / NORM_SPEED  # how long the robot should be in the grey area
GREY_DISTANCE_MAX: float = 2 * GREY_MIN_LENGTH  # how far apart the grey areas can be for it to count as one beacon

LINE_MAX: int = 750  # to determine if the sensor is on the line

GREY_MIN: int = 450  # to determine if the sensor is on the grey area

beacons: dict[int, Beacon] = {1: Beacon("beacon1", 450, 540, math.pi),
                              2: Beacon("beacon2", 500, 60, 0),
                              }
def send_pos(state_queue: queue.Queue, robot_position: list[float]):
    if state_queue is not None:
        state_queue.put({"robot_position": robot_position.copy()})

def main(state_queue: queue.Queue = None):
    robot = wrapper.get_robot(MY_IP)
    robot.init_ground()

    step_counter: StepCounter = StepCounter()

    detector: BeaconDetector = BeaconDetector(NORM_SPEED, GREY_MIN_LENGTH,
                                              GREY_DISTANCE_MAX, GREY_MIN, LINE_MAX, beacons)
    track_follower: TrackFollower = TrackFollower(robot, NORM_SPEED, LINE_MAX)

    odometry: Odometry = Odometry(robot, step_counter)

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()

        odometry.odometry(track_follower.current_speed[0], track_follower.current_speed[1])
        send_pos(state_queue, [odometry.x, odometry.y])

        detector.receive_ground(gs)

        odometry.print_position()

        #print(track_follower.current_speed)


        if detector.new_beacon_found():
            print(f"found beacon: {detector.last_beacon.name}")
            robot_position = [detector.last_beacon.x, detector.last_beacon.y]
            send_pos(state_queue, robot_position)
            odometry.x = robot_position[0]
            odometry.y = robot_position[1]
            odometry.theta = detector.last_beacon.orientation



        if not track_follower.follow_track():
            break

        step_counter.step()

    robot.clean_up()


if __name__ == '__main__':
    main()
