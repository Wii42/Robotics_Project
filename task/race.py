"""
race.py

Entry Point for MarioKart e-puck Robotics Race

This script serves as the main entry point to start the MarioKart robot. It initializes the MarioKart class
with the provided IP address (or a default one) and starts the robot's main control loop.

Usage:
------
Run this script with an optional IP address argument:
    python race.py [ROBOT_IP]

If no IP address is provided, the default MY_IP will be used.

Authors:
--------
- Lukas Künzi
- Thirith Yang

Date:
------
18th May 2025
"""

import sys
from main import MarioKart

MY_IP = '192.168.2.210'

if __name__ == "__main__":
    # Check if an IP address is provided as a command-line argument
    if len(sys.argv) == 2:
        ip = sys.argv[1]
        print("ip: ", ip)
    else:
        ip = MY_IP
    # Initialize MarioKart with the selected IP and start the main control loop
    MarioKart(ip, norm_speed=3, communicate=True).run()