import logging

from celery import shared_task
from django.utils import timezone

from . import models, services
from parts import models as parts_models
from parts.management.commands.scanwebsite import Command as ScanWebsiteCommand
from parts.management.commands.getpartprice import Command as GetPartPriceCommand

logger = logging.getLogger(__name__)

# Number of seconds to pause between scrapes.
COUNTDOWN_INCREMENT = 1


@shared_task
def run_full_scrape():
  logger.info("run_full_scrape: START")
  countdown = COUNTDOWN_INCREMENT
  for website in models.Website.objects.filter(is_active=True, for_testing=False):
    logger.debug(f"delay run_website_scan({website})")
    run_website_scan.apply_async(args=[website.id], countdown=countdown)
    countdown += COUNTDOWN_INCREMENT
  run_full_prices_scrape.apply_async(countdown=countdown)
  logger.info("run_full_scrape: DONE")


@shared_task
def run_website_scan(website_id):
  # Update the website's status and set of manufacturers.
  logger.info(f"run_website_scan({website_id}): START")
  website = parts_models.Website.objects.get(id=website_id)
  info = ScanWebsiteCommand.scan_domain(website.domain_name)
  logger.debug(f"run_website_scan: website={website} info={str(info)}")
  if info:
    ScanWebsiteCommand.apply_domain_info_to_website(info, website)
  logger.info(f"run_website_scan({website_id}): DONE")


@shared_task
def run_full_prices_scrape():
  logger.info("run_full_prices_scrape: START")
  countdown = COUNTDOWN_INCREMENT
  for part in Part.objects.filter(is_active=True, for_testing=False):
    logger.debug(f"delay run_parts_prices_scrape({part})")
    run_part_prices_scrape.apply_async(args=[part.id], countdown=countdown)
    countdown += COUNTDOWN_INCREMENT
  logger.info("run_full_prices_scrape: DONE")


@shared_task
def run_part_prices_scrape(part_id):
  # Find prices for this part on websites that might carry it.
  logger.info(f"run_part_prices_scrape({part_id}): START")
  part = parts_models.Part.objects.get(id=part_id)
  for website in Website.objects.filter(manufacturers=part.manufacturer):
    try:
      info = GetPartPriceCommand.search_website_for_part_price(website, part)
      logger.debug(f"run_part_prices_scrape: website={website} part={part} info={str(info)}")
      if info:
        GetPartPriceCommand.record_part_price(info, website=website, part=part)
    except Exception:
      logger.exception(f"Error searching {website} for {part}")
  logger.info(f"run_part_prices_scrape({part_id}): DONE")
