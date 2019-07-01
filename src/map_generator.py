import random

from .map_basic import *
from time import time


__all__ = ["MapGenerator"]


class Math:
    @staticmethod
    def slope_predict(x, m, b):
        return m * x + b

    @staticmethod
    def conculate_slope(tile1, tile2):
        # y = m * x + b
        m = (tile2.y - tile1.y) / (tile2.x - tile1.x)
        return m, tile1.y - m * tile1.x


class MapGenerator:
    @classmethod
    def generate(cls, width, height, coverage=50, seed=None, randomseed=True,
                 smooth_times=3, minimal_size=3, smooth_pop=4, clean_up=True,
                 clean_up_wall_first=True, connect_closest_roooms=True,
                 connect_main_room=True):
        if randomseed:
            seed = random.randint(1, 10000)

        map_ = Map(width, height)
        cls.random_map(map_, coverage, seed)

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
    def test_generate_speed(cls, width, height, coverage=50, seed=None,
                            randomseed=True, smooth_times=3, minimal_size=3,
                            smooth_pop=4, clean_up=True,
                            clean_up_wall_first=True,
                            connect_closest_roooms=True,
                            connect_main_room=True):
        track_time = {}
        if randomseed:
            seed = random.randint(1, 10000)

        map_ = Map(width, height)

        start = time()
        cls.random_map(map_, coverage, seed)
        track_time["randomisze"] = time() - start

        for i in range(smooth_times):
            start = time()
            cls.smooth(map_, smooth_pop)
            track_time["smooth-" + str(i)] = time() - start

        if clean_up:
            start = time()
            cls.clean_up(map_, minimal_size, clean_up_wall_first)
            track_time["clean"] = time() - start

        if connect_closest_roooms:
            start = time()
            map_.rooms = [Room(region, map_)
                          for region in Region.scan_regions(map_, AIR)]
            track_time["search-rooms"] = time() - start

            start = time()
            cls.connect_closest_rooms(map_)
            track_time["connect-closest"] = time() - start

            if connect_main_room:
                start = time()
                cls.connect_main_room(map_)
                track_time["connect-main"] = time() - start

            start = time()
            cls.smooth(map_, smooth_pop)
            track_time["final-smooth"] = time() - start

        return track_time

    @classmethod
    def random_map(cls, map_, coverage, seed):
        map_.seed = seed
        map_.coverage = coverage

        random.seed(seed)

        for y in range(map_.height):
            for x in range(map_.width):
                if random.randint(1, 100) < coverage:
                    map_.set_block((x, y), WALL)
                else:
                    map_.set_block((x, y), AIR)

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
        non_connect = []
        connected = []
        for r in map_.rooms:
            if r.main_connected:
                connected.append(r)
            else:
                non_connect.append(r)

        if len(non_connect) == 0:
            return

        for ra in non_connect:
            if ra.main_connected:
                continue

            best_dis = 0
            best_ra = None  # room a
            best_rb = None  # room b
            best_ta = None  # tile a
            best_tb = None  # tile b
            connection_found = False

            for rb in connected:
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
                for rb in connected:

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

                connected.append(best_ra)
                for room in best_ra.connected:
                    connected.append(room)

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
