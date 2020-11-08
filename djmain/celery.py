# isort:skip_file
from __future__ import absolute_import, unicode_literals

import celery
import os
import raven

from raven.contrib.celery import register_logger_signal, register_signal

# set the default Django settings module for the "celery" program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djmain.settings")

from django.conf import settings  # noqa

if settings.RAVEN_DSN:

  class CeleryWithSentry(celery.Celery):
    def on_configure(self):
      client = raven.Client(settings.RAVEN_DSN)
      # register a custom filter to filter out duplicate logs
      register_logger_signal(client)
      # hook into the Celery error handler
      register_signal(client)

  app = CeleryWithSentry("djmain")
else:
  app = celery.Celery("djmain")

# Using a string here means the worker doesn"t have to serialize
# the configuration object to child processes.
# - namespace="CELERY" means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
  print("Request: {0!r}".format(self.request))
