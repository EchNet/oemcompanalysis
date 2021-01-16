import logging

from collections import OrderedDict
from django.db.models import Case, IntegerField, When, Value

from . import models

logger = logging.getLogger(__name__)


class AnnotatedWebsite:
  def __init__(self, website, user):
    self.id = website.id
    self.domain_name = website.domain_name
    self.excluded = models.WebsiteExclusion.objects.filter(website=website, user=user).exists()
    self.manufacturers = (m for m in website.manufacturers.all())


class Queries:
  def __init__(self, user):
    self.user = user

  def get_manufacturers(self):
    return models.Manufacturer.objects.all().order_by("name")

  def get_websites(self, website_filters={}):
    return models.Website.objects.filter(**website_filters).exclude(
        exclusions__user=self.user).order_by("domain_name")

  def get_annotated_websites(self):
    return (AnnotatedWebsite(w, self.user)
            for w in models.Website.objects.all().order_by("domain_name"))

  def get_parts_per_cost_price_range(self, part_filters={}):
    """
      Example:
        { { range: "100-200", parts: [ "XYZ-001", "ABC-002" ] },
          { range: "200-250", parts: [ "XYZ-002", "ABC-003" ] } }
      Result is OrderedDict. CostPriceRange keys appear in display order.
    """
    values = models.Part.objects.filter(**part_filters).values(
        "part_number", "cost_price_range").order_by("part_number")
    cost_price_ranges = list(set(pair["cost_price_range"] for pair in values))
    cost_price_range_order = {p[1]: p[0] for p in enumerate(models.CostPriceRange.VALUES)}
    cost_price_ranges = sorted(cost_price_ranges, key=lambda cpr: cost_price_range_order[cpr])
    lookup = OrderedDict()
    for cpr in cost_price_ranges:
      lookup[cpr] = []
    for pair in values:
      lookup[pair["cost_price_range"]].append(pair["part_number"])
    return [{"range": k, "parts": v} for k, v in lookup.items()]

  @staticmethod
  def get_part_cost_for_date(part, date):
    return models.PartCostPoint.objects.filter(
        part=part, start_date__lte=date).order_by("-start_date").first()

  def get_part_pricing_on_date(self, part_filters, date):
    """
      Example:
      {
        part_number: "XYZ-001",
        cost: 50,
        by_website: {
          "parts1.com": { price: 55, markup: 0.10, rank: 1 },
          "parts2.com": { price: 51, markup: 0.02, rank: 2 }
        }
      }
    """
    part = models.Part.objects.filter(**part_filters).get()
    prices = models.PartPrice.objects.filter(
        part=part, date=date, website__manufacturers=part.manufacturer).exclude(
            website__exclusions__user=self.user).distinct("website").values(
                "price", "website__domain_name")
    prices = list(prices)
    prices = sorted(prices, key=lambda d: d.get("price"), reverse=True)
    cost = self.get_part_cost_for_date(part, date)
    by_website = {}
    for pe in enumerate(prices):
      p = pe[1]
      p["rank"] = pe[0] + 1
      if cost:
        p["markup"] = round(((p["price"] - cost.cost) / cost.cost) * 100, 1)
      domain_name = p.pop("website__domain_name")
      by_website[domain_name] = p

    result = {
        "part_number": part.part_number,
        "cost": cost.cost if cost else None,
        "by_website": by_website
    }
    return result
