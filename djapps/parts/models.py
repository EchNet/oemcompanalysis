import datetime

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
                          verbose_name=_("name"))


class Website(models.Model):
  """
    A part vendor website.
  """

  # The site domain name, e.g. "subaruautomotiveparts.com"
  domain_name = models.CharField(blank=False,
                                 db_index=True,
                                 null=False,
                                 max_length=MEDIUM_MAX_LENGTH,
                                 verbose_name=_("domain name"))

  # A site can sell parts from multiple manufacturers.
  manufacturers = models.ManyToManyField(to=Manufacturer, verbose_name=_("manufacturers"))

  # Is this site an OEM client?
  is_client = models.BooleanField(
      blank=False,
      null=False,
      default=False,
      verbose_name=_("is client"),
  )

  # When did entry of data from this site start?
  start_date = models.DateField(blank=False,
                                null=False,
                                default=datetime.date.today,
                                verbose_name=("start date"))


class PartType(object):
  PART = "Part"
  ACCESSORY = "Accessory"
  DEFAULT = PART
  CHOICES = ((PART, PART), (ACCESSORY, ACCESSORY))


class CostPriceRange(object):
  VALUES = ("0-50", "50-100", "100-150", "150-200", "200-300", "300-500", "500+", "500-1000",
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
      verbose_name=_("part number"),
  )

  # "Part" or "Accessory"
  part_type = models.CharField(blank=False,
                               null=False,
                               max_length=SHORT_MAX_LENGTH,
                               default=PartType.DEFAULT,
                               choices=PartType.CHOICES,
                               verbose_name=_("type"))

  # "0-50", "50-100", etc.
  cost_price_range = models.CharField(blank=False,
                                      null=False,
                                      max_length=SHORT_MAX_LENGTH,
                                      default=CostPriceRange.DEFAULT,
                                      choices=CostPriceRange.CHOICES,
                                      verbose_name=_("type"))

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
