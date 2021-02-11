import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from parts import models
from spider.revolution import RevolutionPartsScanner


class Command(BaseCommand):
  help = "Update the list of manufacturers for a domain."

  def add_arguments(self, parser):
    parser.add_argument("domain", nargs="+", type=str)

  def handle(self, *args, **options):
    for domain in options["domain"]:
      self.stdout.write(self.style.SUCCESS(f"{domain} : scanning"))
      Command.scan_domain(domain)

  @staticmethod
  def scan_domain(domain):
    try:
      website = models.Website.objects.filter(domain_name=domain).get()
    except models.Website.DoesNotExist:
      raise CommandError(f"{domain}: no such website")
    info = Command.scan_website(website)
    if info:
      Command.apply_info_to_website(info, website)

  @staticmethod
  def scan_website(website):
    try:
      domain = website.domain_name
      info = RevolutionPartsScanner(domain).scan_domain()
      return info
    except requests.exceptions.HTTPError:
      raise CommandError(f"{domain}: HTTP error")

  @staticmethod
  def apply_info_to_website(info, website):
    if "manufacturers" in info:
      for m in info["manufacturers"]:
        manufacturer, created = models.Manufacturer.objects.get_or_create(name=m)
        website.manufacturers.add(manufacturer)
