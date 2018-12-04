from celery.decorators import task
from PIL import Image

from hipeac.functions import get_image_variant_paths
from hipeac.tools.imaging import contain, generate_square_thumbnail, resize, trim_transparency


@task()
def generate_banner_variants(path: str):
    img = Image.open(path)
    variant_paths = get_image_variant_paths(path, extension='.jpg')
    images = {
        'sm': contain(img.copy(), width=100, height=25),
        'md': contain(img.copy(), width=400, height=100),
        'lg': contain(img.copy(), width=1200, height=300),
        'th': contain(img.copy(), width=200, height=200),
    }

    for size, image in images.items():
        image.save(variant_paths[size], 'JPEG')

    return True


@task()
def generate_logo_variants(path: str):
    trimmed_img = trim_transparency(Image.open(path))
    variant_paths = get_image_variant_paths(path, extension='.png')
    images = {
        'sm': resize(trimmed_img.copy(), max_width=100, max_height=50),
        'md': resize(trimmed_img.copy(), max_width=150, max_height=75),
        'lg': resize(trimmed_img.copy(), max_width=200, max_height=100),
        'th': generate_square_thumbnail(trimmed_img.copy(), side=200, padding=20),
    }

    for size, image in images.items():
        image.save(variant_paths[size], 'PNG')

    return True
