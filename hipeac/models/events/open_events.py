import datetime
import uuid

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from django_countries.fields import CountryField
from typing import List

from hipeac.functions import get_images_path
from .events import validate_event_dates
from ..mixins import ImagesMixin, LinkMixin


class OpenEventQuerySet(models.QuerySet):
    def upcoming(self):
        return self.filter(end_date__gte=timezone.now().date()).order_by("end_date").first()


class OpenEvent(ImagesMixin, LinkMixin, models.Model):
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    secret = models.UUIDField(default=uuid.uuid4, editable=False)

    start_date = models.DateField()
    end_date = models.DateField()
    registration_start_date = models.DateField()
    registration_deadline = models.DateTimeField()

    name = models.CharField(max_length=100)
    presentation = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100)
    country = CountryField(db_index=True)
    hashtag = models.CharField(max_length=32, null=True, blank=True)
    custom_url = models.URLField(null=True, help_text="https://events.hipeac.net/...")
    image = models.FileField("Banner", upload_to=get_images_path, null=True, blank=True, help_text="4:1 format")
    travel_info = models.TextField(null=True, blank=True)

    registrations_count = models.PositiveIntegerField(default=0)

    objects = OpenEventQuerySet.as_manager()

    def clean(self) -> None:
        validate_event_dates(self)
        if self.hashtag:
            self.hashtag = self.hashtag[1:] if self.hashtag.startswith("#") else self.hashtag

    def save(self, *args, **kwargs):
        self.slug = slugify(self.city)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.name

    def dates(self) -> List[datetime.date]:
        dates_range = range(0, self.end_date.toordinal() - self.start_date.toordinal() + 1)
        return [self.start_date + datetime.timedelta(days=x) for x in dates_range]

    def is_active(self) -> bool:
        return self.start_date <= timezone.now().date() <= self.end_date

    def is_finished(self) -> bool:
        return self.end_date < timezone.now().date()

    def is_open_for_registration(self) -> bool:
        now = timezone.now()
        return self.registration_start_date <= now.date() and now <= self.registration_deadline
