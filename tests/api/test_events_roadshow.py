import pytest

from django.urls import reverse
from model_mommy import mommy
from rest_framework import status


class TestForAnonymous:
    roadshow = None
    list_url = reverse('v1:roadshow-list')

    @pytest.fixture(autouse=True)
    def setup_roadshow(self, db):
        if not self.roadshow:
            self.roadshow = mommy.make_recipe('hipeac.roadshow')
        return

    def get_detail_url(self, id: int):
        return reverse('v1:roadshow-detail', args=[id])

    def test_list(self, api_client, db):
        assert api_client.get(self.list_url).status_code == status.HTTP_200_OK

    def test_create(self, api_client):
        assert api_client.post(self.list_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_read(self, api_client, db):
        assert api_client.get(self.get_detail_url(self.roadshow.id)).status_code == status.HTTP_200_OK

    def test_update(self, api_client):
        detail_url = self.get_detail_url(self.roadshow.id)
        assert api_client.patch(detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert api_client.put(detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete(self, api_client):
        detail_url = self.get_detail_url(self.roadshow.id)
        assert api_client.delete(detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
