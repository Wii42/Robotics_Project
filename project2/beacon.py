class Beacon:
    def __init__(self, name: str, x: float, y: float, orientation: float, next_beacon: tuple['Beacon', float] = None):
        self.name: str = name
        self.x: float = x
        self.y: float = y
        self.orientation: float = orientation
        self.next_beacon: tuple[Beacon, float] = next_beacon

