from ..... import exceptions

from . import fs
from .. import types

def catch(type, error):
    class Wrapper(type):
        def __init__(self, value: str):
            if self.validate(value) is not None:
                raise exceptions.S3Error(error)

            super().__init__(value)

    return Wrapper

# NOTE: This current model doesn't work for specific errors, e.g. KeyTooLongError
BucketName = catch(types.BucketName, 'InvalidBucketName')
ObjectKey  = catch(types.BucketName, 'InvalidRequest')

class SimpleStorageService(fs.SimpleStorageService):
    def list_buckets(self, **kwargs):
        return super().list_buckets(**kwargs)

    def get_bucket(self, name: str, **kwargs):
        return super().get_bucket \
        (
            str(BucketName(name)),
            **kwargs,
        )

    def create_bucket(self, name: str, **kwargs):
        return super().create_bucket \
        (
            str(BucketName(name)),
            **kwargs,
        )

    def delete_bucket(self, name: str, **kwargs):
        return super().delete_bucket \
        (
            str(BucketName(name)),
            **kwargs,
        )

    def head_bucket(self, name: str, **kwargs):
        return super().head_bucket \
        (
            str(BucketName(name)),
            **kwargs,
        )

    def put_object(self, bucket_name: str, object_key: str, object_data: bytes, **kwargs):
        return super().put_object \
        (
            str(BucketName(bucket_name)),
            str(ObjectKey(object_key)),
            object_data,
            **kwargs,
        )

    def get_object(self, bucket_name: str, object_key: str, **kwargs):
        return super().get_object \
        (
            str(BucketName(bucket_name)),
            str(ObjectKey(object_key)),
            **kwargs,
        )

    def list_objects(self, bucket_name: str, **kwargs):
        return super().list_objects \
        (
            str(BucketName(bucket_name)),
            **kwargs,
        )

    def delete_object(self, bucket_name: str, object_key: str, **kwargs):
        return super().delete_object \
        (
            str(BucketName(bucket_name)),
            str(ObjectKey(object_key)),
            **kwargs,
        )

    def head_object(self, bucket_name: str, object_key: str, **kwargs):
        return super().head_object \
        (
            str(BucketName(bucket_name)),
            str(ObjectKey(object_key)),
            **kwargs,
        )
