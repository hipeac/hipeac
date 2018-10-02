import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import reverse


class Coupon(models.Model):
    """
    Coupons are used to pay or reduce registration fees.
    """
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    event = models.ForeignKey('hipeac.Event', on_delete=models.CASCADE, related_name='coupons')
    value = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
    notes = models.CharField(max_length=190, null=True, blank=True)

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['code']),
        ]
        ordering = ['event', 'id']

    def __str__(self) -> str:
        return f'{self.code} ({self.value})'


class RegistrationManager(models.Manager):
    def with_profiles(self):
        return super().get_queryset().select_related('user__profile').order_by('user__first_name', 'user__last_name')


class Registration(models.Model):
    """
    A conference registration for a User.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    event = models.ForeignKey('hipeac.Event', on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL, related_name='registrations')
    # days = models.ManyToManyField('hipeac.Day', related_name='registrations')
    sessions = models.ManyToManyField('hipeac.Session', related_name='registrations')

    fee = models.ForeignKey('hipeac.Fee', null=True, on_delete=models.SET_NULL, related_name='registrations')
    saldo = models.IntegerField(default=0)
    coupon = models.OneToOneField(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    invoice_requested = models.BooleanField(default=False)
    invoice_sent = models.BooleanField(default=False)

    visa_requested = models.BooleanField(default=False)
    visa_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = RegistrationManager()

    class Meta:
        indexes = [
            models.Index(fields=['uuid']),
        ]
        ordering = ('-created_at',)
        unique_together = ('event', 'user')

    def __str__(self) -> str:
        return f'{self.uuid} ({self.user})'

    def can_be_managed_by(self, user) -> bool:
        return self.user_id == user.id

    def get_absolute_url(self) -> str:
        return reverse('registration', args=[self.uuid])

    @property
    def is_paid(self) -> bool:
        return self.saldo >= 0


@receiver(post_save, sender=Registration)
def registration_post_save(sender, instance, created, *args, **kwargs):
    if created:
        event = instance.event
        event.registrations_count = event.registrations.count()
        event.save()

        """
        msg = EmailMessage(
            f'[{instance.event.hashtag.upper()}] Your registration for {instance.event}',
            get_template('hipeac/emails/registration.txt').render({
                'registration': instance
            }),
            to=[instance.user.profile.to_email],
            from_email=f'{instance.event.hashtag.upper()} <{settings.HIPEAC_REGISTRATIONS_EMAIL}>'
        )
        msg.send()
        """

        # if instance.visa_requested:
        #    visa_reminder_email(Registration.objects.filter(pk=instance.id))


@receiver(m2m_changed, sender=Registration.sessions.through)
def registration_sessions_changed(sender, instance, **kwargs) -> None:
    if kwargs.get('action') == 'post_add':
        logs = list(RegistrationLog.objects.filter(registration_id=instance.id).values_list('session_id', flat=True))
        new_logs = []

        for session in instance.sessions.exclude(id__in=logs).only('id'):
            new_logs.append(RegistrationLog(registration_id=instance.id, session_id=session.id))

        if new_logs:
            RegistrationLog.objects.bulk_create(new_logs)


class RegistrationLog(models.Model):
    """
    In some occasions, it can be interesting to know when somebody first registered for an activity.
    If later an activity is unselected, this log shows when the initial registration was made.
    """
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='logs')
    session = models.ForeignKey('hipeac.Session', on_delete=models.CASCADE, related_name='logs')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('registration', 'session')
