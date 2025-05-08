class ObstacleDetector:
    def __init__(self, tipping_value: float):
        self.tipping_value = tipping_value


    def is_obstacle(self, proximity_sensors: list[float]) -> bool:
        left_front_diagonal = proximity_sensors[6]
        left_front = proximity_sensors[7]
        right_front = proximity_sensors[0]
        right_front_diagonal = proximity_sensors[1]

        weighted_average = (left_front_diagonal*0.5 + right_front_diagonal*0.5 + left_front + right_front) / 3

        return weighted_average > self.tipping_value
