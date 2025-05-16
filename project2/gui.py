"""
Track Visualization GUI

This script provides a graphical user interface (GUI) for visualizing the positions of robots and beacons on a track.
It uses pygame to render the track, beacons, and robots, and updates robot positions in real time based on messages
received via a queue from the coordinator.

Authors:
    @Lukas Künzi
    @Thirith Yang

Date:
    18 May 2025
"""

import pygame
import queue

from project2.core.beacon import Beacon
from project2.core.position_on_track import position_from_dict


def main(state_queue: queue.Queue, beacons: list[Beacon]):
    """
    Main function to run the track visualization GUI.

    Parameters
    ----------
    state_queue : queue.Queue
        Queue from which robot position updates are received.
    beacons : list[Beacon]
        List of Beacon objects representing the track layout.
    """
    # Pygame-Setup
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    DARK_GREEN = (0, 100, 0)

    ROBOT_COLORS = [BLUE, GREEN, DARK_GREEN]

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Track Visualisierung")
    clock = pygame.time.Clock()

    # Load and transform the background image of the track
    background_image = pygame.image.load("Track_test.jpg")
    background_image = pygame.transform.rotate(background_image, 90)
    background_image = pygame.transform.scale(background_image, (WIDTH * 0.9, HEIGHT * 0.9))

    # Font for robot IDs
    font = pygame.font.SysFont(None, 64)

    # Main loop
    running = True
    robot_position: dict[str, list[int]] = {}  # Stores the current positions of robots

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw background
        screen.fill(WHITE)
        screen.blit(background_image, (WIDTH * 0.05, HEIGHT * 0.05))

        # Draw beacons as red circles
        for beacon in beacons:
            pygame.draw.circle(screen, RED, (int(beacon.x), int(beacon.y)), 10)

        # Update robot positions from the queue
        while not state_queue.empty():
            state = state_queue.get()
            robot_id = state.get("robot_id")
            position_on_track = state.get("position_on_track")
            if position_on_track is not None:
                robot_positions_on_track = position_from_dict(position_on_track, beacons)
                if robot_positions_on_track.from_beacon is not None:
                    position = state.get("robot_position", robot_position)
                    robot_position[robot_id] = position

        # Draw robots and their IDs
        for i, robot_id in enumerate(robot_position):
            robot = robot_position[robot_id]
            x, y = int(robot[0]), int(robot[1])
            pygame.draw.circle(screen, ROBOT_COLORS[i], (x, y), 50)

            # Render the robot ID text and center it on the robot
            text_surface = font.render(str(robot_id.split('_')[-1]), True, WHITE)
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(30)  # 30 FPS

    pygame.quit()
