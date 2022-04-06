from django.contrib.auth import get_user_model
from django.db import models
from django_countries.fields import CountryField


class TopScientist(models.Model):
    """
    European Top Computer Science Scientist based on Reaserch.com rankings:
    https://research.com/scientists-rankings/computer-science
    The list get periodically updated and matched with existing users.
    """

    user = models.OneToOneField(
        get_user_model(), related_name="top_scientist", on_delete=models.SET_NULL, null=True, blank=True
    )
    ranking = models.PositiveSmallIntegerField()
    country = CountryField()
    country_ranking = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=255)
    affiliation = models.CharField(max_length=255, blank=True, null=True)
    h_index = models.PositiveSmallIntegerField(blank=True, null=True)
    citations = models.PositiveIntegerField(blank=True, null=True)
    publications = models.PositiveIntegerField(blank=True, null=True)
    url = models.URLField()

    class Meta:
        db_table = "hipeac_top_scientist"
        ordering = ("ranking",)

    def __str__(self):
        return f"{self.name} (#{self.ranking})"
