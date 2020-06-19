from django.core.validators import validate_comma_separated_integer_list
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
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    title = models.TextField()
    authors = models.TextField(null=True, blank=True)
    abstract = models.TextField(null=True, blank=True)
    topics = models.CharField(max_length=250, blank=True, validators=[validate_comma_separated_integer_list])

    def __str__(self) -> str:
        return self.title

    @property
    def slug(self) -> str:
        return slugify(self.title)
