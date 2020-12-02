import pygame
import pika
from random import randint

class Block():
    def __init__(self, pos, width, height, col=None):
        self.pos = pos
        self.width = width
        self.height = height
        self.curr_rect = self.get_rect_from_pos()
        self.to_remove = False
        self.parent = None
        if col == None:
            self.col = (0, 0, 0)
        else:
            self.col = col

    def add_parent(self, parent):
        self.parent = parent

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
        if self.curr_rect.colliderect(ball.curr_rect):
            self.send_message_bounce(self.get_angle(ball))
            self.parent.remove(self)
        else:
            return False
        return True  # Returning this prevents the ball from colliding twice at the same time

    def send_message_bounce(self, body):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='bounce',
                                 exchange_type='fanout')
        message = body # 1 for vertical, 0 for horizontal
        channel.basic_publish(exchange='bounce',
                              routing_key='',
                              body=message)
        return

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
        self.link_children()

    def link_children(self):
        for block_line in self.blocks:
            for block in block_line:
                block.add_parent(self)

    def update(self):
        self.curr_time += 1
        if self.curr_time == self.timer:
            self.add_line()
            self.curr_time = 0
        return

    def draw(self, surface):
        rects = []
        for block_line in self.blocks:
            for block in block_line:
                rects += block.draw(surface)
        return rects

    def remove(self, block):
        # TODO attraper le lapin
        self.blocks[block.pos[1]][block.pos[0]] = NoBlock()
        self.to_remove = block

    def clear_deleted(self, surface):
        if self.to_remove != None:
            pygame.draw.rect(surface, (255,255,255), self.to_remove.curr_rect)
            self.to_remove = None

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
        self.link_children()
        return

    def check_collisions(self, ball):
        for block_line in self.blocks:
            for block in block_line:
                if block.check_collisions(ball):
                    return

    def send_message_game_over(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='game_over',
                                 exchange_type='fanout')
        message = "blocks"
        channel.basic_publish(exchange='game_over',
                              routing_key='',
                              body=message)

    def generate_block(self, i, j):
        if j > self.height / 3:
            return NoBlock()  # We don't want to start the game with too many blocks
        r = randint(0, 100)
        if r < 67:
            return NoBlock()
        col = (randint(0, 255), randint(0, 255), randint(0, 255))
        block = Block([i, j], self.block_width, self.block_height, col=col)
        return block
