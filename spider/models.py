from django.db import models
from django.utils.translation import ugettext_lazy as _

TYPE_MAX_LENGTH = 16
URL_MAX_LENGTH = 120
METHOD_MAX_LENGTH = 60


class SeedPage(models.Model):
  """
    Where to start crawling, and for what purpose.
  """

  # The absolute URL of the page.
  url = models.CharField(
      blank=False,
      null=False,
      max_length=URL_MAX_LENGTH,
      verbose_name=_("url"),
  )

  # At which phase of the crawl is this seed page accessed?
  type = models.CharField(
      blank=False,
      null=False,
      max_length=TYPE_MAX_LENGTH,
      choices=(("website", "website"), ),
      verbose_name=_("type"),
  )

  # The scraping method. This corresponds to the name of a subtype of scrapy.Spider
  method = models.CharField(
      blank=False,
      null=False,
      max_length=METHOD_MAX_LENGTH,
      verbose_name=_("method"),
  )
