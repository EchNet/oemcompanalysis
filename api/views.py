import logging

from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.utils import dateformat, timezone
from rest_framework import generics, views
from rest_framework.response import Response

from api import serializers as serializers
from parts import models, tasks
from utils.csv import render_to_response_as_csv

logger = logging.getLogger(__name__)


class ManufacturerView(generics.ListAPIView):
  serializer_class = serializers.ManufacturerSerializer

  def get_queryset(self):
    return models.Manufacturer.objects.all().order_by("name")


class WebsiteView(generics.ListAPIView):
  serializer_class = serializers.WebsiteSerializer

  def get_queryset(self):
    return models.Website.objects.all().order_by("domain_name")


class ManufacturerWebsiteView(generics.ListAPIView):
  serializer_class = serializers.WebsiteSerializer

  def get_queryset(self):
    manufacturer_id = self.kwargs.get("manufacturer_id")
    manufacturer = get_object_or_404(models.Manufacturer.objects.all(), id=manufacturer_id)
    return models.Website.objects.filter(
        manufacturers__id=manufacturer_id).order_by("domain_name")


class PartView(generics.ListAPIView):
  serializer_class = serializers.PartSerializer

  def get_queryset(self):
    return models.Part.objects.all().order_by("part_number")


class PartsView(views.APIView):
  def post(self, request):
    file = request.FILES.get("file", None)
    string_data = file.read().decode("utf-8")
    up = models.UploadProgress.objects.create(user=request.user, type="parts")
    tasks.run_parts_upload.delay(up.id, string_data)
    return Response({"progress_id": up.id})

  def get(self, request):
    manufacturer_id = request.GET.get("manufacturer", "")
    query = models.Part.objects.all()
    if manufacturer_id:
      query = query.filter(manufacturer_id=manufacturer_id)
    csv_data = {
        "headers": ("PartNumber", "PartType", "Title", "CostPriceRange", "Manufacturer"),
        "rows": []
    }
    for part in query:
      row = []
      row.append(part.part_number)
      row.append(part.part_type)
      row.append(part.title)
      row.append(part.cost_price_range)
      row.append(part.manufacturer.name)
      csv_data["rows"].append(row)
    return render_to_response_as_csv(csv_data, filename='parts.csv')


class PricesView(views.APIView):
  def post(self, request):
    file = request.FILES.get("file", None)
    string_data = file.read().decode("utf-8")
    up = models.UploadProgress.objects.create(user=request.user, type="prices")
    tasks.run_prices_upload.delay(up.id, string_data)
    return Response({"progress_id": up.id})

  def get(self, request):
    manufacturer_id = request.GET.get("manufacturer", "")
    query = models.PartPrice.objects.all()
    if manufacturer_id:
      query = query.filter(part__manufacturer_id=manufacturer_id)
    csv_data = {"headers": ("Date", "Website", "PartNumber", "PartPrice"), "rows": []}
    for price in query:
      row = []
      row.append(dateformat.format(price.date, "Y-m-d"))
      row.append(price.website.domain_name)
      row.append(price.part.part_number)
      row.append(price.price)
      csv_data["rows"].append(row)
    return render_to_response_as_csv(csv_data, filename='prices.csv')


class CostsView(views.APIView):
  def post(self, request):
    file = request.FILES.get("file", None)
    string_data = file.read().decode("utf-8")
    up = models.UploadProgress.objects.create(user=request.user, type="costs")
    tasks.run_costs_upload.delay(up.id, string_data)
    return Response({"progress_id": up.id})

  def get(self, request):
    manufacturer_id = request.GET.get("manufacturer", "")
    query = models.PartCostPoint.objects.all()
    if manufacturer_id:
      query = query.filter(part__manufacturer_id=manufacturer_id)
    csv_data = {"headers": ("Date", "PartNumber", "Cost"), "rows": []}
    for cost in query:
      row = []
      row.append(dateformat.format(cost.start_date, "Y-m-d"))
      row.append(cost.part.part_number)
      row.append(cost.cost)
      csv_data["rows"].append(row)
    return render_to_response_as_csv(csv_data, filename='costs.csv')


class ProgressView(views.APIView):
  def get(self, request, *args, **kwargs):
    progress_id = self.kwargs.get("progress_id")
    progress = get_object_or_404(request.user.uploads.all(), id=progress_id)
    return Response({
        "status": progress.status,
        "rows_processed": progress.rows_processed,
        "objects_added": progress.objects_added,
        "errors": progress.errors,
    })


class ReportView(views.APIView):
  def get(self, request, *args, **kwargs):
    manufacturer_id = request.GET.get("manufacturer")
    manufacturer = get_object_or_404(models.Manufacturer.objects.all, id=manufacturer_id)
    part_type = request.GET.get("parttype")
    if part_type not in [c[0] for c in models.PartType.CHOICES]:
      raise ValueError(part_type)
    date = (timezone.now() - timedelta(days=1)).date()
    Part.objects.filter(manufacturer=manufacturer, part_type=part_type)
    return Response({})
