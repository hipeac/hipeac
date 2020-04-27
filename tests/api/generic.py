import pytest

from model_mommy import mommy


class UserMixin:
    user = None

    @pytest.fixture(autouse=True)
    def setup_user(self, db):
        if not self.user:
            self.user = mommy.make_recipe("hipeac.user")
        return
