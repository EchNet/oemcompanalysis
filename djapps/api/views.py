import logging

from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseNotAllowed
from rest_framework import status
from rest_framework.response import Response
from rest_framework import views

import api.serializers as serializers

logger = logging.getLogger(__name__)


class BaseApiView(views.APIView):
  class Meta:
    methods = {}

  def handle_request(self, request):
    try:
      logger.info(f"{self.__class__.__name__} {request.method} input={request.data}")
      action = getattr(self, f"do_{request.method.lower()}")
      data = action(request)
      method_descriptor = self.Meta.methods[request.method]
      response_status = method_descriptor.get("ok_response_status", status.HTTP_200_OK)
      many = method_descriptor.get("many", False)
      serializer = method_descriptor.get("serializer", serializers.ThingSerializer)
      response_payload = {"data": serializer(data, many=many).data}
      logger.info(response_payload)
    except ValidationError as ve:
      response_payload = {
          "message": "Invalid request.",
          "errors": ve.args,
      }
      response_status = status.HTTP_400_BAD_REQUEST
    except Http404:
      response_payload = {
          "message": "Not found.",
      }
      response_status = status.HTTP_404_NOT_FOUND
    except Exception as e:
      logger.error(e)
      raise e
    return Response(response_payload, response_status)

  def post(self, request, *args, **kwargs):
    if "POST" in self.Meta.methods:
      return self.handle_request(request)
    return HttpResponseNotAllowed(self.Meta.methods.keys())

  def get(self, request, *args, **kwargs):
    if "GET" in self.Meta.methods:
      return self.handle_request(request)
    return HttpResponseNotAllowed(self.Meta.methods.keys())


class ListThingsView(BaseApiView):
  class Meta:
    methods = {
        "GET": {
            "serializer": serializers.ThingSerializer,
            "many": True,
        }
    }

  def do_get(self, request):
    return [
        {
            "text": "Raindrops on roses"
        },
        {
            "text": "Whiskers on kittens"
        },
        {
            "text": "Bright copper kettles"
        },
        {
            "text": "Warm woolen mittens"
        },
    ]
