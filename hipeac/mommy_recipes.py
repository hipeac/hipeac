import maya

from model_mommy.recipe import Recipe, foreign_key

from hipeac.models import Metadata


now = maya.now()


# institutions

institution = Recipe(
    'hipeac.Institution'
)


# projects

project = Recipe(
    'hipeac.Project'
)


# events

event = Recipe(
    'hipeac.Event',
    registration_start_date=now.date,
    registration_early_deadline=now.add(days=30).datetime,
    registration_deadline=now.add(days=60).datetime,
    start_date=now.add(days=60).date,
    end_date=now.add(days=65).date,
)


# users

user = Recipe(
    'auth.User',
    is_staff=False,
)

member = user.extend(
    is_member=True,
)


# jobs

employment_type = Recipe(
    'hipeac.Metadata',
    type=Metadata.EMPLOYMENT,
)

job = Recipe(
    'hipeac.Job',
    employment_type=foreign_key(employment_type),
    institution=foreign_key(institution),
    project=foreign_key(project),
    deadline=now.add(months=1).datetime,
    created_at=now.datetime,
    created_by=foreign_key(user),
)
