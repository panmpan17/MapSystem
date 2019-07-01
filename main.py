import argparse
import random
import csv

from os.path import join as join_path
from src import (MapGenerator, MapSaver, MapReader, PygameRenderer,
                 Region, AIR, Walker)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("functions", action="store",
                        choices=["generate", "pathfinding", "testspeed"])
    parser.add_argument("--map", "-m", default="map",
                        help="The name of the map, need to be in result")
    parser.add_argument("--testtime", "-t", default=50,
                        type=int)

    args = parser.parse_args()

    map_name = join_path("result", args.map)
    if args.functions == "generate":
        map_ = MapGenerator.generate(
            50, 50, coverage=52, smooth_times=5,
            randomseed=True, minimal_size=30)

        MapSaver.save_image(map_name, map_, block_size=3)
        MapSaver.save_json(map_name, map_)

    elif args.functions == "testspeed":
        records = []
        sum_ = {"type": "sum"}
        smallest = {"type": "smallest"}
        biggest = {"type": "biggest"}

        for i in range(args.testtime):
            record = MapGenerator.test_generate_speed(
                50, 50, coverage=52, smooth_times=5,
                randomseed=True, minimal_size=30)

            for f, v in record.items():
                if f not in sum_:
                    sum_[f] = v
                    smallest[f] = v
                    biggest[f] = v
                else:
                    sum_[f] += v
                    if v < smallest[f]:
                        smallest[f] = v
                    if v > biggest[f]:
                        biggest[f] = v

            record["type"] = "map-" + str(i)
            records.append(record)
            print(".", end="", flush=True)
        print()

        average = {"type": "average"}
        for f, v in sum_.items():
            if f == "type":
                continue

            average[f] = v / len(records)

        with open("result/test.csv", 'w', newline='') as csvfile:
            field = list(records[0].keys())
            field.insert(0, "type")
            writer = csv.DictWriter(csvfile, fieldnames=field)

            writer.writeheader()
            writer.writerow(sum_)
            writer.writerow(average)
            writer.writerow(smallest)
            writer.writerow(biggest)
            writer.writerow({})

            writer.writerows(records)

    else:
        map_ = MapReader.get_map(map_name)
        img = MapReader.get_pygame_img(map_name)

        pos = random.choice(tuple(Region.scan_regions(map_, AIR)[0]))
        walker = Walker(pos)

        renderer = PygameRenderer(img, 3)
        renderer.add_walker(walker)
        renderer.run(map_)
