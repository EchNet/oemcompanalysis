from django.db import models
from django.utils.translation import ugettext_lazy as _

IP_MAX_LENGTH = 20
TYPE_MAX_LENGTH = 16
URL_MAX_LENGTH = 120
METHOD_MAX_LENGTH = 60


class WebProxy(models.Model):

  # The IP address.
  ip = models.CharField(
      blank=False,
      null=False,
      max_length=IP_MAX_LENGTH,
      verbose_name=_("IP address"),
  )

  # When created.
  created_at = models.DateTimeField(
      auto_now_add=True,
      editable=False,
      verbose_name=_("created at"),
  )


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


class WebsiteCrawl(models.Model):

  # The website we're reporting on.
  website = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="crawls",
      to="parts.Website",
      verbose_name=_("website"),
  )

  # The set of manufacturers uncovered by this crawl.
  manufacturers = models.ManyToManyField(
      to="parts.Manufacturer",
      verbose_name=_("manufacturers"),
  )

  # Site has no data.
  site_down = models.BooleanField(
      blank=True,
      default=False,
      null=False,
      verbose_name=_("site is down"),
  )

  # What went wrong (normally empty).
  error = models.TextField(verbose_name=_("error"))

  # When created.
  created_at = models.DateTimeField(
      auto_now_add=True,
      editable=False,
      verbose_name=_("created at"),
  )
