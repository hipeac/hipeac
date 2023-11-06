from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import (
    AcacesCourse,
    AcacesCourseSession,
    Break,
    Committee,
    Event,
    Registration,
    Session,
)

from ..files import FileSerializer
from ..institutions import InstitutionNestedSerializer
from ..metadata import MetadataSerializer
from ..mixins import FilesMixin, LinksMixin
from ..users import UserManagementSerializer, UserPublicMiniSerializer, UserPublicSerializer
from .sessions import SessionListSerializer
from .venues import VenueSerializer


"""
class AcacesPosterAbstractSerializer(serializers.ModelSerializer):
    file = serializers.FileField(use_url=True)
    topics = MetadataSerializer(many=True)

    class Meta:
        model = AcacesPosterAbstract
        exclude = ()
"""


class CommitteeListSerializer(serializers.ModelSerializer):
    members = UserPublicMiniSerializer(many=True)

    class Meta:
        model = Committee
        exclude = ("event", "position")


class BreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Break
        exclude = ("event",)


"""
class PosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poster
        fields = ("id", "title", "authors", "type", "abstract", "presentation", "video_url", "breakout_room")
        read_only_fields = ("abstract", "presentation", "video_url", "breakout_room")
"""


class RegistrationListSerializer(serializers.ModelSerializer):
    user = UserPublicMiniSerializer()

    class Meta:
        model = Registration
        fields = ("created_at", "user")


class AuthRegistrationSerializer(WritableNestedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:auth-registration-detail", read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name="v1:auth-registration-detail", read_only=True)
    payment_href = serializers.URLField(source="get_payment_url", read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    # poster_abstract = AcacesPosterAbstractSerializer(read_only=True)
    user = UserPublicMiniSerializer(read_only=True)
    # courses = serializers.PrimaryKeyRelatedField(queryset=AcacesCourse.objects.all(), many=True, allow_empty=True)
    sessions = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all(), many=True, allow_empty=True)
    # posters = PosterSerializer(many=True, allow_empty=True)
    custom_data = serializers.JSONField(required=False)
    rel_files = serializers.HyperlinkedIdentityField(view_name="v1:auth-registration-files")
    files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = Registration
        exclude = ("paid", "paid_via_invoice")
        write_only_fields = ("event",)
        read_only_fields = ("user", "base_fee", "extra_fees", "saldo", "invoice_sent", "visa_sent", "status")


class RegistrationManagementSerializer(AuthRegistrationSerializer):
    user = UserManagementSerializer()

    class Meta:
        model = Registration
        exclude = ("event",)
        read_only_fields = ("base_fee", "extra_fees", "saldo", "invoice_sent", "visa_sent", "status")


class EventBaseSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:event-detail", read_only=True)

    class Meta:
        model = Event
        fields = ("id", "self")


class EventNestedSerializer(serializers.ModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:event-detail", read_only=True)
    rel_articles = serializers.HyperlinkedIdentityField(view_name="v1:event-articles")
    rel_registrations = serializers.HyperlinkedIdentityField(view_name="v1:event-registrations")
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    country = CountryField(country_dict=True)
    name = serializers.CharField(read_only=True)
    images = serializers.DictField(read_only=True)
    dates = serializers.ListField()
    is_finished = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        exclude = ("coordinating_institution", "logistics", "image", "presentation", "wbs_element", "ingenico_salt")


class EventListSerializer(EventNestedSerializer):
    pass


class EventManagementSerializer(EventNestedSerializer):
    class Meta:
        model = Event
        exclude = ("coordinating_institution", "logistics", "image")


class EventSerializer(LinksMixin, EventNestedSerializer):
    coordinating_institution = InstitutionNestedSerializer()
    fees = serializers.DictField(source="fees_dict", read_only=True)
    breaks = BreakSerializer(many=True, read_only=True)
    sessions = SessionListSerializer(many=True)
    venues = VenueSerializer(many=True, read_only=True)
    is_early = serializers.BooleanField(read_only=True)
    is_open_for_registration = serializers.BooleanField(read_only=True)
    allows_payments = serializers.BooleanField(read_only=True)
    payments_activation = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Event
        exclude = ("wbs_element", "ingenico_salt")


class CourseSessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcacesCourseSession
        exclude = ()


class CourseListSerializer(FilesMixin, LinksMixin, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="v1:course-detail", read_only=True)
    sessions = CourseSessionListSerializer(many=True)
    teachers = UserPublicSerializer(many=True, read_only=True)
    topics = MetadataSerializer(many=True, read_only=True)
    url_videos = serializers.HyperlinkedIdentityField(view_name="v1:course-videos", read_only=True)
    custom_data = serializers.JSONField(required=False)

    class Meta:
        model = AcacesCourse
        exclude = ()
