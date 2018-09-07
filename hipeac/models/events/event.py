from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django_countries.fields import CountryField


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


class Event(models.Model):
    ACACES = 'acaces'
    CONFERENCE = 'conference'
    CSW = 'csw'
    EC_MEETING = 'ec_meeting'
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
    slug = models.CharField(max_length=100, editable=False)

    def clean(self) -> None:
        validate_event_dates(self)

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
