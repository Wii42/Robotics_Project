import queue
import threading

import gui
import controller

if __name__ == "__main__":
    state_queue = queue.Queue()
    gui_thread = threading.Thread(target=gui.main, args=(state_queue,controller.beacons.values()), daemon=True).start()
    controller.main(state_queue)
