from project2.core.position_on_track import PositionOnTrack


def compute_distance(rear_robot: PositionOnTrack, front_robot: PositionOnTrack) -> float | None:
    """
    Compute the distance between two robots.
    :param rear_robot: PositionOnTrack object of the rear robot.
    :param front_robot: PositionOnTrack object of the front robot.
    :return: Distance in meters.
    """
    if rear_robot.from_beacon is None or front_robot.from_beacon is None:
        return None

    # Check if the beacons are the same

    if rear_robot.from_beacon == front_robot.from_beacon:
        # check if the rear robot is behind the front robot on the same track part
        segment_length = front_robot.distance - rear_robot.distance
        if segment_length >= 0:
            return segment_length

    beacon = rear_robot.from_beacon

    distance_of_robots: float = (beacon.next_beacon[1] - rear_robot.distance) if beacon.next_beacon is not None else 0
    if distance_of_robots < 0:
        distance_of_robots = 0
    while beacon.next_beacon is not None:

        next_beacon, segment_length = beacon.next_beacon
        if next_beacon == front_robot.from_beacon:
            distance_of_robots += front_robot.distance
            return distance_of_robots
        distance_of_robots += segment_length
        beacon = next_beacon

    return None


class DistanceCalculator:

    def __init__(self):
        pass
