from django.db import models
from django_countries.fields import CountryField


class PhdMobility(models.Model):
    """
    A HiPEAC PhD mobility case.
    """
    INTERNSHIP = 'internship'
    COLLABORATION = 'collaboration'
    TYPE_CHOICES = (
        (INTERNSHIP, 'Internship'),
        (COLLABORATION, 'Collaboration Grant'),
    )

    type = models.CharField(max_length=16, default=INTERNSHIP, choices=TYPE_CHOICES)
    student = models.ForeignKey('auth.User', related_name='phd_mobilities', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    summary = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    institution = models.ForeignKey('hipeac.Institution', related_name='phd_mobilities', null=True,
                                    on_delete=models.SET_NULL)
    location = models.CharField(max_length=250, help_text='Where will the PhD student be working?')
    country = CountryField()

    job = models.ForeignKey('hipeac.Job', related_name='phd_mobilities', null=True, on_delete=models.SET_NULL)
    internship = models.ForeignKey('hipeac.Internship', related_name='phd_mobilities', null=True,
                                   on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PhD mobility'
        verbose_name_plural = 'PhD mobilities'

    def __str__(self):
        return f'{self.title} ({self.student})'
