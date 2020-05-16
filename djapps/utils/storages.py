import boto3
import os
import tempfile

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from storages.backends.s3boto3 import S3Boto3Storage


@deconstructible
class UserUploadPath(object):
  """Return dynamic upload_to paths, containing user id, for file/image fields.

    Usage:
        `upload_to = UserUploadPath('photos/')`
        will store to MEDIA_ROOT/user-id-<user.id>/photos/<filename>

    Reference:
        - https://code.djangoproject.com/ticket/22999
    """
  path = "{0}/{1}/{2}"

  def __init__(self, sub_path):
    self.sub_path = sub_path

  def __call__(self, instance, filename):
    return self.path.format(instance.user.id, self.sub_path, filename)


class BucketStorageHelper:
  """
    A utility for uploading files to S3 and generating download URLs for them.
    In development environment, mocks S3 storage with local file storage.
  """
  DEFAULT_EXPIRATION = 3600  # One hour.

  def __init__(self, bucket_name, *args, **kwargs):
    if bucket_name and settings.AWS_ACCESS_KEY_ID:
      # True S3 access.
      kwargs['bucket'] = bucket_name
      self.storage = S3Boto3Storage(*args, **kwargs)
      self.bucket_name = bucket_name
      self.s3_client = boto3.client(
          's3',
          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    else:
      # Mocked S3 access.
      self.storage = FileSystemStorage()
      self.s3_client = None

  def save_content(self, s3_key, content, **kwargs):
    """
      Copy the given binary content to the S3 bucket and assign it the given key.
    """
    self.storage.save(s3_key, content)

  def generate_download_url(self, s3_key, **kwargs):
    """
      Generate a signed URL that may be used temporarily to download the S3
      object at the given key.
    """
    if self.s3_client:
      expiration = kwargs.get("expiration", self.DEFAULT_EXPIRATION)
      return self.s3_client.generate_presigned_url(
          'get_object', Params={
              "Bucket": self.bucket_name,
              "Key": s3_key
          }, ExpiresIn=expiration)
    else:
      return f"{settings.SITE_URL}/media/{s3_key}"

  def save_content_for_download(self, s3_key, content, **kwargs):
    """
      Copy the given binary content to the S3 bucket and assign it the given key.
      Return a signed URL that may be used temporarily to download the S3 object.
    """
    self.save_content(s3_key, content, **kwargs)
    return self.generate_download_url(s3_key, **kwargs)
