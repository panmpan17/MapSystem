import random

from .map_const import *
# from .map_saver import ImageSaver


__all__ = ["MapGenerator"]


AROUND = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
CROS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Math:
    @staticmethod
    def slope_predict(x, m, b):
        return m * x + b

    @staticmethod
    def conculate_slope(tile1, tile2):
        # y = m * x + b
        m = (tile2.y - tile1.y) / (tile2.x - tile1.x)
        return m, tile1.y - m * tile1.x


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, Pos):
            return hash(self) == hash(other)
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        else:
            raise TypeError

    def __add__(self, other):
        if isinstance(other, Pos):
            return Pos(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple):
            return Pos(self.x + other[0], self.y + other[1])
        else:
            raise TypeError

    def __repr__(self):
        return f"<Pos {self.x},{self.y}>"

    @staticmethod
    def distance(pos1, pos2):
        return ((pos1.x - pos2.x) ** 2 + (pos1.y - pos2.y) ** 2) ** 0.5


class Room:
    def __init__(self, tiles, map_):
        self.tiles = tiles
        self.room_size = len(tiles)
        self.main_connected = False

        self.connected = set()

        self.edge_tiles = set()
        for tile in self.tiles:
            for d in CROS:
                pos = tile + d

                if map_.is_in_map(pos):
                    if map_.get_block(pos) == WALL:
                        self.edge_tiles.add(tile)

    def __lt__(self, other):
        return self.room_size < other.room_size

    def is_connected(self, other_room):
        return other_room in self.connected

    def connect_main(self):
        self.main_connected = True
        for room in self.connected:
            room.main_connected = True

    @staticmethod
    def connect(ra, rb):
        if ra.main_connected:
            rb.connect_main()
        elif rb.main_connected:
            ra.connect_main()

        ra.connected.add(rb)
        rb.connected.add(ra)


class Region:
    @classmethod
    def scan_regions(cls, map_, block_type):
        regions = []
        map_flags = set()

        for y, row in enumerate(map_.coords):
            for x, block in enumerate(row):
                pos = Pos(x, y)
                if pos not in map_flags and block == block_type:
                    regions.append(cls.scan_blocks(map_, pos))

                    for tile in regions[-1]:
                        map_flags.add(tile)

        return regions

    @classmethod
    def scan_blocks(cls, map_, pos):
        block_type = map_.get_block(pos)
        blocks = set()
        coords_unchecked = set([pos])

        while len(coords_unchecked) > 0:
            block = coords_unchecked.pop()
            blocks.add(block)

            for vec in CROS:
                new_pos = block + vec
                if map_.is_in_map(new_pos):
                    if map_.get_block(new_pos) == block_type:
                        if new_pos not in blocks:
                            coords_unchecked.add(new_pos)

        return blocks


class Map:
    def __init__(self, width, height, coverage, seed):
        self.width = width
        self.height = height
        self.coverage = coverage
        self.seed = seed

        random.seed(seed)

        self.coords = []
        self.rooms = []
        self.passages = []

        for y in range(height):
            self.coords.append([])
            for x in range(self.width):
                if random.randint(1, 100) < coverage:
                    self.coords[-1].append(WALL)
                else:
                    self.coords[-1].append(AIR)

    def __repr__(self):
        return (f"<Map size={self.width}x{self.height} "
                f"coverage={self.coverage} seed={self.seed}>")

    def is_in_map(self, pos):
        if isinstance(pos, Pos):
            return ((pos.x >= 0) and (pos.x < self.width) and
                    (pos.y >= 0) and (pos.y < self.height))
        elif isinstance(pos, tuple):
            return ((pos[0] >= 0) and (pos[0] < self.width) and
                    (pos[1] >= 0) and (pos[1] < self.height))
        else:
            raise TypeError

    def count_wall(self, pos):
        count = 0

        for vec in AROUND:
            new_pos = pos + vec

            if self.is_in_map(new_pos):
                count += self.get_block(new_pos)
            else:
                count += 1

        return count

    def get_block(self, pos):
        if isinstance(pos, Pos):
            return self.coords[pos.y][pos.x]
        elif isinstance(pos, tuple):
            return self.coords[pos[1]][pos[0]]
        else:
            raise TypeError

    def set_block(self, pos, block_type):
        if isinstance(pos, Pos):
            self.coords[pos.y][pos.x] = block_type
        elif isinstance(pos, tuple):
            self.coords[pos[1]][pos[0]] = block_type
        else:
            raise TypeError


class MapGenerator:
    @classmethod
    def generate(cls, width, height, coverage=50, seed=None, randomseed=True,
                 smooth_times=3, minimal_size=3, smooth_pop=4, clean_up=True,
                 clean_up_wall_first=True, connect_closest_roooms=True,
                 connect_main_room=True):
        if randomseed:
            seed = random.randint(1, 10000)

        map_ = Map(width, height, coverage, seed)

        for _ in range(smooth_times):
            cls.smooth(map_, smooth_pop)

        if clean_up:
            cls.clean_up(map_, minimal_size, clean_up_wall_first)

        if connect_closest_roooms:
            map_.rooms = [Room(region, map_)
                          for region in Region.scan_regions(map_, AIR)]

            cls.connect_closest_rooms(map_)

            if connect_main_room:
                cls.connect_main_room(map_)

            cls.smooth(map_, smooth_pop)

        return map_

    @classmethod
    def smooth(cls, map_, smooth_pop, equl_handle=None):
        for x in range(map_.width):
            for y in range(map_.height):
                pos = Pos(x, y)
                count = map_.count_wall(pos)

                # Count block arround to decide which type this block we be
                if count > smooth_pop:
                    map_.set_block(pos, WALL)
                elif count < smooth_pop:
                    map_.set_block(pos, AIR)
                elif equl_handle is not None:
                    map_.set_block(pos, equl_handle)

    @classmethod
    def clean_up(cls, map_, minimal_size, clean_up_wall_first):
        wall_regions = Region.scan_regions(map_, WALL)

        # Find those wall that are too small, then delete them
        for region in wall_regions:
            if len(region) < minimal_size:
                for pos in region:
                    map_.set_block(pos, AIR)

        # Find those rooms that are too small, then fill them up
        air_regions = Region.scan_regions(map_, AIR)
        for region in air_regions:
            if len(region) < minimal_size:
                for pos in region:
                    map_.set_block(pos, WALL)

    @classmethod
    def connect_closest_rooms(cls, map_):
        passages = []

        map_.rooms.sort()
        map_.rooms[-1].main_connected = True

        # Loop threough room, find closest room and connect
        for ra in map_.rooms:
            best_dis = 0
            best_ra = None
            best_rb = None
            best_ta = None
            best_tb = None
            connection_found = False

            if len(ra.connected) > 0:
                continue

            for rb in map_.rooms:
                if ra == rb:
                    continue

                dis, ta, tb = cls.find_best_passage(ra, rb, acceptable_dis=10)
                if dis < best_dis or not connection_found:
                    connection_found = True
                    best_dis = dis
                    best_ta = ta
                    best_tb = tb
                    best_ra = ra
                    best_rb = rb

            if connection_found:
                Room.connect(best_ra, best_rb)
                passages.append((best_ta, best_tb))

        for ta, tb in passages:
            for pos in cls.get_line(ta, tb):
                cls.draw_circle(map_, pos, 3, 5)

    @classmethod
    def connect_main_room(cls, map_):
        rla = []
        rlb = []
        for r in map_.rooms:
            if r.main_connected:
                rlb.append(r)
            else:
                rla.append(r)

        if len(rla) == 0:
            return

        best_dis = 0
        best_ra = None  # room a
        best_rb = None  # room b
        best_ta = None  # tile a
        best_tb = None  # tile b
        connection_found = False

        for ra in rla:
            if ra.main_connected:
                continue

            connection_found = False

            for rb in rlb:
                if ra == rb:
                    continue

                dis, ta, tb = cls.find_best_passage(ra, rb, acceptable_dis=10)
                if dis < best_dis or not connection_found:
                    connection_found = True
                    best_dis = dis
                    best_ta = ta
                    best_tb = tb
                    best_ra = ra
                    best_rb = rb

            for c_ra in ra.connected:
                for rb in rlb:

                    dis, ta, tb = cls.find_best_passage(c_ra, rb,
                                                        acceptable_dis=10)
                    if dis < best_dis or not connection_found:
                        connection_found = True
                        best_dis = dis
                        best_ta = ta
                        best_tb = tb
                        best_ra = ra
                        best_rb = rb

            if connection_found:
                Room.connect(best_ra, best_rb)
                for pos in cls.get_line(best_ta, best_tb):
                    cls.draw_circle(map_, pos, 3, 5)

                rlb.append(best_ra)
                for room in best_ra.connected:
                    rlb.append(room)

    @classmethod
    def find_best_passage(self, ra, rb, acceptable_dis=-1):
        best_dis = 0
        best_ta = None
        best_tb = None

        # Loop through room's edges find closest passage
        for ta in ra.edge_tiles:
            for tb in rb.edge_tiles:
                distance = Pos.distance(ta, tb)

                if distance < acceptable_dis:
                    return distance, ta, tb

                if distance < best_dis or best_dis == 0:
                    best_dis = distance
                    best_ta = ta
                    best_tb = tb

        return best_dis, best_ta, best_tb

    @classmethod
    def draw_circle(cls, map_, pos, rmin, rmax):
        r = random.randint(rmin, rmax)
        for x in range(-r, r + 1):
            for y in range(-r, r + 1):
                if x * x + y * y <= r * r:
                    new_pos = pos + (x, y)
                    if map_.is_in_map(new_pos):
                        map_.set_block(new_pos, AIR)

    @classmethod
    def get_line(cls, tile1, tile2):
        line = set()

        if tile1.x != tile2.x:
            m, b = Math.conculate_slope(tile1, tile2)

            if tile2.x > tile1.x:
                for x in range(tile1.x, tile2.x + 1):
                    line.add(Pos(x, int(Math.slope_predict(x, m, b))))
            else:
                for x in range(tile2.x, tile1.x + 1):
                    line.add(Pos(x, int(Math.slope_predict(x, m, b))))
        else:
            if tile2.y > tile1.y:
                for y in range(tile1.y, tile2.y + 1):
                    line.add(Pos(tile1.x, y))
            else:
                for y in range(tile2.y, tile1.y + 1):
                    line.add(Pos(tile1.x, y))

        return line
