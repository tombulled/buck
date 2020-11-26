from . import exceptions
from . import constants
from . import utils

import datetime
import io
import hashlib
import secrets

class Container(object):
    def __iter__(self):
        for attr_key in dir(self.__class__):
            attr_val = getattr(self.__class__, attr_key)

            if isinstance(attr_val, property):
                yield attr_key, getattr(self, attr_key)

class User(object):
    def __init__(self, access_key, secret_key, display_name, id):
        self.access_key = access_key
        self.secret_key = secret_key
        self.display_name = display_name
        self.id = id

    def __repr__(self):
        return f'<User: [{self.display_name}] {self.access_key}>'

    def __str__(self):
        return self.display_name

    def __iter__(self):
        return (item for item in self.__dict__.items())

class FakeUser(User):
    def __init__(self, access_key = None, secret_key = None, display_name = None, id = None):
        if access_key is None:
            access_key = secrets.token_hex(15)

        if secret_key is None:
            secret_key = secrets.token_hex(15)

        if display_name is None:
            display_name = 'User'

        if id is None:
            id = hashlib.md5(access_key.encode()).hexdigest()

        super().__init__ \
        (
            access_key   = access_key,
            secret_key   = secret_key,
            display_name = display_name,
            id           = id,
        )

class Date(datetime.datetime):
    def __new__(cls, dt: datetime.datetime = None):
        if dt is None:
            dt = datetime.datetime.now()

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

class Region(object):
    def __init__(self, code: str):
        name = constants.REGIONS.get(code)

        if name is None:
            raise ValueError(f'Invalid region code: {code!r}')

        self.code = code
        self.name = name

    def __str__(self):
        return self.code

    def __repr__(self):
        return f'<Region: {self.name} {self.code}>'

    def __iter__(self):
        return utils.generator(self.__dict__.items())

class FakeRegion(Region):
    def __init__(self, code = None):
        if code is None:
            code = 'us-east-2'

        super().__init__ \
        (
            code = code,
        )

class Object(object):
    # def __init__(self, service, bucket, key):
    bucket = None

    def __init__(self, key):
        self.key = key
        # self.arn = ...
        # self.size = ...

        self.last_modified_date = Date(datetime.datetime.now())

    def __str__(self):
        return self.key

    def __repr__(self):
        return f'<Object: {self.key}>'

    def __iter__(self):
        return utils.generator(self.__dict__.items())

    def register(self, bucket):
        self.bucket = bucket

    # @property
    # def key(self):
    #     return self.__key
    #
    # @property
    # def size(self):
    #     return len(self.__data)
    #
    # @property
    # def last_modified_date(self):
    #     return self.__last_modified_date
    #
    # @property
    # def arn(self):
    #     return f'arn:aws:s3::{bucket_name}' # TODO

    # def open(self):
    #     return io.BytesIO(self.__data)
    #
    # def write(self, data):
    #     self.__data = data

class _Object(Container):
    __key: str = None
    __data: bytes = None
    __last_modified_date = None

    def __init__(self, service, bucket, key):
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

    @property
    def arn(self):
        return f'arn:aws:s3::{bucket_name}'

    def open(self):
        return io.BytesIO(self.__data)

    def write(self, data):
        self.__data = data

class Bucket(Container):
    __name = None
    __region = None
    __creation_date = None

    __objects = {}

    def __init__(self, service, name, region = Region('us-east-2')): # region shouldn't be here??
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

class SimpleStorageServiceSession(object):
    def __init__(self, service, user):
        self.user = user

        self._service = service

    def __repr__(self):
        return f'<SimpleStorageServiceSession: {self.user.display_name}@{self._service.implementation}>'

    def _arn(self, *segments):
        arn = 'arn:aws:s3'

        if segments:
            arn += '::'
            arn += ':'.join(segments)

        return arn

    def get_bucket(self, name):
        if name not in self._service._buckets:
            raise exceptions.S3Error('NoSuchBucket')

        return self._service._buckets[name]

    # def list_buckets(self):
    #     for bucket in self._service._buckets.values():
    #         yield bucket

    def list_buckets(self):
        for bucket in self._service._buckets.values():
            data = \
            {
                **bucket,
                'arn': self._arn(bucket.name),
            }

            yield data

    def create_bucket(self, name):
        if name in self._service._buckets:
            raise exceptions.S3Error('BucketAlreadyExists')

        bucket = Bucket(name)

        self._service._buckets[name] = bucket

        return bucket

    def delete_bucket(self, name):
        self.head_bucket(name)

        del self._service._buckets[name]

    def head_bucket(self, name, **kwargs):
        self.get_bucket(name)

# This class handles ACLs etc.?
class SimpleStorageService(object):
    implementation = 'memory'
    session_class = SimpleStorageServiceSession

    _buckets = {}

    def __repr__(self):
        return f'<SimpleStorageService: {self.implementation}>'

    def session(self, access_key):
        # user = User(access_key)
        user = FakeUser()

        return self.session_class(self, user)

    # Temp?
    def get_user(self, access_key):
        # return User(access_key)
        return FakeUser()
