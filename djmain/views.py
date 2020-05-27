import logging

from django.shortcuts import redirect
from django.views.generic.base import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
  """
    The home page.
  """
  def get(self, request, *args, **kwargs):
    if not request.user.is_authenticated:
      return redirect("login")
    return super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["user"] = self.request.user
    return context
