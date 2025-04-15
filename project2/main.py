from unifr_api_epuck import wrapper
from beacon_detector import BeaconDetector
from track_follower import TrackFollower

MY_IP: str = '192.168.2.208'

NORM_SPEED: float = 1
GREY_MIN_LENGTH: float = 10 / NORM_SPEED  # how long the robot should be in the grey area
GREY_DISTANCE_MAX: float = 2 * GREY_MIN_LENGTH  # how far apart the grey areas can be for it to count as one beacon

LINE_MAX: int = 750  # to determine if the sensor is on the line

GREY_MIN: int = 450  # to determine if the sensor is on the grey area


def main():
    robot = wrapper.get_robot(MY_IP)
    robot.init_ground()

    detector: BeaconDetector = BeaconDetector(NORM_SPEED, GREY_MIN_LENGTH,
                                              GREY_DISTANCE_MAX, grey_min_value=GREY_MIN, grey_max_value=LINE_MAX)
    track_follower: TrackFollower = TrackFollower(robot, NORM_SPEED, LINE_MAX)

    while robot.go_on():
        robot.go_on()
        gs: list[int] = robot.get_ground()

        detector.receive_ground(gs)

        if not track_follower.follow_track():
            break

    robot.clean_up()


if __name__ == '__main__':
    main()
