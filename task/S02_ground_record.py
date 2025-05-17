"""
S02_ground_record.py

This script connects to an ePuck robot, initializes its ground sensors, and records ground sensor data
to a CSV file for a specified number of steps. The data can be used for later analysis and plotting.

Authors:
    Lukas Künzi
    Thirith Yang

Date:
    18th May 2025
"""

# run the code to generate IR sensor data 
from unifr_api_epuck import wrapper

# IP address of the ePuck robot
MY_IP = '192.168.2.210'
# Number of steps to record
MAX_STEPS = 750

# Connect to the robot using the provided IP address
robot = wrapper.get_robot(MY_IP)

# Initialize ground sensors
robot.init_ground()

# Open file for writing ground sensor data
data = open("Gsensors.csv", "w")

if data == None:
    print('Error opening data file!\n')
    quit

# Write header in CSV file
data.write('step,')
for i in range(robot.GROUND_SENSORS_COUNT):
    data.write('gs' + str(i) + ',')
data.write('\n')

# Wait 3 seconds before starting data collection
robot.sleep(3)

# Main loop: record ground sensor data for each step
for step in range(MAX_STEPS):
    robot.go_on()  # Advance the robot one step
    gs = robot.get_ground()  # Read ground sensor values

    # Write a line of data: step number and sensor readings
    data.write(str(step) + ',')
    for v in gs:
        data.write(str(v) + ',')
    data.write('\n')

    # Set robot speed (left, right)
    robot.set_speed(2, 2)

# Close the data file after recording is complete
data.close()

# Clean up robot resources
robot.clean_up()
