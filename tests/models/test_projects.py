from model_bakery import baker


class TestMethods:
    def test_is_active(self, now):
        obj = baker.prepare("hipeac.Project", start_date=now.add(days=1).date, end_date=now.add(years=2).date)
        assert obj.is_active() is False
        obj = baker.prepare("hipeac.Project", start_date=now.subtract(days=2).date, end_date=now.subtract(days=1).date)
        assert obj.is_active() is False
        obj = baker.prepare("hipeac.Project", start_date=now.date, end_date=now.add(years=2).date)
        assert obj.is_active() is True

    def test_is_active_missing_data(self, now):
        obj = baker.prepare("hipeac.Project", start_date=None)
        assert obj.is_active() is False
        obj = baker.prepare("hipeac.Project", end_date=None)
        assert obj.is_active() is False
