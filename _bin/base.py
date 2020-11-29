from .. import stack
from .. import exceptions
from .. import utils

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

class SimpleStorageService(stack.StackService):
    def list_buckets(self):
        return utils.generator(())

    def get_bucket(self, name):
        validate_bucket_name(name)

    def create_bucket(self, name):
        validate_bucket_name(name)

    def delete_bucket(self, name):
        validate_bucket_name(name)

    def head_bucket(self, name, **kwargs):
        validate_bucket_name(name)

    def put_object(self, bucket_name, object_key, object_data):
        validate_bucket_name(bucket_name)
        validate_object_key(object_key)

    def get_object(self, bucket_name, object_key):
        validate_bucket_name(bucket_name)
        validate_object_key(object_key)

    def list_objects(self, bucket_name):
        validate_bucket_name(bucket_name)

        return utils.generator(())

    def delete_object(self, bucket_name, object_key):
        validate_bucket_name(bucket_name)
        validate_object_key(object_key)

    def head_object(self, bucket_name, object_key):
        validate_bucket_name(bucket_name)
        validate_object_key(object_key)
