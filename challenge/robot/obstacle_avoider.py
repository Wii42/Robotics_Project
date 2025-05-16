class ObstacleAvoider:
    """
    This class is used to avoid obstacles using proximity sensors.
    """
    def __init__(self, slow_dow_proximity: float, reverse_proximity: float):
        """
        ObstacleAvoider constructor.

        :param slow_dow_proximity: if the proximity is greater than, this, the robot should slow down.
        :param reverse_proximity: if the proximity is greater than this, the robot should reverse.
        """
        self.slow_down_proximity = slow_dow_proximity
        self.reverse_proximity = reverse_proximity

    def get_proximity(self, proximity_sensors: list[float])->float:
        """
        Get the proximity of the robot based on the proximity sensors.
        :param proximity_sensors: List of proximity sensors values.
        :return:
        """
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
        assert self.slow_down_proximity < self.reverse_proximity, "slow_down_proximity must be less than reverse_proximity"
        #return self.lover_behaviour(proximity)

        if proximity <= self.slow_down_proximity:
            return 1.0  # Full speed

        slope = -1.0 / (self.reverse_proximity -self.slow_down_proximity)
        speed = (proximity - self.reverse_proximity) * slope
        return min(1.0, max(speed, -1.0))

    def calc_speed(self, proximity_sensors: list[float]):
        """
        Calculate the speed based on the proximity sensors.
        :return: speed factor
        """
        weighted_average = self.get_proximity(proximity_sensors)
        return self.calc_speed_factor_on_proximity(weighted_average)

    def lover_behaviour(self, prox: float):
        ds = prox / self.reverse_proximity
        return 1 - ds


if __name__ == '__main__':
    a = ObstacleAvoider(40, 100)
    assert(a.calc_speed_factor_on_proximity(0) == 1.0)
    assert(a.calc_speed_factor_on_proximity(40) == 1.0)
    assert(a.calc_speed_factor_on_proximity(100) == 0)


