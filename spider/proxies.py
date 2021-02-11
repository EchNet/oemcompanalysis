from django.conf import settings


class ProxyManager:
  proxy = settings.PROXY_URL
  proxies = {
      "http": proxy,
      "https": proxy,
  } if proxy else None
