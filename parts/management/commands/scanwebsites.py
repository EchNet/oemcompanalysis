from django.core.management.base import BaseCommand, CommandError
from time import sleep

from .scanwebsite import Command as ScanWebsiteCommand
from parts import models


class Command(BaseCommand):
  help = "Update the list of manufacturers for all domains."

  def handle(self, *args, **options):
    for website in models.Website.objects.all():
      if website.is_active:
        domain = website.domain_name
        self.stdout.write(self.style.SUCCESS(f"{domain} : scanning"))
        try:
          info = ScanWebsiteCommand.scan_domain(domain)
          self.stdout.write(self.style.SUCCESS(f"{domain} : {str(info)}"))
          if info:
            ScanWebsiteCommand.apply_domain_info_to_website(info, website)
        except Exception as e:
          self.stderr.write(f"{domain}: {e}")
        sleep(1)
