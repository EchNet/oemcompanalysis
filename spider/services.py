import logging, requests
import requests.exceptions

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
  """ Update the list of websites to crawl. """
  start_urls = list(models.SeedPage.objects.filter(type="website").values_list("url", flat=True))
  run_crawler_process(
      spiders.WebsiteSeedSpider(start_urls=start_urls),
      WebsiteSeedAccumulator(),
  )


def crawl_website(website):
  """ Verify that the given website is still active and update its list of manufacturers. """
  website_crawl = models.WebsiteCrawl(website=website)

  def check_home():
    home_url = f"https://www.{website.domain_name}"
    try:
      res = requests.get(home_url)
      conn_error = False
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
      website_crawl.error = str(e)
      conn_error = True
    if conn_error or res.status_code != 301:  # Expected behavior is to redirect to https:
      website_crawl.site_down = True
      website.is_active = False
      website.save()
      return False
    return True

  def parse_makes(makes):
    manufacturers = set()
    for m in makes:
      manufacturer = parts_models.Manufacturer.objects.filter(name=m.get("ui", "")).first()
      if manufacturer:
        manufacturers.add(manufacturer)
    return manufacturers

  def find_manufacturers():
    makes_url = f"https://www.{website.domain_name}/ajax/vehicle-picker/makes/all"
    res = requests.get(makes_url)
    if res.status_code != 200:
      website_crawl.error = f"GET {makes_url} status code {res.status_code}"
    else:
      try:
        return parse_makes(res.json())
      except Exception as e:
        website_crawl.error = str(e)

  manufacturers = find_manufacturers() if check_home() else None

  website_crawl.save()
  if manufacturers is not None:
    website.manufacturers_set.set(manufacturers)
    website_crawl.manufacturers_set.set(manufacturers)
