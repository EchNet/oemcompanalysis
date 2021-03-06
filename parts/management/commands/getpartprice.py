import requests

from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from parts import models
from spider.revolution import RevolutionPartsScanner


class Command(BaseCommand):
  help = "Search a website for the price of a part it might carry."

  def add_arguments(self, parser):
    parser.add_argument("domain", nargs=1, type=str)
    parser.add_argument("part_number", nargs="?", type=str)

  def handle(self, *args, **options):
    domain = options["domain"][0]
    if options["part_number"]:
      try:
        website = models.Website.objects.filter(domain_name=domain).get()
      except models.Website.DoesNotExist:
        raise CommandError(f"{domain}: no such website")

      part_number = options["part_number"]
      try:
        part = models.Part.objects.filter(part_number=part_number).get()
      except models.Part.DoesNotExist:
        raise CommandError(f"{part_number}: no such part")

      self.stdout.write(self.style.SUCCESS(f"{domain} : searching"))
      try:
        info = Command.search_website_for_part_price(website, part)
      except requests.exceptions.HTTPError:
        raise CommandError(f"{domain}: HTTP error")

      self.stdout.write(self.style.SUCCESS(f"{domain} : {str(info)}"))
      Command.record_part_price(info, website, part)
    else:
      info = Command.scan_url_for_part_price(domain)
      self.stdout.write(self.style.SUCCESS(str(info)))

  @staticmethod
  def search_website_for_part_price(website, part):
    return RevolutionPartsScanner(website.domain_name).search_for_part_price(part.part_number)

  @staticmethod
  def record_part_price(info, website, part):
    if info is not None and "price" in info:
      models.PartPrice.objects.create(date=timezone.now().date(),
                                      part=part,
                                      website=website,
                                      price=Decimal(info["price"]))
