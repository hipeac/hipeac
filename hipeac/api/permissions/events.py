from rest_framework.permissions import IsAuthenticated


class HasRegistrationForEvent(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.registrations.filter(user=request.user).exists()


class HasRegistrationForRelatedEvent(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.event.registrations.filter(user=request.user).exists()


class B2bPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.reserved_by_id is None or obj.reserved_by_id == request.user.id


class RegistrationPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class AcacesManagementPermission(IsAuthenticated):
    def is_manager(self, user=None):
        if not hasattr(self, "user_is_manager"):
            self.user_is_manager = user.groups.filter(name="Management ACACES").exists()
        return self.user_is_manager

    def has_permission(self, request, view):
        return self.is_manager(request.user)

    def has_object_permission(self, request, view, obj):
        return self.is_manager(request.user)
