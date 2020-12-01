from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from . import models


@admin.register(models.Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "name",
  )
  search_fields = ("name", )


@admin.register(models.Website)
class WebsiteAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "domain_name",
  )
  list_filter = ("is_active", )
  search_fields = ("domain_name", )


@admin.register(models.Part)
class PartAdmin(admin.ModelAdmin):
  list_display = ("id", "part_number", "manufacturer")
  search_fields = ("part_number", "title")
  list_filter = (
      AutocompleteFilterFactory("Manufacturer", "manufacturer"),
      "part_type",
      "cost_price_range",
  )

  class Media:  # See django-admin-autocomplete-filter docs
    pass


@admin.register(models.PartPrice)
class PartPriceAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "date",
      "part",
  )
  list_filter = (
      AutocompleteFilterFactory("Part", "part"),
      AutocompleteFilterFactory("Website", "website"),
      "date",
  )


@admin.register(models.PartCostPoint)
class PartCostPointAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "start_date",
      "part",
  )
  list_filter = (AutocompleteFilterFactory("Part", "part"), "start_date")


@admin.register(models.UploadProgress)
class ProgressAdmin(admin.ModelAdmin):
  list_display = ("created_at", "type", "user", "status")
