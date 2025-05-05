class GreyArea:
    def __init__(self, speed: float):
        self.norm_speed = speed

    def grey_min_length(self) -> float:
        """how many steps the robot should be in the grey area"""
        return 10 / self.norm_speed

    def grey_distance_max(self) -> float:
        """how many steps apart the grey areas can be for it to count as one beacon"""
        return 2 * self.grey_min_length()