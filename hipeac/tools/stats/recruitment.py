from django.db.models import Count
from django.db.models.functions import TruncMonth

from hipeac.models.recruitment import Job


def get_jobs_per_month() -> list:
    return list(
        Job.objects.annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
