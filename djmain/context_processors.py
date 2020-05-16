from django.conf import settings


def settings_constants(request=None):
  return dict(
      DEBUG=settings.DEBUG,
      STAGING=settings.STAGING,
      DEMO=settings.DEMO,
      DEFAULT_FROM_EMAIL=settings.DEFAULT_FROM_EMAIL,
      ENV=settings.ENV,
      ENV_COLOR=settings.ENV_COLOR,
      SITE_URL=settings.SITE_URL,
      STRIPE_PUBLISHABLE_KEY=settings.STRIPE_PUBLISHABLE_KEY,
      SUPPORT_URL=settings.SUPPORT_URL,
      REACT_APP_SERVER=settings.REACT_APP_SERVER,
      GOOGLE_SIGNIN_CLIENT_ID=settings.GOOGLE_SIGNIN_CLIENT_ID,
  )
