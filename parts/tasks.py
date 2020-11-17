import csv, logging

from celery import shared_task
from io import StringIO

from .models import UploadProgress
from .services import PartsLoader, PricesLoader, CostsLoader

logger = logging.getLogger(__name__)


def do_upload(LoaderClass, what, upload_progress_id, string_data):
  def update_progress(*args, **kwargs):
    UploadProgress.objects.filter(id=upload_progress_id).update(**kwargs)

  LoaderClass(csv.reader(StringIO(string_data))).process(update_progress)


@shared_task
def run_parts_upload(upload_progress_id, string_data):
  do_upload(PartsLoader, "parts", upload_progress_id, string_data)


@shared_task
def run_prices_upload(upload_progress_id, string_data):
  do_upload(PricesLoader, "prices", upload_progress_id, string_data)


@shared_task
def run_costs_upload(upload_progress_id, string_data):
  do_upload(CostsLoader, "costs", upload_progress_id, string_data)
