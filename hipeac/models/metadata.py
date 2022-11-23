from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.db.utils import ProgrammingError
from typing import Dict, List

from .mixins import KeywordsMixin


class Metadata(KeywordsMixin, models.Model):
    """
    Metadata used by other models.
    """

    GENDER = "gender"
    TITLE = "title"
    MEAL_PREFERENCE = "meal_preference"
    JOB_POSITION = "job_position"
    EMPLOYMENT = "employment_type"
    APPLICATION_AREA = "application_area"
    SESSION_TYPE = "session_type"
    PROJECT_PROGRAMME = "project_programme"
    TOPIC = "topic"
    TYPE_CHOICES = (
        (GENDER, "Gender"),
        (TITLE, "Title"),
        (MEAL_PREFERENCE, "Meal preference"),
        (JOB_POSITION, "Position"),
        (EMPLOYMENT, "Employment type"),
        (APPLICATION_AREA, "Application area"),
        (SESSION_TYPE, "Session type"),
        (TOPIC, "Topic"),
        (PROJECT_PROGRAMME, "EU project programme"),
    )

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    value = models.CharField(max_length=64)
    euraxess_value = models.CharField(max_length=250, null=True, blank=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["type"])]
        ordering = ("type", "position", "value")
        verbose_name_plural = "Metadata"

    def __str__(self) -> str:
        return self.value


class ApplicationArea(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="application_areas")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    application_area = models.ForeignKey(
        Metadata, limit_choices_to={"type": Metadata.APPLICATION_AREA}, on_delete=models.CASCADE
    )

    class Meta:
        db_table = "hipeac_rel_application_area"
        ordering = ("application_area__position", "application_area__value")
        unique_together = ("content_type", "object_id", "application_area")


class Topic(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="topics")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    topic = models.ForeignKey(Metadata, limit_choices_to={"type": Metadata.TOPIC}, on_delete=models.CASCADE)

    class Meta:
        db_table = "hipeac_rel_topic"
        ordering = ("topic__position", "topic__value")
        unique_together = ("content_type", "object_id", "topic")


def get_cached_metadata_queryset() -> List[Metadata]:
    try:
        queryset = cache.get("cached_metadata_queryset")
        if not queryset:
            queryset = Metadata.objects.all()
            cache.set("cached_metadata_queryset", queryset, 30)
        return queryset
    except ProgrammingError:
        return []


def get_cached_metadata() -> Dict[int, Metadata]:
    try:
        objects = cache.get("cached_metadata_objects")
        if not objects:
            objects = {m.id: m for m in get_cached_metadata_queryset()}
            cache.set("cached_metadata_objects", objects, 30)
        return objects
    except ProgrammingError:
        return {}
