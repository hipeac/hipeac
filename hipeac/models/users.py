from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_countries.fields import CountryField

from hipeac.models import Metadata


class ProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user', 'gender', 'title', 'meal_preference')


class Profile(models.Model):
    """
    Extends Django User model with extra profile fields.
    """
    user = models.OneToOneField(get_user_model(), related_name='profile', primary_key=True, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    country = CountryField(db_index=True)
    gender = models.ForeignKey(Metadata, null=True, blank=True, on_delete=models.SET_NULL,
                               limit_choices_to={'type': Metadata.GENDER}, related_name=Metadata.GENDER)
    title = models.ForeignKey(Metadata, null=True, blank=True, on_delete=models.SET_NULL,
                              limit_choices_to={'type': Metadata.TITLE}, related_name='user_' + Metadata.TITLE)
    meal_preference = models.ForeignKey(Metadata, null=True, blank=True, on_delete=models.SET_NULL,
                                        limit_choices_to={'type': Metadata.MEAL_PREFERENCE},
                                        related_name='user_' + Metadata.MEAL_PREFERENCE)

    position = models.ForeignKey(Metadata, null=True, blank=True, on_delete=models.SET_NULL,
                                 limit_choices_to={'type': Metadata.JOB_POSITION},
                                 related_name='user_' + Metadata.JOB_POSITION)
    department = models.CharField(max_length=200, null=True, blank=True)
    institution = models.ForeignKey('hipeac.Institution', null=True, blank=False, on_delete=models.SET_NULL,
                                    related_name='profiles')
    second_institution = models.ForeignKey('hipeac.Institution', null=True, blank=False, on_delete=models.SET_NULL,
                                           related_name='second_profiles')

    is_bouncing = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    application_areas = models.CharField(max_length=250, default='', validators=[validate_comma_separated_integer_list])
    topics = models.CharField(max_length=250, default='', validators=[validate_comma_separated_integer_list])
    projects = models.ManyToManyField('hipeac.Project', related_name='profiles')
    links = GenericRelation('hipeac.Link')
    objects = ProfileManager()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.user.username


@receiver(post_save, sender=get_user_model())
def post_save_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.updated_at = timezone.now()
        instance.profile.save()
