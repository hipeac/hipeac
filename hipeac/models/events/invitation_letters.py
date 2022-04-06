from django.db import models

from .registrations import Registration


class InvitationLetter(models.Model):
    """
    Information necessary to issue an invitation letter.
    """

    PAPER = "paper"
    POSTER = "poster"
    SUBMITTED_CHOICES = (
        (PAPER, "Paper"),
        (POSTER, "Poster"),
    )

    registration = models.OneToOneField(Registration, primary_key=True, related_name="letter", on_delete=models.CASCADE)
    name = models.CharField(max_length=190)
    passport_number = models.CharField(max_length=60)
    nationality = models.CharField(max_length=190)
    birthdate = models.DateField(null=True, blank=True)
    address = models.TextField()
    submitted = models.CharField(max_length=16, null=True, blank=True, default=None, choices=SUBMITTED_CHOICES)
    submitted_title = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "hipeac_event_invitation_letter"

    def __str__(self) -> str:
        return str(self.registration.uuid)
