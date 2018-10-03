from django.db import models


class Sponsor(models.Model):
    GOLD = 1
    SILVER = 2
    BRONZE = 3
    ACADEMIC = 9
    TYPE_CHOICES = (
        (GOLD, 'Gold'),
        (SILVER, 'Silver'),
        (BRONZE, 'Bronze'),
        (ACADEMIC, 'Academic'),
    )

    event = models.ForeignKey('hipeac.Event', related_name='sponsors', on_delete='CASCADE')
    institution = models.ForeignKey('hipeac.Institution', related_name='sponsored_events', null=True, blank=True,
                                    on_delete='CASCADE')
    project = models.ForeignKey('hipeac.Project', related_name='sponsored_events', null=True, blank=True,
                                on_delete='CASCADE')
    sponsorship_type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=BRONZE)
    amount = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sponsorship_type', '-amount', 'institution__name']
