from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class HasAdminPermissionOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff or obj.can_be_managed_by(request.user)
