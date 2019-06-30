AIR = 0
WALL = 1
MARKER = 2

AROUND = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
CROS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Pos:
    def __init__(self, x, y=None):
        if isinstance(x, tuple):
            self.x = x[0]
            self.y = x[1]
        else:
            if y is None:
                raise ValueError

            self.x = x
            self.y = y

    def __repr__(self):
        return f"<Pos {self.x},{self.y}>"

    def __hash__(self):
        return hash((self.x, self.y))

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError

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

    def __sub__(self, other):
        if isinstance(other, Pos):
            return Pos(self.x - other.x, self.y - other.y)
        elif isinstance(other, tuple):
            return Pos(self.x - other[0], self.y - other[1])
        else:
            raise TypeError

    def __mul__(self, multiplier):
        return Pos(self.x * multiplier, self.y * multiplier)

    def __iadd__(self, other):
        if isinstance(other, Pos):
            self.x += other.x
            self.y += other.y
        elif isinstance(other, tuple):
            self.x += other[0]
            self.y += other[1]
        else:
            raise TypeError

    def __isub__(self, other):
        if isinstance(other, Pos):
            self.x -= other.x
            self.y -= other.y
        elif isinstance(other, tuple):
            self.x -= other[0]
            self.y -= other[1]
        else:
            raise TypeError

    def __imul__(self, multiplier):
        if isinstance(multiplier, int):
            self.x *= multiplier
            self.y *= multiplier
        else:
            raise TypeError

    def __ifloordiv__(self, num):
        if isinstance(num, int):
            self.x //= num
            self.y //= num
            return self
        else:
            raise TypeError

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
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.coverage = 0
        self.seed = None

        self.coords = [[0 for x in range(width)] for y in range(height)]
        self.rooms = []

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
