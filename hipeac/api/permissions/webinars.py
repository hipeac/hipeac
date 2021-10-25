from rest_framework.permissions import IsAuthenticated


class HasRegistrationForWebinar(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.registrations.filter(user=request.user).exists()
