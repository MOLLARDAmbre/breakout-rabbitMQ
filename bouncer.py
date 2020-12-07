import pygame
import pika
import _thread
import uuid
from events import event_type
from rabbit_sender import send, recv

class Bouncer():
    def __init__(self, init_pos, width=60, height=10):
        self.pos = init_pos
        self.width = width
        self.height = height
        self.curr_rect = self.get_rect_from_pos()
        self.direction = 0
        _thread.start_new_thread(self.listen_for_event, ())

    def update(self):
        if self.direction <= -1:
            self.pos = [self.pos[0] - 10, self.pos[1]]
        if self.direction >= 1:
            self.pos = [self.pos[0] + 10, self.pos[1]]
        return

    def move_left(self):
        self.direction -= 1
        if self.direction < -1:
            self.direction = -1

    def move_right(self):
        self.direction += 1
        if self.direction > 1:
            self.direction = 1


    def draw(self, surface):
        rects = [self.curr_rect]
        new_rect = self.get_rect_from_pos()
        pygame.draw.rect(surface, (255,255,255), self.curr_rect)
        rects.append(new_rect)
        self.curr_rect = new_rect
        pygame.draw.rect(surface, (0,0,0), self.curr_rect)
        return rects

    def check_collisions(self, ball):
        if self.curr_rect.colliderect(ball.curr_rect):
            self.send_message_bounce()
            ball.pos[1] -= 6 # Fix better

    def send_message_bounce(self):
        send('bounce', 1)

    def listen_for_event(self):
        def callback(ch, method, properties, body):
            if int(body) == event_type.MOVE_LEFT:
                self.move_left()
            if int(body) == event_type.MOVE_RIGHT:
                self.move_right()
        return recv('event', callback)

    def get_rect_from_pos(self):
        return pygame.Rect(self.pos[0] - self.width / 2, self.pos[1] - self.height / 2, \
                           self.width, self.height)
