from collections import namedtuple
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.utils.decorators import method_decorator

from .base import EventDetail


def namedtuplefetchall(cursor):
    desc = cursor.description
    nt_result = namedtuple("Result", [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


class AcacesDetail(EventDetail):
    """Displays a ACACES page.
    """

    template_name = "events/acaces/acaces.html"

    def get_object(self, queryset=None):
        if not hasattr(self, "object"):
            self.object = self.get_queryset().get(type="acaces", start_date__year=self.kwargs.get("year"))
        return self.object


class AcacesRegistration(AcacesDetail):
    template_name = "events/acaces/registration.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class AcacesStats(AcacesDetail):
    template_name = "events/acaces/stats.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have the necessary permissions to view this page.")
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.*, teachers.names AS teachers, COUNT(r.id) AS registrations
                FROM hipeac_event_course AS c
                LEFT JOIN hipeac_registration_courses AS r ON c.id = r.course_id
                LEFT JOIN (
                    SELECT c.id, GROUP_CONCAT(CONCAT(u.first_name, ' ', u.last_name) SEPARATOR ', ') as names
                    FROM hipeac_event_course AS c
                    LEFT JOIN hipeac_event_course_teachers AS rel ON c.id = rel.course_id
                    LEFT JOIN auth_user AS u ON rel.user_id = u.id
                    GROUP BY c.id
                ) AS teachers ON c.id = teachers.id
                WHERE c.event_id = %s
                GROUP BY c.id
                ORDER BY registrations DESC
            """, [self.get_object().id])
            context["regbycourse"] = namedtuplefetchall(cursor)

            cursor.execute("""
                SELECT p.registrations AS courses, COUNT(p.id) AS registrations
                FROM (
                    SELECT r.id, COUNT(r.id) AS registrations
                    FROM hipeac_registration_courses AS c
                    INNER JOIN hipeac_registration AS r ON r.id = c.registration_id
                    WHERE r.event_id = %s
                    GROUP BY registration_id
                    HAVING registrations > 0
                ) AS p
                GROUP BY p.registrations
            """, [self.get_object().id])
            context["coursebyreg"] = namedtuplefetchall(cursor)

            cursor.execute("""
                SELECT i.name, c.name AS country, COUNT(r.id) AS registrations
                FROM hipeac_institution AS i
                LEFT JOIN tmp_country AS c ON i.country = c.code
                LEFT JOIN hipeac_profile AS p ON i.id = p.institution_id
                LEFT JOIN hipeac_registration AS r ON p.user_id = r.user_id
                WHERE r.event_id = %s
                GROUP BY i.id
                ORDER BY registrations DESC
            """, [self.get_object().id])
            context["regbyinstitution"] = namedtuplefetchall(cursor)

            cursor.execute("""
                SELECT c.name, COUNT(r.id) AS registrations
                FROM tmp_country AS c
                LEFT JOIN hipeac_profile AS p ON c.code = p.country
                LEFT JOIN hipeac_registration AS r ON p.user_id = r.user_id
                WHERE r.event_id = %s
                GROUP BY c.code
                ORDER BY registrations DESC
            """, [self.get_object().id])
            context["regbycountry"] = namedtuplefetchall(cursor)

        return context
