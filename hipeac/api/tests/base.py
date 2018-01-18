from django.test import TestCase


class BaseTestCase(TestCase):
    def test_passes(self):
        self.assertEqual('hipeac', 'hipeac')
