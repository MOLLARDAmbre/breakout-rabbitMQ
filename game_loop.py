import pygame
import sys
import _thread
import pika
import uuid
from pygame.locals import *
from ui import ui_manager

def main(fps):
    pygame.init()
    ui = ui_manager()
    clock = pygame.time.Clock()
    FPS = fps

    while True:  # Game loop
        rects = ui.draw_elements()
        ui.update_elements()
        pygame.display.update(rects)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            else:
                ui.forward_event(event)
        clock.tick(FPS)
    pygame.quit()
    sys.exit(0)


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
