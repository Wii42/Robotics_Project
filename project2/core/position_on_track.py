from project2.core.beacon import Beacon


class PositionOnTrack:
    """"
    Represents the position of a robot on the track.
    Specified by the distance from the last beacon, and the beacon it is coming from.
    """

    def __init__(self, distance: float, from_beacon: Beacon | None = None):
        """
        PositionOnTrack constructor.
        :param distance: Distance from the last beacon, in meters.
        :param from_beacon: Beacon the robot is coming from.
        """
        self.distance: float = distance
        self.from_beacon: Beacon = from_beacon

    def to_dict(self) -> dict[str, float | str | None]:
        """
        Convert the PositionOnTrack object to a dictionary for serialization.
        :return: Dictionary representation of the PositionOnTrack object.
        """
        return {
            "distance": self.distance,
            "from_beacon": self.from_beacon.name if self.from_beacon else None
        }

    def __repr__(self) -> str:
        return f"PositionOnTrack(distance={self.distance}, from_beacon={self.from_beacon.name if self.from_beacon else None})"


def position_from_dict(data: dict[str, float | str | None], beacon_list: list[Beacon]) -> PositionOnTrack:
    """
    Create a PositionOnTrack object from a dictionary, used in deserialization.
    :param beacon_list: List of beacons to find the from_beacon.
    :param data: Dictionary containing the data to create the object.
    :return: PositionOnTrack object.
    """
    distance = data.get("distance", 0.0)
    from_beacon_name = data.get("from_beacon", None)
    from_beacon = None
    if from_beacon_name is not None:
        for beacon in beacon_list:
            if beacon.name == from_beacon_name:
                from_beacon = beacon
                break

    return PositionOnTrack(distance, from_beacon)
