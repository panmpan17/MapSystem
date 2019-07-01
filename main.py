import argparse
import random

from os.path import join as join_path
from src import (MapGenerator, MapSaver, MapReader, PygameRenderer,
                 Region, AIR, Walker)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("functions", action="store",
                        choices=["generate", "pathfinding"])
    parser.add_argument("--map", "-m", default="map",
                        help="The name of the map, need to be in result")

    args = parser.parse_args()

    map_name = join_path("result", args.map)
    if args.functions == "generate":
        map_ = MapGenerator.generate(500, 500, coverage=52, smooth_times=5,
                                     randomseed=False, seed=1, minimal_size=30)

        MapSaver.save_image(map_name, map_, block_size=3)
        MapSaver.save_json(map_name, map_)
    else:
        map_ = MapReader.get_map(map_name)
        img = MapReader.get_pygame_img(map_name)

        pos = random.choice(tuple(Region.scan_regions(map_, AIR)[0]))
        walker = Walker(pos)

        renderer = PygameRenderer(img, 3)
        renderer.add_walker(walker)
        renderer.run(map_)
