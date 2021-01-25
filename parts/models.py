import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

SHORT_MAX_LENGTH = 16
MEDIUM_MAX_LENGTH = 40
LONG_MAX_LENGTH = 100


class Manufacturer(models.Model):
  """
    A manufacturer of parts.
  """

  # The manufacturer name, e.g. "Subaru"
  name = models.CharField(blank=False,
                          null=False,
                          max_length=MEDIUM_MAX_LENGTH,
                          unique=True,
                          verbose_name=_("name"))

  def __str__(self):
    return self.name


class Website(models.Model):
  """
    A part vendor website.
  """

  # The site domain name, e.g. "subaruautomotiveparts.com"
  domain_name = models.CharField(blank=False,
                                 db_index=True,
                                 null=False,
                                 max_length=MEDIUM_MAX_LENGTH,
                                 unique=True,
                                 verbose_name=_("domain name"))

  # A site can sell parts from multiple manufacturers.
  manufacturers = models.ManyToManyField(to=Manufacturer,
                                         blank=True,
                                         verbose_name=_("manufacturers"))

  # Is this site an OEM client?
  is_client = models.BooleanField(
      blank=False,
      null=False,
      default=False,
      verbose_name=_("is client"),
  )

  # When did entry of data from this site start?
  start_date = models.DateField(
      auto_now_add=True,
      blank=False,
      null=False,
      verbose_name=("start date"),
  )

  # Was this site still reachable, last we checked?
  is_active = models.BooleanField(
      blank=False,
      null=False,
      default=True,
      verbose_name=_("is active"),
  )

  # Distinguish test data.
  for_testing = models.BooleanField(
      blank=False,
      null=False,
      default=False,
      verbose_name=_("for testing"),
  )

  def __str__(self):
    return self.domain_name


class PartType(object):
  PART = "Part"
  ACCESSORY = "Accessory"
  DEFAULT = PART
  CHOICES = ((PART, PART), (ACCESSORY, ACCESSORY))


class CostPriceRange(object):
  # VALUES appear in display order.
  # 500+ applies only to accessories, while 500-1000, 1000-2000 and 2000+ apply to parts.
  VALUES = ("0-50", "50-100", "100-150", "150-200", "200-250", "250-500", "500+", "500-1000",
            "1000-2000", "2000+")
  DEFAULT = VALUES[0]
  CHOICES = ((v, v) for v in VALUES)


class Part(models.Model):
  """
    An automotive part or accessory.  Something that can have a price.
  """

  # The commercial ID as it appears in a part catalog.
  part_number = models.CharField(
      blank=False,
      db_index=True,
      null=False,
      max_length=MEDIUM_MAX_LENGTH,
      unique=True,
      verbose_name=_("part number"),
  )

  # "Part" or "Accessory"
  part_type = models.CharField(blank=False,
                               null=False,
                               max_length=SHORT_MAX_LENGTH,
                               default=PartType.DEFAULT,
                               choices=PartType.CHOICES,
                               verbose_name=_("type"))

  # Descriptive text
  title = models.CharField(
      blank=True,
      db_index=False,
      null=True,
      max_length=MEDIUM_MAX_LENGTH,
      verbose_name=_("title"),
  )

  # "0-50", "50-100", etc.
  cost_price_range = models.CharField(blank=False,
                                      null=False,
                                      max_length=SHORT_MAX_LENGTH,
                                      default=CostPriceRange.DEFAULT,
                                      choices=CostPriceRange.CHOICES,
                                      verbose_name=_("cost price range"))

  # The manufacturer of the part.
  manufacturer = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="parts",
      to=Manufacturer,
      verbose_name=_("manufacturer"),
  )

  # Distinguish test data.
  for_testing = models.BooleanField(
      blank=False,
      null=False,
      default=False,
      verbose_name=_("for testing"),
  )

  def __str__(self):
    return self.part_number

  @property
  def manufacturer_name(self):
    return self.manufacturer.name


class PartPrice(models.Model):
  """
    Price of a part by vendor on a particular day.
  """

  # The date for which this price was obtained.
  date = models.DateField(
      blank=False,
      db_index=True,
      null=False,
      verbose_name=_("date"),
  )

  # The associated part.
  part = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="part_prices",
      to=Part,
      verbose_name=_("part"),
  )

  # The website that the price was obtained from.
  website = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="part_prices",
      to=Website,
      verbose_name=_("website"),
  )

  # The price.
  price = models.DecimalField(
      blank=False,
      decimal_places=2,
      max_digits=9,
      null=False,
      verbose_name=_("price"),
  )

  @property
  def part_number(self):
    return self.part.part_number


class WebsiteExclusion(models.Model):

  # The owner of this filter.
  user = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="website_exclusions",
      to=get_user_model(),
      verbose_name=_("user"),
  )

  # The website to exclude.
  website = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="exclusions",
      to=Website,
      verbose_name=_("website"),
  )


class PartCostPoint(models.Model):
  """
    Cost of a part on a particular date and forward.
  """

  # The associated part.
  part = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="part_cost_points",
      to=Part,
      verbose_name=_("part"),
  )

  # The first date for which this cost applies.
  start_date = models.DateField(
      blank=False,
      db_index=True,
      null=False,
      verbose_name=_("start date"),
  )

  # The cost.
  cost = models.DecimalField(
      blank=False,
      decimal_places=2,
      max_digits=9,
      null=False,
      verbose_name=_("cost"),
  )

  @property
  def part_number(self):
    return self.part.part_number


class UploadProgress(models.Model):

  # The associated user.
  user = models.ForeignKey(
      blank=False,
      db_index=True,
      null=False,
      on_delete=models.CASCADE,
      related_name="uploads",
      to=get_user_model(),
      verbose_name=_("user"),
  )

  # Descriptive text
  type = models.CharField(
      blank=True,
      db_index=False,
      null=True,
      max_length=SHORT_MAX_LENGTH,
      verbose_name=_("type"),
  )

  # Status: "running", "done", "error".
  status = models.CharField(
      blank=False,
      max_length=12,
      null=False,
      default="running",
      verbose_name=_("status"),
  )

  rows_processed = models.PositiveIntegerField(default=0)
  objects_added = models.PositiveIntegerField(default=0)
  errors = models.JSONField(blank=True, null=True)

  created_at = models.DateTimeField(
      auto_now_add=True,
      editable=False,
      verbose_name=_("created at"),
  )

  updated_at = models.DateTimeField(
      auto_now=True,
      editable=False,
      verbose_name=_("updated at"),
  )
