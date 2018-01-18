import os

from celery.decorators import task
from PIL import Image

from hipeac.tools.imaging import generate_square_thumbnail, resize, trim_transparency


@task()
def generate_image_variants(path: str):
    parts = os.path.splitext(path)
    trimmed_img = trim_transparency(Image.open(path))

    variants = {
        'sm': resize(trimmed_img.copy(), max_width=100, max_height=50),
        'md': resize(trimmed_img.copy(), max_width=150, max_height=75),
        'lg': resize(trimmed_img.copy(), max_width=200, max_height=100),
        'th': generate_square_thumbnail(trimmed_img.copy(), side=200, padding=20),
    }

    for size, image in variants.items():
        image.save(''.join([parts[0], '_', size, '.png']), 'PNG')

    return True
