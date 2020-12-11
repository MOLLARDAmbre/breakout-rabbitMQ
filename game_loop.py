import pygame
import sys
import _thread
import pika
import uuid
from pygame.locals import *
from ui import ui_manager
from events import event_type
from rabbit_sender import send, recv

def main(fps):
    pygame.init()
    ui = ui_manager()
    clock = pygame.time.Clock()
    FPS = fps

    while True:  # Game loop
        rects = ui.draw_elements()  # Draws elements
        ui.update_elements()  # Update elements
        pygame.display.update(rects)  # pygame command to actually update the display
        clock.tick(FPS)  # Limits the fps rate to 60
        for event in pygame.event.get():  # Get the pygame events and forward them
            forward_event(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
    pygame.quit()
    sys.exit(0)


def forward_event(event):
    """
    Sends rabbitmq messages to forward pygame key events
    """
    message = -1 # Default
    if event.type == QUIT:
        message = event_type.QUIT
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            message = event_type.MOVE_LEFT
        if event.key == pygame.K_RIGHT:
            message = event_type.MOVE_RIGHT
    message = int(message)
    send('event', message)


def listen_for_game_over():
    """
    Checks for messages signaling a game over
    """
    def callback(ch, method, properties, body):
        pygame.event.post(pygame.event.Event(QUIT))
    recv('game_over', callback)


if __name__ == "__main__":
    _thread.start_new_thread(listen_for_game_over, ())
    main(60)
