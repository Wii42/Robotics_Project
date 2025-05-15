class GreyArea:
    def __init__(self, speed: float):
        """
        GreyArea constructor.
        :param speed:
        The speed of the robot in rad/s. This is used to calculate the time it takes to cross the grey area.
        """
        self.norm_speed = speed

    def grey_min_length(self) -> float:
        """How many steps the robot should be in the grey area"""
        return 20 / self.norm_speed

    def grey_distance_max(self) -> float:
        """How many steps apart the grey areas can be for it to count as one beacon"""
        return 2 * self.grey_min_length()