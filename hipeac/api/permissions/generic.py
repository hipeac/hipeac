from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, IsAuthenticatedOrReadOnly


class HasManagerPermission(IsAuthenticated):  # new naming conventions; TODO: change other
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.can_be_managed_by(request.user)


class HasManagerPermissionOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff or obj.can_be_managed_by(request.user)


class HasAdminPermissionOrReadOnly(HasManagerPermissionOrReadOnly):  # legacy
    pass


class HasManagementPermission(IsAuthenticated):
    def can_manage(self, user=None):
        if not hasattr(self, "can_manage"):
            self.can_manage = user.groups.filter(name="Management").exists()
        return self.can_manage

    def has_permission(self, request, view):
        return request.user and self.can_manage(request.user)

    def has_object_permission(self, request, view, obj):
        return self.can_manage(request.user)
