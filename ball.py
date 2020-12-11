import pygame
import sys
import _thread
import uuid
import pika
from random import randint
from rabbit_sender import send, recv

class Ball():
    """
    A class that describes the ball
    """
    def __init__(self, init_pos, size=6):
        self.speed = [randint(1, 4) + 0.2, -randint(1, 4) - 0.2]
        self.pos = init_pos
        self.size = size
        self.curr_rect = self.get_rect_from_pos()
        self.just_bounced = 5 # Prevents back and forth
        _thread.start_new_thread(self.listen_for_bounce, ())

    def update(self):
        self.just_bounced -= 1
        self.pos = [self.pos[0] + self.speed[0], self.pos[1] + self.speed[1]]
        return

    def draw(self, surface):
        rects = [self.curr_rect]
        new_rect = self.get_rect_from_pos()
        pygame.draw.rect(surface, (255,255,255), self.curr_rect)
        rects.append(new_rect)
        self.curr_rect = new_rect
        pygame.draw.rect(surface, (0,0,0), self.curr_rect)
        return rects

    def check_bounds(self, limit):
        """
        Checks the ball is within the given bounds (x-axis only)
        """
        if self.pos[0] < 0:
            self.pos[0] += limit
        if self.pos[0] > limit:
            self.pos[0] -= limit
        return

    def check_ceiling(self):
        """
        Makes sure the ball bounces on the ceiling
        """
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.speed[1] = abs(self.speed[1])
        return

    def check_death(self, limit):
        """
        Triggers game over on ball low enough
        """
        if self.pos[1] > limit:
            self.send_message_game_over()

    def send_message_game_over(self):
        send('game_over', "blocks")

    def bounce(self, vertical):
        """
        Bounces the ball.
        vertical represents where to bounce from,
        """
        if self.just_bounced > 0:
            return
        else:
            self.just_bounced = 5
        if vertical:
            self.speed = [self.speed[0], -self.speed[1]]
        else:
            self.speed = [-self.speed[0], self.speed[1]]

    def listen_for_bounce(self):
        """
        Listens for a bounce message
        """
        def callback(ch, method, properties, body):
            if int(body) == 0:
                self.bounce(False)
            else:
                self.bounce(True)
        recv('bounce', callback)

    def get_rect_from_pos(self):
        return pygame.Rect(self.pos[0] - self.size / 2, self.pos[1] - self.size / 2, \
                           self.size, self.size)
