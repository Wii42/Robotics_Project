import queue
import threading

import gui
import robot_controller
from project2 import coordinator

ROBOTS: list[str] = ['192.168.2.205', '192.168.2.210']

if __name__ == "__main__":
    state_queue = queue.Queue()
    gui_thread = threading.Thread(target=gui.main, args=(state_queue,robot_controller.BEACONS.values()), daemon=True).start()
    coordinator.main(ROBOTS, state_queue)
