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

    def list_buckets(self, **kwargs):
        children = self.fs.glob('*/')

        for child in children:
            bucket_name = child.info.name

            if not self.fs.isdir(str(bucket_name)):
                continue

            bucket = self.get_bucket(bucket_name)

            yield bucket

    def get_bucket(self, name: str, **kwargs):
        self.head_bucket(name)

        bucket = models.Bucket \
        (
            name          = name,
            region        = self.region,
            creation_date = self.fs.getdetails(name).modified,
        )

        return bucket

    def create_bucket(self, name: str, **kwargs):
        if self.fs.isdir(str(name)):
            raise exceptions.S3Error('BucketAlreadyExists')

        self.fs.makedir(str(name))

    def delete_bucket(self, name: str, **kwargs):
        if self.fs.isdir(str(name)):
            self.fs.removedir(str(name))

    def head_bucket(self, name: str, **kwargs):
        if not self.fs.isdir(str(name)):
            raise exceptions.S3Error('NoSuchBucket')

    def put_object(self, bucket_name: str, object_key: str, object_data: bytes, **kwargs):
        bucket = self.get_bucket(bucket_name)

        path = pathlib.Path(bucket_name).joinpath(object_key)

        if self.fs.isdir(str(path)):
            raise exceptions.S3Error('InvalidRequest')

        # TODO: Recursively add sub-folders

        # path.parent.mkdir \
        # (
        #     parents  = True,
        #     exist_ok = True,
        # )

        with s3.open(str(path), 'wb') as file:
            file.write(object_data)

    def get_object(self, bucket_name: str, object_key: str, **kwargs):
        self.head_object(bucket_name, object_key)

        path = str(pathlib.Path(bucket_name).joinpath(object_key))

        return self.fs.open(path, 'rb')

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

    def delete_object(self, bucket_name: str, object_key: str, **kwargs):
        self.head_bucket(bucket_name)

        bucket_dir = self.fs.getdetails(bucket_name)

        object_path = bucket_dir.make_path(object_key)

        if not self.fs.is_file(object_path):
            return

        self.fs.remove(object_path)

        # TODO: Recursively delete empty parent directories

        # for parent in path.parents:
        #     if parent == self.path:
        #         break
        #
        #     if not is_dir_empty(parent):
        #         break
        #
        #     parent.rmdir()

    def head_object(self, bucket_name: str, object_key: str, **kwargs):
        self.head_bucket(bucket_name)

        bucket_dir = self.fs.getdetails(bucket_name)

        object_path = bucket_dir.make_path(object_key)

        if self.fs.is_dir(object_path):
            raise exceptions.S3Error('InvalidRequest')

        if not self.fs.is_file(object_path):
            raise exceptions.S3Error('NoSuchKey')
