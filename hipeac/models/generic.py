import os

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.db.utils import ProgrammingError
from django.dispatch import receiver
from django_countries import Countries
from typing import Dict, List

from hipeac.functions import get_european_countries, get_h2020_associated_countries, send_task


class HipeacCountries(Countries):
    only = get_european_countries() + get_h2020_associated_countries()


class Image(models.Model):
    """
    Application images.
    """
    FOLDER = 'public/images'

    image = models.FileField('Image', upload_to=FOLDER, null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0)
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
    CORDIS = 'cordis'
    GOOGLE_MAPS = 'google_maps'
    GOOGLE_PHOTOS = 'google_photos'
    OTHER = 'other'
    TYPE_CHOICES = (
        (WEBSITE, 'Website'),
        (DBLP, 'DBLP'),
        (LINKEDIN, 'LinkedIn'),
        (GITHUB, 'GitHub'),
        (TWITTER, 'Twitter'),
        (YOUTUBE, 'YouTube'),
        (EASYCHAIR, 'EasyChair'),
        (CORDIS, 'Cordis'),
        (GOOGLE_MAPS, 'Google Maps'),
        (GOOGLE_PHOTOS, 'Google Photos'),
        (OTHER, 'Other'),
    )

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    url = models.URLField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='links')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-type']


@receiver(post_save, sender=Link)
def post_save_link(sender, instance, created, **kwargs):
    if instance.type == Link.DBLP and instance.content_type.model == 'profile':
        send_task('hipeac.tasks.dblp.extract_publications_for_user', (instance.object_id,))


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
    SESSION_TYPE = 'session_type'
    PROJECT_PROGRAMME = 'project_programme'
    TOPIC = 'topic'
    TYPE_CHOICES = (
        (GENDER, 'Gender'),
        (TITLE, 'Title'),
        (MEAL_PREFERENCE, 'Meal preference'),
        (JOB_POSITION, 'Position'),
        (EMPLOYMENT, 'Employment type'),
        (APPLICATION_AREA, 'Application area'),
        (SESSION_TYPE, 'Session type'),
        (TOPIC, 'Topic'),
        (PROJECT_PROGRAMME, 'EU project programme'),
    )

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    value = models.CharField(max_length=64)
    euraxess_value = models.CharField(max_length=250, null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['type'])
        ]
        ordering = ['type', 'value']

    def __str__(self) -> str:
        return self.value


def get_cached_metadata_queryset() -> List[Metadata]:
    try:
        queryset = cache.get('cached_metadata_queryset')
        if not queryset:
            queryset = Metadata.objects.all()
            cache.set('cached_metadata_queryset', queryset, 30)
        return queryset
    except ProgrammingError:
        return []


def get_cached_metadata() -> Dict[int, Metadata]:
    try:
        objects = cache.get('cached_metadata_objects')
        if not objects:
            objects = {m.id: m for m in get_cached_metadata_queryset()}
            cache.set('cached_metadata_objects', objects, 30)
        return objects
    except ProgrammingError:
        return {}


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


class DeleteFileMixin:

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)


class PrivateFile(DeleteFileMixin, models.Model):
    """
    Session files / attachments.
    """
    FOLDER = 'private/files'

    def get_upload_path(instance, filename):
        return f'{instance.FOLDER}/{instance.content_type_id}/{instance.object_id}/{filename}'

    file = models.FileField(upload_to=get_upload_path)
    position = models.PositiveSmallIntegerField(default=0)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='private_files')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'hipeac_files_private'
        ordering = ['content_type', 'object_id', 'position']


class PublicFile(DeleteFileMixin, models.Model):
    """
    TODO: should we merge these two?
    Session files / attachments.
    """
    FOLDER = 'public/files'

    def get_upload_path(instance, filename):
        return f'{instance.FOLDER}/{instance.content_type_id}/{instance.object_id}/{filename}'

    file = models.FileField(upload_to=get_upload_path)
    position = models.PositiveSmallIntegerField(default=0)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='public_files')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'hipeac_files_public'
        ordering = ['content_type', 'object_id', 'position']
