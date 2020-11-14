import logging

from django.shortcuts import redirect
from django.views.generic import TemplateView
from rest_framework_jwt.settings import api_settings as jwt_api_settings

logger = logging.getLogger(__name__)


class PageView(TemplateView):
  def get(self, request, *args, **kwargs):
    if not request.user.is_authenticated:
      return redirect("login")
    return super().get(request, *args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context.update({
        "user": self.request.user,
        "token": self.get_token(),
    })
    return context

  def get_token(self):
    jwt_payload_handler = jwt_api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = jwt_api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(self.request.user)
    return jwt_encode_handler(payload)


class HomeView(PageView):
  template_name = "home.html"
