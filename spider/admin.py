from django.contrib import admin

from . import models


@admin.register(models.SeedPage)
class SeedPageAdmin(admin.ModelAdmin):
  list_display = (
      "url",
      "type",
  )
