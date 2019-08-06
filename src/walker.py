from .map_basic import CROS, WALL


SPEED = 10


class Walker:
    def __init__(self, pos):
        self.pos = pos
        self.walking = False
        self.destination = None

        self.path = []
        self.path_length = 0
        self.walk_progress = 0

    def set_destination(self, pos):
        self.destination = pos

    def find_path(self, map_, start=False):
        dis_index = {self.pos: 0}
        uncheck_pos = [self.pos]
        breaked = False

        while len(uncheck_pos) > 0 and not breaked:
            pos = uncheck_pos.pop(0)
            dis = dis_index[pos]

            for vec in CROS:
                new_pos = pos + vec

                if not map_.is_in_map(new_pos):
                    continue
                if map_.get_block(new_pos) == WALL:
                    continue
                if new_pos in dis_index:
                    continue

                if new_pos == self.destination:
                    dis_index[new_pos] = dis + 1
                    breaked = True
                    self.path_length = dis + 1
                    break

                dis_index[new_pos] = dis + 1

                uncheck_pos.append(new_pos)

        self.path.append(self.destination)
        while self.path[0] != self.pos:
            last_pos = self.path[0]

            best_next = None
            best_next_dis = dis_index[last_pos]

            for vec in CROS:
                new_pos = last_pos + vec

                if new_pos not in dis_index:
                    continue

                if dis_index[new_pos] < best_next_dis:
                    best_next = new_pos
                    best_next_dis = dis_index[new_pos]

            self.path.insert(0, best_next)

        if start:
            self.walking = True

    def walk(self, tick):
        self.walk_progress += SPEED / tick

        if self.walk_progress >= 1:
            self.walk_progress = 0
            self.pos = self.path.pop(0)

            if len(self.path) == 0:
                self.walking = False
