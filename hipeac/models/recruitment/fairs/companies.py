from django.contrib.auth import get_user_model
from django.db import models


class JobFairCompany(models.Model):
    """
    A company that is participating in a job fair.
    This extends the standard rel_insitutions and is used primarily for managing access to applicant data.
    """

    fair = models.ForeignKey("hipeac.JobFair", related_name="companies", on_delete=models.CASCADE)
    institution = models.ForeignKey("hipeac.Institution", related_name="job_fairs", on_delete=models.CASCADE)
    users = models.ManyToManyField(get_user_model(), related_name="job_fairs", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hipeac_job_fair_company"
        unique_together = ("fair", "institution")
        verbose_name_plural = "Job fair companies"

    def __str__(self) -> str:
        return str(self.institution.name)

    def can_be_managed_by(self, user) -> bool:
        return self.users.filter(id=user.id).exists()
