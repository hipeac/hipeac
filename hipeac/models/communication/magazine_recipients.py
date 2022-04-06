from django.contrib.auth import get_user_model
from django.db import models
from django_countries.fields import CountryField


class MagazineRecipient(models.Model):
    name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = CountryField(blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    send_electronic = models.BooleanField(default=True)

    user = models.OneToOneField(
        get_user_model(), related_name="address", on_delete=models.CASCADE, blank=True, null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hipeac_comm_magazine_recipient"

    def __str__(self) -> str:
        return self.name
