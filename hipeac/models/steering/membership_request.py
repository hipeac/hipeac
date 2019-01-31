from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


class MembershipRequest(models.Model):
    """
    HiPEAC Membership request.
    """
    MEMBERSHIP_TYPE_CHOICES = (
        ('member', 'Member'),
        ('member,non-eu', 'Associated member'),
    )

    user = models.ForeignKey(get_user_model(), related_name='membership_requests', null=True, blank=True,
                             on_delete=models.SET_NULL)
    name = models.CharField(max_length=250)
    affiliation = models.CharField(null=True, blank=True, max_length=250)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    motivation = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    membership_type = models.CharField(db_index=True, max_length=16, null=True, blank=True,
                                       choices=MEMBERSHIP_TYPE_CHOICES)
    accepted = models.BooleanField(default=None, null=True)
    decision_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        db_table = 'hipeac_steering_membership_request'
        ordering = ('-created_at',)

    def clean(self):
        """
        Validates the model before saving.
        """
        if self.accepted is None:
            self.decision_date = None
        else:
            if self.decision_date is None:
                raise ValidationError('A decision date is required for "Accepted" or "Rejected" membership requests.')

        if not self.email and not self.user:
            raise ValidationError('Please set a related User if no email is given.')

    @property
    def clean_email(self) -> str:
        return self.user.email if self.user else self.email
