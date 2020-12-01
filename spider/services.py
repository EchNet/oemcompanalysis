import logging, scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher

from . import models, spiders
from parts import models as parts_models

logger = logging.getLogger(__name__)


def update_website_list():
  logger.info("update_website_list: start")
  results = {"item_count": 0}

  def gather_results(signal, sender, item, response, spider):
    parts_models.Website.objects.update_or_create(domain_name=item["domain_name"],
                                                  defaults={"is_active": item["is_active"]})
    results["item_count"] += 1

  dispatcher.connect(gather_results, signal=scrapy.signals.item_passed)

  process = CrawlerProcess({})
  start_urls = list(models.SeedPage.objects.filter(type="website").values_list("url", flat=True))
  logger.info(f"update_website_list: start_urls={start_urls}")
  process.crawl(spiders.WebsiteSeedSpider, start_urls=start_urls)
  process.start(stop_after_crawl=False)

  dispatcher.disconnect(gather_results, signal=scrapy.signals.item_passed)
  logger.info(f"update_website_list done: items: {results['item_count']}")
