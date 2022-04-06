from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField

from ..mixins import ApplicationAreasMixin, TopicsMixin


class PhdMobility(ApplicationAreasMixin, TopicsMixin, models.Model):
    """
    A HiPEAC PhD mobility case.
    """

    INTERNSHIP = "internship"
    COLLABORATION = "collaboration"
    TYPE_CHOICES = (
        (INTERNSHIP, "Internship"),
        (COLLABORATION, "Collaboration"),
    )

    type = models.CharField(max_length=16, default=INTERNSHIP, choices=TYPE_CHOICES)
    student = models.ForeignKey("auth.User", related_name="phd_mobilities", on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    summary = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    institution = models.ForeignKey(
        "hipeac.Institution", related_name="phd_mobilities", null=True, on_delete=models.SET_NULL
    )
    location = models.CharField(max_length=250, help_text="Where will the PhD student be working?")
    country = CountryField()

    job = models.ForeignKey(
        "hipeac.Job", related_name="phd_mobilities", null=True, blank=True, on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hipeac_phd_mobility"
        ordering = ("-start_date",)
        verbose_name = "PhD mobility"
        verbose_name_plural = "PhD mobilities"

    def __str__(self):
        return f"{self.title} ({self.start_date.year})"

    def get_absolute_url(self) -> str:
        return reverse("user", args=[self.student.username])
