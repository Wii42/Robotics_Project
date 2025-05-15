import queue
import threading

import gui
from project2.coordinator import coordinator

ROBOTS: list[str] = ['192.168.2.216', '192.168.2.208']

if __name__ == "__main__":
    state_queue = queue.Queue()
    gui_thread = threading.Thread(target=gui.main, args=(state_queue, coordinator.BEACONS.values()), daemon=True).start()
    coordinator.Coordinator(ROBOTS, state_queue, optimal_distance=0.6).run()
