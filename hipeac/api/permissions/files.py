from rest_framework.permissions import IsAuthenticated


class FilePermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        """
        Users can only DELETE images if they can manage the related object.
        """
        return request.user.is_staff or obj.content_object.can_be_managed_by(request.user)
