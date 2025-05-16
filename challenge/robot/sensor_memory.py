class SensorMemory:
    def __init__(self, length: int):
        """
        Initialize the sensor memory with a specified length. Only the last 'length' entries will be kept in memory.
        :param length:
        """
        self.memory: list[list[int]] = []
        self.length = length

    def update_memory(self, sensor_data: list[int]):
        """Update the memory with new sensor data."""
        if len(self.memory) >= self.length:
            # Remove the oldest data if memory is full
            self.memory.pop(0)
        self.memory.append(sensor_data)


    def get_average(self):
        """Calculate the average of the sensor data in memory."""
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
        """Clear all stored sensor data."""
        self.memory.clear()