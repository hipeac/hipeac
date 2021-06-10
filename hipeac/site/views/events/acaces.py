from collections import namedtuple
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django_countries import countries
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = dict(countries)
        return context


class AcacesManagement(AcacesDetail):
    template_name = "events/acaces/management/management.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="Management").exists():
            messages.error(request, "You don't have the necessary permissions to view this page.")
            raise PermissionDenied

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
            cursor.execute(
                """
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
            """,
                [self.get_object().id],
            )
            context["regbycourse"] = namedtuplefetchall(cursor)

            cursor.execute(
                """
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
            """,
                [self.get_object().id],
            )
            context["coursebyreg"] = namedtuplefetchall(cursor)

            cursor.execute(
                """
                SELECT i.name, c.name AS country, COUNT(r.id) AS registrations
                FROM hipeac_institution AS i
                LEFT JOIN tmp_country AS c ON i.country = c.code
                LEFT JOIN hipeac_profile AS p ON i.id = p.institution_id
                LEFT JOIN hipeac_registration AS r ON p.user_id = r.user_id
                WHERE r.event_id = %s
                GROUP BY i.id
                ORDER BY registrations DESC
            """,
                [self.get_object().id],
            )
            context["regbyinstitution"] = namedtuplefetchall(cursor)

            cursor.execute(
                """
                SELECT c.name, COUNT(r.id) AS registrations
                FROM tmp_country AS c
                LEFT JOIN hipeac_profile AS p ON c.code = p.country
                LEFT JOIN hipeac_registration AS r ON p.user_id = r.user_id
                WHERE r.event_id = %s
                GROUP BY c.code
                ORDER BY registrations DESC
            """,
                [self.get_object().id],
            )
            context["regbycountry"] = namedtuplefetchall(cursor)

            cursor.execute(
                """
                SELECT r.id, CONCAT(u.first_name, ' ', u.last_name) as full_name, u.email, i.name as institution, c.name AS country, pos.title as poster, c1.registered as c1, c2.registered as c2, c3.registered as c3, c4.registered as c4, c5.registered as c5, c6.registered as c6, c8.registered as c8, c9.registered as c9, c10.registered as c10, c11.registered as c11, c12.registered as c12
                FROM auth_user as u
                INNER JOIN hipeac_profile AS p ON u.id = p.user_id
                LEFT JOIN hipeac_institution AS i ON p.institution_id = i.id
                LEFT JOIN tmp_country AS c ON i.country = c.code
                INNER JOIN hipeac_registration AS r ON u.id = r.user_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 1) AS c1 ON r.id = c1.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 2) AS c2 ON r.id = c2.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 3) AS c3 ON r.id = c3.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 4) AS c4 ON r.id = c4.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 5) AS c5 ON r.id = c5.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 6) AS c6 ON r.id = c6.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 8) AS c8 ON r.id = c8.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 9) AS c9 ON r.id = c9.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 10) AS c10 ON r.id = c10.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 11) AS c11 ON r.id = c11.registration_id
                LEFT JOIN (SELECT registration_id, 'true' AS registered FROM hipeac_registration_courses WHERE course_id = 12) AS c12 ON r.id = c12.registration_id
                LEFT JOIN hipeac_poster AS pos ON r.id = pos.registration_id
                WHERE r.event_id = %s
                ORDER BY r.created_at
            """,
                [self.get_object().id],
            )
            context["json_data"] = [t._asdict() for t in namedtuplefetchall(cursor)]

        return context
