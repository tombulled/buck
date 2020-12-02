from .. import stack
from .. import exceptions

from . import entities
from . import validation
from .types import BucketName, ObjectKey

import datetime
import io

# from typing import Union

class SimpleStorageService(stack.StackService):
    _storage = {}
    _region = entities.Region('us-east-2')

    def list_buckets(self):
        for bucket in self._storage.values():
            yield bucket['bucket']

    @validation.validate_arguments
    def get_bucket(self, name: BucketName):
        self.head_bucket(name)

        return self._storage[name]['bucket']

    @validation.validate_arguments
    def create_bucket(self, name: BucketName):
        if name in self._storage:
            raise exceptions.S3Error('BucketAlreadyExists')

        bucket = entities.Bucket \
        (
            name = name,
            region = self._region,
            creation_date = datetime.datetime.now(),
        )

        self._storage[bucket.name] = \
        {
            'bucket': bucket,
            'objects': {},
        }

    @validation.validate_arguments
    def delete_bucket(self, name: BucketName):
        if name in self._storage:
            del self._storage[name]

    @validation.validate_arguments
    def head_bucket(self, name: BucketName, **kwargs):
        if name not in self._storage:
            raise exceptions.S3Error('NoSuchBucket')

    @validation.validate_arguments
    def put_object(self, bucket_name: BucketName, object_key: ObjectKey, object_data: bytes):
        bucket = self.get_bucket(bucket_name)

        object = entities.Object \
        (
            key = object_key,
            bucket = bucket,
            last_modified_date = datetime.datetime.now(),
        )

        self._storage[bucket.name]['objects'][object.key] = object

    @validation.validate_arguments
    def get_object(self, bucket_name: BucketName, object_key: ObjectKey):
        self.head_object(bucket_name, object_key)

        data = self._storage[bucket_name]['objects'][object_key]['data']

        return io.BytesIO(data)

    @validation.validate_arguments
    def list_objects(self, bucket_name: BucketName):
        self.head_bucket(bucket_name)

        for object in self._storage[bucket_name]['objects'].values():
            yield object

    @validation.validate_arguments
    def delete_object(self, bucket_name: BucketName, object_key: ObjectKey):
        self.head_bucket(bucket_name)

        if object_key in self._storage[bucket_name]['objects']:
            del self._storage[bucket_name]['objects'][object_key]

    @validation.validate_arguments
    def head_object(self, bucket_name: BucketName, object_key: ObjectKey):
        if object_key not in self._storage[bucket_name]['objects']:
            raise exceptions.S3Error('NoSuchKey')
