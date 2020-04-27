from django.db import models
from django.template.defaultfilters import slugify


class Poster(models.Model):
    STUDENT = "student"
    INDUSTRY = "industry"
    PROJECT = "project"
    TYPE_CHOICES = (
        (STUDENT, "Student poster"),
        (INDUSTRY, "Company poster"),
        (PROJECT, "EU Project poster"),
    )

    registration = models.ForeignKey("hipeac.Registration", related_name="posters", on_delete=models.CASCADE)
    title = models.TextField()
    authors = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)

    def __str__(self) -> str:
        return self.title

    @property
    def slug(self) -> str:
        return slugify(self.title)
