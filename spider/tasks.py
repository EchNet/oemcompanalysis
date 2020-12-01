import logging

from celery import shared_task

from . import models, services
from parts import models as parts_models
from parts import queries as parts_queries

logger = logging.getLogger(__name__)


@shared_task
def run_full_scrape():
  services.update_website_list()
  for website in parts_queries.get_websites({"active": True}):
    run_website_scrape.delay(website.id)


@shared_task
def run_website_scrape(website_id):
  website = parts_models.Website.objects.get(website_id)
  logger.info("run_website_scrape", 
