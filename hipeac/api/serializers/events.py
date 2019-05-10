from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.functions import truncate_md
from hipeac.models import (
    B2b, Event, Committee, Registration, Poster, Roadshow, Session, Break, Sponsor, Venue, Room, Project, Institution
)
from .generic import JsonField, LinkSerializer, MetadataFieldWithPosition, MetadataListField, PrivateFileSerializer
from .institutions import InstitutionNestedSerializer
from .projects import ProjectNestedSerializer
from .users import UserPublicMiniSerializer, UserPublicSerializer


class B2bSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='v1:b2b-detail', read_only=True)

    class Meta:
        model = B2b
        exclude = ('updated_at',)
        lookup_field = 'pk'


class CommitteeListSerializer(serializers.ModelSerializer):
    members = UserPublicMiniSerializer(many=True)

    class Meta:
        model = Committee
        exclude = ('event', 'position')


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        exclude = ('venue',)


class VenueSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True)

    class Meta:
        model = Venue
        exclude = ('id', 'country')


class BreakSerializer(serializers.ModelSerializer):

    class Meta:
        model = Break
        exclude = ('event',)


class SponsorSerializer(serializers.ModelSerializer):
    institution = InstitutionNestedSerializer()
    project = ProjectNestedSerializer()

    class Meta:
        model = Sponsor
        exclude = ('event',)


class PosterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poster
        fields = ('id', 'title', 'authors', 'type')


class RegistrationListSerializer(serializers.ModelSerializer):
    user = UserPublicMiniSerializer()

    class Meta:
        model = Registration
        fields = ('created_at', 'user')


class AuthRegistrationSerializer(WritableNestedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='v1:auth-registration-detail', read_only=True)
    payment_href = serializers.URLField(source='get_payment_url', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    posters = PosterSerializer(many=True)

    class Meta:
        model = Registration
        exclude = ('user', 'paid', 'paid_via_invoice')
        write_only_fields = ('event',)
        read_only_fields = ('base_fee', 'extra_fees', 'saldo', 'invoice_sent', 'visa_sent')


class SessionNestedSerializer(WritableNestedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='v1:session-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)
    session_type = MetadataFieldWithPosition()
    keywords = JsonField(read_only=True)

    class Meta:
        model = Session
        exclude = ('summary', 'program', 'organizers', 'max_attendees', 'extra_attendees_fee',
                   'institutions', 'projects', 'main_speaker', 'created_at', 'updated_at', 'event')


class SessionListSerializer(SessionNestedSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()


class SessionSerializer(SessionListSerializer):
    event = serializers.HyperlinkedIdentityField(view_name='v1:event-detail', read_only=True)
    date = serializers.DateField(read_only=True)
    links = LinkSerializer(required=False, many=True, allow_null=True)
    href = serializers.URLField(source='get_absolute_url', read_only=True)
    editor_href = serializers.URLField(source='get_editor_url', read_only=True)
    main_speaker = UserPublicSerializer(read_only=True)
    excerpt = serializers.SerializerMethodField(read_only=True)
    projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True, allow_null=True)
    projects_info = serializers.SerializerMethodField(read_only=True)
    institutions = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all(), many=True, allow_null=True)
    institutions_info = serializers.SerializerMethodField(read_only=True)
    is_industrial_session = serializers.BooleanField(read_only=True)
    private_files = PrivateFileSerializer(many=True, read_only=True)

    class Meta(SessionNestedSerializer.Meta):
        exclude = ('created_at', 'updated_at',)

    def get_excerpt(self, obj):
        return truncate_md(obj.summary, limit=350)

    def get_projects_info(self, obj):
        return [{
            'name': project.short_name,
            'href': project.get_absolute_url(),
            'image': project.images['sm'] if project.images and 'sm' in project.images else None,
        } for project in obj.projects.all()]

    def get_institutions_info(self, obj):
        return [{
            'name': institution.short_name,
            'href': institution.get_absolute_url(),
            'image': institution.images['sm'] if institution.images and 'sm' in institution.images else None,
        } for institution in obj.institutions.all()]


class EventNestedSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:event-detail', read_only=True)
    url_articles = serializers.HyperlinkedIdentityField(view_name='v1:event-articles')
    url_registrations = serializers.HyperlinkedIdentityField(view_name='v1:event-registrations')
    href = serializers.CharField(source='get_absolute_url', read_only=True)
    name = serializers.CharField(read_only=True)
    images = serializers.DictField(read_only=True)
    dates = serializers.ListField()

    class Meta:
        model = Event
        exclude = ('coordinating_institution', 'venues', 'travel_info', 'image')


class EventListSerializer(EventNestedSerializer):
    pass


class EventSerializer(EventNestedSerializer):
    coordinating_institution = InstitutionNestedSerializer()
    fees = serializers.DictField(source='fees_dict', read_only=True)
    links = LinkSerializer(required=False, many=True, allow_null=True)
    breaks = BreakSerializer(many=True, read_only=True)
    sessions = SessionListSerializer(many=True)
    sponsors = SponsorSerializer(many=True, read_only=True)
    venues = VenueSerializer(many=True, read_only=True)
    is_early = serializers.BooleanField(read_only=True)
    is_open_for_registration = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        exclude = ()


class RoadshowNestedSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    institutions = InstitutionNestedSerializer(many=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Roadshow
        exclude = ()


class RoadshowListSerializer(RoadshowNestedSerializer):
    pass


class RoadshowSerializer(RoadshowNestedSerializer):
    pass
