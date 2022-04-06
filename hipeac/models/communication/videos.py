from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from hipeac.models.mixins import ApplicationAreasMixin, InstitutionsMixin, ProjectsMixin, TopicsMixin, UsersMixin
from .vars import SECTION_CHOICES


class VideoManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "event",
                "rel_application_areas__application_area",
                "rel_institutions__institution",
                "rel_projects__project",
                "rel_topics__topic",
                "rel_users__user__profile",
            )
        )


class Video(ApplicationAreasMixin, InstitutionsMixin, ProjectsMixin, TopicsMixin, UsersMixin, models.Model):
    type = models.CharField(max_length=16, null=True, blank=True, choices=SECTION_CHOICES)
    title = models.CharField(max_length=250)
    publication_date = models.DateField()
    youtube_id = models.CharField("YouTube ID", max_length=40, unique=True)
    is_expert = models.BooleanField(default=True)
    shows_on_homepage = models.BooleanField(default=False)

    event = models.ForeignKey("hipeac.Event", null=True, blank=True, on_delete=models.SET_NULL, related_name="videos")

    objects = VideoManager()

    class Meta:
        db_table = "hipeac_comm_video"

    def __str__(self) -> str:
        return f"{self.youtube_id}: {self.title}"


class RelatedVideo(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="videos")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "hipeac_rel_video"
        ordering = ("content_type", "object_id", "position")
