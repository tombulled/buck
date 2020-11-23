from .. import exceptions
from .. import constants

import datetime
import io

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

    __objects = {}

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

        self.__objects[key] = data

    def get_object(self, key):
        if key not in self.__objects:
            raise exceptions.S3Error('NoSuchKey')

        return self.__objects[key]

    def list_objects(self):
        for object in self.__objects.values():
            yield object

    def delete_object(self, key):
        self.head_object(key)

        del self.__objects[key]

    def head_object(self, key):
        self.get_object(key)

class SimpleStorageService(object):
    __buckets = {}

    __implementation = 'memory'

    def __repr__(self):
        return f'<SimpleStorageService: {self.__implementation}>'

    def get_bucket(self, name):
        if name not in self.__buckets:
            raise exceptions.S3Error('NoSuchBucket')

        return self.__buckets[name]

    def list_buckets(self):
        for bucket in self.__buckets.values():
            yield bucket

    def create_bucket(self, name):
        if name in self.__buckets:
            raise exceptions.S3Error('BucketAlreadyExists')

        bucket = Bucket(name)

        self.__buckets[name] = bucket

        return bucket

    def delete_bucket(self, name):
        self.head_bucket(name)

        del self.__buckets[name]

    def head_bucket(self, name, **kwargs):
        self.get_bucket(name)
