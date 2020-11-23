from . import constants
from . import exceptions

import pathlib
import datetime
import shutil
import magic
import os
import io
import hashlib

class User(object):
    def __init__(self, access_key):
        self.access_key = access_key

    @property
    def id(self) -> str:
        if self.access_key:
            return hashlib.md5(self.access_key.encode()).hexdigest()

        return ''

    @property
    def display_name(self) -> str:
        if self.access_key:
            return self.access_key

        return ''

class Model(object):
    def __iter__(self):
        for attr_key in dir(self.__class__):
            attr_val = getattr(self.__class__, attr_key)

            if isinstance(attr_val, property):
                yield attr_key, getattr(self, attr_key)

class Date(datetime.datetime):
    def __new__(cls, dt: datetime.datetime):
        return super().__new__ \
        (
            cls,
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            dt.tzinfo,
        )

    def __repr__(self):
        return f'<Date: {self!s}>'

    def __str__(self):
        return f'{self.isoformat()}Z'

class SimpleStorageService(object):
    __buckets = []

    # service = 's3'

    def __repr__(self):
        return f'<SimpleStorageService>'

    def get_bucket(self, name):
        for bucket in self.__buckets:
            if bucket.name == name:
                return bucket

    def list_buckets(self):
        return self.__buckets

    def create_bucket(self, name):
        bucket = Bucket(name)

        self.__buckets.append(bucket)

        return bucket

    def delete_bucket(self, name):
        bucket = self.get_bucket(name)

        # if bucket:
        self.__buckets.remove(bucket)

        # return True

    def head_bucket(self, name, **kwargs):
        for bucket in self.__buckets:
            if bucket.name == name:
                return

        raise exceptions.S3Error('NoSuchBucket')

class Region(Model):
    __name = None
    __code = None

    def __init__(self, code: str):
        self.code = code

    def __str__(self):
        return self.code

    def __repr__(self):
        return f'<Region: {self.name} {self.code}>'

    @property
    def name(self): return self.__name

    @property
    def code(self): return self.__code

    @code.setter
    def code(self, value):
        name = constants.REGIONS.get(value)

        if name is None:
            raise ValueError(f'Invalid region code: {value!r}')

        self.__code = value
        self.__name = name

class Object(Model):
    __key: str = None
    __data: bytes = None
    __last_modified_date = None

    def __init__(self, key, data):
        self.__key = key
        self.__data = data

        self.__last_modified_date = Date(datetime.datetime.now())

    def __str__(self):
        return self.key

    def __repr__(self):
        return f'<Object: {self.key}>'

    @property
    def key(self):
        return self.__key

    @property
    def size(self):
        return len(self.__data)

    @property
    def last_modified_date(self):
        return self.__last_modified_date

    def open(self):
        return io.BytesIO(self.__data)

class Bucket(Model):
    __name = None
    __region = None
    __creation_date = None

    __objects = []

    def __init__(self, name, region = Region('us-east-2')):
        self.__name = name
        self.__region = region
        self.__creation_date = Date(datetime.datetime.now())

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Bucket: {self.name} ({self.region!s})>'

    @property
    def name(self):
        return self.__name

    @property
    def creation_date(self):
        return self.__creation_date

    @property
    def arn(self):
        return f'arn:aws:s3::{self.name}'

    @property
    def region(self):
        return self.__region

    def put_object(self, key, data):
        object = Object(key, data)

        self.__objects.append(object)

        return object

    def get_object(self, key):
        for object in self.__objects:
            if object.key == nakeyme:
                return object

    def list_objects(self):
        return self.__objects

    def delete_object(self, key):
        object = self.get_object(key)

        if object is not None:
            self.__objects.remove(object)

        return True

    def head_object(self, key):
        return self.get_object(key) is not None

##################################################

class FSSimpleStorageService(SimpleStorageService):
    def __init__(self, path):
        self._path = pathlib.Path(str(path)).absolute()

        super().__init__()

    def get_bucket(self, name):
        path = self._path.joinpath(name)

        if not path.is_dir():
            # raise Exception('bucket doesnt exist')
            return

        bucket = FSBucket(path)

        return bucket

    def list_buckets(self):
        children = list(self._path.glob('*/'))

        buckets = []

        for child in children:
            if child.is_dir():
                bucket = FSBucket(child)

                buckets.append(bucket)

        return buckets

    def create_bucket(self, name):
        path = self._path.joinpath(name)

        if path.is_dir():
            # raise Exception('bucket already exists')
            return

        path.mkdir()

        bucket = FSBucket(path)

        return bucket

    def delete_bucket(self, name):
        bucket = self.get_bucket()

        # if bucket is not None:
        shutil.rmtree(bucket._path)

        # return True

    def head_bucket(self, name, **kwargs):
        path = self._path.joinpath(name)

        if not path.is_dir():
            raise exceptions.S3Error('NoSuchBucket')

class FSObject(Object):
    def __init__(self, path):
        self._path = pathlib.Path(str(path)).absolute()

        super().__init__(self._path.name, b'')

    @property
    def size(self):
        return self._path.lstat().st_size

    @property
    def last_modified_date(self):
        return Date(datetime.datetime.fromtimestamp(self._path.lstat().st_mtime))

    def open(self):
        return self._path.open('rb')

class FSBucket(Bucket):
    def __init__(self, path):
        self._path = pathlib.Path(str(path)).absolute()

        super().__init__(self.name)

    @property
    def name(self):
        return self._path.name

    @property
    def creation_date(self):
        return Date(datetime.datetime.fromtimestamp(self._path.lstat().st_ctime))

    def put_object(self, key, data):
        path = self._path.joinpath(key)

        if path.exists():
            return # Error

        path.parent.mkdir \
        (
            parents  = True,
            exist_ok = True,
        )

        with open(path, 'wb') as file:
            file.write(data)

    def get_object(self, key):
        path = self._path.joinpath(key)

        if not path.exists():
            return

        object = FSObject(path)

        return object

    def list_objects(self, *, prefix=''):
        if prefix:
            tree = self._path.joinpath(prefix)
        else:
            tree = self._path

        if not tree.is_dir():
            return [] # Error

        for path, dirs, files in os.walk(tree):
            path = pathlib.Path(path)

            for file in files:
                file_path = path.joinpath(file)

                object = FSObject(file_path)

                yield object

    def delete_object(self, key):
        object = self.get_object(key)

        if object is not None:
            object._path.unlink()

    def head_object(self, key):
        path = self._path.joinpath(key)

        return path.exists()

#########################################################

"""
class Object(object):
    def __init__(self, path):
        path = pathlib.Path(str(path)).absolute()

        self.path = path

    def __str__(self):
        return '<{class_name}({path})>'.format \
        (
            class_name = self.__class__.__name__,
            path = repr(str(self.path)),
        )

    def __repr__(self):
        return self.__str__()

    def _as_dict(self):
        data = \
        {
            'name': self.name,
            'creation_date': self.creation_date,
            'mime_type': self.mime_type,
            'last_modified': self.last_modified_date,
            'size': self.size,
        }

        return data

    def _touch(self):
        if self._exists(): return

        self.path.parent.mkdir \
        (
            parents = True,
            exist_ok = True,
        )

        with open(self.path, 'w') as file:
            pass

    def _exists(self):
        return self.path.exists()

    @property
    def name(self):
        return self.path.name

    @property
    def creation_date(self):
        return datetime.datetime.fromtimestamp(self.path.lstat().st_ctime)

    @property
    def last_modified_date(self):
        return datetime.datetime.fromtimestamp(self.path.lstat().st_mtime)

    @property
    def size(self):
        return self.path.lstat().st_size

    @property
    def mime_type(self):
        return magic.from_file(str(self.path), mime = True)

    def delete(self):
        if not self._exists(): return True

        self.path.unlink()

        return True

class Bucket(object):
    def __init__(self, path):
        path = pathlib.Path(str(path)).absolute()

        self.path = path

    def __str__(self):
        return '<{class_name}({path})>'.format \
        (
            class_name = self.__class__.__name__,
            path = repr(str(self.path)),
        )

    def __repr__(self):
        return self.__str__()

    def _as_dict(self):
        data = \
        {
            'name': self.name,
            'creation_date': self.creation_date,
        }

        return data

    def _touch(self):
        if self._exists(): return

        self.path.mkdir \
        (
            parents = True,
            exist_ok = True,
        )

    def _exists(self):
        return self.path.exists()

    @property
    def name(self):
        return self.path.name

    @property
    def creation_date(self):
        return datetime.datetime.fromtimestamp(self.path.lstat().st_ctime)

    def put_object(self, path, data):
        path = self.path.joinpath(path)

        object = Object(path)

        if object._exists(): return

        object._touch()

        with object.path.open('wb') as file:
            file.write(data)

        return object

    def get_object(self, path):
        path = self.path.joinpath(path)

        object = Object(path)

        return object

    def list_objects(self, *, prefix=''):
        if prefix:
            tree = self.path.joinpath(prefix)
        else:
            tree = self.path

        if not tree.is_dir():
            return [] # Error

        for path, dirs, files in os.walk(tree):
            path = pathlib.Path(path)

            for file in files:
                file_path = path.joinpath(file)

                object = Object(file_path)

                yield object

class Storage(object):
    def __init__(self, path):
        path = pathlib.Path(str(path)).absolute()

        path.mkdir \
        (
            parents = True,
            exist_ok = True,
        )

        self.path = path

    def __str__(self):
        return '<{class_name}({path})>'.format \
        (
            class_name = self.__class__.__name__,
            path = repr(str(self.path)),
        )

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _to_bucket(path):
        return Bucket(path)

    def _create_bucket(self, name, bucket_type):
        path = self.path.joinpath(name)

        bucket = bucket_type(path)

        if bucket._exists(): return

        bucket._touch()

        return bucket

    def get_bucket(self, name):
        path = self.path.joinpath(name)

        bucket = self._to_bucket(path)

        if bucket._exists(): return bucket

    def list_buckets(self):
        children = list(self.path.glob('*/'))

        buckets = []

        for child in children:
            if not child.is_dir():
                continue

            bucket = self._to_bucket(child)

            buckets.append(bucket)

        return buckets

    def create_bucket(self, name):
        return self._create_bucket(name, Bucket)

    def delete_bucket(self, name):
        path = self.path.joinpath(name)

        bucket = self._to_bucket(path)

        if not bucket._exists(): return False

        shutil.rmtree(str(path))

        return not bucket._exists()

    def head_bucket(self, name):
        path = self.path.joinpath(name)

        bucket = self._to_bucket(path)

        return bucket._exists()
"""
