class ObstacleAvoider:
    def __init__(self, slow_dow_proximity: float, reverse_proximity: float):
        """

        :param slow_dow_proximity: if the proximity is greater than, this, the robot should slow down.
        :param reverse_proximity: if the proximity is greater than this, the robot should reverse.
        """
        self.slow_down_proximity = slow_dow_proximity
        self.reverse_proximity = reverse_proximity

    def get_proximity(self, proximity_sensors: list[float])->float:
        left_front_diagonal = proximity_sensors[6]
        left_front = proximity_sensors[7]
        right_front = proximity_sensors[0]
        right_front_diagonal = proximity_sensors[1]

        return (left_front_diagonal * 0.5 + right_front_diagonal * 0.5 + left_front + right_front) / 3

    def is_obstacle(self, proximity_sensors: list[float]) -> bool:
        weighted_average = self.get_proximity(proximity_sensors)

        return weighted_average > self.slow_down_proximity

    def calc_speed_factor_on_proximity(self, proximity: float) -> float:
        """
        Calculate the speed factor based on the proximity sensors.
        :return: speed factor
        """

        # calculate the as a linear function
        if proximity <= self.slow_down_proximity:
            return 1.0  # Full speed

        slope = -1.0 / (self.slow_down_proximity - self.reverse_proximity)
        intercept = slope * self.slow_down_proximity
        return slope * proximity + intercept

    def calc_speed(self, proximity_sensors: list[float]):
        """
        Calculate the speed based on the proximity sensors.
        :return: speed factor
        """
        weighted_average = self.get_proximity(proximity_sensors)
        return self.calc_speed_factor_on_proximity(weighted_average)




