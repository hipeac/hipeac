import pytest

from django.http import QueryDict

from hipeac.services.payments.ingenico import Ingenico


@pytest.mark.parametrize(
    "query_string,salt",
    [
        (
            "AAVADDRESS=NO&AAVCHECK=KO&AAVZIP=KO&ACCEPTANCE=067891&AMOUNT=150&BIN=471532&BRAND=VISA&CARDNO=XXXXXXXXXXXX5594&CCCTY=GB&CN=Evan&CREDITDEBIT=&CURRENCY=EUR&CVCCHECK=OK&ECI=5&ED=0422&IPCTY=GB&NCERROR=0&ORDERID=1365/1599730668&PAYID=5451031176&PM=CreditCard&SHASIGN=E0B1DC00DB95CA8FDA14EBD7D877979709C980DE21C10BADB49D404C009FBA8E2F4BDB779B07E6331B6A691792CD155D4A50FFE55F17408C3C8B0E2B09EF59F3&STATUS=9&SUBBRAND=Visa Purchasing&TRXDATE=09/10/20&VC=NO",
            "ogonehash",
        )
    ],
)
def test_valid_query_parameters(query_string, salt):
    assert Ingenico.validate_out_parameters(QueryDict(query_string), outsalt=salt)
