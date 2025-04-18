import pygame
import queue
from beacon import Beacon

def main(state_queue: queue.Queue, beacons: list[Beacon]):
    # Pygame-Setup
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Track Visualisierung")
    clock = pygame.time.Clock()

    background_image = pygame.image.load("Track_test.jpg")
    background_image = pygame.transform.rotate(background_image, 90)
    background_image = pygame.transform.scale(background_image, (WIDTH*0.9, HEIGHT*0.9))

    # Hauptschleife für pygame
    running = True
    robot_position = [50, 50]  # Initiale Position
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Hintergrund zeichnen
        screen.fill(WHITE)
        screen.blit(background_image, (WIDTH*0.05, HEIGHT*0.05))

        # Beacons zeichnen
        for beacon in beacons:
            pygame.draw.circle(screen, RED, (int(beacon.x), int(beacon.y)), 10)

        # Aktualisiere Roboterposition aus der Queue
        while not state_queue.empty():
            state = state_queue.get()
            robot_position = state.get("robot_position", robot_position)

        # Roboter zeichnen
        pygame.draw.circle(screen, BLUE, (int(robot_position[0]), int(robot_position[1])), 10)

        # Anzeige aktualisieren
        pygame.display.flip()
        clock.tick(30)  # 30 FPS

    pygame.quit()