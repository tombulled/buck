from .. import exceptions

from . import entities

def validate_bucket_name(bucket_name: str) -> None:
    try:
        entities.Bucket.valid_name(bucket_name)
    except ValueError:
        raise exceptions.S3Error('InvalidBucketName')

def validate_object_key(object_key: str) -> None:
    try:
        entities.Object.valid_key(object_key)
    except ValueError:
        raise exceptions.S3Error('InvalidArgument')
