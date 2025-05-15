from unifr_api_epuck import wrapper
import time
from datetime import datetime

# Initialize the race manager client to communicate with the robot
race_manager = wrapper.get_client(client_id='Race Manager', host_ip='http://127.0.0.1:8000')

# Variables to store timestamps for race events
time_start = None  # Time when the race starts
time_goal1 = None  # Time when the robot reaches the first goal
time_goal2 = None  # Time when the robot reaches the second goal

# Define states for the race
IDLE = 0  # Waiting for the race to start
RACE = 1  # Race is ongoing
FIRST = 2  # First goal reached
SECOND = 3  # Second goal reached

# Initialize the state to IDLE
state = IDLE

# Main loop to manage the race
while True:
    # Check if a message has been received from the race manager
    if race_manager.has_receive_msg():
        msg = race_manager.receive_msg()  # Retrieve the message
        print(msg)  # Print the received message for debugging

        # Handle the "start" message to begin the race
        if msg == "start":
            time_start = datetime.now()  # Record the start time
            state = RACE  # Update the state to RACE

        # Handle the "goal" message when the robot reaches a goal
        elif msg == "goal":
            if state == RACE:
                # Record the time for the first goal and update the state
                time_goal1 = datetime.now()
                print("first " + str(time_goal1 - time_start))  # Print the time difference
                state = FIRST
            elif state == FIRST:
                # Record the time for the second goal and update the state
                time_goal2 = datetime.now()
                print("second " + str(time_goal2 - time_start))  # Print the time difference
                state = SECOND

    # Exit the loop if the second goal has been reached
    if state == SECOND:
        break

# Define the time format for displaying timestamps
timeformat = "%H:%M:%S %f"

# Print the race results, including start time, goal times, and the time difference
print(
    f"\nStart time: {time_start}\n\nArrival times:\n\n\t1. {time_goal1.strftime(timeformat)}\n\t2. {time_goal2.strftime(timeformat)}\n\nDifference: {time_goal2 - time_goal1}")

