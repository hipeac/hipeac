from model_mommy import mommy


class TestProperties:

    def test_subscribers(self, db, now):
        user = mommy.make_recipe('hipeac.user')
        obj = mommy.make('hipeac.MailingList', query='select username, email from auth_user')
        assert len(obj.subscribers) == 1
        assert obj.subscribers[0] == f'{user.username} {user.email}'
