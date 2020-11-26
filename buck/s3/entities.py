from .. import constants

import datetime

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
        return f'<Region: code={self.code!r} name={self.name!r}>'

    def __iter__(self):
        return utils.generator(self.__dict__.items())

class Object(object):
    def __init__(self, key, bucket):
        self.bucket = bucket

        self.key = key
        self.arn = f'{bucket.arn}:{self.key}'

        self.last_modified_date = Date(datetime.datetime.now()) # Temp

    def __repr__(self):
        return f'<Object: key={self.key!r} bucket={self.bucket.name!r}>'

    def __iter__(self):
        return utils.generator(self.__dict__.items())

class Bucket(object):
    __name = None
    __region = None
    __creation_date = None

    def __init__(self, name, region = Region('us-east-2')): # no default region?
        self.name = name
        self.region = region

        self.creation_date = Date(datetime.datetime.now())
        self.arn = f'arn:aws:s3::{self.name}'

    def __repr__(self):
        return f'<Bucket: name={self.name!r} region={self.region.code!r}>'
