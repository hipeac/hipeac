from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from hipeac.functions import send_task
from ..mixins import KeywordsMixin


class Membership(KeywordsMixin, models.Model):
    """
    HiPEAC Membership.
    """

    AFFILIATED_PHD = "affiliated_phd"
    AFFILIATED_MEMBER = "affiliated_member"
    ASSOCIATED_MEMBER = "associated_member"
    MEMBER = "member"
    MEMBERSHIP_TYPE_CHOICES = (
        (MEMBER, "Member"),
        (ASSOCIATED_MEMBER, "Associated member"),
        (AFFILIATED_MEMBER, "Affiliated member"),
        (AFFILIATED_PHD, "Affiliated PhD"),
    )

    user = models.ForeignKey(get_user_model(), related_name="memberships", on_delete=models.CASCADE)
    type = models.CharField(db_index=True, max_length=20, null=True, blank=True, choices=MEMBERSHIP_TYPE_CHOICES)
    date = models.DateField()
    revocation_date = models.DateField(null=True, blank=True)
    advisor = models.ForeignKey(
        get_user_model(),
        related_name="affiliates",
        null=True,
        blank=True,
        limit_choices_to={"memberships__type": "member"},
        on_delete=models.SET_NULL,
    )
    comments = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "hipeac_membership"
        ordering = ("date",)

    @property
    def tags(self) -> str:
        return self.keywords


@receiver(post_save, sender=Membership)
def membership_post_save(sender, instance, created, *args, **kwargs):
    send_task("hipeac.tasks.db.refresh_member_view")
