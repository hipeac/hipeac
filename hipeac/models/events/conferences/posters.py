from django.db import models


class ConferencePoster(models.Model):
    registration = models.ForeignKey("hipeac.ConferenceRegistration", related_name="posters", on_delete=models.CASCADE)
    session = models.ForeignKey(
        "hipeac.Session", null=True, blank=True, on_delete=models.SET_NULL, related_name="posters"
    )
    title = models.CharField(max_length=250)

    class Meta:
        db_table = "hipeac_conference_poster"
