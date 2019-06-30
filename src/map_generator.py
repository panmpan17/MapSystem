import random

from .map_const import *


__all__ = ["MapGenerator"]


AROUND = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
CROS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Room:
    def __init__(self, tiles, map_coords):
        self.tiles = tiles
        self.room_size = len(tiles)
        self.main_connected = False

        self.connected = set()

        self.edge_tiles = set()
        for tile in self.tiles:
            for d in CROS:
                x = tile.x + d[0]
                y = tile.y + d[1]

                try:
                    if map_coords[y][x] == WALL:
                        self.edge_tiles.add(tile)
                except IndexError:
                    pass

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
                pos = (x, y)
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
                new_pos = block[0] + vec[0], block[1] + vec[1]
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
        self.room = []
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
        x, y = pos
        return (x >= 0) and (x < self.width) and (y >= 0) and (y < self.height)

    def count_wall(self, pos):
        count = 0

        for vec_x, vec_y in AROUND:
            new_pos = (pos[0] + vec_x, pos[1] + vec_y)

            if self.is_in_map(new_pos):
                count += self.get_block(new_pos)
            else:
                count += 1

        return count

    def get_block(self, pos):
        return self.coords[pos[1]][pos[0]]

    def set_block(self, pos, block_type):
        self.coords[pos[1]][pos[0]] = block_type


class MapGenerator:
    @classmethod
    def generate(cls, width, height, coverage=50, seed=None, randomseed=True,
                 smooth_times=3, minimal_size=3, smooth_pop=4, clean_up=True,
                 clean_up_wall_first=True):
        if randomseed:
            seed = random.randint(1, 10000)

        map_ = Map(width, height, coverage, seed)

        for _ in range(smooth_times):
            cls.smooth(map_, smooth_pop)

        if clean_up:
            cls.clean_up(map_, minimal_size, clean_up_wall_first)

        return map_

    @classmethod
    def smooth(cls, map_, smooth_pop, equl_handle=None):
        for x in range(map_.width):
            for y in range(map_.height):
                pos = (x, y)
                count = map_.count_wall(pos)

                if count > smooth_pop:
                    map_.set_block(pos, 1)
                elif count < smooth_pop:
                    map_.set_block(pos, 0)
                else:
                    if equl_handle is not None:
                        map_.set_block(pos, equl_handle)

    @classmethod
    def clean_up(cls, map_, minimal_size, clean_up_wall_first):
        wall_regions = Region.scan_regions(map_, WALL)

        for region in wall_regions:
            if len(region) < minimal_size:
                for pos in region:
                    map_.set_block(pos, AIR)

        air_regions = Region.scan_regions(map_, AIR)
        for region in air_regions:
            if len(region) < minimal_size:
                for pos in region:
                    map_.set_block(pos, WALL)
