import pytest


from django.core.exceptions import ValidationError
from model_mommy import mommy


class TestValidators:
    def test_date_outside_event_dates(self, now):
        event = mommy.prepare_recipe("hipeac.event", start_date=now.add(days=90).date, end_date=now.add(days=95).date)

        obj = mommy.prepare_recipe("hipeac.session", event=event, date=now.add(days=80).date)
        with pytest.raises(ValidationError):
            obj.full_clean()

        obj = mommy.prepare_recipe("hipeac.session", event=event, date=now.add(days=100).date)
        with pytest.raises(ValidationError):
            obj.full_clean()
