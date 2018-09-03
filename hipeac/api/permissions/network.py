from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly

from hipeac.models import Permission


class NetworkAdminPermission(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_staff or
            obj.acl.filter(user_id=request.user.id, level__gte=Permission.ADMIN).exists()
        )
