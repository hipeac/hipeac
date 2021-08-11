from rest_framework.permissions import IsAuthenticated


class FilePermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        """
        Users can only DELETE images if they can edit the related object.
        """
        return obj.content_object.editable_by_user(request.user)
