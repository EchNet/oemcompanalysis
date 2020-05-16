import logging

from django.views.generic.base import TemplateView

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
  template_name = "home.html"
