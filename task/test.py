"""
test.py

This script demonstrates basic robot control and step counting for the ePuck robot.
It initializes the robot, sets up a step counter, and moves the robot forward while
printing the current step count at each iteration. The script is intended for testing
basic movement and integration of the step counting functionality.

Authors:
    Lukas Künzi
    Thirith Yang

Date:
    18th May 2025
"""

from unifr_api_epuck import wrapper
from step_counter import StepCounter
from track_follower import TrackFollower
from determine_side import DetermineSide
from ground_sensor_memory import GroundSensorMemory
from line_alignment import LineAlignment
import utils
import os
import time

# Constants for robot configuration
MY_IP = '192.168.2.211'  # IP address of the robot
LINE_MAX_VALUE = 500     # Maximum value for the line to be considered black
STEPS_TO_DETERMINE_SIDE = 20  # Number of steps to determine the side

def main():
    """
    Main function to control the robot's basic movement and step counting.

    - Initializes the robot using the provided IP address.
    - Sets up a step counter to track the robot's movement.
    - Continuously moves the robot forward while counting steps.
    - Cleans up the robot's resources after the loop ends.
    """
    # Initialize the robot using the wrapper library
    robot = wrapper.get_robot(MY_IP)
    
    # Directory for storing object detection data (not used in this script)
    output_dir = "./object_detections"

    # Initialize the step counter
    counter = StepCounter()
    
    # Wait for 1 second before starting the main loop
    time.sleep(1)

    # Main loop to control the robot
    while robot.go_on():
        # Get the current step count
        steps = counter.get_steps()
        
        # Set the robot's speed (left and right wheel speeds)
        robot.set_speed(2 * 1.2, 2 * 0.9)
        
        # Print the current step count for debugging
        print(steps)
        
        # Increment the step counter
        counter.step()

    # Clean up the robot's resources after exiting the loop
    robot.clean_up()

# Entry point of the script
if __name__ == "__main__":
    main()
