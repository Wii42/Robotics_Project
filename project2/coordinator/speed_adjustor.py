"""
Speed Adjustor Module

This module provides the SpeedAdjustor class, which is responsible for calculating and sending
speed adjustment factors to robots in order to maintain an optimal distance between them on the track.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication


class SpeedAdjustor:
    """
    Class to adjust the speed of the robots to keep the optimal distance to the next robot.
    Calculates the speed factor to reach the optimal distance and sends it to the robot.

    Attributes
    ----------
    client : SocketClientCommunication
        The communication client to communicate with the robot controllers.
    optimal_distance : float
        Distance (in meters) the robots should keep from each other.
    sensitivity_range : float
        Determines how sensitive the speed factor is to the distance to the next robot.
        The speed factor at the optimal distance is 1.0, and the speed at optimal distance - sensitivity_range is 0.
    """

    def __init__(self, client: SocketClientCommunication, optimal_distance: float, sensitivity_range: float = 0.25):
        """
        SpeedAdjustor constructor.

        Parameters
        ----------
        client : SocketClientCommunication
            The communication client to communicate with the robot controllers.
        optimal_distance : float
            Distance the robots should keep from each other, in meters.
        sensitivity_range : float, optional
            Determines how sensitive the speed factor is to the distance to the next robot.
            The speed factor at the optimal distance is 1.0, and the speed at optimal distance - sensitivity_range is 0.
        """
        self.optimal_distance = optimal_distance
        self.client = client
        self.sensitivity_range = sensitivity_range

    def calculate_speed_factor_to_reach_optimal_distance(self, distance_to_next_robot: float) -> float | None:
        """
        Calculate the speed factor to reach the optimal distance.

        The speed factor is calculated as follows:
        The factor is linear, with a slope of 1 / optimal_distance / sensitivity_range.
        The speed factor is bounded between -0.5 and 2.0.
        This means that the speed factor is 1.0 at the optimal distance, and the speed factor is 0.0 at the optimal distance - sensitivity_range.

        Parameters
        ----------
        distance_to_next_robot : float
            The distance to the next robot in meters.

        Returns
        -------
        float or None
            The speed factor to reach the optimal distance, or None if the distance to the next robot is None.
        """
        if distance_to_next_robot is None:
            return None
        x = distance_to_next_robot - self.optimal_distance
        m = (1 / self.optimal_distance) / self.sensitivity_range
        speed_factor = m * x + 1.0
        bounded_speed_factor = max(-0.5, min(speed_factor, 2.0))
        if bounded_speed_factor == 0.0:
            bounded_speed_factor = 0.01  # needed as else the robot can't receive the message

        return bounded_speed_factor

    def send_speed_factor(self, robot_id: str, distance_to_next_robot: float):
        """
        Send the speed factor to the robot.

        Parameters
        ----------
        robot_id : str
            The id of the robot, where the speed factor should be sent to.
        distance_to_next_robot : float
            The distance to the next robot in meters.

        Returns
        -------
        None
        """
        speed_factor = self.calculate_speed_factor_to_reach_optimal_distance(distance_to_next_robot)
        if speed_factor is not None:
            self.client.send_msg_to(robot_id, {"speed_factor": speed_factor})
            print(f"sending speed factor to {robot_id.split('_')[-1]}: {speed_factor}")

