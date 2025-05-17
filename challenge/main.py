"""
Main Entry Point for Robotics Project

This script initializes and starts the coordinator and GUI for robot track management and visualization.
It sets up the communication queue, launches the GUI in a separate thread, and starts the Coordinator
to manage robot distances and state updates.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""
import os
import queue
import sys
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import challenge.gui as gui
from challenge.coordinator import coordinator

# List of robot IP addresses to be managed by the coordinator
ROBOTS: list[str] = ['192.168.2.214', '192.168.2.210']

if __name__ == "__main__":
    # Create a queue for state updates between coordinator and GUI
    state_queue = queue.Queue()
    # Start the GUI in a separate daemon thread
    gui_thread = threading.Thread(
        target=gui.main,
        args=(state_queue, list(coordinator.BEACONS.values())),
        daemon=True
    )
    gui_thread.start()
    # Start the coordinator to manage robots and communicate with the GUI
    coordinator.Coordinator(ROBOTS, state_queue, optimal_distance=0.6).run()
