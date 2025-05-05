from unifr_api_epuck import wrapper

from project2.track_follower import TrackFollower

MY_IP = '192.168.2.208'
LINE_MAX_VALUE: int = 575

def main():
    robot = wrapper.get_robot(MY_IP)

    robot.init_ground()

    line_follower = TrackFollower(robot, 5, LINE_MAX_VALUE)

    while robot.go_on():
        gs: list[int] = robot.get_ground()
        print(gs)
        # print(gs)
        #robot.set_speed(5,5)
        if not line_follower.follow_track(use_two_sensors_approach=True):
            break

    robot.clean_up()


if __name__ == "__main__":
    main()