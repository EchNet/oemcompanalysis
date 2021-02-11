import requests

from lxml import html

from spider.proxies import ProxyManager

TIMEOUT_SECONDS = 4


class RevolutionPartsScanner:
  def __init__(self, domain_name):
    self.domain_name = domain_name

  def scan_domain(self):
    url = f"https://www.{self.domain_name}/ajax/vehicle-picker/makes/all"
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": f"https://www.{self.domain_name}/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "oeminteractive.com",
    }
    r = requests.get(url, timeout=TIMEOUT_SECONDS, headers=headers, proxies=ProxyManager.proxies)
    r.raise_for_status()
    try:
      rj = r.json()
    except Exception:
      return None
    return {"manufacturers": [obj["ui"] for obj in rj]}

  def search_for_part_price(self, part_number):
    url = f"https://www.{self.domain_name}/search?search_str={part_number}"
    headers = {
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": f"https://www.{self.domain_name}/",
        "user-agent": "oeminteractive.com",
    }
    r = requests.get(url, timeout=TIMEOUT_SECONDS, headers=headers, proxies=ProxyManager.proxies)
    r.raise_for_status()
    htmldoc = html.fromstring(r.content)
    prices = htmldoc.xpath('//span[contains(@class,"sale-price-amount")]/text()')
    print(prices)
    if prices:
      price = prices[0].replace("$", "")
      return {"price": price}
    else:
      return {"message": "No price found in page."}
