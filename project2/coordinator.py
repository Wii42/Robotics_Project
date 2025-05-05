import math
import subprocess
import sys

from unifr_api_epuck import wrapper
from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication

from beacon_detector import BeaconDetector
from beacon import Beacon
import queue

beacons: dict[int, Beacon] = {1: Beacon("beacon1", 450, 540, math.pi, 0),
                              2: Beacon("beacon2", 500, 60, 0, 0.80),
                              }

COORDINATOR_ID: str = 'coordinator'

def main(robots: list[str], state_queue: queue.Queue = None):
    client: SocketClientCommunication = wrapper.get_client(client_id=COORDINATOR_ID, host_ip='http://127.0.0.1:8000')

    for robot in robots:
        subprocess.Popen(['python3', 'robot_controller.py', robot], shell=False,
                         #stdout=sys.stdout,
                         stderr=sys.stderr)


    robot_positions_on_track: dict[str, float] = {}



    while True:
        if client.has_receive_msg():
            msg = client.receive_msg()
            robot_id = msg.get("robot_id")
            state_queue.put(msg)
            position_on_track = msg.get("position_on_track")
            if position_on_track is not None:
                robot_positions_on_track[robot_id] = position_on_track
                print(robot_positions_on_track)
            #print(msg)



if __name__ == '__main__':
    main([])
