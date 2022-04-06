import maya

from model_bakery.recipe import Recipe, foreign_key

from hipeac.models import Metadata


now = maya.now()


# institutions

institution = Recipe("hipeac.Institution")


# projects

project = Recipe("hipeac.Project", start_date=now.date, end_date=now.add(years=2).date)


# events

event = Recipe(
    "hipeac.Event",
    coordinating_institution=foreign_key(institution),
    registration_start_date=now.date,
    registration_early_deadline=now.add(days=30).datetime,
    registration_deadline=now.add(days=60).datetime,
    start_date=now.add(days=60).date,
    end_date=now.add(days=65).date,
)
roadshow = Recipe("hipeac.Roadshow", start_date=now.add(days=30).date, end_date=now.add(days=35).date)
session_type = Recipe("hipeac.Metadata", type=Metadata.SESSION_TYPE)
session = Recipe(
    "hipeac.Session",
    type=foreign_key(session_type),
    start_at=now.add(days=62).datetime,
    end_at=now.add(days=62, minutes=90).datetime,
    event=foreign_key(event),
)


# users

user = Recipe("auth.User", is_staff=False, profile__institution=foreign_key(institution))
staff = user.extend(is_staff=True)
member = user.extend(profile__membership_tags="member")


# jobs

employment_type = Recipe("hipeac.Metadata", type=Metadata.EMPLOYMENT)
job = Recipe(
    "hipeac.Job",
    employment_type=foreign_key(employment_type),
    institution=foreign_key(institution),
    email="recruitment@hipeac.net",
    project=foreign_key(project),
    deadline=now.add(months=1).datetime,
    created_at=now.datetime,
    created_by=foreign_key(user),
)
