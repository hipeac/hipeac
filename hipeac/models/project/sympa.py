from django.db import connection, models
from django.utils.functional import cached_property
from typing import List


class MailingList(models.Model):
    """
    Sympa mailing list.
    """

    code = models.CharField(max_length=160)
    password = models.CharField(max_length=160)
    query = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code

    @cached_property
    def subscribers(self) -> List[str]:
        with connection.cursor() as cursor:
            cursor.execute(self.query)
            subscribers = [f"{row[0]} {row[1]}" for row in cursor.fetchall()]

        return subscribers
