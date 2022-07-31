from . import abc
from .. import models
from .... import exceptions

import fs
import pathlib

from fs.base import FS

class SimpleStorageServiceSession(abc.SimpleStorageServiceSession):
    fs: FS
    region: models.Region = models.Region('us-east-2')

    def __init__(self, *, service, stack, user):
        super().__init__ \
        (
            service = service,
            stack   = stack,
            user    = user,
            fs      = service.fs,
        )

    def _bucket_exists(self, name: str):
        return self.fs.isdir(name)

    def _get_bucket(self, name: str):
        if self._bucket_exists(name):
            return models.Bucket \
            (
                name          = name,
                region        = self.region,
                creation_date = self.fs.getdetails(name).modified,
                owner         = None,
            )

    def _get_owned_bucket(self, name: str):
        if bucket := self._get_bucket(name):
            if bucket.owner in (None, self.user):
                return bucket

    def _object_exists(self, bucket_name: str, object_key: str):
        object_path = str(pathlib.Path(bucket_name).joinpath(object_key))

        return self.fs.isfile(object_path)

    def _get_object(self, bucket_name: str, object_key: str):
        if self._object_exists(bucket_name, object_key):
            object_path = str(pathlib.Path(bucket_name).joinpath(object_key))

            file_details = self.fs.getdetails(object_path)

            return models.Object \
            (
                key                = object_key,
                bucket             = bucket,
                last_modified_date = file_details.modified,
            )

    def list_buckets(self, **kwargs):
        '''Returns a list of all buckets owned by the authenticated sender of the request.'''

        children = self.fs.glob('*/')

        for child in children:
            if bucket := self._get_owned_bucket(child.info.name):
                yield bucket

    def create_bucket(self, name: str, **kwargs):
        if bucket := self._get_bucket(name):
            if bucket.owner == self.user:
                raise exceptions.S3Error('BucketAlreadyOwnedByYou')

            raise exceptions.S3Error('BucketAlreadyExists')

        self.fs.makedir(name)

    def delete_bucket(self, name: str, **kwargs):
        if bucket := self._get_owned_bucket(name):
            self.fs.removedir(bucket.name)

    def head_bucket(self, name: str, **kwargs):
        if not self._get_owned_bucket(name):
            raise exceptions.S3Error('NoSuchBucket')

    def put_object(self, bucket_name: str, object_key: str, object_data: bytes, **kwargs):
        self.head_bucket(bucket_name)

        path = pathlib.Path(bucket_name).joinpath(object_key)

        if self.fs.isdir(str(path)):
            raise exceptions.S3Error('InvalidRequest')

        for parent in map(str, list(path.parents)[-3::-1]):
            if self.fs.isfile(parent):
                raise exceptions.S3Error('InvalidRequest')

            if not self.fs.isdir(parent):
                self.fs.makedir(parent)

        with self.fs.open(str(path), 'wb') as file:
            file.write(object_data)

    def get_object(self, bucket_name: str, object_key: str, **kwargs):
        self.head_object(bucket_name, object_key)

        path = str(pathlib.Path(bucket_name).joinpath(object_key))

        return self.fs.open(path, 'rb')

    '''
    def list_objects(self, bucket_name: str, **kwargs):
        bucket = self.get_bucket(bucket_name)

        for path, dirs, files in self.fs.walk():
            path = pathlib.Path(path)

            for file in files:
                object_key = str(path.joinpath(file.name))

                file_details = self.fs.getdetails(object_key)

                object = models.Object \
                (
                    key                = object_key,
                    bucket             = bucket,
                    last_modified_date = file_details.modified,
                )

                yield object
    '''

    def delete_object(self, bucket_name: str, object_key: str, **kwargs):
        self.head_bucket(bucket_name)

        if self._object_exists(bucket_name, object_key):
            path = pathlib.Path(bucket_name).joinpath(object_key)

            if self.fs.isfile(str(path)):
                self.fs.remove(str(path))

            for parent in map(str, list(path.parents)[:-2]):
                if self.fs.isempty(parent):
                    self.fs.removedir(parent)

    def head_object(self, bucket_name: str, object_key: str, **kwargs):
        self.head_bucket(bucket_name)
        
        if not self._object_exists(bucket_name, object_key):
            raise exceptions.S3Error('NoSuchKey')
