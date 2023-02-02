from rest_framework.permissions import IsAuthenticated


class HasJobFairRecruiterPermission(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.id in obj.companies.values_list("users", flat=True)
