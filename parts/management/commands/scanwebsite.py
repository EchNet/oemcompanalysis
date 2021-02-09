import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from parts import models


class Command(BaseCommand):
  help = "Update the list of manufacturers for a domain."

  def add_arguments(self, parser):
    parser.add_argument("domain", nargs="+", type=str)

  def handle(self, *args, **options):
    for domain in options["domain"]:
      try:
        website = models.Website.objects.filter(domain_name=domain).get()
      except models.Website.DoesNotExist:
        raise CommandError(f"{domain}: no such website")
      self.stdout.write(self.style.SUCCESS(f"{domain} : scanning"))
      try:
        info = Command.scan_domain(domain)
      except requests.exceptions.HTTPError:
        raise CommandError(f"{domain}: HTTP error")
      self.stdout.write(self.style.SUCCESS(f"{domain} : {str(info)}"))
      if info:
        Command.apply_domain_info_to_website(info, website)

  @staticmethod
  def scan_domain(domain_name):
    #if settings.DEBUG: return {"manufacturers": ["Buick", "Volkswagen"]}
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": f"https://www.{domain_name}/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "oeminteractive.com",
    }
    r = requests.get(f"https://www.{domain_name}/ajax/vehicle-picker/makes/all",
                     timeout=1,
                     headers=headers)
    r.raise_for_status()
    try:
      rj = r.json()
    except Exception:
      return None
    return {"manufacturers": [obj["ui"] for obj in rj]}

  @staticmethod
  def apply_domain_info_to_website(info, website):
    if "manufacturers" in info:
      for m in info["manufacturers"]:
        manufacturer, created = models.Manufacturer.objects.get_or_create(name=m)
        website.manufacturers.add(manufacturer)
