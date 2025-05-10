import math
import subprocess
import sys
from time import sleep

from unifr_api_epuck import wrapper
from unifr_api_epuck.communication.socket_client_communication import SocketClientCommunication

from project2.core.beacon import Beacon
import queue

from project2.coordinator.distance_calculator import compute_distance
from project2.core.position_on_track import PositionOnTrack, position_from_dict
from project2.coordinator.speed_adjustor import SpeedAdjustor

BEACONS: dict[int, Beacon] = {1: Beacon("beacon1", 450, 540, math.pi),
                              2: Beacon("beacon2", 500, 60, 0),
                              }

BEACONS[1].next_beacon = (BEACONS[2], 0.74)
BEACONS[2].next_beacon = (BEACONS[1], 0.65)

COORDINATOR_ID: str = 'coordinator'


def main(robots: list[str], state_queue: queue.Queue = None):
    client: SocketClientCommunication = wrapper.get_client(client_id=COORDINATOR_ID, host_ip='http://127.0.0.1:8000')

    speed_adjustor: SpeedAdjustor = SpeedAdjustor(client, 0.3)

    for robot in robots:
        subprocess.Popen(['python3', 'robot/robot_controller.py', robot], shell=False,
                         # stdout=sys.stdout,
                         stderr=sys.stdout)

    robot_positions_on_track: dict[str, PositionOnTrack] = {}

    #csv_file = open('distances.csv', mode='w', newline='')
    #csv_writer = csv.writer(csv_file)
    #csv_writer.writerow(['rear', 'front', 'distance'])

    while True:
        if client.has_receive_msg():
            msg = client.receive_msg()
            state_queue.put(msg)
            robot_id = msg.get("robot_id")
            state_queue.put(msg)
            position_on_track = msg.get("position_on_track")
            if position_on_track is not None:
                robot_positions_on_track[robot_id] = position_from_dict(position_on_track, list(BEACONS.values()))
                print(robot_positions_on_track)
                calculate_all_robot_distances(robot_positions_on_track, speed_adjustor)
            # print(msg)


def calculate_all_robot_distances(robot_positions_on_track, speed_adjustor: SpeedAdjustor):
    robots = list(robot_positions_on_track.keys())
    robot_pairs = [(x, y) for x in robots for y in robots if x != y]
    for rear, front in robot_pairs:
        dist = compute_distance(robot_positions_on_track[rear], robot_positions_on_track[front])
        print(f"Distance between {rear} and {front}: {dist}")
        speed_adjustor.send_speed_factor(rear, dist)
        # csv_writer.writerow([rear, front, dist])
        # csv_file.flush()




if __name__ == '__main__':
    main([])
