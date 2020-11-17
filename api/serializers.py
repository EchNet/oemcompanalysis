from rest_framework import serializers

from parts.models import (Manufacturer, Website, Part)


class ManufacturerSerializer(serializers.ModelSerializer):
  class Meta:
    model = Manufacturer
    fields = ("id", "name")


class PartSerializer(serializers.ModelSerializer):
  class Meta:
    model = Part
    fields = ("id", "part_number", "part_type", "cost_price_range", "manufacturer")


class WebsiteSerializer(serializers.ModelSerializer):
  class Meta:
    model = Website
    fields = ("id", "domain_name", "is_client", "start_date")
