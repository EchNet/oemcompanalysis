import random

from datetime import date
from decimal import Decimal
from django.utils.crypto import get_random_string

from parts.models import *


def create_test_data():
  create_test_manufacturers()
  create_test_websites()
  create_test_parts()
  create_test_part_costs()
  create_test_part_prices()


def remove_test_data():
  Website.objects.filter(for_testing=True).delete()
  Part.objects.filter(for_testing=True).delete()


def create_test_manufacturers():
  Manufacturer.objects.get_or_create(name="Ford")
  Manufacturer.objects.get_or_create(name="Honda")
  Manufacturer.objects.get_or_create(name="Nissan")
  Manufacturer.objects.get_or_create(name="Subaru")
  Manufacturer.objects.get_or_create(name="Toyota")
  Manufacturer.objects.get_or_create(name="Volkswagen")


def create_test_websites():
  manufacturers = list(Manufacturer.objects.all())
  for m in manufacturers:
    for suffix in ("-parts.com", "-parts.net", "stuff.com"):
      website, created = Website.objects.get_or_create(domain_name=f"{m.name.lower()}{suffix}",
                                                       defaults=dict(
                                                           is_client=True,
                                                           is_active=True,
                                                           for_testing=True,
                                                           start_date='2021-01-10',
                                                       ))
      if website.for_testing:
        website.manufacturers.set([m])

  for prefix in ("abc", "bcd", "cde", "def", "efg", "fgh", "123", "456", "000", "ace", "wow"):
    website, created = Website.objects.get_or_create(domain_name=f"{prefix}parts.com",
                                                     defaults=dict(
                                                         is_client=True,
                                                         is_active=True,
                                                         for_testing=True,
                                                         start_date='2021-01-10',
                                                     ))
    if website.for_testing:
      assign_random_manufacturers(website, manufacturers.copy())


def assign_random_manufacturers(website, manufacturers):
  ms = []
  while manufacturers:
    m = random.choice(manufacturers)
    ms.append(m)
    manufacturers.remove(m)
    if random.randint(0, 4):
      break
  website.manufacturers.set(ms)


def create_test_parts():
  for m in Manufacturer.objects.all():
    create_test_parts_of_type(m, PartType.PART, 60,
                              ("0-50", "50-100", "100-150", "150-200", "200-250", "250-500",
                               "500-1000", "1000-2000", "2000+"))
    create_test_parts_of_type(
        m, PartType.ACCESSORY, 25,
        ("0-50", "50-100", "100-150", "150-200", "200-250", "250-500", "500+"))


def create_test_parts_of_type(manufacturer, part_type, target_count, cost_price_ranges):
  count = manufacturer.parts.filter(part_type=part_type, for_testing=True).count()
  while count < target_count:
    part = Part.objects.create(part_number=generate_part_number(),
                               part_type=part_type,
                               cost_price_range=random.choice(cost_price_ranges),
                               manufacturer=manufacturer,
                               for_testing=True)
    count += 1


def generate_part_number():
  p1 = get_random_string(length=3)
  p2 = get_random_string(length=4)
  p3 = get_random_string(length=4)
  return f"{p1}-{p2}-{p3}"


COSTS_FOR_RANGE = {
    "0-50": (Decimal("1.99"), Decimal("25.99"), Decimal("45.99")),
    "50-100": (Decimal("50.99"), Decimal("75.99"), Decimal("99.99")),
    "100-150": (Decimal("100.99"), Decimal("125.99"), Decimal("145.99")),
    "150-200": (Decimal("150.99"), Decimal("175.99"), Decimal("195.99")),
    "200-250": (Decimal("200.99"), Decimal("225.99"), Decimal("245.99")),
    "250-500": (Decimal("250.99"), Decimal("275.99"), Decimal("495.99")),
    "500-1000": (Decimal("500.99"), Decimal("750.99"), Decimal("899.99")),
    "1000-2000": (Decimal("1000.99"), Decimal("1500.99"), Decimal("1899.99")),
    "2000+": (Decimal("2000.99"), Decimal("2500.99"), Decimal("3000")),
    "500+": (Decimal("500.99"), Decimal("600.99"), Decimal("700")),
}


def create_test_part_costs():
  for p in Part.objects.filter(for_testing=True):
    PartCostPoint.objects.create(
        part=p,
        start_date=date.today(),
        cost=random.choice(COSTS_FOR_RANGE[p.cost_price_range]),
    )


def create_test_part_prices():
  for p in Part.objects.filter(for_testing=True):
    part_cost_point = p.part_cost_points.order_by("-start_date").first()
    cost = part_cost_point.cost if part_cost_point else COSTS_FOR_RANGE[p.cost_price_range][0]
    for w in Website.objects.filter(for_testing=True, manufacturers=p.manufacturer):
      markup = 1.05 + ((hash(w.domain_name) % 40) / 100.0)
      price = Decimal(str(round(float(cost) * markup)) + ".99")
      PartPrice.objects.create(
          date=date.today(),
          part=p,
          website=w,
          price=price,
      )
