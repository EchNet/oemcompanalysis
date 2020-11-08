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


class WebsiteAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "domain_name",
  )


class PartAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "part_number",
  )


class PartPriceAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "date",
      "part_number",
  )


class PartCostPointAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "start_date",
      "part_number",
  )


admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Website, WebsiteAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(PartPrice, PartPriceAdmin)
admin.site.register(PartCostPoint, PartCostPointAdmin)
