class Beacon:
    """
    Represents a beacon on the track.
    """
    def __init__(self, name: str, x: float, y: float, orientation: float, next_beacon: tuple['Beacon', float] = None):
        """
        Beacon constructor.
        :param name: String identifier of the beacon.
        :param x: x-coordinate of the beacon.
        :param y: y-coordinate of the beacon.
        :param orientation: Orientation of the robot at the beacon, when driving clockwise on the track.
        :param next_beacon: Tuple containing the next beacon and the distance to it, when approached clockwise.
        """
        self.name: str = name
        self.x: float = x
        self.y: float = y
        self.orientation: float = orientation
        self.next_beacon: tuple[Beacon, float] = next_beacon

