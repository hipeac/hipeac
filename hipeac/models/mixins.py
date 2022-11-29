import os

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from typing import Dict, List, Optional

from hipeac.functions import get_absolute_uri, get_image_variant_paths


class ApplicationAreasMixin(models.Model):
    rel_application_areas = GenericRelation("hipeac.ApplicationArea")

    class Meta:
        abstract = True

    @cached_property
    def application_areas(self):
        return [rel.application_area for rel in self.rel_application_areas.all()]

    def get_application_areas_display(self, separator: str = ", ") -> str:
        values = [obj.value for obj in self.topics]
        values.sort()
        return separator.join(values)


class EditorMixin:
    def get_editor_url(self) -> str:
        content_type = ContentType.objects.get_for_model(self)
        return reverse("editor", args=[content_type.id, self.id])


class FilesMixin(models.Model):
    files = GenericRelation("hipeac.File")

    class Meta:
        abstract = True


class ImagesMixin(models.Model):
    images = GenericRelation("hipeac.Image")

    class Meta:
        abstract = True


class InstitutionsMixin(models.Model):
    rel_institutions = GenericRelation("hipeac.RelatedInstitution")

    class Meta:
        abstract = True

    @cached_property
    def institutions(self):
        return [rel.institution for rel in self.rel_institutions.all()]


class KeywordsMixin(models.Model):
    keywords = ArrayField(models.CharField(max_length=190), default=list, blank=True)

    class Meta:
        abstract = True


class LinksMixin(models.Model):
    links_cache = None
    links = GenericRelation("hipeac.Link")

    class Meta:
        abstract = True

    def get_ordered_links(self) -> List:
        from hipeac.models import Link

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
        from hipeac.models import Link

        twitter_link = self.get_link(Link.TWITTER)  # noqa
        return twitter_link.split("/")[-1] if twitter_link else None  # noqa

    @property
    def website(self) -> Optional[str]:
        from hipeac.models import Link

        return self.get_link(Link.WEBSITE)


class ImageMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__image_path = self.image.path if self.image else None

    def image_has_changed(self):
        return self.image and self.image.path != self.__image_path

    @property
    def images(self) -> Optional[Dict[str, str]]:
        if not self.image:  # noqa
            return None

        _, extension = os.path.splitext(os.path.basename(self.image.url))
        extension = ".jpg" if extension.lower() == ".jpeg" else extension.lower()
        return get_image_variant_paths(self.image.url, extension=extension, pre=get_absolute_uri())


class PermissionsMixin(models.Model):
    acl = GenericRelation("hipeac.Permission")

    class Meta:
        abstract = True

    def _can_be_managed_by(self, user) -> bool:
        from hipeac.models import Permission

        return self.acl.filter(user_id=user.id, level__gte=Permission.ADMIN).exists()

    def can_be_managed_by(self, user) -> bool:
        return self._can_be_managed_by(user)


class ProjectsMixin(models.Model):
    rel_projects = GenericRelation("hipeac.RelatedProject")

    class Meta:
        abstract = True

    @cached_property
    def projects(self):
        return [rel.project for rel in self.rel_projects.all()]


class UsersMixin(models.Model):
    rel_users = GenericRelation("hipeac.RelatedUser")

    class Meta:
        abstract = True

    @cached_property
    def users(self):
        return [rel.user for rel in self.rel_users.all()]


class TopicsMixin(models.Model):
    rel_topics = GenericRelation("hipeac.Topic")

    class Meta:
        abstract = True

    @cached_property
    def topics(self):
        return [rel.topic for rel in self.rel_topics.all()]

    def get_topics_display(self, separator: str = ", ") -> str:
        values = [obj.value for obj in self.topics]
        values.sort()
        return separator.join(values)


class VideosMixin(models.Model):
    rel_videos = GenericRelation("hipeac.RelatedVideo")

    class Meta:
        abstract = True

    @cached_property
    def videos(self):
        return [rel.video for rel in self.rel_videos.all()]
