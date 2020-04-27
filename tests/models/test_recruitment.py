from model_mommy import mommy


class TestMethods:
    def test_deadline_is_near(self, now):
        obj = mommy.prepare_recipe("hipeac.job", deadline=now.add(days=6).date)
        assert obj.deadline_is_near() is True
        obj = mommy.prepare_recipe("hipeac.job", deadline=now.add(days=7).date)
        assert obj.deadline_is_near() is False
        obj = mommy.prepare_recipe("hipeac.job", deadline=now.add(days=8).date)
        assert obj.deadline_is_near() is False
