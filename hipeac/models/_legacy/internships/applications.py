from django.db import models


class InternshipApplication(models.Model):
    """
    A HiPEAC PhD Internship application.
    """

    STATUS_CHOICES = (
        ("UN", "Pending"),
        ("OK", "Accepted"),
        ("NO", "Rejected"),
    )

    internship = models.ForeignKey("hipeac.Internship", related_name="applications", on_delete=models.CASCADE)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="UN")
    host_decision = models.CharField(max_length=2, choices=STATUS_CHOICES, default="UN")
    rank = models.SmallIntegerField(default=0)
    comments = models.TextField()
    available_from = models.DateField(help_text="YYYY-MM-DD")
    available_to = models.DateField(help_text="YYYY-MM-DD")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "auth.User", related_name="internship_applications", null=True, on_delete=models.SET_NULL
    )

    selected = models.BooleanField(default=False)
    summary = models.TextField(null=True, blank=True, help_text="Summary sent by the student to HiPEAC.")
    advisor_string = models.CharField(
        "Advisor", max_length=250, null=True, blank=True, help_text="Fill in your advisors's name here."
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("internship", "created_by")

    def clean(self):
        """
        Validates the model before saving.
        This rules only apply when creating a new object.
        """
        """ TODO!
        if not self.pk:
            # 1: A student must be studing in an European institution.
            eu_countries = HipeacCountries()
            if not self.created_by.institution or self.created_by.institution.country not in eu_countries:
                raise ValidationError('Only students from a European institution can apply '
                                      'for the HiPEAC PhD Mobility Programme.')
            # 2: A student cannot apply to more than 2 companies in the same call.
            other_institutions = Institution.objects \
                                            .filter(
                                                internships__applications__created_by=self.created_by,
                                                internships__call=self.internship.call) \
                                            .exclude(id=self.internship.institution.id) \
                                            .distinct() \
                                            .count()
            if other_institutions > 1:
                raise ValidationError('Sorry, but a student cannot apply to more than 2 companies in the same call.')
            # 3: A student can only apply to 2 internships within a company in the same call.
            applications_within_institution = Application.objects \
                                                         .filter(
                                                             created_by=self.created_by,
                                                             internship__institution=self.internship.institution,
                                                             internship__call=self.internship.call) \
                                                         .count()
            if applications_within_institution > 1:
                raise ValidationError('Sorry, but a student can only apply to 2 internships within a company in the '
                                      'same call.')
        """
        pass

    def __str__(self):
        return f"{self.applicant().profile.name} (to {self.internship.institution})"

    def applicant(self):
        return self.created_by

    @property
    def year(self) -> int:
        return self.available_from.year

    def is_granted(self):
        return self.status == "OK"

    is_granted.boolean = True
    is_granted.short_description = "Granted"

    def is_editable_by_user(self, user):
        """
        Internship applications can be edited by creators, advisors or call manager.
        """
        if user.is_staff or user.id == self.created_by.id or user.id == self.internship.call.manager.id:
            return True
        elif self.created_by.advisor:
            return user.id == self.created_by.advisor.id
        else:
            return False
