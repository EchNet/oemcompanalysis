import logging

from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.utils import dateformat, timezone
from rest_framework import generics, serializers, views
from rest_framework.response import Response

from api import serializers as serializers
from parts import models, tasks
from parts.queries import Queries
from utils.csv import render_to_response_as_csv

logger = logging.getLogger(__name__)


class ManufacturerView(generics.ListAPIView):
  serializer_class = serializers.ManufacturerSerializer

  def get_queryset(self):
    return models.Manufacturer.objects.all().order_by("name")


class WebsiteView(generics.ListAPIView):
  serializer_class = serializers.WebsiteSerializer

  def get_queryset(self):
    q = Queries(self.request.user)
    m = self.request.GET.get("m", None)
    if m is not None:
      q.website_filters = {
          "manufacturers__id": m
      } if m.isnumeric() else {
          "manufacturers__name": m
      }
    return q.get_websites()


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


class PartsPerCostPriceRangeView(views.APIView):
  def get(self, request, *args, **kwargs):
    part_filters = {}
    m = self.request.GET.get("m", None)
    if m is not None:
      if m.isnumeric():
        part_filters["manufacturer_id"] = m
      else:
        part_filters["manufacturer__name"] = m
    t = self.request.GET.get("t", None)
    if t is not None:
      if t not in [c[0] for c in models.PartType.CHOICES]:
        raise serializers.ValidationError(f"{t}: invalid part type")
      part_filters["part_type"] = t
    return Response(Queries(request.user).get_parts_per_cost_price_range(part_filters))


class PartPricingOnDateView(views.APIView):
  def get(self, request, *args, **kwargs):
    part_filters = {"part_number": self.kwargs.get("part_number")}
    d = request.GET.get("d", None)
    if d is not None:
      date = datetime.strptime(d, "%Y-%m-%d").date()
    else:
      date = (timezone.now() - timedelta(days=1)).date()
    result = Queries(request.user).get_part_pricing_on_date(part_filters, date)
    logger.info(f"Part filters={part_filters} date={date}: result={result}")
    return Response(result)


class WebsiteExclusionView(views.APIView):
  def put(self, request):
    user = request.user
    excluded_website_ids = request.GET.get("excluded_website_ids", [])
    user.website_exclusions.set(excluded_website_ids)
    return Response({"status": "OK"})

  def get(self, request):
    user = request.user
    excluded_website_ids = user.website_exclusions.all().values_list("website_id", flat=True)
    return Response({"user": user.id, "excluded_website_ids": excluded_website_ids})
