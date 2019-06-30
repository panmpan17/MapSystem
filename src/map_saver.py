from PIL import Image, ImageDraw
from .map_const import *


__all__ = ["ImageSaver"]


WALL_COLOR = (0, 0, 0)
AIR_COLOR = (255, 255, 255)
MARKER_COLOR = (255, 100, 100)


class ImageSaver:
    @staticmethod
    def save_as_image(file_name, map_, block_size=4):
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
