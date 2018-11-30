from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.functions import truncate_md
from hipeac.models import Event, Registration, Poster, Roadshow, Session, Break, Sponsor, Project, get_cached_metadata
from .generic import LinkSerializer, MetadataField, MetadataFieldWithPosition, MetadataListField
from .institutions import InstitutionNestedSerializer
from .projects import ProjectNestedSerializer
from .users import UserPublicListSerializer


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
    user = UserPublicListSerializer()

    class Meta:
        model = Registration
        fields = ('created_at', 'user')


class AuthRegistrationSerializer(WritableNestedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='v1:auth-registration-detail', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    posters = PosterSerializer(many=True)

    class Meta:
        model = Registration
        exclude = ('user',)
        write_only_fields = ('event',)
        read_only_fields = ('fee', 'saldo', 'invoice_sent', 'visa_sent')


class SessionNestedSerializer(WritableNestedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='v1:session-detail', read_only=True)
    href = serializers.CharField(source='get_absolute_url', read_only=True)
    links = LinkSerializer(required=False, many=True, allow_null=True)
    session_type = MetadataFieldWithPosition()

    class Meta:
        model = Session
        exclude = ('projects', 'summary', 'program', 'organizers', 'max_attendees', 'extra_attendees_fee',
                   'created_at', 'updated_at')


class SessionListSerializer(SessionNestedSerializer):
    application_areas = MetadataListField()
    topics = MetadataListField()
    excerpt = serializers.SerializerMethodField(read_only=True)
    main_speaker = serializers.SerializerMethodField(read_only=True)

    def is_keynote(self, obj):
        if not hasattr(self, '_metadata'):
            self._metadata = get_cached_metadata()
        return self._metadata[obj.session_type_id].value == 'Keynote'

    def get_excerpt(self, obj):
        return truncate_md(obj.summary, limit=350) if self.is_keynote(obj) else ''

    def get_main_speaker(self, obj):
        if self.is_keynote(obj) and obj.main_speaker_id:
            return UserPublicListSerializer(obj.main_speaker, context=self.context).data
        return None


class SessionSerializer(SessionListSerializer):
    event = serializers.HyperlinkedIdentityField(view_name='v1:event-detail', read_only=True)
    date = serializers.DateField(read_only=True)
    projects = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), many=True, allow_null=True)
    href = serializers.URLField(source='get_absolute_url', read_only=True)
    editor_href = serializers.URLField(source='get_editor_url', read_only=True)
    main_speaker = UserPublicListSerializer(read_only=True)

    class Meta(SessionNestedSerializer.Meta):
        exclude = ('created_at', 'updated_at')


class EventNestedSerializer(serializers.ModelSerializer):
    coordinating_institution = InstitutionNestedSerializer()
    country = CountryField(country_dict=True)
    url = serializers.HyperlinkedIdentityField(view_name='v1:event-detail', read_only=True)
    url_articles = serializers.HyperlinkedIdentityField(view_name='v1:event-articles')
    url_registrations = serializers.HyperlinkedIdentityField(view_name='v1:event-registrations')
    href = serializers.CharField(source='get_absolute_url', read_only=True)
    name = serializers.CharField(read_only=True)
    links = LinkSerializer(required=False, many=True, allow_null=True)
    images = serializers.DictField(read_only=True)
    dates = serializers.ListField()

    class Meta:
        model = Event
        exclude = ()


class EventListSerializer(EventNestedSerializer):
    pass


class EventSerializer(EventNestedSerializer):
    breaks = BreakSerializer(many=True, read_only=True)
    sessions = SessionListSerializer(many=True)
    sponsors = SponsorSerializer(many=True, read_only=True)


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
