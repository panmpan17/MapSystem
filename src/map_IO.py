from json import dump as json_dump, load as json_load
from PIL import Image, ImageDraw
from .map_basic import WALL, MARKER
from pygame.image import load as pygame_load_img


__all__ = ["MapSaver"]


WALL_COLOR = (0, 0, 0)
AIR_COLOR = (255, 255, 255)
MARKER_COLOR = (255, 100, 100)


class MapSaver:
    @staticmethod
    def save_image(file_name, map_, block_size=4):
        img = Image.new("RGB",
                        (map_.width * block_size, map_.height * block_size),
                        AIR_COLOR)

        draw = ImageDraw.Draw(img)

        for y, row in enumerate(map_.coords):
            for x, block in enumerate(row):
                pos = x * block_size, y * block_size
                pos += (pos[0] + block_size - 1, pos[1] + block_size - 1)

                if block == WALL:
                    draw.rectangle(pos, WALL_COLOR)
                elif block == MARKER:
                    draw.rectangle(pos, MARKER_COLOR)

        img.save(file_name + ".png", "PNG")
        img.close()

    @staticmethod
    def save_json(file_name, map_):
        json_dump({
            "width": map_.width,
            "height": map_.height,
            "coverage": map_.coverage,
            "seed": map_.seed,
            "coords": map_.coords,
        }, open(file_name + ".json", "w"), indent=1)


class MapReader:
    @staticmethod
    def get_pil_img(file_name):
        return Image.open(file_name + ".png")

    @staticmethod
    def get_pygame_img(file_name):
        return pygame_load_img(file_name + ".png")

    @staticmethod
    def get_map(file_name):
        data = json_load(open(file_name) + ".json")
        
