from unifr_api_epuck import wrapper

from project2.robot.step_counter import StepCounter
from project2.robot.track_follower import TrackFollower
from task_2.determine_side import DetermineSide
from task_2.ground_sensor_memory import GroundSensorMemory
from task_2.line_alignment import LineAlignment

MY_IP = '192.168.2.211'
LINE_MAX_VALUE: int = 500

STEPS_TO_DETERMINE_SIDE: int = 20


def main():
    robot = wrapper.get_robot(MY_IP)

    robot.init_ground()
    robot.init_camera("./tmp")
    robot.initiate_model()

    counter: StepCounter = StepCounter()

    line_follower: TrackFollower = TrackFollower(robot, 3, LINE_MAX_VALUE)

    sensor_memory: GroundSensorMemory = GroundSensorMemory(3)

    determine_side: DetermineSide = DetermineSide(750, LINE_MAX_VALUE, STEPS_TO_DETERMINE_SIDE)

    line_alignment: LineAlignment = LineAlignment()

    check_side_necessary: bool = True

    while robot.go_on():
        if counter.get_steps() > STEPS_TO_DETERMINE_SIDE and check_side_necessary:
            line_alignment.check_line_alignment(determine_side.get_probable_side())
            check_side_necessary = False


        gs: list[int] = robot.get_ground()
        sensor_memory.update_memory(gs)
        # print(gs)
        # print(gs)
        # robot.set_speed(5,5)
        if not line_follower.follow_track(sensor_memory.get_average(), use_two_sensors_approach=True,
                                          invert_side=line_alignment.get_follow_left_side()):
            break
        determine_side.determine_side(sensor_memory.get_average(), line_follower.position,
                                      invert_side=line_alignment.get_follow_left_side())
        print(determine_side.get_probable_side())
        print()

        counter.step()

    robot.clean_up()


if __name__ == "__main__":
    main()
