from .. import constants

import datetime
import pydantic
import string
import re

from typing import Union

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

    def __iter__(self):
        keys = \
        (
            'year',
            'month',
            'day',
            'hour',
            'minute',
            'second',
            'microsecond',
        )

        for key in keys:
            yield key, getattr(self, key)

class Region(pydantic.BaseModel):
    code: Union[str, None]
    name: Union[str, None]

    class Config:
        allow_mutation = False

    def __init__(self, code: str = None, name: str = None):
        if code is not None:
            name = constants.REGIONS.get(code)
        elif name is not None:
            code = constants.REGIONS.inverse.get(name)
        else:
            raise TypeError('missing 1 required argument: `code` or `name`')

        super().__init__ \
        (
            code = code,
            name = constants.REGIONS.get(code),
        )

    def __repr__(self):
        return f'<Region: code={self.code!r} name={self.name!r}>'

    @pydantic.validator('code')
    def validate_code(cls, value):
        if value is None: return

        if value not in constants.REGIONS:
            raise ValueError(f'Invalid region code: {value!r}')

        return value

    @pydantic.validator('name')
    def validate_name(cls, value):
        if value is None: return

        if value not in constants.REGIONS.inverse:
            raise ValueError(f'Invalid region name: {value!r}')

        return value

class Bucket(pydantic.BaseModel):
    name: str
    region: Region
    arn: str
    creation_date: Date

    class Config:
        allow_mutation = False

    @pydantic.validate_arguments
    def __init__ \
            (
                self,
                name: str,
                region: Region,
                creation_date: datetime.datetime,
            ):
        super().__init__ \
        (
            name = name,
            region = region,
            arn = f'arn:aws:s3::{name!s}',
            creation_date = Date(creation_date),
        )

    def __repr__(self):
        return f'<Bucket: name={self.name!r} region={self.region.code!r}>'

    @pydantic.validator('name')
    def valid_name(cls, value):
        # Rules for s3 bucket naming: (https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html#bucketnamingrules)
        #   * Bucket names must be between 3 and 63 characters long.
        #   * Bucket names can consist only of lowercase letters, numbers, dots (.), and hyphens (-).
        #   * Bucket names must begin and end with a letter or number.
        #   * Bucket names must not be formatted as an IP address (for example, 192.168.5.4).
        #   * Bucket names can't begin with xn-- (for buckets created after February 2020).

        len_min = 3
        len_max = 63
        acceptable_chars = tuple(f'{string.ascii_lowercase}{string.digits}.-')
        acceptable_end_chars = tuple(f'{string.ascii_lowercase}{string.digits}')
        unacceptable_formats = \
        {
            'an IP address': r'(\d)\.(\d)\.(\d)\.(\d)',
        }
        unacceptable_starts = ('xn--',)

        if not len_min <= len(value) <= len_max:
            raise ValueError(f'Invalid bucket name - must be between 3 and 63 characters long')

        for char in value:
            if char not in acceptable_chars:
                raise ValueError(f'Invalid bucket name - can consist only of lowercase letters, numbers, dots (.), and hyphens (-)')

        for char in (value[0], value[-1]):
            if char not in acceptable_end_chars:
                raise ValueError(f'Invalid bucket name - must begin and end with a letter or number')

        for format_name, format_pattern in unacceptable_formats.items():
            if re.match(format_pattern, value):
                raise ValueError(f'Invalid bucket name - must not be formatted as {format_name}')

        for unacceptable_start in unacceptable_starts:
            if value.startswith(unacceptable_start):
                raise ValueError(f'Invalid bucket name - can\'t begin with {unacceptable_start!r}')

        return value

class Object(pydantic.BaseModel):
    bucket: Bucket
    key: str
    arn: str
    last_modified_date: Date

    class Config:
        allow_mutation = False

    @pydantic.validate_arguments
    def __init__ \
            (
                self,
                key: str,
                bucket: Bucket,
                last_modified_date: datetime.datetime,
            ):
        super().__init__ \
        (
            key = key,
            bucket = bucket,
            arn = f'{bucket.arn!s}:{key!s}',
            last_modified_date = Date(last_modified_date),
        )

    def __repr__(self):
        return f'<Object: key={self.key!r} bucket={self.bucket.name!r}>'

    @pydantic.validator('key')
    def valid_key(cls, value):
        # Safe object key chars: (https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingMetadata.html#object-key-guidelines-safe-characters)
        #     * Alphanumeric characters:
        #         * 0-9
        #         * a-z
        #         * A-Z
        #     * Special characters:
        #         * Forward slash (/)
        #         * Exclamation point (!)
        #         * Hyphen (-)
        #         * Underscore (_)
        #         * Period (.)
        #         * Asterisk (*)
        #         * Single quote (')
        #         * Open parenthesis (()
        #         * Close parenthesis ())

        acceptable_chars = tuple(f'{string.ascii_letters}{string.digits}/!-_.*\'()')

        for char in value:
            if char not in acceptable_chars:
                raise ValueError('Unsafe object key')

        return value
