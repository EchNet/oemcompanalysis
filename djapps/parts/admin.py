from admin_auto_filters.filters import AutocompleteFilterFactory
from django.contrib import admin

from .models import (
    Manufacturer,
    Website,
    Part,
    PartPrice,
    PartCostPoint,
)


class ManufacturerAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "name",
  )
  search_fields = ("name", )


class WebsiteAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "domain_name",
  )
  search_fields = ("domain_name", )


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


class PartCostPointAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "start_date",
      "part",
  )
  list_filter = (AutocompleteFilterFactory("Part", "part"), "start_date")


admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(PartPrice, PartPriceAdmin)
admin.site.register(PartCostPoint, PartCostPointAdmin)
