import pygame
import sys
import _thread
import pika
import uuid
from pygame.locals import *
from ui import ui_manager
from events import event_type

def main(fps):
    pygame.init()
    ui = ui_manager()
    clock = pygame.time.Clock()
    FPS = fps

    while True:  # Game loop
        rects = ui.draw_elements()
        ui.update_elements()
        pygame.display.update(rects)
        clock.tick(FPS)
        for event in pygame.event.get():
            forward_event(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
    pygame.quit()
    sys.exit(0)


def forward_event(event):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='event',
                             exchange_type='fanout')
    message = -1 # Default
    if event.type == QUIT:
        message = event_type.QUIT
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            message = event_type.MOVE_LEFT
        if event.key == pygame.K_RIGHT:
            message = event_type.MOVE_RIGHT
    message = str(int(message))
    channel.basic_publish(exchange='event',
                          routing_key='',
                          body=message)


def listen_for_game_over():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='game_over', exchange_type='fanout')
    _uuid=str(uuid.uuid4())
    result = channel.queue_declare(exclusive=True, queue=_uuid)
    queue_name = result.method.queue
    channel.queue_bind(exchange='game_over', queue=queue_name)

    def callback(ch, method, properties, body):
        pygame.event.post(pygame.event.Event(QUIT))

    channel.basic_consume(queue_name, callback,
                          auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    _thread.start_new_thread(listen_for_game_over, ())
    main(60)
