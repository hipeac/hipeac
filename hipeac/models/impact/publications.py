import datetime

from django.db import models
from django.db.models import Q
from django_countries.fields import CountryField

from ..mixins import UsersMixin


class PublicationConference(models.Model):
    """
    Conferences taken in account for HiPEAC Paper Awards.
    We need this model to have a relation of DBLP urls to scrap, per year.
    """

    CONFERENCES = (
        ("ASPLOS", "Conference on Architectural Support for Programming Languages and Operating Systems"),
        ("DAC", "Design Automation Conference"),
        ("FCCM", "Symposium on Field-Programmable Custom Computing Machines"),
        ("HPCA", "International Symposium on High Performance Computer Architecture"),
        ("ISCA", "International Symposium on Computer Architecture"),
        ("MICRO", "Symposium on Microarchitecture"),
        ("PLDI", "Conference on Programming Language Design and Implementation"),
        ("POPL", "Symposium on Principles of Programming Languages"),
    )

    acronym = models.CharField(max_length=16, choices=CONFERENCES)
    year = models.PositiveSmallIntegerField(db_index=True)
    country = CountryField()
    url = models.URLField("DBLP event page")

    class Meta:
        db_table = "hipeac_publication_conference"
        ordering = ("-year", "acronym")

    def __str__(self):
        return f"{self.acronym} {self.year}"


class PublicationQuerySet(models.QuerySet):
    def awarded(self, *, year: int):
        date = datetime.date(year, 12, 31)
        return (
            self.filter(conference__isnull=False, conference__year=year, itemtype="ScholarlyArticle")
            .prefetch_related("conference")
            .order_by("-conference__year", "conference__acronym", "title")
            .distinct()
        )
        return (
            self.filter(conference__isnull=False, conference__year=year, itemtype="ScholarlyArticle")
            .filter(
                (
                    Q(rel_users__user__profile__membership_tags__contains="member")
                    & ~Q(rel_users__user__profile__membership_tags__contains="non-eu")
                ),
                (
                    Q(rel_users__user__profile__membership_date__lte=date)
                    | Q(rel_users__user__profile__membership_date__isnull=True)
                ),
                (
                    Q(rel_users__user__profile__membership_revocation_date__gt=date)
                    | Q(rel_users__user__profile__membership_revocation_date__isnull=True)
                ),
            )
            .prefetch_related("conference")
            .order_by("-conference__year", "conference__acronym", "title")
            .distinct()
        )


class Publication(UsersMixin, models.Model):
    """
    Any research publication (paper) by a HiPEAC user.
    All the information comes from the DBLP database.
    http://dblp.uni-trier.de/
    """

    year = models.PositiveSmallIntegerField(db_index=True)
    title = models.TextField()
    authors_string = models.TextField("Full authors string from DBLP")
    dblp_key = models.CharField(unique=True, max_length=200)
    url = models.URLField("Electronic edition", null=True, blank=True)
    itemtype = models.CharField(null=True, blank=True, max_length=200)
    conference = models.ForeignKey(
        PublicationConference, null=True, blank=True, related_name="publications", on_delete=models.SET_NULL
    )

    objects = PublicationQuerySet.as_manager()

    class Meta:
        ordering = ("-year", "title")

    def __str__(self):
        return f"{self.title} ({self.conference})" if self.conference else self.title

    @property
    def authors(self):
        return self.users
