from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.functions import truncate_md
from hipeac.models import Session
from ..institutions import InstitutionNestedSerializer
from ..metadata import MetadataSerializer
from ..mixins import ApplicationAreasMixin, FilesMixin, LinksMixin, TopicsMixin
from ..projects import ProjectNestedSerializer
from ..users import UserPublicMiniSerializer


class SessionNestedSerializer(WritableNestedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:session-detail", read_only=True)
    url = serializers.URLField(source="get_absolute_url", read_only=True)
    type = MetadataSerializer()
    keywords = serializers.JSONField(read_only=True)
    main_speaker = UserPublicMiniSerializer(required=False, read_only=True)

    class Meta:
        model = Session
        exclude = (
            "summary",
            "program",
            "organizers",
            "max_attendees",
            "extra_attendees_fee",
            "created_at",
            "updated_at",
            "event",
        )


class SessionListSerializer(ApplicationAreasMixin, TopicsMixin, SessionNestedSerializer):
    excerpt = serializers.SerializerMethodField(read_only=True)

    def get_excerpt(self, obj) -> str:
        return truncate_md(obj.summary, limit=350) if obj.summary else ""


class SessionSerializer(FilesMixin, LinksMixin, SessionListSerializer):
    rel_attendees = serializers.HyperlinkedIdentityField(view_name="v1:session-attendees")
    event = serializers.HyperlinkedIdentityField(view_name="v1:event-detail", read_only=True)
    date = serializers.DateField(read_only=True)
    editor_href = serializers.URLField(source="get_editor_url", read_only=True)
    projects = ProjectNestedSerializer(many=True, read_only=True)
    institutions = InstitutionNestedSerializer(many=True, read_only=True)
    is_industrial_session = serializers.BooleanField(read_only=True)

    class Meta(SessionNestedSerializer.Meta):
        exclude = ("created_at", "updated_at")


"""
class SessionAccessLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionAccessLink
        exclude = ()
"""
