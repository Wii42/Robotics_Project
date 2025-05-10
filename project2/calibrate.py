import sys

from project2.robot.robot_controller import RobotController

if __name__ == '__main__':
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        ip = '192.168.2.205'
    RobotController(ip).calibrate_robot()