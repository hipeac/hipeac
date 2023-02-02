from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django_countries.fields import CountryField

from hipeac.models.mixins import EditorMixin, InstitutionsMixin, LinksMixin, PermissionsMixin


class JobFair(EditorMixin, InstitutionsMixin, LinksMixin, PermissionsMixin, models.Model):
    """
    A HiPEAC Job fair for an event (external, like DATE, or internal).
    """

    code = models.CharField(unique=True, max_length=16)
    is_virtual = models.BooleanField(default=False, verbose_name="virtual", help_text="Is it a virtual fair?")
    name = models.CharField(max_length=250)
    presentation = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    city = models.CharField(max_length=100, null=True, blank=True, help_text="Empty for virtual events.")
    country = CountryField(db_index=True, null=True, blank=True, help_text="Empty for virtual events.")

    event = models.OneToOneField(
        "hipeac.Event", related_name="job_fair", null=True, blank=True, on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hipeac_job_fair"
        ordering = ("-start_date",)
        verbose_name = "Job fair"

    def __str__(self) -> str:
        return self.name

    def can_be_managed_by(self, user) -> bool:
        return self._can_be_managed_by(user)

    def get_absolute_url(self) -> str:
        return reverse("jobfair", args=[self.code])

    def is_open_for_registration(self) -> bool:
        return timezone.now().date() < self.end_date

    @cached_property
    def jobs(self):
        return self.get_jobs()

    def get_jobs(self, company_ids: list = None):
        from hipeac.models import Job

        if company_ids is None:
            company_ids = [institution.id for institution in self.institutions]

        return (
            Job.objects.active()
            .filter(
                (Q(institution__in=company_ids) | Q(institution__parent_id__in=company_ids)),
            )
            .prefetch_related("institution")
            .order_by("institution__name", "deadline")
        )
