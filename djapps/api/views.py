import logging

from rest_framework import generics
from rest_framework.response import Response

from api import serializers as serializers
from parts.models import (Manufacturer, Website, Part)

logger = logging.getLogger(__name__)


class ManufacturerView(generics.ListAPIView):
  serializer_class = serializers.ManufacturerSerializer

  def get_queryset(self):
    return Manufacturer.objects.all().order_by("name")


class WebsiteView(generics.ListAPIView):
  serializer_class = serializers.WebsiteSerializer

  def get_queryset(self):
    return Website.objects.all().order_by("domain_name")


class PartView(generics.ListAPIView):
  serializer_class = serializers.PartSerializer

  def get_queryset(self):
    return Part.objects.all().order_by("part_number")
