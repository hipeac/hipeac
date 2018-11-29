from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


SUCCEEDED = 'succeeded'


class Payment(models.Model):
    """
    Higher permission levels inherit lower permissions, simplifying queries.
    """
    INVOICE = 'invoice'
    UGENT = 'ugent'
    PROVIDER_CHOICES = (
        (INVOICE, 'UGent (invoice)'),
        (UGENT, 'UGent Payments'),
    )

    SUCCEEDED = SUCCEEDED
    PENDING = 'pending'
    FAILED = 'failed'
    STATUS_CHOICES = (  # https://stripe.com/docs/api#charge_object-status
        (SUCCEEDED, 'Succeeded'),
        (PENDING, 'Pending'),
        (FAILED, 'Failed'),
    )

    user = models.ForeignKey(get_user_model(), blank=True, on_delete=models.CASCADE, related_name='payments')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='payments')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    currency = models.CharField(max_length=3, default='EUR', editable=False)
    subtotal = models.DecimalField(default=0.00, max_digits=5, decimal_places=2, editable=False)
    vat = models.DecimalField(default=0.00, max_digits=5, decimal_places=2, editable=False)
    total = models.DecimalField(default=0.00, max_digits=5, decimal_places=2, editable=False)

    provider = models.CharField(max_length=8, choices=PROVIDER_CHOICES)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=PENDING)
    reference = models.CharField(max_length=64, null=True, blank=True)
    response = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs) -> None:
        if self.type:
            self.currency = self.type.currency
            self.total = Decimal(self.type.total).quantize(Decimal('.01'))
            self.vat = Decimal((self.type.total / 100) * self.type.vat_rate).quantize(Decimal('.01'))
            self.subtotal = Decimal(self.total - self.vat).quantize(Decimal('.01'))
        super().save(*args, **kwargs)
