from django.conf import settings


def context_settings(request=None):
  return {
      "DEBUG": settings.DEBUG,
      "DEMO": settings.DEMO,
      "STAGING": settings.STAGING,
  }
