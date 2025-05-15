from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication


class SpeedAdjustor:
    """
    Class to adjust the speed of the robots to keep the optimal distance to the next robot.
    Calculates the speed factor to reach the optimal distance and sends it to the robot.
    """
    def __init__(self, client: SocketClientCommunication, optimal_distance: float, sensitivity_range: float = 0.25):
        """
        SpeedAdjustor constructor.
        :param client: the communication client to communicate with the robot controllers.
        :param optimal_distance: Distance the robots should keep from each other, in meters.
        :param sensitivity_range: determines how sensitive the speed factor is to the distance to the next robot.
        The speed factor at the optimal distance is 1.0, and the speed at optimal distance - sensitivity_range 0.
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
        :param distance_to_next_robot: the distance to the next robot in meters.
        :return: the speed factor to reach the optimal distance, or None if the distance to the next robot is None.
        """
        if distance_to_next_robot is None:
            return None
        x = distance_to_next_robot - self.optimal_distance
        m = (1 / self.optimal_distance) / self.sensitivity_range
        speed_factor = m * x + 1.0
        bounded_speed_factor = max(-0.5, min(speed_factor, 2.0))
        if bounded_speed_factor == 0.0:
            bounded_speed_factor = 0.01 # needed as else the robot cant receive the message

        return bounded_speed_factor


    def send_speed_factor(self, robot_id: str, distance_to_next_robot: float):
        """
        Send the speed factor to the robot.
        :param robot_id: the id of the robot, where the speed factor should be sent to.
        :param distance_to_next_robot: the distance to the next robot in meters.
        :return: None
        """
        speed_factor = self.calculate_speed_factor_to_reach_optimal_distance(distance_to_next_robot)
        if speed_factor is not None:
            self.client.send_msg_to(robot_id, {"speed_factor": speed_factor})
            print(f"sending speed factor to {robot_id.split("_")[-1]}: {speed_factor}")

