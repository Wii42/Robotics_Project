"""
Beacon Module

This module provides the Beacon class, which represents a beacon (waypoint) on the robot track.
Beacons are used to define the geometry of the track and the relationships between segments.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

class Beacon:
    """
    Represents a beacon (waypoint) on the track.

    Attributes
    ----------
    name : str
        String identifier of the beacon.
    x : float
        x-coordinate of the beacon.
    y : float
        y-coordinate of the beacon.
    orientation : float
        Orientation of the robot at the beacon, when driving clockwise on the track (in radians).
    next_beacon : tuple[Beacon, float] or None
        Tuple containing the next beacon and the distance to it, when approached clockwise.
    """

    def __init__(self, name: str, x: float, y: float, orientation: float, next_beacon: tuple['Beacon', float] = None):
        """
        Initialize a Beacon object.

        Parameters
        ----------
        name : str
            String identifier of the beacon.
        x : float
            x-coordinate of the beacon.
        y : float
            y-coordinate of the beacon.
        orientation : float
            Orientation of the robot at the beacon, when driving clockwise on the track (in radians).
        next_beacon : tuple[Beacon, float], optional
            Tuple containing the next beacon and the distance to it, when approached clockwise.
        """
        self.name: str = name
        self.x: float = x
        self.y: float = y
        self.orientation: float = orientation
        self.next_beacon: tuple[Beacon, float] = next_beacon

