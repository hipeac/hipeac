from PIL import Image


def generate_square_thumbnail(img: Image, side=200, padding=20, bg_color='white') -> Image:
    size = (side, side)
    img = img.convert('RGBA')
    img.thumbnail((size[0] - padding * 2, size[1] - padding * 2), Image.ANTIALIAS)
    background = Image.new('RGB', size, bg_color)
    background.paste(img, (int((size[0] - img.size[0]) / 2), int((size[1] - img.size[1]) / 2)), mask=img)
    return background


def resize(img: Image, max_width=300, max_height=200) -> Image:
    img = img.convert('RGBA')
    img.thumbnail((max_width, max_height), Image.ANTIALIAS)
    return img


def trim_transparency(img: Image) -> Image:
    img = img.convert('RGBA')
    return img.crop(img.getbbox())
