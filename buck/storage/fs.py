from .. import exceptions

from . import memory

import pathlib
import datetime
import shutil
import os

class FSObject(memory.Object):
    def __init__(self, path):
        self._path = pathlib.Path(str(path)).absolute()

        super().__init__(self._path.name, b'')

    @property
    def size(self):
        return self._path.lstat().st_size

    @property
    def last_modified_date(self):
        return memory.Date(datetime.datetime.fromtimestamp(self._path.lstat().st_mtime))

    def open(self):
        return self._path.open('rb')

class FSBucket(memory.Bucket):
    def __init__(self, path):
        self._path = pathlib.Path(str(path)).absolute()

        super().__init__(self.name)

    @property
    def name(self):
        return self._path.name

    @property
    def creation_date(self):
        return memory.Date(datetime.datetime.fromtimestamp(self._path.lstat().st_ctime))

    def put_object(self, key, data):
        path = self._path.joinpath(key)

        path.parent.mkdir \
        (
            parents  = True,
            exist_ok = True,
        )

        with open(path, 'wb') as file:
            file.write(data)

    def get_object(self, key):
        path = self._path.joinpath(key)

        if not path.is_file():
            raise exceptions.S3Error('NoSuchKey')

        object = FSObject(path)

        return object

    def list_objects(self, **kwargs):
        for path, dirs, files in os.walk(self._path):
            path = pathlib.Path(path)

            for file in files:
                file_path = path.joinpath(file)

                object = FSObject(file_path)

                yield object

    def delete_object(self, key):
        self.head_object(key)

        path = self._path.joinpath(key)

        path.unlink()

    def head_object(self, key):
        self.get_object(key)

class FSSimpleStorageService(memory.SimpleStorageService):
    def __init__(self, path):
        self._path = pathlib.Path(str(path)).absolute()

        super().__init__()

    def get_bucket(self, name):
        path = self._path.joinpath(name)

        if not path.is_dir():
            raise exceptions.S3Error('NoSuchBucket')

        bucket = FSBucket(path)

        return bucket

    def list_buckets(self):
        children = list(self._path.glob('*/'))

        for child in children:
            if child.is_dir():
                bucket = FSBucket(child)

                yield bucket

    def create_bucket(self, name):
        path = self._path.joinpath(name)

        if path.is_dir():
            raise exceptions.S3Error('BucketAlreadyExists')

        path.mkdir()

        bucket = FSBucket(path)

        return bucket

    def delete_bucket(self, name):
        self.head_bucket(name)

        path = self._path.joinpath(name)

        shutil.rmtree(path)

    def head_bucket(self, name, **kwargs):
        self.get_bucket(name)
