"""
Coordinator Module

This module provides the Coordinator class, which manages a group of robots on a track,
ensuring they maintain optimal distances from each other by communicating with their controllers
and adjusting their speeds as necessary. The Coordinator also interfaces with a GUI via a queue.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

import math
import subprocess
import sys

from unifr_api_epuck import wrapper
from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication

from challenge.core.beacon import Beacon
import queue

from challenge.coordinator.distance_calculator import compute_distance
from challenge.core.position_on_track import PositionOnTrack, position_from_dict
from challenge.coordinator.speed_adjustor import SpeedAdjustor

# Define the beacons on the track and their relationships
BEACONS: dict[int, Beacon] = {
    1: Beacon("beacon1", 360, 540, math.pi),
    2: Beacon("beacon2", 510, 50, 0),
}
BEACONS[1].next_beacon = (BEACONS[2], 0.74)
BEACONS[2].next_beacon = (BEACONS[1], 0.65)

COORDINATOR_ID: str = 'coordinator'


class Coordinator:
    """
    Coordinates a group of robots, manages their communication, and ensures they maintain
    optimal distances on the track.

    Attributes
    ----------
    robots : list[str]
        List of the IP addresses of the robots to be coordinated.

    state_queue : queue.Queue
        Queue to send information to an attached GUI across threads.

    optimal_distance : float
        Distance (in meters) the robots should keep from each other.

    client : SocketClientCommunication | None
        Communication client for interacting with robot controllers.

    speed_adjustor : SpeedAdjustor | None
        Determines and sends speed adjustment factors to robots to maintain optimal distance.

    robot_positions_on_track : dict[str, PositionOnTrack]
        Stores the positions of the robots on the track. Keys are robot IDs, values are PositionOnTrack objects.
    """

    def __init__(self, robots: list[str], state_queue: queue.Queue = None, optimal_distance: float = 0.6):
        """
        Coordinator constructor.

        Parameters
        ----------
        robots : list[str]
            List of the IP addresses of the robots to be coordinated.
        state_queue : queue.Queue, optional
            Queue to send information to an attached GUI across threads.
        optimal_distance : float, optional
            Distance (in meters) the robots should keep from each other (default is 0.6).
        """
        self.robots: list[str] = robots
        self.state_queue: queue.Queue = state_queue
        self.client: SocketClientCommunication | None = None
        self.speed_adjustor: SpeedAdjustor | None = None  # Will be initialized after client
        self.robot_positions_on_track: dict[str, PositionOnTrack] = {}
        self.optimal_distance: float = optimal_distance

    def init_client(self):
        """
        Initializes the client for communication with robot controllers.
        """
        self.client = wrapper.get_client(client_id=COORDINATOR_ID, host_ip='http://127.0.0.1:8000')

    def init_speed_adjustor(self):
        """
        Initializes the speed adjustor to determine the speed factor for each robot.
        Must be called after init_client().
        """
        self.speed_adjustor: SpeedAdjustor = SpeedAdjustor(self.client, self.optimal_distance)

    def run(self):
        """
        Main loop of the coordinator. Initializes the client and speed adjustor, starts the robots,
        and continuously handles incoming messages from the robots, updating their positions and
        calculating distances.
        """
        self.init_client()
        self.init_speed_adjustor()
        self.start_robots()

        while True:
            self.handle_incoming_message()

    def handle_incoming_message(self):
        """
        Handles incoming messages from the robots. Updates their positions, calculates distances,
        and sends the appropriate speed factor to the robots to maintain the optimal distance.
        Forwards all messages to the GUI via the state_queue.
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
        """
        for robot in self.robots:
            subprocess.Popen(
                ['python3', 'robot/robot_controller.py', robot],
                shell=False,
                stdout=sys.stdout,
                stderr=sys.stdout
            )

    def calculate_all_robot_distances(self):
        """
        Calculates the distances between all robots and sends the appropriate speed factor to each robot.
        """
        robots = list(self.robot_positions_on_track.keys())
        robot_pairs = [(x, y) for x in robots for y in robots if x != y]
        for rear, front in robot_pairs:
            dist = compute_distance(self.robot_positions_on_track[rear], self.robot_positions_on_track[front])
            print(f"Distance between {rear} and {front}: {dist}")
            self.speed_adjustor.send_speed_factor(rear, dist)


if __name__ == '__main__':
    Coordinator([]).run()
