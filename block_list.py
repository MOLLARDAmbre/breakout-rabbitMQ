import pygame
import pika
import uuid
import _thread
from random import randint
from rabbit_sender import send, recv

class Block():
    def __init__(self, pos, width, height, table_width, col=None):
        self.pos = pos
        self.width = width
        self.height = height
        self.table_width = table_width
        self.curr_rect = self.get_rect_from_pos()
        self.collision_enabled = True
        if col == None:
            self.col = (0, 0, 0)
        else:
            self.col = col

    def draw(self, surface):
        rects = [self.curr_rect]
        new_rect = self.get_rect_from_pos()
        pygame.draw.rect(surface, (255,255,255), self.curr_rect)
        rects.append(new_rect)
        self.curr_rect = new_rect
        pygame.draw.rect(surface, self.col, self.curr_rect)
        return rects

    def isnt_noblock(self):
        return True

    def get_angle(self, ball):
        xy = [self.pos[0] - ball.pos[0], self.pos[1] - ball.pos[1]]
        scal = xy[0] * 1 + xy[1] * 0  # Compute scalar product with unit vector (1, 0)
        scal = scal * scal  # We compare the square of the scalar product to avoid dealing with orientation
        scal = scal / (xy[0] * xy[0] + xy[1] * xy[1])  # Divide by the norm of the vector
        if scal > 0.5:
            return "0"
        return "1"


    def check_collisions(self, ball):
        if not self.collision_enabled:
            return False
        if self.curr_rect.colliderect(ball.curr_rect):
            self.send_message_bounce(self.get_angle(ball))
            self.send_message_remove()
            self.collision_enabled = False  # Disable collision to avoir problems while waiting for the message to be received
        else:
            return False
        return True  # Returning this prevents the ball from colliding twice at the same time

    def encode_pos(self):
        return str(self.pos[1] * self.table_width + self.pos[0])

    def send_message_remove(self):
        send('remove', self.encode_pos())

    def send_message_bounce(self, body):
        send('bounce', body)

    def get_rect_from_pos(self):
        return pygame.Rect(self.pos[0] * self.width, self.pos[1] * self.height, \
                           self.width, self.height)

class NoBlock(Block):
    """
    Represents a lack of block.
    """
    def __init__(self):
        return

    def draw(self, surface):
        return []

    def check_collisions(self, ball):
        return False

    def isnt_noblock(self):
        return False

class BlockList():
    def __init__(self, width, block_width, height, block_height, timer=600):
        self.width = width
        self.height = height
        self.block_width = block_width
        self.block_height = block_height
        self.timer = timer
        self.curr_time = 0
        self.to_remove = None
        self.blocks = [[self.generate_block(i, j) for i in range(width)] for j in range(height)]
        _thread.start_new_thread(self.listen_for_remove, ())

    def update(self):
        self.curr_time += 1
        if self.curr_time == self.timer:
            self.add_line()
            self.curr_time = 0
        if self.to_remove != None:
            height, width = self.to_remove
            self.blocks[height][width] = NoBlock()
            self.to_remove = None
        return

    def draw(self, surface):
        rects = []
        for block_line in self.blocks:
            for block in block_line:
                rects += block.draw(surface)
        return rects

    def decode_pos(self, encoded_str):
        nb = int(encoded_str)
        height = nb // self.width
        width = nb % self.width
        return [width, height]

    def listen_for_remove(self):
        def callback(ch, method, properties, body):
            self.remove(body)
        recv('remove', callback)

    def remove(self, encoded_str):
        width, height = self.decode_pos(encoded_str)
        block = self.blocks[height][width]
        self.to_remove = (height, width)
        block.col = (255, 255, 255)

    def add_line(self):
        new_blocks = [[NoBlock() for i in range(self.width)] for j in range(self.height)]
        for block_line in self.blocks:
            for block in block_line:
                if block.isnt_noblock():
                    if block.pos[1] >= self.height - 1:
                        self.send_message_game_over()  # The blocks are too close, game over
                        return
                    block.pos = [block.pos[0], block.pos[1]+1]
                    new_blocks[block.pos[1]][block.pos[0]] = block
        self.blocks = new_blocks
        self.blocks[0] = [self.generate_block(i, 0) for i in range(self.width)]
        return

    def check_collisions(self, ball):
        for block_line in self.blocks:
            for block in block_line:
                if block.check_collisions(ball):
                    return

    def send_message_game_over(self):
        send('game_over', "blocks")

    def generate_block(self, i, j):
        if j > self.height / 3:
            return NoBlock()  # We don't want to start the game with too many blocks
        r = randint(0, 100)
        if r < 67:
            return NoBlock()
        col = (randint(0, 255), randint(0, 255), randint(0, 255))
        block = Block([i, j], self.block_width, self.block_height, self.width, col=col)
        return block
