from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from hipeac.functions import get_asset_path
from hipeac.models import Institution
# from hipeac.apps.core.models import Hipeac


class Call(models.Model):
    """
    A call for Collaboration Grants.
    Each call can have a different manager and reviewers.
    """
    STATUS_ASSIGNING = 'ASSIGN'
    STATUS_REVIEWING = 'REVIEW'
    STATUS_CLOSED = 'CLOSED'
    STATUS_CHOICES = (
        (STATUS_ASSIGNING, 'Assigning reviewers'),
        (STATUS_REVIEWING, 'Reviewing'),
        (STATUS_CLOSED, 'Closed'),
    )
    start_date = models.DateField()
    end_date = models.DateField()
    manager = models.ForeignKey(get_user_model(), null=True, related_name='managed_collaboration_calls',
                                on_delete=models.SET_NULL)
    reviewers = models.ManyToManyField(get_user_model(), related_name='reviewed_collaboration_calls',
                                       limit_choices_to={'membership_type__isnull': False})
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default=STATUS_ASSIGNING,
                              help_text='Once a Call is "Closed" no further editing is posible on applications or '
                                        'reviews.')

    class Meta(object):
        ordering = ('-start_date',)

    def __unicode__(self):
        return self.start_date.strftime('%Y %b')

    def get_management_url(self):
        return reverse('collaborations:application_list', args=(str(self.id),))

    def year(self):
        return self.start_date.year

    def is_active(self):
        return self.start_date <= timezone.now().date() <= self.end_date
    is_active.boolean = True
    is_active.short_description = 'Active'

    def has_ended(self):
        return timezone.now().date() > self.end_date
    has_ended.boolean = True
    has_ended.short_description = 'Ended'

    def hipeac(self):
        return None
        # return Hipeac.objects.get(start_date__lte=self.start_date, end_date__gte=self.end_date)

    def is_editable_by_user(self, user):
        """
        Call can be managed (in some way) by manager or reviewers.
        """
        if self.status == self.STATUS_REVIEWING:
            return (
                user.is_staff or
                user.id == self.manager.id or
                self.reviewers.filter(id=user.id).exists()
            )
        else:
            return (
                user.is_staff or
                user.id == self.manager.id
            )

    def is_open_for_review(self):
        return self.status == self.STATUS_REVIEWING

    def get_reviewed_application_ids(self, user):
        """Staff and manager can view all applications. Reviewers will get a limited list."""
        if user.is_staff or user.id == self.manager.id:
            return [application.id for application in self.applications.all()]
        else:
            return [application.id for application in self.applications.filter(reviews__reviewer_id=user.id)]

    def user_is_manager(self, user):
        return user.is_staff or user.id == self.manager.id or user.is_steering_member

    def applications_accepted(self):
        return self.applications.filter(status='OK').count()


class Application(models.Model):
    """
    A HiPEAC Collaboration Grant application.
    """
    STATUS_CHOICES = (
        ('OK', 'Accepted'),
        ('NO', 'Rejected'),
        ('UN', 'Pending'),
        ('BY', 'Retired (after being accepted)'),
    )
    call = models.ForeignKey(Call, related_name='applications', on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='UN')
    rank = models.PositiveSmallIntegerField(null=True, blank=True)
    advisor = models.ForeignKey(get_user_model(), related_name='managed_collaborations', null=True, blank=True,
                                on_delete=models.SET_NULL, help_text='Applicant\'s advisor or manager.')
    advisor_string = models.CharField('Advisor (alt)', max_length=250, null=True, blank=True,
                                      help_text='Fill in only if advisor is not in the dropdown list.')
    institution = models.ForeignKey(Institution, related_name='collaborations', null=True, blank=True,
                                    on_delete=models.SET_NULL, help_text='Applicant\'s institution.')
    host = models.ForeignKey(get_user_model(), related_name='hosted_collaborations', null=True, blank=True,
                             on_delete=models.SET_NULL, help_text='Host in the collaborating institution.')
    host_string = models.CharField('Host (alt)', max_length=250, null=True, blank=True,
                                   help_text='Fill in only if host is not in the dropdown list.')
    host_institution = models.ForeignKey(Institution, related_name='hosted_collaborations', null=True, blank=True,
                                         # limit_choices_to={'users__membership_type__isnull': False},
                                         on_delete=models.SET_NULL, help_text='Collaborating institution.')
    host_institution_string = models.CharField('Host institution (alt)', max_length=250, null=True,
                                               blank=True, help_text='Fill in only if host institution is not in the '
                                                                     'dropdown list.')
    title = models.CharField('Title for the collaboration', max_length=250)
    description = models.TextField('Goals of the project')
    statement = models.TextField('About the collaboration',
                                 help_text='Has there been research collaboration between the institutions before?')
    project_file = models.FileField(upload_to=get_asset_path, null=True, blank=True,
                                    help_text='Maximum 1 page!')
    start_date = models.DateField('Estimated start date', null=True, blank=True, help_text='YYYY-MM-DD')
    end_date = models.DateField('Estimated end date', null=True, blank=True, help_text='YYYY-MM-DD')
    notes = models.CharField(max_length=250, null=True, blank=True)
    cv_file = models.FileField('Curriculum Vitae', upload_to=get_asset_path, null=True, blank=True,
                               help_text='This file will only be visible for the application reviewers.')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), null=True, related_name='collaborations',
                                   on_delete=models.SET_NULL)
    summary = models.TextField(null=True, blank=True, help_text='Summary sent by the student to HiPEAC.')

    class Meta(object):
        pass

    def clean(self):
        """
        Validates the model before saving.
        """
        # 1: advisor or host MUST be a HiPEAC member
        if not self.advisor and not self.host:
            raise ValidationError('Advisor OR Host must be a HiPEAC Member.')
        # 2: if no advisor is selected, then advisor_string is necessary
        if not self.advisor and not self.advisor_string:
            raise ValidationError('Please select an advisor, or write down his/her name.')
        # 3: if no host is selected, then host_string is necessary
        if not self.host and not self.host_string:
            raise ValidationError('Please select a host, or write down his/her name.')

    def get_asset_directory(self):
        return 'private/collaborations/application'

    def __unicode__(self):
        return u'%s (%s)' % (self.title, self.call)

    def get_absolute_url(self):
        return reverse('collaborations:application_detail', args=(str(self.id),))

    def get_management_url(self):
        return reverse('collaborations:application_review', args=(str(self.id),))

    def applicant(self):
        return self.created_by

    def advisor_name(self):
        return self.advisor if self.advisor else (u'%s' % self.advisor_string)

    def advisor_is_member(self):
        return False
        # return self.advisor and self.advisor.membership_type in User.MEMBERS + (User.MEMBERSHIP_AFFILIATED,)

    def host_name(self):
        return self.host if self.host else (u'%s' % self.host_string)

    def host_is_member(self):
        return False
        # return self.host and self.host.membership_type in User.MEMBERS + (User.MEMBERSHIP_AFFILIATED,)

    def host_institution_name(self):
        return self.host_institution.name if self.host_institution else (u'%s' % self.host_institution_string)

    def is_granted(self):
        return self.status == 'OK'
    is_granted.boolean = True
    is_granted.short_description = 'Granted'

    def is_editable_by_user(self, user):
        """
        Application can be edited by applicant, advisor or host.
        """
        advisor_id = self.advisor.id if self.advisor else 0
        host_id = self.host.id if self.host else 0

        return (
            user.is_staff or
            user.id == self.created_by.id or
            user.id == advisor_id or
            user.id == host_id
        )

    def is_viewable_by_user(self, user):
        """
        Application can be viewed by applicant, advisor, host, manager or reviewers.
        """
        advisor_id = self.advisor.id if self.advisor else 0
        host_id = self.host.id if self.host else 0

        return (
            user.is_staff or
            user.id == self.created_by.id or
            user.id == advisor_id or
            user.id == host_id or
            user.id == self.call.manager.id or
            self.call.reviewers.filter(id=user.id).exists()
        )

    def reviewers_list(self):
        return [review.reviewer.id for review in self.reviews.all()]


class Review(models.Model):
    """
    A review of a Collaboration Grant application, by each of the reviewers.
    """
    TRACK_RECORD_CHOICES = (
        (0, '---'),
        (4, 'Weak'),
        (8, 'Average'),
        (12, 'Good'),
        (16, 'Very good'),
        (20, 'Excellent'),
    )
    PUBLICATION_RATE_CHOICES = (
        (0, '---'),
        (4, 'Very unlikely'),
        (8, 'Unlikely'),
        (12, 'Possibly'),
        (16, 'Likely'),
        (20, 'Very Likely'),
    )
    DESTINATION_CHOICES = (
        (0, '---'),
        (2, 'Weak'),
        (4, 'Average'),
        (6, 'Good'),
        (8, 'Very good'),
        (10, 'Excellent'),
    )
    MEMBER_STATUS_CHOICES = (
        (0, '---'),
        (1, 'None'),
        (5, 'Both partners'),
        (8, 'Member + partner'),
        (10, 'Both members'),
    )
    LINKAGE_CHOICES = (
        (0, '---'),
        (1, 'Existing Collaboration'),
        (5, 'More or less new collaboration'),
        (10, 'Totally new collaboration'),
    )
    INDEPENDENCE_CHOICES = (
        (0, '---'),
        (1, 'Not independent'),
        (5, 'Rather independent'),
        (10, 'Very independent'),
    )
    application = models.ForeignKey(Application, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(get_user_model(), null=True, related_name='collaboration_reviews',
                                 on_delete=models.SET_NULL)
    track_record = models.PositiveSmallIntegerField(choices=TRACK_RECORD_CHOICES, default=0)
    publication_rate = models.PositiveSmallIntegerField(choices=PUBLICATION_RATE_CHOICES, default=0)
    destination = models.PositiveSmallIntegerField(choices=DESTINATION_CHOICES, default=0)
    member_status = models.PositiveSmallIntegerField(choices=MEMBER_STATUS_CHOICES, default=0)
    linkage = models.PositiveSmallIntegerField(choices=LINKAGE_CHOICES, default=0)
    independence = models.PositiveSmallIntegerField(choices=INDEPENDENCE_CHOICES, default=0)
    sum = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    comments = models.TextField('Private comments for reviewers', null=True, blank=True)
    feedback = models.TextField('Feedback for student', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ('-created_at',)
        unique_together = ('application', 'reviewer',)

    def save(self, *args, **kwargs):
        """
        Updates the `sum` of points.
        """
        total = (self.track_record + self.publication_rate + self.destination + self.member_status + self.linkage +
                 self.independence)
        self.sum = 0 if total == 0 else ((total / 8) * 10)
        super(Review, self).save(*args, **kwargs)


"""
SIGNALS
"""


@receiver(signals.post_save, sender=Application)
def post_save_CollaborationApplication(sender, instance, created, *args, **kwargs):
    if created:
        """
        Send email: CollaborationApplication
        """
        to_emails = (instance.created_by.email,)
        cc_emails = ()
        if instance.advisor:
            cc_emails = cc_emails + (instance.advisor.email,)
            if instance.created_by.advisor and instance.created_by.advisor.email != instance.advisor.email:
                cc_emails = cc_emails + (instance.created_by.advisor.email,)
        if instance.host:
            cc_emails = cc_emails + (instance.host.email,)

        """
        email = Mailer('management@hipeac.net', to_emails, 'Your HiPEAC Collaboration Grant application')
        email.set_context({'application': instance})
        email.set_text_template('collaboration/_emails/application_created.txt')
        email.set_html_template('collaboration/_emails/application_created.html')
        email.set_cc_emails(cc_emails)
        email.send()
        """
