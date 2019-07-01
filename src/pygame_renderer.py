import pygame

from .map_basic import Pos


CYAN = (100, 200, 220)
RED = (220, 100, 100)


class PygameRenderer:
    def __init__(self, map_img, multilier):
        self.map_img = map_img
        self.marker = []
        self.walker = []
        self.multilier = multilier

    def add_walker(self, walker):
        self.walker.append(walker)

    def pos_to_rect(self, pos):
        return (pos.x * self.multilier, pos.y * self.multilier,
                self.multilier, self.multilier)

    def run(self, map_):
        window = pygame.display.set_mode(self.map_img.get_size())
        pygame.display.set_caption("Map System")

        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = Pos(event.pos)
                    pos //= self.multilier

                    for walker in self.walker:
                        if not walker.walking:
                            walker.set_destination(pos)
                            walker.find_path(map_)

            window.blit(self.map_img, self.map_img.get_rect())

            for walker in self.walker:
                pygame.draw.rect(window, CYAN,
                                 self.pos_to_rect(walker.pos))

                for i, pos in enumerate(walker.path):
                    pygame.draw.rect(
                        window, (0, (255 / len(walker.path)) * i, 0),
                        self.pos_to_rect(pos))

                if walker.destination is not None:
                    pygame.draw.rect(window, RED,
                                     self.pos_to_rect(walker.destination))

            pygame.display.flip()
            clock.tick(30)
