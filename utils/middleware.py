from django.conf import settings
from django.http import HttpResponseRedirect


class MySslMiddleware(object):
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):

    if not any([
        settings.DEBUG,
        request.is_secure(),
        request.META.get("HTTP_X_FORWARDED_PROTO", "") == 'https'
    ]):
      url = request.build_absolute_uri(request.get_full_path())
      secure_url = url.replace("http://", "https://")
      response = HttpResponseRedirect(secure_url)
    else:
      response = self.get_response(request)
    return response
