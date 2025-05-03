import math
import subprocess
import sys

from unifr_api_epuck import wrapper
from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication

from beacon_detector import BeaconDetector
from beacon import Beacon
from project2.odometry import Odometry
from project2.step_counter import StepCounter
from track_follower import TrackFollower
import queue

beacons: dict[int, Beacon] = {1: Beacon("beacon1", 450, 540, math.pi),
                              2: Beacon("beacon2", 500, 60, 0),
                              }

COORDINATOR_ID: str = 'coordinator'

def main(robots: list[str], state_queue: queue.Queue = None):
    client: SocketClientCommunication = wrapper.get_client(client_id=COORDINATOR_ID, host_ip='http://127.0.0.1:8000')

    for robot in robots:
        subprocess.Popen(['python3', 'robot_controller.py', robot], shell=False, stdout=sys.stdout, stderr=sys.stderr)



    while True:
        if client.has_receive_msg():
            msg = client.receive_msg()
            state_queue.put(msg)
            #print(msg)



if __name__ == '__main__':
    main([])
