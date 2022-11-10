from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from hipeac.models import Registration, Session
from ..users import UserPublicMiniSerializer


class RegistrationSerializer(WritableNestedModelSerializer):
    payment_url = serializers.URLField(source="get_payment_url", read_only=True)
    sessions = serializers.PrimaryKeyRelatedField(queryset=Session.objects.all(), many=True, allow_empty=True)
    user = UserPublicMiniSerializer(read_only=True)

    class Meta:
        model = Registration
        exclude = ("paid", "paid_via_invoice")
        write_only_fields = ("event",)
        read_only_fields = (
            "created_at",
            "updated_at",
            "user",
            "base_fee",
            "extra_fees",
            "saldo",
            "invoice_sent",
            "visa_sent",
        )
