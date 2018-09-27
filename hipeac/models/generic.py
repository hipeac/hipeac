import os

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from typing import Dict, List
from django_countries import Countries

from hipeac.functions import get_european_countries, get_h2020_associated_countries


class HipeacCountries(Countries):
    only = get_european_countries() + get_h2020_associated_countries()


class Image(models.Model):
    """
    Application images.
    """
    FOLDER = 'public/images'

    image = models.FileField('Image', upload_to=FOLDER, null=True, blank=True)
    position = models.PositiveSmallIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='images')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['content_type', 'object_id', 'position']

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)


class Link(models.Model):
    """
    Online accounts and other links.
    """
    WEBSITE = 'website'
    DBLP = 'dblp'
    TWITTER = 'twitter'
    LINKEDIN = 'linkedin'
    GITHUB = 'github'
    YOUTUBE = 'youtube'
    EASYCHAIR = 'easychair'
    GOOGLE_MAPS = 'google_maps'
    GOOGLE_PHOTOS = 'google_photos'
    OTHER = 'other'
    TYPE_CHOICES = (
        (WEBSITE, 'Website'),
        (DBLP, 'DBLP'),
        (TWITTER, 'Twitter'),
        (LINKEDIN, 'LinkedIn'),
        (GITHUB, 'GitHub'),
        (YOUTUBE, 'YouTube'),
        (GOOGLE_MAPS, 'Google Maps'),
        (GOOGLE_PHOTOS, 'Google Photos'),
        (EASYCHAIR, 'EasyChair'),
        (OTHER, 'Other'),
    )

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    url = models.URLField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='links')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-type']


class Metadata(models.Model):
    """
    Metadata used by other models.
    """
    GENDER = 'gender'
    TITLE = 'title'
    MEAL_PREFERENCE = 'meal_preference'
    JOB_POSITION = 'job_position'
    EMPLOYMENT = 'employment_type'
    APPLICATION_AREA = 'application_area'
    TOPIC = 'topic'
    TYPE_CHOICES = (
        (GENDER, 'Gender'),
        (TITLE, 'Title'),
        (MEAL_PREFERENCE, 'Meal preference'),
        (JOB_POSITION, 'Position'),
        (EMPLOYMENT, 'Employment type'),
        (APPLICATION_AREA, 'Application area'),
        (TOPIC, 'Topic'),
    )

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    value = models.CharField(max_length=64)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['type'])
        ]
        ordering = ['type', 'value']

    def __str__(self) -> str:
        return self.value


def get_cached_metadata_queryset() -> List[Metadata]:
    queryset = cache.get('cached_metadata_queryset')
    if not queryset:
        queryset = Metadata.objects.all()
        cache.set('cached_metadata_queryset', queryset, 30)
    return queryset


def get_cached_metadata() -> Dict[int, Metadata]:
    objects = cache.get('cached_metadata_objects')
    if not objects:
        objects = {m.id: m for m in get_cached_metadata_queryset()}
        cache.set('cached_metadata_objects', objects, 30)
    return objects


class Permission(models.Model):
    """
    Higher permission levels inherit lower permissions, simplifying queries.
    """
    OWNER = 9
    ADMIN = 7
    GUEST = 1
    LEVEL_CHOICES = (
        (OWNER, 'Owner'),
        (ADMIN, 'Administrator'),
        (GUEST, 'Guest'),
    )

    user = models.ForeignKey(get_user_model(), blank=True, on_delete=models.CASCADE, related_name='xpermissions')
    level = models.PositiveSmallIntegerField(db_index=True, choices=LEVEL_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='xpermissions')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self) -> str:
        return f'{self.user} ({self.get_level_display()})'
