import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django_countries.fields import CountryField
from typing import List

from hipeac.functions import get_images_path, send_task
from hipeac.models import Link
from ..mixins import ImagesMixin, LinkMixin


EC_MEETING = "ec_meeting"


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
    def public(self):
        return self.exclude(type=EC_MEETING)

    def registering(self):
        now = timezone.now()
        return self.filter(registration_start_date__lte=now.date(), registration_deadline__gt=now)

    def upcoming(self):
        return self.public().filter(end_date__gte=timezone.now().date()).order_by("end_date").first()


class Event(ImagesMixin, LinkMixin, models.Model):
    ACACES = "acaces"
    CONFERENCE = "conference"
    CSW = "csw"
    EC_MEETING = EC_MEETING
    TYPE_CHOICES = (
        (CSW, "CSW"),
        (CONFERENCE, "Conference"),
        (ACACES, "ACACES Summer School"),
        (EC_MEETING, "EC Consultation Meeting"),
    )

    start_date = models.DateField()
    end_date = models.DateField()
    registration_start_date = models.DateField()
    registration_early_deadline = models.DateTimeField(null=True, blank=True)
    registration_deadline = models.DateTimeField()
    is_ready = models.BooleanField(default=False, help_text="Is programme ready?")

    type = models.CharField(max_length=16, editable=False, choices=TYPE_CHOICES)
    coordinating_institution = models.ForeignKey(
        "hipeac.Institution", null=True, blank=True, on_delete=models.SET_NULL, related_name="coordinated_events"
    )
    presentation = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100)
    country = CountryField(db_index=True)
    hashtag = models.CharField(max_length=32, null=True, blank=True)
    slug = models.CharField(max_length=100, editable=False)
    redirect_url = models.URLField(null=True, editable=False)
    image = models.FileField("Banner", upload_to=get_images_path, null=True, blank=True, help_text="4:1 format")
    travel_info = models.TextField(null=True, blank=True)

    registrations_count = models.PositiveIntegerField(default=0)

    links = GenericRelation("hipeac.Link")
    venues = models.ManyToManyField("hipeac.Venue", blank=True, related_name="events")

    objects = EventQuerySet.as_manager()

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

    def can_be_viewed_by(self, user) -> bool:
        return user.id in self.committee_member_ids

    @cached_property
    def committee_member_ids(self):
        return get_user_model().objects.filter(committees__event_id=self.id).only("id").values_list("id", flat=True)

    def dates(self) -> List[datetime.date]:
        dates_range = range(0, self.end_date.toordinal() - self.start_date.toordinal() + 1)
        return [self.start_date + datetime.timedelta(days=x) for x in dates_range]

    def get_absolute_url(self) -> str:
        if self.type == self.EC_MEETING:
            return reverse(self.type, args=[self.id])
        return reverse(self.type, args=[self.start_date.year, self.slug])

    @property
    def google_maps_url(self) -> str:
        return self.get_link(Link.GOOGLE_MAPS)

    @property
    def google_photos_url(self) -> str:
        return self.get_link(Link.GOOGLE_PHOTOS)

    def is_early(self) -> bool:
        if not self.registration_early_deadline:
            return False
        return timezone.now() <= self.registration_early_deadline

    def is_active(self) -> bool:
        return self.start_date <= timezone.now().date() <= self.end_date

    def is_finished(self) -> bool:
        return self.end_date < timezone.now().date()

    def is_open_for_registration(self) -> bool:
        now = timezone.now()
        return self.registration_start_date <= now.date() and now <= self.registration_deadline

    @property
    def name(self) -> str:
        if self.type == self.ACACES:
            return f"ACACES {self.start_date.year}, {self.city}"
        elif self.type == self.CONFERENCE:
            return f"HiPEAC {self.start_date.year}, {self.city}"
        elif self.type == self.CSW:
            season = "Spring" if (self.start_date.month < 8) else "Autumn"
            return f"CSW {season} {self.start_date.year}, {self.city}"

        return f'{self.city}, {self.start_date.strftime("%B %Y")}'

    @property
    def fees_dict(self):
        if not hasattr(self, "_fees"):
            self._fees = dict(self.fees.values_list("type", "value"))
        return self._fees

    @cached_property
    def jobs(self):
        from hipeac.models import Job

        sponsors = self.sponsors.values_list("institution_id", "project_id")
        if sponsors:
            a, b = map(list, zip(*sponsors))
            institution_ids, project_ids = list(filter(None, a)), list(filter(None, b))
            queryset = (
                Job.objects.active()
                .filter(
                    (
                        Q(institution__in=institution_ids)
                        | Q(project__in=project_ids)
                        | Q(institution__parent_id__in=institution_ids)
                    ),
                )
                .order_by("institution__name", "deadline")
            )
        else:
            queryset = Job.objects.none()
        return queryset

    @property
    def year(self) -> int:
        return self.start_date.year


@receiver(post_save, sender=Event)
def event_post_save(sender, instance, created, *args, **kwargs):
    if instance.image_has_changed():
        send_task("hipeac.tasks.imaging.generate_banner_variants", (instance.image.path,))
