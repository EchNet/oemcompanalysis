import re, scrapy
from datetime import datetime, timedelta


class NullSpider(scrapy.Spider):
  """ Temporary, for testing. """
  name = 'null'
  start_urls = []

  def __init__(self, *args, **kwargs):
    self.start_urls = kwargs.pop("start_urls", self.start_urls)
    super().__init__(*args, **kwargs)

  def parse(self, response):
    pass


class WebsiteSeedSpider(scrapy.Spider):
  name = 'website_seed'
  start_urls = ['https://viewdns.info/reverseip/?host=34.199.110.134&t=1']
  url_pattern = '^([A-Za-z0-9]\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\.){1,3}[A-Za-z]{2,6}$'

  def __init__(self, *args, **kwargs):
    self.start_urls = kwargs.pop("start_urls", self.start_urls)
    super().__init__(*args, **kwargs)

  def parse(self, response):
    expired = (datetime.now() - timedelta(7)).date()
    for row in response.xpath('//tr'):
      row_contents = row.xpath('td/text()').getall()
      if len(row_contents) != 2:
        continue
      domain = row_contents[0].lower()
      if not re.match(self.url_pattern, domain):
        continue
      last_resolved_date = row_contents[1]
      try:
        last_resolved_date = datetime.strptime(last_resolved_date, "%Y-%m-%d").date()
      except Exception as e:
        continue
      is_active = last_resolved_date > expired
      yield {"domain_name": domain, "is_active": is_active}
