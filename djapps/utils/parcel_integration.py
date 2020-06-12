import os

from django.conf import settings
from html.parser import HTMLParser
from os.path import isfile


class WebAssetFinder(HTMLParser):
  # For integration with parcel JS/CSS bundler.

  def __init__(self, **kwargs):
    super().__init__()
    self.url_prefix = kwargs.get("url_prefix", None)
    self._find_assets()

  def handle_starttag(self, tag, attrs):
    attrs = dict(attrs)
    if tag == "link" and attrs.get("rel", None) == "stylesheet":
      self._stylesheets.append(attrs.get("href")[1:])  # remove leading slash
    if tag == "script":
      self._scripts.append(attrs.get("src")[1:])

  def _find_assets(self):
    self._stylesheets = []
    self._scripts = []
    if isfile("dist/index.html"):
      # Development mode: scrape the name of the compiled JS file and CSS files out of the
      # index file in the parcel dist folder.
      with open("dist/index.html", "r") as input_file:
        self.feed(input_file.read())
    else:
      # Production: JS and CSS files were built by "npm build".
      self._stylesheets = ["index.css"]
      self._scripts = ["index.js"]

  def _prefix_all(self, fnamelist):
    return (os.path.join(settings.STATIC_URL, self.url_prefix, fname) for fname in fnamelist)

  @property
  def stylesheets(self):
    return self._prefix_all(self._stylesheets)

  @property
  def scripts(self):
    return self._prefix_all(self._scripts)
