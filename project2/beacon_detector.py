class BeaconDetector:

    def __init__(self, robot_norm_speed: float, grey_min_length: float, grey_distance_max: float, grey_min_value: int,
                 grey_max_value: int):
        self.grey_length: int = 0
        self.grey_distance: int = 0
        self.grey_area_count: int = 0

        self.robot_norm_speed: float = robot_norm_speed
        self.grey_min_length: float = grey_min_length
        self.grey_distance_max: float = grey_distance_max
        self.grey_min_value: int = grey_min_value
        self.grey_max_value: int = grey_max_value

    def reset(self):
        self.grey_length = 0
        self.grey_distance = 0
        self.grey_area_count = 0

    def receive_ground(self, gs: list[int]):
        # print(gs)
        if any([self.in_grey(x) for x in gs]):
            # print("grey")
            self.grey_length += 1
            self.grey_distance = 0
        else:
            if self.grey_length > 0:
                if self.grey_length >= self.grey_min_length:
                    print(f"grey length: {self.grey_length}")
                    self.grey_area_count += 1
                self.grey_length = 0
            if self.grey_area_count > 0:
                self.grey_distance += 1

        if self.grey_distance >= self.grey_distance_max:
            print(f"grey areas: {self.grey_area_count}")
            self.reset()

    def in_grey(self, value: int) -> bool:
        return self.grey_min_value <= value <= self.grey_max_value
