import uuid

from django.core.validators import MinValueValidator
from django.db import models


class Coupon(models.Model):
    event = models.ForeignKey("hipeac.Event", related_name="coupons", on_delete=models.CASCADE)
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    value = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
    notes = models.CharField(max_length=190, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hipeac_event_coupon"
        indexes = [models.Index(fields=["code"])]
        ordering = ("event", "id")

    def __str__(self) -> str:
        return f"{self.code} ({self.value})"
