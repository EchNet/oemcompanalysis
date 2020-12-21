import logging

from celery import shared_task

from . import models, services
from parts import models as parts_models
from parts import queries as parts_queries

logger = logging.getLogger(__name__)


@shared_task
def run_full_crawl():
  logger.info("run_full_crawl: START")
  services.update_proxy_ips()
  services.update_website_list()
  start_website_crawls()
  logger.info("run_full_crawl: DONE")


def start_website_crawls():
  for website in parts_queries.get_websites({"is_active": True}):
    run_website_crawl.delay(website.id)


@shared_task
def run_website_crawl(website_id):
  logger.info(f"run_website_crawl({website_id}): START")
  website = parts_models.Website.objects.get(id=website_id)
  services.crawl_website(website)
  logger.info(f"run_website_crawl({website_id}): DONE")
