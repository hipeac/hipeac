from django_countries.serializer_fields import CountryField
from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Institution, RelatedInstitution
from .mixins import ApplicationAreasMixin, LinksMixin, TopicsMixin


class InstitutionSerializer(ApplicationAreasMixin, LinksMixin, TopicsMixin, WritableNestedModelSerializer):
    self = serializers.HyperlinkedIdentityField(view_name="v1:institution-detail", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)  # deprecated
    href = serializers.CharField(source="get_absolute_url", read_only=True)
    children = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    country = CountryField(country_dict=True)
    short_name = serializers.CharField(read_only=True)

    class Meta:
        model = Institution
        read_only_fields = ("image", "images")
        exclude = ("colloquial_name",)


class InstitutionMiniSerializer(InstitutionSerializer):
    class Meta:
        model = Institution
        fields = ("id", "self", "url", "href", "type", "name", "local_name", "short_name", "country")


class InstitutionNestedSerializer(InstitutionSerializer):
    class Meta:
        model = Institution
        fields = (
            "id",
            "self",
            "url",
            "href",
            "type",
            "name",
            "local_name",
            "short_name",
            "location",
            "country",
            "images",
        )


class InstitutionListSerializer(InstitutionNestedSerializer):
    pass


class RelatedInstitutionSerializer(serializers.ModelSerializer):
    oid = serializers.PrimaryKeyRelatedField(source="institution", queryset=Institution.objects.all())

    class Meta:
        model = RelatedInstitution
        fields = ("id", "oid")


class InstitutionsMixin(serializers.ModelSerializer):
    institutions = InstitutionNestedSerializer(many=True, read_only=True)
    rel_institutions = RelatedInstitutionSerializer(many=True)
