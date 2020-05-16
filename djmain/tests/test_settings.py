from django.test import TestCase
from django.conf import settings


class SettingsTestCase(TestCase):
  def test_env(self):
    self.assertEqual(settings.ENV, "DEV")
    self.assertFalse(settings.DEBUG)
    self.assertFalse(settings.DEMO)
    self.assertFalse(settings.STAGING)
