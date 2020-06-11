import logging
import os

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from html.parser import HTMLParser
from os.path import isfile

logger = logging.getLogger(__name__)

AUTHENTICATE = False


class HomeView(TemplateView):
  """
    The home page.
  """
  def get(self, request, *args, **kwargs):
    if AUTHENTICATE and not request.user.is_authenticated:
      return redirect("login")
    return super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["user"] = self.request.user
    return context

  class IndexHtmlParser(HTMLParser):
    def __init__(self):
      super().__init__()
      self.stylesheets = []
      self.scripts = []

    def handle_starttag(self, tag, attrs):
      attrs = dict(attrs)
      if tag == "link" and attrs.get("rel", None) == "stylesheet":
        self.stylesheets.append(attrs.get("href")[1:])  # remove leading slash
      if tag == "script":
        self.scripts.append(attrs.get("src")[1:])

  def get_context_data(self, **kwargs):
    # Scrape the name of the compiled JS file out of the index file in the
    # parcel dist folder.
    parser = self.IndexHtmlParser()
    if isfile("dist/index.html"):
      with open("dist/index.html", "r") as input_file:
        parser.feed(input_file.read())
      stylesheets = parser.stylesheets
      scripts = parser.scripts
    else:
      stylesheets = ["index.css"]
      scripts = ["index.js"]

    def prefix_all(fnamelist):
      return (os.path.join(settings.STATIC_URL, "rapp", fname) for fname in fnamelist)

    return {
        "stylesheets": prefix_all(stylesheets),
        "scripts": prefix_all(scripts),
    }
