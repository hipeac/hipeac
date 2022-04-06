import pytest


from django.core.exceptions import ValidationError
from model_bakery import baker


class TestValidators:
    def test_date_outside_event_dates(self, now):
        event = baker.prepare_recipe("hipeac.event", start_date=now.add(days=90).date, end_date=now.add(days=95).date)

        obj = baker.prepare_recipe("hipeac.session", event=event, start_at=now.add(days=80).datetime())
        with pytest.raises(ValidationError):
            obj.full_clean()

        obj = baker.prepare_recipe("hipeac.session", event=event, start_at=now.add(days=100).datetime())
        with pytest.raises(ValidationError):
            obj.full_clean()
