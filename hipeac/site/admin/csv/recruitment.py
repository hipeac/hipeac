import csv
import json

from django.http import HttpResponse

from hipeac.models import Job
from hipeac.tools.csv import ModelCsvWriter


class JobCsvWriter(ModelCsvWriter):
    model = Job
    custom_fields = ("institution_type",)
    exclude = ("links", "evaluation")
    metadata_fields = ("application_areas", "career_levels", "topics")


def csv_keywords_analysis(queryset, filename):
    """
    Given a Jobs queryset, it returns a CSV response with the distribution of keywords.
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="' + filename + '"'
    writer = csv.writer(response)

    # Don't use "ID" in uppercase as starting characters for a CSV! Excel don't like.
    columns = ["keyword", "hits"]
    keywords = {}

    writer.writerow(columns)

    for job in queryset:
        for keyword in json.loads(job.keywords):
            if keyword not in keywords:
                keywords[keyword] = 0

            keywords[keyword] += 1

    for t in sorted(keywords.items()):
        writer.writerow(list(t))

    # return HttpResponse('<html><body></body></html>')
    return response
