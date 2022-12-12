import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django_countries.fields import CountryField
from textwrap import dedent
from typing import List

from hipeac.functions import get_images_path, send_task
from ..links import Link
from ..mixins import LinksMixin, ImageMixin, VideosMixin


def validate_date(date, event) -> None:
    if date < event.start_date or date > event.end_date:
        raise ValidationError("Date is not valid for this event.")


def validate_event_dates(event):
    if event.end_date < event.start_date:
        raise ValidationError("End date cannot be earlier than start date.")
    if event.start_date <= event.registration_start_date:
        raise ValidationError("Registrations should open before the conference starts.")
    if event.registration_deadline.date() < event.registration_start_date:
        raise ValidationError("Registrations cannot end before they start...")

    if event.registration_early_deadline:
        if event.registration_early_deadline.date() < event.registration_start_date:
            raise ValidationError("Early deadline cannot be earlier than registration start date.")
        if event.registration_early_deadline > event.registration_deadline:
            raise ValidationError("Early deadline cannot be later than registration deadline.")


class EventQuerySet(models.QuerySet):
    def registering(self):
        now = timezone.now()
        return self.filter(registration_start_date__lte=now.date(), registration_deadline__gt=now)

    def upcoming(self):
        return self.filter(end_date__gte=timezone.now().date()).order_by("end_date").first()


class Event(ImageMixin, LinksMixin, VideosMixin, models.Model):
    ACACES = "acaces"
    CONFERENCE = "conference"
    CSW = "csw"

    type = models.CharField(max_length=16, editable=False)
    is_virtual = models.BooleanField(default=False, verbose_name="virtual", help_text="Is it a virtual event?")
    city = models.CharField(max_length=100, null=True, blank=True, help_text="Empty for virtual events.")
    country = CountryField(db_index=True, null=True, blank=True, help_text="Empty for virtual events.")
    slug = models.SlugField(max_length=32, editable=False)

    start_date = models.DateField()
    end_date = models.DateField()
    registration_start_date = models.DateField()
    registration_early_deadline = models.DateTimeField(null=True, blank=True)
    registration_deadline = models.DateTimeField()
    is_ready = models.BooleanField(default=False, help_text="Is programme ready?")
    registrations_count = models.PositiveIntegerField(default=0)

    hashtag = models.CharField(max_length=32, null=True, blank=True)
    presentation = models.TextField(null=True, blank=True)
    logistics = models.TextField(null=True, blank=True)

    wbs_element = models.CharField(max_length=32, null=True, blank=True, verbose_name="WBS element")
    ingenico_salt = models.CharField(max_length=200, null=True, blank=True)
    allows_invoices = models.BooleanField(default=True, help_text="If unchecked users cannot request an invoice.")
    payments_activation = models.DateField(null=True, blank=True)

    coordinating_institution = models.ForeignKey(
        "hipeac.Institution",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_coordinated",
    )
    venue = models.ForeignKey("hipeac.Venue", related_name="events", on_delete=models.SET_NULL, null=True, blank=True)
    image = models.FileField("Banner", upload_to=get_images_path, null=True, blank=True, help_text="4:1 format")

    objects = EventQuerySet.as_manager()

    class Meta:
        ordering = ("-start_date",)

    def clean(self) -> None:
        validate_event_dates(self)
        if self.hashtag:
            self.hashtag = self.hashtag[1:] if self.hashtag.startswith("#") else self.hashtag

    def save(self, *args, **kwargs):
        if self.is_virtual:
            self.city = None
            self.country = None
        self.slug = "virtual" if self.is_virtual else slugify(self.city or "-")
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def can_be_viewed_by(self, user) -> bool:
        return user.id in self.committees.values_list("rel_users__user_id", flat=True)

    def get_absolute_url(self) -> str:
        if self.type == self.ACACES:
            return reverse("acaces", args=[self.year])
        if self.type == self.CONFERENCE:
            return reverse("conference", args=[self.year, self.slug])
        if self.type == self.CSW:
            return reverse("csw", args=[self.year, self.slug])
        return "#"

    def allows_payments(self) -> bool:
        if self.ingenico_salt is None:
            return False
        if self.payments_activation:
            return self.payments_activation <= timezone.now().date()
        return True

    def is_active(self) -> bool:
        return self.start_date <= timezone.now().date() <= self.end_date

    def is_early(self) -> bool:
        if not self.registration_early_deadline:
            return False
        return timezone.now() <= self.registration_early_deadline

    def is_finished(self) -> bool:
        return self.end_date < timezone.now().date()

    def is_open_for_registration(self) -> bool:
        now = timezone.now()
        return self.registration_start_date <= now.date() and now <= self.registration_deadline

    def dates(self) -> List[datetime.date]:
        dates_range = range(0, self.end_date.toordinal() - self.start_date.toordinal() + 1)
        return [self.start_date + datetime.timedelta(days=x) for x in dates_range]

    @property
    def name(self) -> str:
        try:
            return {
                self.ACACES: f"ACACES {self.year}",
                self.CONFERENCE: f"HiPEAC {self.year}",
                self.CSW: f"CSW {self.season} {self.year}",
            }[self.type]
        except KeyError:
            return f"{self.type} {self.year}"

    @cached_property
    def extra_venues(self):
        from .venues import Venue

        venue_id = [self.venue_id] if self.venue_id else []
        ids = self.sessions.exclude(room__venue_id__in=venue_id).values_list("room__venue_id", flat=True).distinct()
        return Venue.objects.prefetch_related("rooms").filter(id__in=ids)

    @property
    def google_maps_url(self) -> str:
        return self.get_link(Link.GOOGLE_MAPS)

    @property
    def google_photos_url(self) -> str:
        return self.get_link(Link.GOOGLE_PHOTOS)

    @property
    def season(self) -> str:
        return "Spring" if (self.start_date.month < 8) else "Autumn"

    @property
    def signature(self) -> str:
        return dedent(
            """
            The coordinator,\u0020\u0020
            **Koen De Bosschere**\u0020\u0020
            Ghent University\u0020\u0020
            Gent, Belgium\u0020\u0020
            <koen.debosschere@ugent.be>
        """
        )

    @property
    def year(self) -> int:
        return self.start_date.year


@receiver(post_save, sender=Event)
def event_post_save(sender, instance, created, *args, **kwargs):
    if instance.image_has_changed():
        send_task("hipeac.tasks.imaging.generate_banner_variants", (instance.image.path,))
