import os

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from typing import Dict, List, Optional

from hipeac.functions import get_absolute_uri, get_image_variant_paths
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

        name, extension = os.path.splitext(os.path.basename(self.image.url))
        extension = '.jpg' if extension.lower() == '.jpeg' else extension.lower()
        return get_image_variant_paths(self.image.url, extension=extension, pre=get_absolute_uri())


class LinkMixin:
    links_cache = None

    def get_ordered_links(self) -> List[Link]:
        links = list(dict(Link.TYPE_CHOICES).keys())
        links_order = {links[i]: i for i in range(0, len(links))}

        if not self.links_cache:
            self.links_cache = self.links.all()  # noqa
        return sorted(self.links_cache, key=lambda x: links_order[x.type])

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
        value = getattr(self, field_name)
        if value == '':
            return []
        keys = [int(key) for key in getattr(self, field_name).split(',')]
        metadata = get_cached_metadata()
        return [metadata[key] for key in keys if key in metadata]

    def get_metadata_display(self, field_name: str, separator: str = ', ') -> str:
        metadata = [str(m) for m in self.get_metadata(field_name)]
        return separator.join(metadata)


class EditorMixin:

    def get_editor_url(self) -> str:
        content_type = ContentType.objects.get_for_model(self)
        return reverse('editor', args=[content_type.id, self.id])  # noqa


class UrlMixin(EditorMixin):
    route_name = None

    def get_absolute_url(self) -> str:
        return reverse(self.route_name, args=[self.id, self.slug])  # noqa
