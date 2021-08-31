import pytest


from django.core.exceptions import ValidationError
from model_bakery import baker


class TestValidators:
    def test_end_date_before_start_date(self, now):
        obj = baker.prepare_recipe("hipeac.event", end_date=now.subtract(days=-1).date)
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_start_date_before_registration_start_date(self, now):
        obj = baker.prepare_recipe(
            "hipeac.event",
            start_date=now.add(days=1).date,
            registration_start_date=now.add(days=10).date,
        )
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_registration_early_deadline_before_registration_start_date(self, now):
        obj = baker.prepare_recipe(
            "hipeac.event",
            registration_early_deadline=now.add(days=1).datetime,
            registration_start_date=now.add(days=10).date,
        )
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_registration_deadline_before_registration_start_date(self, now):
        obj = baker.prepare_recipe(
            "hipeac.event",
            registration_deadline=now.add(days=1).datetime,
            registration_start_date=now.add(days=10).date,
        )
        with pytest.raises(ValidationError):
            obj.full_clean()

    def test_start_date_before_registration_deadline(self, now):
        obj = baker.prepare_recipe(
            "hipeac.event",
            start_date=now.add(days=1).date,
            registration_deadline=now.add(days=10).datetime,
        )
        with pytest.raises(ValidationError):
            obj.full_clean()
