from unifr_api_epuck import wrapper

from project2.track_follower import TrackFollower
from task_2.determine_side import DetermineSide, TrackSide
from task_2.ground_sensor_memory import GroundSensorMemory

MY_IP = '192.168.2.216'
LINE_MAX_VALUE: int = 575

def main():
    robot = wrapper.get_robot(MY_IP)

    robot.init_ground()

    line_follower = TrackFollower(robot, 3, LINE_MAX_VALUE)

    sensor_memory: GroundSensorMemory = GroundSensorMemory(2)

    determine_side: DetermineSide = DetermineSide(750, LINE_MAX_VALUE)

    invert_sides: bool = True

    while robot.go_on():
        gs: list[int] = robot.get_ground()
        sensor_memory.update_memory(gs)
        #print(gs)
        # print(gs)
        #robot.set_speed(5,5)
        if not line_follower.follow_track(sensor_memory.get_average(), use_two_sensors_approach=True, invert_side=invert_sides):
            break
        print(line_follower.position)
        determine_side.det_side(sensor_memory.get_average(), line_follower.position, invert_side= invert_sides)
        print(determine_side.get_probable_side(5))
        print()

    robot.clean_up()


if __name__ == "__main__":
    main()