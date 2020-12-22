import csv
import math
import pytz

from django.http import HttpResponse
from django.utils.timezone import make_aware

from hipeac.models import Event
from hipeac.tools.zoom import attendee_report


def csv_zoom_attendee_report(event: Event, filename):
    """
    Given a Event queryset, it returns a CSV response with Zoom merged zoom reports for courses.
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="' + filename + '"'
    writer = csv.writer(response)

    # Don't use "ID" in uppercase as starting characters for a CSV! Excel don't like.
    columns = [
        "user_id",
        "email",
        "full name",
        "affiliation",
        "institution country",
    ]
    minute_columns = ["actual_duration", "", "", "", ""]
    registrations = {}
    email_map = {}
    full_name_map = {}
    minutes = {}
    join_time = {}

    for registration in (
        event.registrations.select_related("user__profile").prefetch_related("user__profile__institution").all()
    ):
        registrations[registration.user_id] = {
            "user_id": registration.user_id,
            "email": registration.user.email,
            "full name": registration.user.profile.name,
            "affiliation": registration.user.profile.institution.name if registration.user.profile.institution else "-",
            "institution country": (
                registration.user.profile.institution.country.name
                if (registration.user.profile.institution and registration.user.profile.institution.country)
                else "-"
            ),
        }
        email_map[registration.user.email] = registration.user_id
        full_name_map[registration.user.profile.name] = registration.user_id

    for session in event.sessions.all():
        session_field = f"{session.id} - {session.title}"
        session_join_field = f"{session.id} - join time"
        columns.append(session_field)
        columns.append(session_join_field)
        minutes[session_field] = {}
        join_time[session_join_field] = {}
        duration = 0

        if session.zoom_attendee_report:
            duration, report = attendee_report(str(session.zoom_attendee_report.file))

            for u in report:
                name = f'{u["first_name"]} {u["last_name"]}'

                # find user registration
                if u["email"] in email_map:
                    uid = email_map[u["email"]]
                elif name in full_name_map:
                    uid = full_name_map[name]
                else:
                    uid = None
                    continue

                if uid in minutes[session_field]:
                    minutes[session_field][uid] += u["minutes"]
                else:
                    minutes[session_field][uid] = u["minutes"]
                    if u["minutes"] == 0:
                        join_time[session_join_field][uid] = 0
                    else:
                        jt = make_aware(u["join_time"], timezone=pytz.timezone("Europe/Brussels"))
                        diff = (jt - session.start_at).total_seconds() / 60
                        join_time[session_join_field][uid] = math.floor(diff) if diff > 0 else 0

        for user_id, data in registrations.items():
            if user_id in minutes[session_field]:
                registrations[user_id][session_field] = minutes[session_field][user_id]
                registrations[user_id][session_join_field] = join_time[session_join_field][user_id]
            else:
                registrations[user_id][session_field] = "-"
                registrations[user_id][session_join_field] = "-"

        minute_columns = minute_columns + [duration, "-"]

    for course in event.courses.all():
        course_field = f"{course.id} - {course.teachers_string}"
        course_join_field = f"{course.id} - join time"
        columns.append(course_field)
        columns.append(course_join_field)
        durations = [0]
        s = 1
        minutes[course_field] = {}
        join_time[course_join_field] = {}

        for session in course.sessions.all():
            sid = f"{course.id}#{s}"
            s += 1
            sminutes = session.minutes

            minutes[sid] = {}
            join_time[sid] = {}
            columns.append(sid)

            if session.zoom_attendee_report:
                sminutes, report = attendee_report(str(session.zoom_attendee_report.file))

                for u in report:
                    name = f'{u["first_name"]} {u["last_name"]}'

                    # find user registration
                    if u["email"] in email_map:
                        uid = email_map[u["email"]]
                    elif name in full_name_map:
                        uid = full_name_map[name]
                    else:
                        uid = None
                        continue

                    if uid in minutes[sid]:
                        minutes[sid][uid] += u["minutes"]
                    else:
                        minutes[sid][uid] = u["minutes"]
                        join_time[sid][uid] = u["join_time"]

                    if uid in minutes[course_field]:
                        minutes[course_field][uid] += u["minutes"]
                    else:
                        minutes[course_field][uid] = u["minutes"]
                        join_time[course_join_field][uid] = u["join_time"]

            durations[0] = durations[0] + sminutes
            durations.append(sminutes)
            durations.append("-")

            for user_id, data in registrations.items():
                if user_id in minutes[sid]:
                    registrations[user_id][sid] = minutes[sid][user_id]
                else:
                    registrations[user_id][sid] = "-"

        for user_id, data in registrations.items():
            if user_id in minutes[course_field]:
                registrations[user_id][course_field] = minutes[course_field][user_id]
                registrations[user_id][course_join_field] = join_time[course_join_field][user_id]
            else:
                registrations[user_id][course_field] = "-"
                registrations[user_id][course_join_field] = "-"

        minute_columns = minute_columns + durations

    # main columns
    writer.writerow(columns)

    # minute information
    writer.writerow(minute_columns)

    for registration in registrations.values():
        writer.writerow([registration[k] for k in columns])

    return response
