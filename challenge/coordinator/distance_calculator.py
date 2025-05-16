"""
Distance Calculator Module

This module provides functions to compute the distance between two robots on a segmented track.
It considers both robots on the same segment and robots on different segments, traversing the
track's beacon structure to calculate the correct distance.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

from challenge.core.position_on_track import PositionOnTrack


def compute_distance(rear_robot: PositionOnTrack, front_robot: PositionOnTrack) -> float | None:
    """
    Compute the distance between two robots on the track.

    If both robots are on the same segment (beacon), the function returns the direct distance
    between them if the rear robot is actually behind the front robot. If the robots are on
    different segments, the function delegates to _distance_across_segments to traverse the
    track and sum up the segment lengths.

    Parameters
    ----------
    rear_robot : PositionOnTrack
        PositionOnTrack object of the rear robot.
    front_robot : PositionOnTrack
        PositionOnTrack object of the front robot.

    Returns
    -------
    float or None
        Distance in meters between the two robots, or None if the distance cannot be computed.
    """
    if rear_robot.from_beacon is None or front_robot.from_beacon is None:
        return None

    # If both robots are on the same beacon/segment
    if rear_robot.from_beacon == front_robot.from_beacon:
        # Only return the distance if the rear robot is actually behind the front robot
        segment_length = front_robot.distance - rear_robot.distance
        if segment_length >= 0:
            return segment_length

    # Otherwise, compute the distance across segments
    return _distance_across_segments(rear_robot, front_robot)


def _distance_across_segments(rear_robot: PositionOnTrack, front_robot: PositionOnTrack) -> float | None:
    """
    Compute the distance between two robots that are on different segments of the track.

    This function traverses the track from the rear robot's segment, following the beacon links,
    and accumulates the segment lengths until it reaches the segment of the front robot.

    Parameters
    ----------
    rear_robot : PositionOnTrack
        PositionOnTrack object of the rear robot.
    front_robot : PositionOnTrack
        PositionOnTrack object of the front robot.

    Returns
    -------
    float or None
        Distance in meters between the two robots, or None if the distance cannot be computed.
    """
    beacon = rear_robot.from_beacon
    # Start with the remaining distance on the current segment
    distance_of_robots: float = (beacon.next_beacon[1] - rear_robot.distance) if beacon.next_beacon is not None else 0
    if distance_of_robots < 0:
        distance_of_robots = 0

    # Traverse the track segments until the front robot's segment is found
    while beacon.next_beacon is not None:
        next_beacon, segment_length = beacon.next_beacon
        if next_beacon == front_robot.from_beacon:
            distance_of_robots += front_robot.distance
            return distance_of_robots
        distance_of_robots += segment_length
        beacon = next_beacon
    return None
