from celery.execute import send_task
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField

from hipeac.functions import get_images_path
from hipeac.models import Link
from ..mixins import ImagesMixin, LinkMixin


EC_MEETING = 'ec_meeting'


def validate_event_dates(event):
    if event.end_date < event.start_date:
        raise ValidationError('End date cannot be earlier than start date.')
    if event.start_date <= event.registration_start_date:
        raise ValidationError('Registrations should open before the conference starts.')
    if event.registration_deadline.date() < event.registration_start_date:
        raise ValidationError('Registrations cannot end before they start...')

    if event.registration_early_deadline:
        if event.registration_early_deadline.date() < event.registration_start_date:
            raise ValidationError('Early deadline cannot be earlier than registration start date.')
        if event.registration_early_deadline > event.registration_deadline:
            raise ValidationError('Early deadline cannot be later than registration deadline.')


class EventManager(models.Manager):
    def public(self):
        return super().get_queryset().exclude(type=EC_MEETING)


class Event(ImagesMixin, LinkMixin, models.Model):
    ACACES = 'acaces'
    CONFERENCE = 'conference'
    CSW = 'csw'
    EC_MEETING = EC_MEETING
    TYPE_CHOICES = (
        (CSW, 'CSW'),
        (CONFERENCE, 'Conference'),
        (ACACES, 'ACACES Summer School'),
        (EC_MEETING, 'EC Consultation Meeting'),
    )

    start_date = models.DateField()
    end_date = models.DateField()
    registration_start_date = models.DateField()
    registration_early_deadline = models.DateTimeField(null=True, blank=True)
    registration_deadline = models.DateTimeField()

    type = models.CharField(max_length=16, editable=False, choices=TYPE_CHOICES)
    coordinating_institution = models.ForeignKey('hipeac.Institution', null=True, blank=True, on_delete=models.SET_NULL,
                                                 related_name='coordinated_events')
    city = models.CharField(max_length=100)
    country = CountryField(db_index=True)
    hashtag = models.CharField(max_length=32, null=True, blank=True)
    slug = models.CharField(max_length=100, editable=False)
    redirect_url = models.URLField(null=True, editable=False)
    image = models.FileField('Banner', upload_to=get_images_path, null=True, blank=True, help_text='4:1 format')
    travel_info = models.TextField(null=True, blank=True)

    registrations_count = models.PositiveIntegerField(default=0)

    links = GenericRelation('hipeac.Link')

    objects = EventManager()

    def clean(self) -> None:
        validate_event_dates(self)
        if self.hashtag:
            self.hashtag = self.hashtag[1:] if self.hashtag.startswith('#') else self.hashtag

    def save(self, *args, **kwargs):
        self.slug = slugify(self.city)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date']

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        if self.type == self.EC_MEETING:
            return reverse(self.type, args=[self.id])
        return reverse(self.type, args=[self.start_date.year, self.slug])

    @property
    def google_maps_url(self) -> str:
        self.get_link(Link.GOOGLE_MAPS)

    @property
    def google_photos_url(self) -> str:
        self.get_link(Link.GOOGLE_PHOTOS)

    def is_active(self) -> bool:
        return self.start_date <= timezone.now().date() <= self.end_date

    def is_open_for_registration(self) -> bool:
        now = timezone.now()
        return self.registration_start_date <= now.date() and now <= self.registration_deadline

    @property
    def name(self) -> str:
        if self.type == self.ACACES:
            return f'ACACES {self.start_date.year}, {self.city}'
        elif self.type == self.CONFERENCE:
            return f'HiPEAC {self.start_date.year}, {self.city}'
        elif self.type == self.CSW:
            season = 'Spring' if (self.start_date.month < 8) else 'Autumn'
            return f'CSW {season} {self.start_date.year}, {self.city}'

        return f'{self.city}, {self.start_date.strftime("%B %Y")}'


@receiver(post_save, sender=Event)
def event_post_save(sender, instance, created, *args, **kwargs):
    if instance.image_has_changed():
        send_task('hipeac.tasks.imaging.generate_banner_variants', (instance.image.path,))
