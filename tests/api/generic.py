import pytest

from model_bakery import baker


class UserMixin:
    user = None

    @pytest.fixture(autouse=True)
    def setup_user(self, db):
        if not self.user:
            self.user = baker.make_recipe("hipeac.user")
        return
