import argparse
from os.path import join as join_path

from src import MapGenerator, MapSaver, MapReader


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("functions", action="store",
                        choices=["generate", "pathfinding"])
    parser.add_argument("--map", "-m", default="map",
                        help="The name of the map, need to be in result")

    args = parser.parse_args()

    map_name = join_path("result", args.map)
    if args.functions == "generate":
        map_ = MapGenerator.generate(80, 80, coverage=52, smooth_times=5,
                                     randomseed=False, seed=1, minimal_size=30)

        MapSaver.save_image(map_name, map_, block_size=5)
        MapSaver.save_json(map_name, map_)
    else:
        pygame_img = MapReader.get_pygame_img(map_name)

        pass
