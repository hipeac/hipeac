from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Permission(models.Model):
    """
    ACL permissions.
    Higher permission levels inherit lower permissions, simplifying queries.
    """

    OWNER = 9
    ADMIN = 5
    GUEST = 1
    LEVEL_CHOICES = (
        (OWNER, "Owner"),
        (ADMIN, "Administrator"),
        (GUEST, "Guest"),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="perms")
    object_id = models.IntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(get_user_model(), blank=True, related_name="perms", on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(db_index=True, choices=LEVEL_CHOICES)

    class Meta:
        db_table = "hipeac_rel_permission"
        unique_together = ["content_type", "object_id", "user"]

    def __str__(self) -> str:
        return f"{self.user} ({self.get_level_display()})"
