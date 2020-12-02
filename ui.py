import pygame
from block_list import BlockList, Block
from bouncer import Bouncer
from ball import Ball

class ui_manager():
    def __init__(self, width=25, width_mul=20, height=15, height_mul=20):
        WHITE = (255, 255, 255)
        self.width = width * width_mul
        self.height = height * height_mul
        self.surface = pygame.display.set_mode((self.width, self.height))
        self.surface.fill(WHITE)
        pygame.display.update()
        self.blocks = BlockList(width, width_mul, height, height_mul)
        self.bouncer = Bouncer([int(width * width_mul / 2), height_mul * (height - 1)])
        self.ball = Ball([int(width * width_mul / 2), int(height * height_mul / 2)])

    def draw_elements(self):
        rects = []
        rects += self.blocks.draw(self.surface)
        rects += self.bouncer.draw(self.surface)
        rects += self.ball.draw(self.surface)
        return rects

    def update_elements(self):
        self.blocks.update()
        self.bouncer.update()
        self.ball.update()
        self.check_collisions()

    def check_collisions(self):
        self.bouncer.check_collisions(self.ball)
        self.blocks.check_collisions(self.ball)
        self.ball.check_bounds(self.width)
        self.ball.check_ceiling()
        self.ball.check_death(self.height)
        self.blocks.clear_deleted(self.surface)

    def forward_event(self, event):
        # TODO lancer des lapins
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.bouncer.move_left()
            if event.key == pygame.K_RIGHT:
                self.bouncer.move_right()
