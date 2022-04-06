from django.db.models.signals import post_save
from django.dispatch import receiver

from ..registrations import Registration, registration_post_save


class CswRegistration(Registration):
    class Meta:
        db_table = "hipeac_csw_registration"
        verbose_name = "CSW registration"


@receiver(post_save, sender=CswRegistration)
def conference_registration_post_save(sender, instance, created, *args, **kwargs):
    registration_post_save(sender, instance, created, *args, **kwargs)
