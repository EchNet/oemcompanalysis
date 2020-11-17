import json, logging, re, requests, urllib

from dateutil.parser import parse
from django.core.exceptions import ValidationError

from .models import Part, PartPrice, PartCostPoint

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

    for row in self.reader:
      row_index += 1
      if not "".join(row):  # Ignore empty rows
        pass
      elif not self.mappings:
        # Scan for headers to determine schema.
        self._map_headers(row)  # May raise ValidationError
      else:
        try:
          rows_processed += 1
          self.objects_added.append(self._process_row(row))
        except ValidationError as e:
          self.errors.append({'key': row_index, 'row': row, 'error': e})
        if updater:
          updater(rows_processed=rows_processed,
                  objects_added=len(self.objects_added),
                  errors=self.errors)

  def _process_row(self, row):
    data = {}
    for f in self.FIELDS:
      data[f] = row[self.mappings[f]] if self.mappings[f] < len(row) else ""
    return self._process_data(data)
    return (self.MODEL_CLASS).objects.create(**self._map_data(data))

  def _map_headers(self, row):
    mappings = {}
    for idx, val in enumerate(row):
      h = self.normalize_header(val)
      if h in self.FIELDS:
        mappings[h] = idx
      else:
        raise ValidationError(f"Unrecognized header {val}")

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

  FIELDS = set(["partnumber", "parttype", "costpricerange", "manufacturer"])
  MODEL_CLASS = Part

  def _map_data(self, data):
    mapped_data = {}
    mapped_data["part_number"] = data["partnumber"]
    mapped_data["part_type"] = data["parttype"]
    mapped_data["cost_price_range"] = data["costpricerange"]
    mapped_data["manufacturer_id"] = Manufacturer.objects.get(name=data["manufacturer"])
    return mapped_data


class PricesLoader(GenericLoader):

  FIELDS = set(["date", "website", "partnumber", "partprice"])
  MODEL_CLASS = PartPrice

  def _map_data(self, data):
    mapped_data = {}
    mapped_data["date"] = data["date"]
    mapped_data["website"] = Website.objects.get(domain_name=data["website"])
    mapped_data["part"] = Part.objects.get(part_number=data["partnumber"])
    mapped_data["part_price"] = data["partprice"]
    return mapped_data


class CostsLoader(GenericLoader):

  FIELDS = set(["date", "partnumber", "cost"])
  MODEL_CLASS = PartCostPoint

  def _map_data(self, data):
    mapped_data = {}
    mapped_data["start_date"] = data["date"]
    mapped_data["part"] = Part.objects.get(part_number=data["partnumber"])
    mapped_data["cost"] = data["cost"]
    return mapped_data
