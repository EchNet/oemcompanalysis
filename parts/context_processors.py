from django.conf import settings

from .models import CostPriceRange, PartType


def context_settings(request=None):
  return {
      "CostPriceRange": CostPriceRange,
      "PartType": PartType,
  }
