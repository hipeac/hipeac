import os

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from typing import Dict, Optional

from hipeac.functions import get_absolute_uri
from hipeac.models import Link, get_cached_metadata


class ImagesMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__image_path = self.image.path if self.image else None

    def image_has_changed(self):
        return self.image and self.image.path != self.__image_path

    @property
    def images(self) -> Optional[Dict[str, str]]:
        if not self.image:  # noqa
            return None

        parts = os.path.splitext(self.image.url)  # noqa
        extension = parts[1].lower()
        extension = '.jpg' if extension == '.jpeg' else extension
        sizes = ['sm', 'md', 'lg', 'th']
        return {size: ''.join([get_absolute_uri(), parts[0], '_', size, extension]) for size in sizes}


class LinkMixin:
    links_cache = None

    def get_link(self, link_type: str) -> Optional[str]:
        if not self.links_cache:
            self.links_cache = self.links.all()  # noqa
        for link in self.links_cache:
            if link.type == link_type:
                return link.url
        return None

    @property
    def twitter_username(self) -> Optional[str]:
        twitter_link = self.get_link(Link.TWITTER)  # noqa
        return twitter_link.split('/')[-1] if twitter_link else None  # noqa

    @property
    def website(self) -> Optional[str]:
        return self.get_link(Link.WEBSITE)


class MetadataMixin:

    def get_metadata(self, field_name: str):
        if field_name not in ['application_areas', 'career_levels', 'topics']:
            return []
        keys = [int(key) for key in getattr(self, field_name).split(',')]
        metadata = get_cached_metadata()
        return [metadata[key] for key in keys if key in metadata]


class UrlMixin:
    route_name = None

    def get_absolute_url(self) -> str:
        return reverse(self.route_name, args=[self.id, self.slug])  # noqa

    def get_editor_url(self) -> str:
        content_type = ContentType.objects.get_for_model(self)
        return reverse('editor', args=[content_type.id, self.id])  # noqa
