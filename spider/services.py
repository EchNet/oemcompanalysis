import logging

from billiard.context import Process
from scrapy.crawler import Crawler
from scrapy import signals
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from . import models, spiders
from parts import models as parts_models

logger = logging.getLogger(__name__)


class CrawlerProcess(Process):
  def __init__(self, spider):
    Process.__init__(self)
    settings = get_project_settings()
    self.crawler = Crawler(spider.__class__, settings)
    self.crawler.signals.connect(self.gather_results, signal=signals.item_passed)
    self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
    self.item_count = 0
    self.spider = spider

  def gather_results(self, signal, sender, item, response, spider):
    parts_models.Website.objects.update_or_create(domain_name=item["domain_name"],
                                                  defaults={"is_active": item["is_active"]})
    self.item_count += 1

  def run(self):
    self.crawler.crawl(self.spider)
    reactor.run()


def update_website_list():
  logger.info("update_website_list: start")
  start_urls = list(models.SeedPage.objects.filter(type="website").values_list("url", flat=True))
  logger.info(f"update_website_list: start_urls={start_urls}")
  process = CrawlerProcess(spiders.WebsiteSeedSpider(start_urls=start_urls))
  process.start()
  process.join()
  logger.info(f"update_website_list done: items: {process.item_count}")
