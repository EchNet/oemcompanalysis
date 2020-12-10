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
  def __init__(self, spider, accumulator):
    Process.__init__(self)
    settings = get_project_settings()
    self.crawler = Crawler(spider.__class__, settings)
    self.crawler.signals.connect(self.gather_results, signal=signals.item_passed)
    self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
    self.spider = spider
    self.accumulator = accumulator

  def gather_results(self, signal, sender, item, response, spider):
    self.accumulator.take(item)

  def run(self):
    self.crawler.crawl(self.spider)
    reactor.run()


def run_crawler_process(spider, accumulator):
  logger.info("run_crawler_process {spider.name}: start")
  process = CrawlerProcess(spider, accumulator)
  process.start()
  process.join()
  accumulator.log_results()
  logger.info("run_crawler_process {spider.name}: done")


class WebsiteSeedAccumulator:
  item_count = 0

  def take(self, item):
    domain_name = item["domain_name"]
    is_active = item["is_active"]
    parts_models.Website.objects.update_or_create(domain_name=domain_name,
                                                  defaults={"is_active": is_active})
    self.item_count += 1

  def log_results(self):
    logger.info(f"found websites: {self.item_count}")


def update_website_list():
  start_urls = list(models.SeedPage.objects.filter(type="website").values_list("url", flat=True))
  run_crawler_process(
      spiders.WebsiteSeedSpider(start_urls=start_urls),
      WebsiteSeedAccumulator(),
  )


def crawl_website(website):
  start_urls = [f"https://{website.domain_name}/sitemap"]
  run_crawler_process(
      spiders.NullSpider(start_urls=start_urls),
      WebsiteSeedAccumulator(),
  )
