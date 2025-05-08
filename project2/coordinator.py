import math
import subprocess
import sys

from unifr_api_epuck import wrapper
from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication

from beacon_detector import BeaconDetector
from beacon import Beacon
import queue

from project2.distance_calculator import compute_distance
from project2.position_on_track import PositionOnTrack, position_from_dict

BEACONS: dict[int, Beacon] = {1: Beacon("beacon1", 450, 540, math.pi),
                              2: Beacon("beacon2", 500, 60, 0),
                              }

BEACONS[1].next_beacon = (BEACONS[2], 0.14+0.18+0.15)
BEACONS[2].next_beacon = (BEACONS[1], 0.11+0.18+0.14)

COORDINATOR_ID: str = 'coordinator'


def main(robots: list[str], state_queue: queue.Queue = None):
    client: SocketClientCommunication = wrapper.get_client(client_id=COORDINATOR_ID, host_ip='http://127.0.0.1:8000')

    for robot in robots:
        subprocess.Popen(['python3', 'robot_controller.py', robot], shell=False,
                         # stdout=sys.stdout,
                         stderr=sys.stderr)

    robot_positions_on_track: dict[str, PositionOnTrack] = {}



    while True:
        if client.has_receive_msg():
            msg = client.receive_msg()
            robot_id = msg.get("robot_id")
            state_queue.put(msg)
            position_on_track = msg.get("position_on_track")
            if position_on_track is not None:
                robot_positions_on_track[robot_id] = position_from_dict(position_on_track, [*BEACONS.values()])
                print(robot_positions_on_track)
                robots = list(robot_positions_on_track.keys())
                robot_pairs = [(x, y) for x in robots for y in robots if x != y]
                for rear, front in robot_pairs:
                    dist = compute_distance(robot_positions_on_track[rear], robot_positions_on_track[front])
                    print(f"Distance between {rear} and {front}: {dist}")
            # print(msg)





if __name__ == '__main__':
    main([])
