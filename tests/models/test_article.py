from model_mommy import mommy


class TestMethods:

    def test_is_published(self, now):
        obj = mommy.prepare('hipeac.Article', is_ready=True, publication_date=now.add(days=1).date)
        assert obj.is_published() is False
        obj = mommy.prepare('hipeac.Article', is_ready=True, publication_date=now.subtract(days=1).date)
        assert obj.is_published() is True
        obj = mommy.prepare('hipeac.Article', is_ready=False, publication_date=now.subtract(days=1).date)
        assert obj.is_published() is False
