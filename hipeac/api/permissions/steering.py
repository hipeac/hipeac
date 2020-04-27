from rest_framework.permissions import IsAuthenticated


class IsSteeringMember(IsAuthenticated):
    def is_steering(self, user=None):
        if not hasattr(self, "user_is_steering"):
            self.user_is_steering = user.groups.filter(name="Steering Committee").exists()
        return self.user_is_steering

    def has_permission(self, request, view):
        return request.user and self.is_steering(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return request.user.is_staff
        return self.is_steering(request.user)


class ActionPointPermission(IsSteeringMember):
    pass
