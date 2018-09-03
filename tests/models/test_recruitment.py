from model_mommy import mommy


class TestMethods:

    def test_deadline_is_near(self, now):
        job = mommy.prepare_recipe('hipeac.job', deadline=now.add(days=6).date)
        assert job.deadline_is_near() is True
        job = mommy.prepare_recipe('hipeac.job', deadline=now.add(days=7).date)
        assert job.deadline_is_near() is False
        job = mommy.prepare_recipe('hipeac.job', deadline=now.add(days=8).date)
        assert job.deadline_is_near() is False
