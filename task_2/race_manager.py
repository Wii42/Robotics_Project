"""
race_manager.py

Race Manager Script for MarioKart e-puck Robotics Project

This script acts as a central race manager for coordinating and timing a MarioKart-inspired robotics race
between two e-puck robots. It listens for "start" and "goal" messages from the robots, records their arrival times,
and prints the results, including the time difference between the two finishers.

How it works:
-------------
- Waits for a "start" message to begin the race and records the start time.
- Listens for "goal" messages from the robots.
- Records the finish times for the first and second robots to cross the finish line.
- Prints the start time, both finish times, and the time difference.

Usage:
------
Run this script before starting the robots. The robots should be configured to send "start" and "goal" messages
to the race manager's host IP.

Authors:
--------
- Lukas Künzi
- Thirith Yang

Date:
------
18th May 2025
"""

from unifr_api_epuck import wrapper
import time
from datetime import datetime

# Initialize the race manager client to listen for messages from robots
race_manager = wrapper.get_client(client_id='Race Manager', host_ip='http://127.0.0.1:8000')

# Variables to store the start and finish times
time_start = None
time_goal1 = None
time_goal2 = None

# Define states for the race manager
IDLE = 0
RACE = 1
FIRST = 2
SECOND = 3

state = IDLE

# Main loop to listen for messages and manage race timing
while True:
    if race_manager.has_receive_msg():
        msg = race_manager.receive_msg()
        print(msg)
        if msg == "start":
            # Record the start time when the race begins
            time_start = datetime.now()
            state = RACE
        elif msg == "goal":
            if state == RACE:
                # Record the time for the first robot to finish
                time_goal1 = datetime.now()
                print("first " + str(time_goal1 - time_start))
                state = FIRST
            elif state == FIRST:
                # Record the time for the second robot to finish
                time_goal2 = datetime.now()
                print("second " + str(time_goal2 - time_start))
                state = SECOND
    if state == SECOND:
        # Exit loop after both robots have finished
        break

# Format for displaying times
timeformat = "%H:%M:%S %f"

# Print the results
print(f"\nStart time: {time_start}\n\nArrival times:\n\n\t1. {time_goal1.strftime(timeformat)}\n\t2. {time_goal2.strftime(timeformat)}\n\nDifference: {time_goal2-time_goal1}")


