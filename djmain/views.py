import logging

from django.shortcuts import redirect
from django.views.generic import TemplateView

from utils.parcel_integration import WebAssetFinder

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
  """
    The home page, which houses the app.
  """
  def get(self, request, *args, **kwargs):
    if not request.user.is_authenticated:
      return redirect("login")
    return super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    web_asset_finder = WebAssetFinder(url_prefix="rapp")
    context = super().get_context_data(**kwargs)
    context.update({
        "stylesheets": web_asset_finder.stylesheets,
        "scripts": web_asset_finder.scripts,
        "user": self.request.user,
    })
    return context
