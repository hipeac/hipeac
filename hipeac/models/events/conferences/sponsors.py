from django.db import models


class ConferenceSponsor(models.Model):
    GOLD = 1
    SILVER = 2
    BRONZE = 3
    ACADEMIC = 9
    TYPE_CHOICES = (
        (GOLD, "Gold"),
        (SILVER, "Silver"),
        (BRONZE, "Bronze"),
        (ACADEMIC, "Academic"),
    )

    conference = models.ForeignKey("hipeac.Conference", related_name="sponsors", on_delete=models.CASCADE)
    institution = models.ForeignKey(
        "hipeac.Institution", related_name="sponsored_conferences", null=True, blank=True, on_delete=models.CASCADE
    )
    project = models.ForeignKey(
        "hipeac.Project", related_name="sponsored_conferences", null=True, blank=True, on_delete=models.CASCADE
    )
    sponsorship_type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=BRONZE)
    amount = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hipeac_conference_sponsor"
        ordering = ("sponsorship_type", "-amount", "institution__name")
