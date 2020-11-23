import json, logging, re, requests, urllib

from dateutil.parser import parse
from django.core.exceptions import ValidationError

from .models import Manufacturer, Part, PartPrice, PartCostPoint, Website

logger = logging.getLogger(__name__)


class GenericLoader:
  @staticmethod
  def normalize_header(header):
    header = re.sub(r"""[^a-zA-Z0-9]+""", " ", header)
    return header.strip().lower()

  def __init__(self, reader, *args, **kwargs):
    self.reader = reader
    self.kwargs = kwargs

  def process(self, updater=None):
    self.objects_added = []
    self.errors = []
    self.mappings = None
    row_index = -1
    rows_processed = 0

    keep_going = True
    for row in self.reader:
      row_index += 1
      if not "".join(row):  # Ignore empty rows
        continue
      try:
        if not self.mappings:
          self._map_headers(row)
        else:
          rows_processed += 1
          obj, created = self._process_row(row)
          if created:
            self.objects_added.append(obj)
      except ValidationError as e:
        for msg in iter(e):
          self.errors.append(f"row {row_index + 1}: {str(msg)}")
        keep_going = self.mappings is not None
      except Exception as e:
        self.errors.append(f"row {row_index + 1}: {str(e)}")
        keep_going = self.mappings is not None
      if updater:
        updater(status="running" if keep_going else "error",
                rows_processed=rows_processed,
                objects_added=len(self.objects_added),
                errors=self.errors)
      if not keep_going:
        return
    updater(status="done")

  def _process_row(self, row):
    data = {}
    for f in self.KEY_FIELDS + self.FIELDS:
      data[f] = row[self.mappings[f]] if self.mappings[f] < len(row) else ""
    keys, fields = self._map_data(data)
    return (self.MODEL_CLASS).objects.update_or_create(**keys, defaults=fields)

  def _map_headers(self, row):
    mappings = {}
    for idx, val in enumerate(row):
      h = self.normalize_header(val)
      if h in self.KEY_FIELDS + self.FIELDS:
        mappings[h] = idx

    # Check that all fields are present.
    missing_fields = []
    for field_name in self.FIELDS:
      if field_name not in mappings:
        missing_fields.append(field_name)
    if missing_fields:
      raise ValidationError("The data file is missing required %s field%s." %
                            (", ".join(missing_fields), "s" if len(missing_fields) != 1 else ""))
    self.mappings = mappings


class PartsLoader(GenericLoader):

  KEY_FIELDS = ["partnumber"]
  FIELDS = ["parttype", "costpricerange", "title", "manufacturer"]
  MODEL_CLASS = Part

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["part_number"] = data["partnumber"]
    fields["part_type"] = data["parttype"]
    fields["cost_price_range"] = data["costpricerange"]
    fields["title"] = data["title"]
    fields["manufacturer"] = Manufacturer.objects.get(name=data["manufacturer"])
    return keys, fields


class PricesLoader(GenericLoader):

  KEY_FIELDS = ["date", "website", "partnumber"]
  FIELDS = ["partprice"]
  MODEL_CLASS = PartPrice

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["date"] = data["date"]
    keys["website"] = Website.objects.get(domain_name=data["website"])
    keys["part"] = Part.objects.get(part_number=data["partnumber"])
    fields["price"] = data["partprice"]
    return keys, fields


class CostsLoader(GenericLoader):

  KEY_FIELDS = ["date", "partnumber"]
  FIELDS = ["cost"]
  MODEL_CLASS = PartCostPoint

  def _map_data(self, data):
    keys = {}
    fields = {}
    keys["start_date"] = data["date"]
    keys["part"] = Part.objects.get(part_number=data["partnumber"])
    fields["cost"] = data["cost"]
    return keys, fields
