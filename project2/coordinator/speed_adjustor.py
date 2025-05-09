from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication


class SpeedAdjustor:
    def __init__(self, client: SocketClientCommunication, optimal_distance: float):
        self.optimal_distance = optimal_distance
        self.client = client


    def calculate_speed_factor_to_reach_optimal_distance(self, robot_id: str, distance_to_next_robot: float) -> float | None:
        if distance_to_next_robot is None:
            return None
        x = distance_to_next_robot - self.optimal_distance
        m = (1 / self.optimal_distance) / 0.5
        speed_factor = m * x + 1.0
        #if distance_to_next_robot < self.optimal_distance:
        #    speed_factor = 0.1
        #else:
        #    speed_factor =  2.0

        return max(0.001, min(speed_factor, 2.0))

    def send_speed_factor(self, robot_id: str, distance_to_next_robot: float):
        speed_factor = self.calculate_speed_factor_to_reach_optimal_distance(robot_id, distance_to_next_robot)
        if speed_factor is not None:
            self.client.send_msg_to(robot_id, {"speed_factor": speed_factor})
            print(f"sending speed factor to {robot_id.split("_")[-1]}: {speed_factor}")

