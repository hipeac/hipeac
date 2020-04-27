from django.db import models


class InternshipReview(models.Model):
    """
    A review of a PhD Internship application, by each of the reviewers.
    """

    application = models.ForeignKey(
        "hipeac.InternshipApplication", related_name="collaborations", on_delete=models.CASCADE
    )
    comments = models.TextField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("auth.User", related_name="internship_reviews", null=True, on_delete=models.SET_NULL)

    def reviewer(self):
        return self.created_by
