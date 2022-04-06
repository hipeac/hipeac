from django.db import models


class AcacesPoster(models.Model):
    registration = models.OneToOneField("hipeac.AcacesRegistration", related_name="poster", on_delete=models.CASCADE)
    title = models.CharField(max_length=250, null=True, blank=True)
    authors = models.CharField(max_length=250, null=True, blank=True)
    abstract = models.FileField(upload_to="public/acaces/abstract", null=True, blank=True)
    poster = models.FileField(upload_to="public/acaces/poster", null=True, blank=True)
    position = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "hipeac_acaces_poster"
        ordering = ("position",)
