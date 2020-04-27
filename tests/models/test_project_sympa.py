from model_bakery import baker


class TestProperties:
    def test_subscribers(self, db, now):
        user = baker.make_recipe("hipeac.user")
        obj = baker.make("hipeac.MailingList", query="select username, email from auth_user")
        assert len(obj.subscribers) == 1
        assert obj.subscribers[0] == f"{user.username} {user.email}"
