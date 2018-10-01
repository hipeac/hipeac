from django.contrib.auth import get_user_model
from django.db import models


class Quote(models.Model):
    TYPE_CHOICES = (
        ('general', 'General'),
        ('jobs', 'Jobs'),
        ('internships', 'PhD Internships'),
        ('industry', 'Industry'),
        ('innovation', 'Innovation community'),
        ('csw', 'Computing Systems Week'),
        ('conference', 'HiPEAC Conference'),
        ('acaces', 'ACACES'),
        ('roadshow', 'HiPEAC Roadshow'),
        ('collaborations', 'Collaboration Grants'),
    )

    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    text = models.TextField()
    author = models.CharField(max_length=250)
    institution = models.ForeignKey('hipeac.Institution', related_name='quotes', null=True, blank=True,
                                    on_delete=models.SET_NULL)
    user = models.ForeignKey(get_user_model(), related_name='quotes', null=True, blank=True, on_delete=models.SET_NULL)
    is_featured = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f'Quote: {self.type} ({self.author})'
