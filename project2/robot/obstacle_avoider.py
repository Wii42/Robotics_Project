"""
obstacle_avoider.py

Implements obstacle avoidance logic for the ePuck robot using proximity sensors.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

class ObstacleAvoider:
    """
    The ObstacleAvoider class provides methods to detect obstacles and
    adjust the robot's speed based on proximity sensor readings.
    """
    def __init__(self, slow_dow_proximity: float, reverse_proximity: float):
        """
        Initialize the ObstacleAvoider.

        Args:
            slow_dow_proximity (float): If the proximity is greater than this value, the robot should slow down.
            reverse_proximity (float): If the proximity is greater than this value, the robot should reverse.
        """
        self.slow_down_proximity = slow_dow_proximity
        self.reverse_proximity = reverse_proximity

    def get_proximity(self, proximity_sensors: list[float]) -> float:
        """
        Calculate a weighted average proximity value from the robot's front sensors.

        Args:
            proximity_sensors (list[float]): List of proximity sensor values.

        Returns:
            float: Weighted average proximity value.
        """
        left_front_diagonal = proximity_sensors[6]
        left_front = proximity_sensors[7]
        right_front = proximity_sensors[0]
        right_front_diagonal = proximity_sensors[1]

        # Weighted sum: diagonals are weighted half, fronts are weighted full
        return (left_front_diagonal * 0.5 + right_front_diagonal * 0.5 + left_front + right_front) / 3

    def is_obstacle(self, proximity_sensors: list[float]) -> bool:
        """
        Determine if an obstacle is detected based on the weighted average proximity.

        Args:
            proximity_sensors (list[float]): List of proximity sensor values.

        Returns:
            bool: True if an obstacle is detected, False otherwise.
        """
        weighted_average = self.get_proximity(proximity_sensors)
        return weighted_average > self.slow_down_proximity

    def calc_speed_factor_on_proximity(self, proximity: float) -> float:
        """
        Calculate the speed factor based on the proximity value.
        The speed factor is 1.0 at or below slow_down_proximity and decreases linearly
        to 0.0 at reverse_proximity.

        Args:
            proximity (float): Weighted average proximity value.

        Returns:
            float: Speed factor between -1.0 and 1.0.
        """
        assert self.slow_down_proximity < self.reverse_proximity, "slow_down_proximity must be less than reverse_proximity"

        if proximity <= self.slow_down_proximity:
            return 1.0  # Full speed

        slope = -1.0 / (self.reverse_proximity - self.slow_down_proximity)
        speed = (proximity - self.reverse_proximity) * slope
        return min(1.0, max(speed, -1.0))

    def calc_speed(self, proximity_sensors: list[float]) -> float:
        """
        Calculate the speed factor based on the proximity sensors.

        Args:
            proximity_sensors (list[float]): List of proximity sensor values.

        Returns:
            float: Speed factor between -1.0 and 1.0.
        """
        weighted_average = self.get_proximity(proximity_sensors)
        return self.calc_speed_factor_on_proximity(weighted_average)

    def lover_behaviour(self, prox: float) -> float:
        """
        Alternative speed calculation: linearly decreases speed as proximity increases.

        Args:
            prox (float): Proximity value.

        Returns:
            float: Speed factor.
        """
        ds = prox / self.reverse_proximity
        return 1 - ds


if __name__ == '__main__':
    # Example usage and simple tests
    a = ObstacleAvoider(40, 100)
    assert(a.calc_speed_factor_on_proximity(0) == 1.0)
    assert(a.calc_speed_factor_on_proximity(40) == 1.0)
    assert(a.calc_speed_factor_on_proximity(100) == 0)


