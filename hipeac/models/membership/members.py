from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField
from typing import Optional

from .membership import Membership
from ..institutions import Institution
from ..mixins import KeywordsMixin


class Member(KeywordsMixin, models.Model):
    username = models.CharField(max_length=255, unique=True)
    user = models.OneToOneField(get_user_model(), related_name="member", primary_key=True, on_delete=models.DO_NOTHING)
    email = models.EmailField()
    name = models.CharField(max_length=255)
    country = CountryField()
    date = models.DateField()
    type = models.CharField(max_length=20, choices=Membership.MEMBERSHIP_TYPE_CHOICES)
    gender = models.CharField(max_length=255)
    advisor = models.ForeignKey(get_user_model(), related_name="_affiliates", on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, related_name="_i1", on_delete=models.SET_NULL, null=True)
    second_institution = models.ForeignKey(Institution, related_name="_i2", on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = "hipeac_membership_member"
        managed = False

    def get_absolute_url(self) -> Optional[str]:
        return reverse("user", args=[self.username]) if self.is_public else None

    def affiliates(self):
        return [aff.user for aff in self.user._affiliates.all()]
