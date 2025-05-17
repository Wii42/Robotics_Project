"""
record_ground_sensors.py

This module provides utility functions for recording ground sensor data from the ePuck robot
to a CSV file. It allows for easy logging and later analysis of sensor readings during robot operation.

Functions:
    init_gsensors_record(self): Initializes the CSV file for recording ground sensor data.
    record_gsensors(self, data, gs): Records a single row of ground sensor data to the CSV file.

Authors:
    Lukas Künzi
    Thirith Yang
"""

def init_gsensors_record(self):
    """
    Initialize the CSV file for recording ground sensor data.

    Returns:
        file object: The opened file object for writing sensor data, or None if opening fails.
    """
    data = open("Gsensors.csv", "w")
    if data is None:
        print('Error opening data file!\n')
        return None

    # Write header in CSV file
    data.write('step,')
    for i in range(self.robot.GROUND_SENSORS_COUNT):
        data.write('gs' + str(i) + ',')
    data.write('\n')
    return data

def record_gsensors(self, data, gs):
    """
    Record a single row of ground sensor data to the CSV file.

    Args:
        data (file object): The file object to write to.
        gs (list): The list of ground sensor readings to record.
    """
    # Write the current step and sensor values to the file
    data.write(str(self.counter.get_steps()) + ',')
    for v in gs:
        data.write(str(v) + ',')
    data.write('\n')