from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from hipeac.models.membership import Member, Membership
from ...serializers import MemberSerializer


class MemberViewSet(ListModelMixin, GenericViewSet):
    queryset = Member.objects.prefetch_related("institution", "second_institution")
    pagination_class = None
    serializer_class = MemberSerializer

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(type__in=[Membership.MEMBER, Membership.ASSOCIATED_MEMBER]).select_related('user__profile').prefetch_related('user__profile__institution', 'user___affiliates__user')
        return super().list(request, *args, **kwargs)

    @action(detail=False)
    def affiliates(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(type__in=[Membership.AFFILIATED_MEMBER, Membership.AFFILIATED_PHD])
        return super().list(request, *args, **kwargs)


"""
class MemberViewSet(ListModelMixin, GenericViewSet):
    queryset = (
        get_user_model()
        .objects.filter(is_active=True)
        .select_related("profile")
        .defer("profile__bio")
        .order_by("first_name", "last_name")
    )
    pagination_class = None
    serializer_class = UserPublicMembershipSerializer

    def list(self, request, *args, **kwargs):
        members = self.queryset.filter(
            profile__membership_tags__contains="member", profile__membership_revocation_date__isnull=True
        )
        affiliates = self.queryset.filter(
            profile__membership_tags__contains="affiliated", profile__membership_revocation_date__isnull=True
        )
        institution_ids = list(members.values_list("profile__institution_id", flat=True))
        second_institution_ids = list(members.values_list("profile__second_institution_id", flat=True))
        institutions = Institution.objects.filter(id__in=institution_ids + second_institution_ids)
        ctx = {"request": request}

        return Response(
            {
                "institutions": InstitutionNestedSerializer(institutions, many=True, context=ctx).data,
                "members": UserPublicMembershipSerializer(members, many=True, context=ctx).data,
                "affiliates": UserPublicMembershipSerializer(affiliates, many=True, context=ctx).data,
            }
        )

    @action(detail=False)
    def affiliates(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(
            is_active=True,
            profile__membership_tags__contains="affiliated",
            profile__membership_revocation_date__isnull=True,
        )
        return super().list(request, *args, **kwargs)
"""
