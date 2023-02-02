import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .mixins import KeywordsMixin


def get_upload_path(instance, filename):
    return f"{instance.type}/{instance.content_type_id}/{instance.object_id}/{filename}".lower()


class File(KeywordsMixin, models.Model):
    PUBLIC = "public"
    PRIVATE = "private"
    TYPE_CHOICES = (
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="files")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    file = models.FileField(upload_to=get_upload_path)
    position = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hipeac_rel_file"
        indexes = [models.Index(fields=["file"])]
        ordering = ("content_type", "object_id", "position")

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def files_viewable_by_user(self, user) -> bool:
        return user.is_authenticated
