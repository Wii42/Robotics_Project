"""
Calibration Script

This script is used to calibrate a robot by running its calibration routine.
It accepts an optional command-line argument for the robot's IP address.
If no IP is provided, it defaults to '192.168.2.208'.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

import sys
from challenge.robot.robot_controller import RobotController

if __name__ == '__main__':
    # Check if an IP address was provided as a command-line argument
    if len(sys.argv) == 2:
        ip = sys.argv[1]
    else:
        ip = '192.168.2.208'
    # Start the calibration routine for the specified robot
    RobotController(ip).calibrate_robot()