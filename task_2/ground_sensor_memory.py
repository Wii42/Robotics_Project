class GroundSensorMemory:
    def __init__(self, length: int):
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



memory = GroundSensorMemory(length=2)  # Example length of memory
# Example sensor data
sensor_data = [100, 200, 300]
memory.update_memory(sensor_data)
print(memory.memory)
data2 = [50, 150, 250]
memory.update_memory(data2)
print(memory.memory)
average = memory.get_average()
print("Average:", average)