import pytest

from model_mommy import mommy

from hipeac.models import Link


class TestLinkMixin:
    obj = None

    @pytest.fixture(autouse=True)
    def setup_project(self, db):
        if not self.obj:
            self.obj = mommy.make_recipe("hipeac.project")
            Link(content_object=self.obj, type=Link.TWITTER, url="https://twitter.com/hipeac").save()
            Link(content_object=self.obj, type=Link.WEBSITE, url="https://www.hipeac.net/").save()
            Link(content_object=self.obj, type=Link.LINKEDIN, url="https://www.hipeac.net/linkedin").save()
        return

    def test_get_link(self):
        assert self.obj.get_link(Link.LINKEDIN) == "https://www.hipeac.net/linkedin"
        assert self.obj.get_link(Link.YOUTUBE) is None

    def test_twitter_username(self):
        assert self.obj.twitter_username == "hipeac"

    def test_website(self):
        assert self.obj.website == "https://www.hipeac.net/"
