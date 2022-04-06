import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Image(models.Model):
    """
    Application images.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="images")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    image = models.FileField("Image", upload_to="public/images", null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hipeac_rel_image"
        ordering = ("content_type", "object_id", "position")

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.image.path):
            os.remove(self.image.path)
        super().delete(*args, **kwargs)
