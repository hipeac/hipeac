from django.db import models
from django.template.defaultfilters import slugify
from django_countries.fields import CountryField


class Internship(models.Model):
    """
    A HiPEAC PhD Internship.
    """

    call = models.ForeignKey("hipeac.InternshipCall", related_name="internships", on_delete=models.CASCADE)
    institution = models.ForeignKey(
        "hipeac.Institution", related_name="internships", null=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, editable=False)
    description = models.TextField()
    timing = models.CharField(max_length=400, help_text="Describe the duration and the periods of the Internship.")
    location = models.CharField(max_length=250, help_text="Where will the PhD student be working?")
    country = CountryField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "auth.User", related_name="posted_phd_internships", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        truncated_title = (self.title[:75] + "...") if len(self.title) > 75 else self.title
        return f"{self.institution}: {truncated_title} ({self.call})"

    def is_editable_by_user(self, user):
        """
        Internships can be edited by creators or call manager.
        """
        return user.is_staff or user.id == self.created_by.id or user.id == self.call.manager.id
