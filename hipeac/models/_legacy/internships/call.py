import datetime

from django.db import models
from django.utils import timezone


class InternshipCall(models.Model):
    """
    A call for PhD Internships.
    Each call can have a different manager and reviewers.
    """
    start_date = models.DateField()
    internship_deadline = models.DateField('Deadline for submitting internships')
    application_deadline = models.DateField('Deadline for submitting applications')
    end_date = models.DateField()
    manager = models.ForeignKey('auth.User', related_name='managed_internships', null=True, on_delete=models.SET_NULL,
                                limit_choices_to={'membership_tags__contains': 'member'})
    created_at = models.DateTimeField(auto_now_add=True)
    is_frozen = models.BooleanField(default=False,
                                    help_text='Check this box to avoid further editing on applications or reviews.')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.start_date.strftime('%Y %b')

    def year(self):
        return self.start_date.year

    def is_active(self):
        return self.start_date <= timezone.now().date() <= self.final_date()
    is_active.boolean = True
    is_active.short_description = 'Active'

    def is_open_for_internship(self):
        return self.start_date <= timezone.now().date() <= self.internship_deadline

    def is_open_for_application(self):
        return self.internship_deadline < timezone.now().date() <= self.application_deadline

    def is_open_for_evaluation(self):
        return self.application_deadline < timezone.now().date() <= self.end_date

    def final_date(self):
        return self.end_date + datetime.timedelta(days=7)
