import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics, views
from rest_framework.response import Response

from api import serializers as serializers
from parts.models import (Manufacturer, Website, Part, UploadProgress)
from parts.tasks import run_parts_upload, run_prices_upload, run_costs_upload

logger = logging.getLogger(__name__)


class ManufacturerView(generics.ListAPIView):
  serializer_class = serializers.ManufacturerSerializer

  def get_queryset(self):
    return Manufacturer.objects.all().order_by("name")


class WebsiteView(generics.ListAPIView):
  serializer_class = serializers.WebsiteSerializer

  def get_queryset(self):
    return Website.objects.all().order_by("domain_name")


class ManufacturerWebsiteView(generics.ListAPIView):
  serializer_class = serializers.WebsiteSerializer

  def get_queryset(self):
    manufacturer_id = self.kwargs.get("manufacturer_id")
    manufacturer = get_object_or_404(Manufacturer.objects.all(), id=manufacturer_id)
    return Website.objects.filter(manufacturers__id=manufacturer_id).order_by("domain_name")


class PartView(generics.ListAPIView):
  serializer_class = serializers.PartSerializer

  def get_queryset(self):
    return Part.objects.all().order_by("part_number")


class PartsView(views.APIView):
  def post(self, request):
    file = request.FILES.get("file", None)
    string_data = file.read().decode("utf-8")
    up = UploadProgress.objects.create(user=request.user)
    run_parts_upload.delay(up.id, string_data)
    return Response({"progress_id": up.id})


class PricesView(views.APIView):
  def post(self, request):
    file = request.FILES.get("file", None)
    string_data = file.read().decode("utf-8")
    up = UploadProgress.objects.create(user=request.user)
    run_prices_upload.delay(up.id, string_data)
    return Response({"progress_id": up.id})


class CostsView(views.APIView):
  def post(self, request):
    file = request.FILES.get("file", None)
    string_data = file.read().decode("utf-8")
    up = UploadProgress.objects.create(user=request.user)
    run_costs_upload.delay(up.id, string_data)
    return Response({"progress_id": up.id})


class ProgressView(generics.ListAPIView):
  def get(self, request, *args, **kwargs):
    progress_id = self.kwargs.get("progress_id")
    progress = get_object_or_404(request.user.uploads.all(), id=progress_id)
    return Response({
        "status": progress.status,
        "rows_processed": progress.rows_processed,
        "objects_added": progress.objects_added,
        "errors": progress.errors,
    })
