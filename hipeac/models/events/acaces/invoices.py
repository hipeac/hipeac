from django.db import models


class AcacesInvoice(models.Model):
    registration = models.OneToOneField("hipeac.AcacesRegistration", on_delete=models.CASCADE)

    class Meta:
        db_table = "hipeac_acaces_invoice"
