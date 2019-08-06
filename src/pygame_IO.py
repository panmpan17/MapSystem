import random
import pygame

from threading import Thread
from .walker import Walker


CYAN = (100, 200, 220)
RED = (220, 100, 100)
TICK_NUM = 30


class PygameController:
    def __init__(self, air_block, map_):
        self.air_block = air_block
        self.marker = []
        self.walker = []
        self.map = map_

    def spawn_walker(self, num):
        for _ in range(num):
            pos = random.choice(self.air_block)
            self.walker.append(Walker(pos))

    def tick(self):
        for walker in self.walker:
            if not walker.walking:
                walker.set_destination(random.choice(self.air_block))
                t = Thread(target=walker.find_path, args=(self.map, ),
                           kwargs={"start": True})
                t.start()

            else:
                walker.walk(TICK_NUM)


class PygameRenderer:
    def __init__(self, controller, map_img, multilier):
        self.controller = controller
        self.map_img = map_img
        self.multilier = multilier

    def add_walker(self, walker):
        self.walker.append(walker)

    def pos_to_rect(self, pos):
        return (pos.x * self.multilier, pos.y * self.multilier,
                self.multilier, self.multilier)

    def run(self):
        window = pygame.display.set_mode(self.map_img.get_size())
        pygame.display.set_caption("Map System")

        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            window.blit(self.map_img, self.map_img.get_rect())

            for walker in self.controller.walker:
                pygame.draw.rect(window, CYAN,
                                 self.pos_to_rect(walker.pos))
            self.controller.tick()

            # for i, pos in enumerate(walker.path):
            #     pygame.draw.rect(
            #         window, (0, (255 / len(walker.path)) * i, 0),
            #         self.pos_to_rect(pos))

            # if walker.destination is not None:
            #     pygame.draw.rect(window, RED,
            #                      self.pos_to_rect(walker.destination))

            pygame.display.flip()
            clock.tick(TICK_NUM)
