import requests

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
        results = Command.scan_domain(domain)
      except requests.exceptions.HTTPError:
        raise CommandError(f"{domain}: HTTP error")
      self.stdout.write(self.style.SUCCESS(f"{domain} : {str(results)}"))

  @staticmethod
  def scan_domain(domain_name):
    r = requests.get(f"https://www.{domain_name}/ajax/vehicle-picker/makes/all", timeout=1)
    r.raise_for_status()
    try:
      rj = r.json()
    except Exception:
      return None
    return {"manufacturers": [obj["ui"] for obj in rj]}
