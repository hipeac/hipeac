from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Link(models.Model):
    """
    Online accounts and other links.
    """

    WEBSITE = "website"
    DBLP = "dblp"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    YOUTUBE = "youtube"
    EASYCHAIR = "easychair"
    CORDIS = "cordis"
    GOOGLE_MAPS = "google_maps"
    GOOGLE_PHOTOS = "google_photos"
    ZOOM = "zoom"
    OTHER = "other"
    TYPE_CHOICES = (
        (WEBSITE, "Website"),
        (DBLP, "DBLP"),
        (LINKEDIN, "LinkedIn"),
        (GITHUB, "GitHub"),
        (TWITTER, "Twitter"),
        (YOUTUBE, "YouTube"),
        (EASYCHAIR, "EasyChair"),
        (CORDIS, "Cordis"),
        (GOOGLE_MAPS, "Google Maps"),
        (GOOGLE_PHOTOS, "Google Photos"),
        (ZOOM, "Zoom.us"),
        (OTHER, "Other"),
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="links")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    url = models.URLField()

    class Meta:
        db_table = "hipeac_rel_link"
        ordering = ("-type",)


@receiver(post_save, sender=Link)
def post_save_link(sender, instance, created, **kwargs):
    if instance.type == Link.DBLP and instance.content_type.model == "profile":
        pass
        # send_task("hipeac.tasks.dblp.extract_publications_for_user", (instance.object_id,))
