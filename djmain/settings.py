"""
 Django app settings.
"""
import datetime, os, raven, sys

from celery.schedules import crontab
from decouple import config
from dj_database_url import parse as db_url

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPS_ROOT = SITE_ROOT
sys.path.insert(0, APPS_ROOT)

# Environment
DEBUG = config("DEBUG", cast=bool, default=False)
STAGING = config("STAGING", cast=bool, default=False)
DEMO = config("DEMO", cast=bool, default=False)
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"
SITE_URL = config("SITE_URL")
ALLOWED_HOSTS = ["*"]

# Web server
USE_X_FORWARDED_PORT = True

# Application definition
INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # 3rd party
    "admin_auto_filters",
    "django_extensions",
    "django_object_actions",
    "djcelery_email",
    "raven.contrib.django.raven_compat",
    "storages",
    "widget_tweaks",
    "corsheaders",
    "rest_framework",
    "rest_framework_swagger",
    'import_export',

    # custom apps
    "parts",
    "spider",
)

MIDDLEWARE = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    "utils.middleware.MySslMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # to serve static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

ROOT_URLCONF = "djmain.urls"
WSGI_APPLICATION = "djmain.wsgi.application"

# Caching
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "MAX_ENTRIES": 1000,
        }
    }
}

# Database
DATABASES = {"default": config("DATABASE_URL", cast=db_url)}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DATABASES["default"]["CONN_MAX_AGE"] = 60

# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [config("REDIS_URL")],
        },
    },
}

# Authentication
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/login/"
LOGIN_ERROR_URL = "/login-error/"
LOGOUT_REDIRECT_URL = LOGIN_URL
SECRET_KEY = config("SECRET_KEY")
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": ("django.contrib.auth.password_validation"
                 ".UserAttributeSimilarityValidator")
    },
    {
        "NAME": ("django.contrib.auth.password_validation"
                 ".MinimumLengthValidator")
    },
    {
        "NAME": ("django.contrib.auth.password_validation"
                 ".CommonPasswordValidator")
    },
    {
        "NAME": ("django.contrib.auth.password_validation"
                 ".NumericPasswordValidator")
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        # Send all messages to console
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        # This is the "catch all" logger
        "": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": True,
            "filters": ["require_debug_true"]
        },
    }
}

# SSL
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", cast=bool, default=True)

# Static files
SERVE_MEDIA = DEBUG
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, "media")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, "static")
STATICFILES_DIRS = (os.path.join(SITE_ROOT, "static_dev"), )
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(SITE_ROOT, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "djmain.context_processors.context_settings",
                "parts.context_processors.context_settings",
            ],
        },
    },
]

# celery
CELERY_ACCEPT_CONTENT = ["application/x-python-serialize", "application/json"]
CELERY_BROKER_URL = config("REDIS_URL")
CELERY_REDIS_MAX_CONNECTIONS = 4
CELERY_RESULT_BACKEND = config("REDIS_URL")
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_RESULT_EXPIRES = 60 * 60  # seconds
CELERY_TASK_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_WORKER_CONCURRENCY = 2
CELERY_BEAT_SCHEDULER = "redbeat.RedBeatScheduler"
CELERY_BEAT_SCHEDULE = {
    "nightly": {
        "task": "spider.tasks.run_full_crawl",
        "schedule": crontab(minute="0", hour="1"),  # every day at 1am
        "options": {
            "expires": 30 * 60  # seconds
        }
    },
    "celery.backend_cleanup": {
        "task": "celery.backend_cleanup",
        "schedule": crontab(minute="0", hour="*"),  # every hour
        "options": {
            "expires": 30 * 60  # seconds
        }
    },
}

# raven/sentry
RAVEN_DSN = config("RAVEN_DSN", default=None)
try:
  release = raven.fetch_git_sha(SITE_ROOT)
except Exception:
  # TODO: Fix this
  release = None
if RAVEN_DSN:
  RAVEN_CONFIG = {
      "dsn": RAVEN_DSN,
      # "release": raven.fetch_git_sha(SITE_ROOT),
  }
  if release:
    RAVEN_CONFIG["release"] = release

# storages
DEFAULT_FILE_STORAGE = config("DEFAULT_FILE_STORAGE")
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default=None)
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default=None)
AWS_DOWNLOAD_BUCKET_NAME = config("AWS_DOWNLOAD_BUCKET_NAME", default=None)
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "private"

# rest_framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
    ],
}

# JWT
JWT_AUTH = {
    "JWT_ALLOW_REFRESH": True,
    "JWT_AUTH_HEADER_PREFIX": "JWT",
    "JWT_EXPIRATION_DELTA": datetime.timedelta(days=1),
    "JWT_REFRESH_EXPIRATION_DELTA":
    datetime.timedelta(days=1),  # There is no point in exceeding JWT_EXPIRATION_DELTA
    "JWT_SECRET_KEY": SECRET_KEY,
    "JWT_VERIFY": True,
    "JWT_VERIFY_EXPIRATION": True,
}
