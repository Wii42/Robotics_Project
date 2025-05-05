class Beacon:
    def __init__(self, name: str, x: float, y: float, orientation: float, position_on_track: float):
        self.name: str = name
        self.x: float = x
        self.y: float = y
        self.orientation: float = orientation
        self.position_on_track = position_on_track