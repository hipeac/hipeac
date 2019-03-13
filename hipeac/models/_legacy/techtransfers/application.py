from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class TechTransferApplication(models.Model):
    """
    A technology transfer example eligible for a Technology Transfer Award.
    """
    STATUS_CHOICES = (
        ('OK', 'Awarded'),
        ('NO', 'Rejected'),
        ('UN', 'Pending'),
    )

    call = models.ForeignKey('hipeac.TechTransferCall', related_name='applications', on_delete=models.CASCADE)
    applicant = models.ForeignKey('auth.User', related_name='technology_transfer_award_applications', null=True,
                                  on_delete=models.SET_NULL)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='UN')
    title = models.CharField(max_length=250)
    description = models.TextField('Description of the technology being transferred')
    partners_description = models.TextField('Description of the academic partners and the company involved')
    value = models.TextField('Estimate of the value of the agreement')
    team = models.ManyToManyField('auth.User', blank=True, related_name='technology_transfer_awards',
                                  help_text='Team members that will receive an award (certificate).')

    team_string = models.TextField('Team (text)', null=True, blank=True)
    awardee = models.OneToOneField('auth.User', null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='technology_transfer_financial_award')
    awarded_summary = models.TextField('Summary', null=True, help_text='Summary, if awarded, to show online.')
    awarded_from = models.ForeignKey('hipeac.Institution', related_name='ttawards_from', null=True, blank=True,
                                     on_delete=models.SET_NULL)
    awarded_to = models.ForeignKey('hipeac.Institution', related_name='ttawards_to', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def clean(self):
        """
        Validates the model before saving.
        """
        if self.call.is_frozen:
            raise ValidationError('Call is "frozen": no more changes are allowed in applications.')
        if self.awardee and self.status != 'OK':
            raise ValidationError('Please check that the `status` has been updated.')

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('research:techtransfer_detail', args=[self.id])

    def is_awarded(self) -> bool:
        return self.status == 'OK'
