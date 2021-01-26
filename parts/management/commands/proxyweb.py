import requests

from django.core.management.base import BaseCommand


class Command(BaseCommand):
  help = "Run a web request and dump the results to the console."

  def add_arguments(self, parser):
    parser.add_argument("url", nargs=1, type=str)

  def handle(self, *args, **options):
    url = options["url"][0]
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    self.stdout.write(r.text)
