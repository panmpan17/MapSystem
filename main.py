import argparse

from src import MapGenerator, ImageSaver


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--generate", "-g", action="store_true", )
    parser.add_argument("--map", "-m", default="map")

    args = parser.parse_args()

    map_ = MapGenerator.generate(80, 80, coverage=52, smooth_times=3,
                                 randomseed=False, seed=1, minimal_size=30)
    ImageSaver.save_as_image("resault/test", map_, block_size=5)
