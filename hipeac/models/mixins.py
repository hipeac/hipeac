import os

from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.urls import reverse
from typing import Dict, Optional

from hipeac.functions import get_absolute_uri
from hipeac.models import Link


class ContentTypeMixin:
    content_type = None

    def get_content_type(self) -> ContentType:
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self)
        return self.content_type


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
        return {size: ''.join([get_absolute_uri(), parts[0], '_', size, parts[1]]) for size in ['sm', 'md', 'th']}


class LinkMixin:
    links_cache = None

    def get_link(self, link_type: str) -> Optional[str]:
        if not self.links_cache:
            self.links_cache = self.links.all()  # noqa
        for link in self.links_cache:
            if link.type == link_type:
                return link.url
        return None

    def twitter(self) -> Optional[str]:
        return self.get_link(Link.TWITTER)

    def twitter_username(self) -> Optional[str]:
        return self.twitter().split('/')[-1] if self.twitter() else None  # noqa

    def website(self) -> Optional[str]:
        return self.get_link(Link.WEBSITE)


class UrlMixin(ContentTypeMixin):
    route_name = None

    def get_absolute_url(self) -> str:
        return reverse(self.route_name, args=[str(self.id), self.slug])  # noqa

    def get_editor_url(self) -> str:
        return reverse('editor', args=[self.get_content_type().id, self.id])  # noqa
