import csv

from datetime import date
from django.db import connection
from django.http import HttpResponse

from hipeac.models import Member, Membership


def csv_users_activity(queryset, filename):
    """
    Given a User queryset, it returns a CSV response.
    """
    year = date.today().year
    years = range(year - 3, year + 1)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="' + filename + '"'
    writer = csv.writer(response)

    # Don't use "ID" in uppercase as starting characters for a CSV! Excel don't like.
    columns = [
        "id",
        "Full name",
        "Membership date",
        "Membership tags",
        "Email",
        "Affiliation",
        "Institution type",
        "Institution country",
        "Affiliates",
    ]

    for year in years:
        year_str = str(year)
        columns.append(year_str + " Publications")
        columns.append(year_str + " Paper Awards")
        columns.append(year_str + " Conference attendance")
        columns.append(year_str + " CSW attendance")
        columns.append(year_str + " ACACES attendance")
        columns.append(year_str + " Organized activities")
        columns.append(year_str + " Posted jobs")
        columns.append(year_str + " Magazine contributions")

    writer.writerow(columns)

    for user in queryset.select_related("profile", "member"):
        affiliates = 0

        if user.member.type != Membership.MEMBER:
            continue
        else:
            affiliates = Member.objects.filter(advisor_id=user.id).count()

        # Initialize objects
        organized_activities = {}
        publications = {}
        paper_awards = {}
        conferences = {}
        csws = {}
        summer_schools = {}
        posted_jobs = {}
        magazine_contributions = {}

        for year in years:
            # Initialize data
            organized_activities[year] = 0
            publications[year] = 0
            paper_awards[year] = 0
            conferences[year] = 0
            csws[year] = 0
            summer_schools[year] = 0
            posted_jobs[year] = 0
            magazine_contributions[year] = 0

        # Events

        with connection.cursor() as cursor:
            query = """
                SELECT e.type, EXTRACT(year FROM e.start_date), COUNT(*)
                FROM hipeac_event_registration AS r
                INNER JOIN hipeac_event AS e ON r.event_id = e.id
                WHERE r.user_id IN (
                    SELECT user_id
                    FROM hipeac_membership_member
                    WHERE user_id = %s OR advisor_id = %s
                ) AND e.start_date BETWEEN '%s-01-01' AND '%s-12-31'
                GROUP BY e.type, EXTRACT(year FROM e.start_date)
            """
            cursor.execute(query, [user.id, user.id, years[0], years[-1]])

            for row in cursor.fetchall():
                if row[0] == "conference":
                    conferences[row[1]] = row[2]
                if row[0] == "csw":
                    csws[row[1]] = row[2]
                if row[0] == "acaces":
                    summer_schools[row[1]] = row[2]

        # Publications

        with connection.cursor() as cursor:
            query = """
                SELECT p.year, COUNT(*)
                FROM hipeac_publication AS p
                INNER JOIN (
                    SELECT *
                    FROM hipeac_rel_user
                    WHERE content_type_id = 50
                ) AS a ON p.id = a.object_id
                WHERE a.user_id IN (
                    SELECT user_id
                    FROM hipeac_membership_member
                    WHERE user_id = %s OR advisor_id = %s
                ) AND p.year BETWEEN %s AND %s
                GROUP BY p.year
            """
            cursor.execute(query, [user.id, user.id, years[0], years[-1]])

            for row in cursor.fetchall():
                publications[row[0]] = row[1]

        with connection.cursor() as cursor:
            query = """
                SELECT p.year, COUNT(*)
                FROM hipeac_publication AS p
                INNER JOIN (
                    SELECT *
                    FROM hipeac_rel_user
                    WHERE content_type_id = 50
                ) AS a ON p.id = a.object_id
                WHERE a.user_id IN (
                    SELECT user_id
                    FROM hipeac_membership_member
                    WHERE user_id = %s OR advisor_id = %s
                ) AND p.conference_id IS NOT NULL AND p.year BETWEEN %s AND %s
                GROUP BY p.year
            """
            cursor.execute(query, [user.id, user.id, years[0], years[-1]])

            for row in cursor.fetchall():
                paper_awards[row[0]] = row[1]

        # Organized activities

        with connection.cursor() as cursor:
            query = """
                SELECT EXTRACT(year FROM s.start_at), COUNT(*)
                FROM hipeac_event_session AS s
                INNER JOIN (
                    SELECT *
                    FROM hipeac_rel_permission
                    WHERE content_type_id = 41
                ) AS p ON s.id = p.object_id
                WHERE p.user_id IN (
                    SELECT user_id
                    FROM hipeac_membership_member
                    WHERE user_id = %s OR advisor_id = %s
                ) AND s.start_at BETWEEN '%s-01-01 00:00' AND '%s-12-31 23:59'
                GROUP BY EXTRACT(year FROM s.start_at)
            """
            cursor.execute(query, [user.id, user.id, years[0], years[-1]])

            for row in cursor.fetchall():
                organized_activities[row[0]] = row[1]

        # Jobs

        with connection.cursor() as cursor:
            query = """
                SELECT EXTRACT(year FROM j.created_at), COUNT(*)
                FROM hipeac_job AS j
                WHERE j.created_by_id IN (
                    SELECT user_id
                    FROM hipeac_membership_member
                    WHERE user_id = %s OR advisor_id = %s
                ) AND j.created_at BETWEEN '%s-01-01' AND '%s-12-31'
                GROUP BY EXTRACT(year FROM j.created_at)
            """
            cursor.execute(query, [user.id, user.id, years[0], years[-1]])

            for row in cursor.fetchall():
                posted_jobs[row[0]] = row[1]

        # Magazine contributions

        with connection.cursor() as cursor:
            query = """
                SELECT EXTRACT(year FROM m.publication_date), COUNT(*)
                FROM hipeac_comm_magazine AS m
                INNER JOIN (
                    SELECT *
                    FROM hipeac_rel_user
                    WHERE content_type_id = 38
                ) AS rel ON m.id = rel.object_id
                WHERE rel.user_id = %s
                    AND m.publication_date BETWEEN '%s-01-01' AND '%s-12-31'
                GROUP BY EXTRACT(year FROM m.publication_date)
            """
            cursor.execute(query, [user.id, years[0], years[-1]])

            for row in cursor.fetchall():
                magazine_contributions[row[0]] = row[1]

        # Make file

        institution_country = user.profile.institution.country.name if user.profile.institution else None
        institution_type = user.profile.institution.type if user.profile.institution else None
        user_data = [
            user.id,
            user.profile.name,
            user.member.date,
            user.member.keywords,
            user.email,
            user.profile.institution,
            institution_type,
            institution_country,
            affiliates,
        ]

        for year in years:
            user_data.append(publications[year])
            user_data.append(paper_awards[year])
            user_data.append(conferences[year])
            user_data.append(csws[year])
            user_data.append(summer_schools[year])
            user_data.append(organized_activities[year])
            user_data.append(posted_jobs[year])
            user_data.append(magazine_contributions[year])

        writer.writerow(user_data)

    # return HttpResponse('<html><body></body></html>')
    return response
