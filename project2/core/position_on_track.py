"""
Position On Track Module

This module provides the PositionOnTrack class, which represents the position of a robot
on the track, specified by the distance from the last beacon and the beacon it is coming from.
It also provides a utility function to convert between dictionary representations and PositionOnTrack objects.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

from project2.core.beacon import Beacon


class PositionOnTrack:
    """
    Represents the position of a robot on the track.

    Attributes
    ----------
    distance : float
        Distance from the last beacon, in meters.
    from_beacon : Beacon or None
        The beacon the robot is coming from.
    """

    def __init__(self, distance: float, from_beacon: Beacon | None = None):
        """
        PositionOnTrack constructor.

        Parameters
        ----------
        distance : float
            Distance from the last beacon, in meters.
        from_beacon : Beacon, optional
            The beacon the robot is coming from.
        """
        self.distance: float = distance
        self.from_beacon: Beacon = from_beacon

    def to_dict(self) -> dict[str, float | str | None]:
        """
        Convert the PositionOnTrack object to a dictionary for serialization.

        Returns
        -------
        dict[str, float | str | None]
            Dictionary representation of the PositionOnTrack object.
        """
        return {
            "distance": self.distance,
            "from_beacon": self.from_beacon.name if self.from_beacon else None
        }

    def __repr__(self) -> str:
        """
        Return a string representation of the PositionOnTrack object.

        Returns
        -------
        str
            String representation of the object.
        """
        return f"PositionOnTrack(distance={self.distance}, from_beacon={self.from_beacon.name if self.from_beacon else None})"


def position_from_dict(data: dict[str, float | str | None], beacon_list: list[Beacon]) -> PositionOnTrack:
    """
    Create a PositionOnTrack object from a dictionary, used in deserialization.

    Parameters
    ----------
    data : dict[str, float | str | None]
        Dictionary containing the data to create the object.
    beacon_list : list[Beacon]
        List of beacons to find the from_beacon.

    Returns
    -------
    PositionOnTrack
        The created PositionOnTrack object.
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
