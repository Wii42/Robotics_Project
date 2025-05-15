import math
import subprocess
import sys

from unifr_api_epuck import wrapper
from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication

from project2.core.beacon import Beacon
import queue

from project2.coordinator.distance_calculator import compute_distance
from project2.core.position_on_track import PositionOnTrack, position_from_dict
from project2.coordinator.speed_adjustor import SpeedAdjustor

BEACONS: dict[int, Beacon] = {1: Beacon("beacon1", 360, 540, math.pi),
                              2: Beacon("beacon2", 510, 50, 0),
                              }

BEACONS[1].next_beacon = (BEACONS[2], 0.74)
BEACONS[2].next_beacon = (BEACONS[1], 0.65)

COORDINATOR_ID: str = 'coordinator'


class Coordinator:
    """
    Coordinates a group of robots and manages their communication and positioning.

    Attributes
    ----------
    robots : list[str]
        List of the IP addresses of the robots which should be used.

    state_queue : queue.Queue
        Queue to send information to an attached GUI across threads.

    optimal_distance : float
        Distance the robots should keep from each other, in meters.

    client : SocketClientCommunication | None
        Communication client to communicate with the robo controllers. Set up during runtime if required.

    speed_adjustor : SpeedAdjustor | None
        Determines by what factor a robot has to adjust its speed to keep the optimal distance
        to the next robot, and sends it to the robot.

    robot_positions_on_track : dict[str, PositionOnTrack]
        Storing the positions of the robots on the track. The keys are the robot IDs, and the
        values are PositionOnTrack objects.
    """

    def __init__(self, robots: list[str], state_queue: queue.Queue = None, optimal_distance: float = 0.6):
        """
        Coordinator constructor.
        :param robots: List of the ip addresses of the robots which should be used.
        :param state_queue: Queue to send information to an attached gui across threads.
        :param optimal_distance: Distance the robots should keep from each other, in meters
        """
        self.robots: list[str] = robots
        self.state_queue: queue.Queue = state_queue
        self.client: SocketClientCommunication | None = None
        self.speed_adjustor: SpeedAdjustor | None = None  # dependent on client
        self.robot_positions_on_track: dict[str, PositionOnTrack] = {}
        self.optimal_distance: float = optimal_distance

    def init_client(self):
        """
        Initializes the client to communicate with the robot controllers.
        :return: None
        """
        self.client = wrapper.get_client(client_id=COORDINATOR_ID, host_ip='http://127.0.0.1:8000')

    def init_speed_adjustor(self):
        """
        Initializes the speed adjustor to determine the speed factor for each robot. init_client() has to be called before.
        :return: None
        """
        self.speed_adjustor: SpeedAdjustor = SpeedAdjustor(self.client, self.optimal_distance)

    def run(self):
        """
        Main loop of the coordinator. Initializes the client and speed adjustor, starts the robots,
        and handles incoming messages from the robots, updating their positions and calculating distances.
        :return: None
        """
        self.init_client()
        self.init_speed_adjustor()
        self.start_robots()

        while True:
            self.handle_incoming_message()

    def handle_incoming_message(self):
        """
        Handles incoming messages from the robots. Updates their positions and calculates distances,
        and sends the appropriate speed factor tho the robots so the keep the optimal distance.
        Forwards all messages to the GUI.
        :return: None
        """
        if self.client.has_receive_msg():
            msg = self.client.receive_msg()
            self.state_queue.put(msg)
            robot_id = msg.get("robot_id")
            position_on_track = msg.get("position_on_track")
            if position_on_track is not None:
                self.robot_positions_on_track[robot_id] = position_from_dict(position_on_track, list(BEACONS.values()))
                self.calculate_all_robot_distances()

    def start_robots(self):
        """
        Starts the robot controllers in separate processes.
        :return: None
        """
        for robot in self.robots:
            subprocess.Popen(['python3', 'robot/robot_controller.py', robot], shell=False,
                             stdout=sys.stdout,
                             stderr=sys.stdout)

    def calculate_all_robot_distances(self):
        """
        Calculates the distances between all robots and sends the appropriate speed factor to each robot.
        :return: None
        """
        robots = list(self.robot_positions_on_track.keys())
        robot_pairs = [(x, y) for x in robots for y in robots if x != y]
        for rear, front in robot_pairs:
            dist = compute_distance(self.robot_positions_on_track[rear], self.robot_positions_on_track[front])
            print(f"Distance between {rear} and {front}: {dist}")
            self.speed_adjustor.send_speed_factor(rear, dist)


if __name__ == '__main__':
    Coordinator([]).run()
