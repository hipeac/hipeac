from rest_framework.permissions import IsAuthenticated


class HasRegistrationForEvent(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.registrations.filter(user=request.user).exists()


class B2bPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.reserved_by_id is None or obj.reserved_by_id == request.user.id


class RegistrationPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
