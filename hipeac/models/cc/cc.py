from django.db import models


class CC(models.Model):
    """A Computing Continuum participant."""

    project = models.OneToOneField("hipeac.Project", on_delete=models.CASCADE, related_name="cc")
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "cc_projects"
        ordering = ("project__name",)
