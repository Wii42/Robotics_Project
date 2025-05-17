"""
sensor_memory.py

Stores and processes recent sensor readings for the ePuck robot.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

class SensorMemory:
    """
    The SensorMemory class stores a fixed number of recent sensor readings
    and provides methods to update, average, and clear the memory.
    """
    def __init__(self, length: int):
        """
        Initialize the sensor memory with a specified length.
        Only the last 'length' entries will be kept in memory.

        Args:
            length (int): The maximum number of sensor readings to store.
        """
        self.memory: list[list[int]] = []
        self.length = length

    def update_memory(self, sensor_data: list[int]):
        """
        Update the memory with new sensor data. If the memory is full,
        remove the oldest entry before adding the new data.

        Args:
            sensor_data (list[int]): The latest sensor reading to store.
        """
        if len(self.memory) >= self.length:
            # Remove the oldest data if memory is full
            self.memory.pop(0)
        self.memory.append(sensor_data)

    def get_average(self):
        """
        Calculate the average of the sensor data in memory.

        Returns:
            list[float] | None: The average value for each sensor, or None if memory is empty.
        """
        if not self.memory:
            return None
        # Calculate the average for each sensor
        average = [0] * len(self.memory[0])
        for data in self.memory:
            for i in range(len(data)):
                average[i] += data[i]

        # Divide by the number of entries to get the average
        for i in range(len(average)):
            average[i] /= len(self.memory)
        return average

    def clear_memory(self):
        """
        Clear all stored sensor data from memory.

        Returns:
            None
        """
        self.memory.clear()