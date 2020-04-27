import math

from PIL import Image


def crop(img: Image, width: int = 300, height: int = 200) -> Image:
    size = (width, height)
    img_format = img.format
    image = img.copy()
    old_size = img.size
    left = (old_size[0] - size[0]) / 2
    top = (old_size[1] - size[1]) / 2
    right = old_size[0] - left
    bottom = old_size[1] - top
    rect = [int(math.ceil(x)) for x in (left, top, right, bottom)]
    left, top, right, bottom = rect
    img = image.crop((left, top, right, bottom))
    img.format = img_format
    return img


def contain(img: Image, width: int = 300, height: int = 200) -> Image:
    size = (width, height)
    original_size = img.size
    ratio = max(size[0] / original_size[0], size[1] / original_size[1])
    new_size = (int(math.ceil(original_size[0] * ratio)), int(math.ceil(original_size[1] * ratio)))
    img = img.resize((new_size[0], new_size[1]), Image.LANCZOS)
    return crop(img, width, height)


def generate_square_thumbnail(img: Image, side: int = 200, padding: int = 20, bg_color="white") -> Image:
    size = (side, side)
    img = img.convert("RGBA")
    img.thumbnail((size[0] - padding * 2, size[1] - padding * 2), Image.ANTIALIAS)
    background = Image.new("RGB", size, bg_color)
    background.paste(img, (int((size[0] - img.size[0]) / 2), int((size[1] - img.size[1]) / 2)), mask=img)
    return background


def resize(img: Image, max_width: int = 300, max_height: int = 200) -> Image:
    img = img.convert("RGBA")
    img.thumbnail((max_width, max_height), Image.ANTIALIAS)
    return img


def trim_transparency(img: Image) -> Image:
    img = img.convert("RGBA")
    return img.crop(img.getbbox())
