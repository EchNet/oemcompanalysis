from django.core.management.base import BaseCommand, CommandError
from time import sleep

from .getpartprice import Command as GetPartPriceCommand
from parts import models


class Command(BaseCommand):
  help = "Get all part prices from website"

  def handle(self, *args, **options):
    for website in models.Website.objects.all():
      if website.is_active:
        domain = website.domain_name
        try:
          for m in website.manufacturers.all():
            self.stdout.write(self.style.SUCCESS(f"{domain} : scanning {m} parts"))
            for p in models.Part.objects.filter(manufacturer=m):
              info = GetPartPriceCommand.search_website_for_part_price(website, p)
              self.stdout.write(self.style.SUCCESS(f"{domain} : {str(info)}"))
              sleep(1)
        except Exception as e:
          self.stderr.write(f"{domain}: {e}")
