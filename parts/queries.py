from . import models

from collections import OrderedDict


def get_parts_per_cost_price_range(part_filters={}):
  """
    Example:
      { "100-200": [ "XYZ-001", "ABC-002" ],
        "200-250": [ "XYZ-002", "ABC-003" ] }
    Result is OrderedDict. CostPriceRange keys appear in display order.
  """
  values = models.Part.objects.filter(**part_filters).values(
      "part_number", "cost_price_range").order_by("part_number")
  cost_price_ranges = list(set(pair["cost_price_range"] for pair in values))
  cost_price_range_order = {p[1]: p[0] for p in enumerate(models.CostPriceRange.VALUES)}
  cost_price_ranges = sorted(cost_price_ranges, key=lambda cpr: cost_price_range_order[cpr])
  result = OrderedDict()
  for cpr in cost_price_ranges:
    result[cpr] = []
  for pair in values:
    result[pair["cost_price_range"]].append(pair["part_number"])
  return result


def get_pricing_data_for_part_number_and_date(part_number, date):
  pass
