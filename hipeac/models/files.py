import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


def get_upload_path(instance, filename):
    return f"{instance.type}/{instance.content_type_id}/{instance.object_id}/{filename}".lower()


class File(models.Model):
    """
    Model related files.
    """

    PUBLIC = "public"
    PRIVATE = "private"
    TYPE_CHOICES = (
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
    )

    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    file = models.FileField(upload_to=get_upload_path)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="files")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        indexes = [
            models.Index(fields=["file"]),
        ]
        ordering = ["content_type", "object_id"]

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)
