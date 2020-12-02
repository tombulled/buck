from .. import constants

from .types import BucketName, ObjectKey, RegionName, RegionCode

import datetime
import pydantic
import string
import re

import arrow

from typing import Union

class DateTime(arrow.Arrow):
    def __str__(self):
        return super().__str__() + 'Z'

class Config:
    arbitrary_types_allowed: bool = True

def validate_arguments(func):
    return pydantic.validate_arguments \
    (
        func   = func,
        config = Config,
    )

class BaseModel(pydantic.BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed: bool = True

    def __repr__(self, fields = None):
        if fields is None:
            fields = self.dict()

        class_name = self.__class__.__name__

        if not fields: return f'<{class_name} />'

        attributes = ' '.join \
        (
            f'{key}={val!r}'
            for key, val in fields.items()
        )

        return f'<{class_name}: {attributes}>'

    def __str__(self):
        return self.__repr__()

class Region(BaseModel):
    code: RegionCode
    name: RegionName

    def __init__ \
            (
                self,
                code: Union[str, None] = None,
                name: Union[str, None] = None,
            ):
        if code is not None:
            code = RegionCode(code)
            name = RegionName(constants.REGIONS.get(code))
        elif name is not None:
            name = RegionName(name)
            code = RegionCode(constants.REGIONS.inverse.get(name))

        super().__init__ \
        (
            code = code,
            name = name,
        )

    def __repr__(self):
        return super().__repr__ \
        ({
            'code': self.code,
            'name': self.name,
        })

class Bucket(BaseModel):
    name: BucketName
    region: Region
    arn: str
    creation_date: DateTime

    @validate_arguments
    def __init__ \
            (
                self,
                name: str,
                region: Region,
                creation_date: DateTime,
            ):
        super().__init__ \
        (
            name          = BucketName(name),
            region        = region,
            arn           = f'arn:aws:s3::{name!s}',
            creation_date = creation_date,
        )

    def __repr__(self):
        return super().__repr__ \
        ({
            'name': self.name,
            'region': self.region.code,
        })

class Object(BaseModel):
    bucket: Bucket
    key: ObjectKey
    arn: str
    last_modified_date: DateTime

    @validate_arguments
    def __init__ \
            (
                self,
                key: str,
                bucket: Bucket,
                last_modified_date: DateTime,
            ):
        super().__init__ \
        (
            key                = ObjectKey(key),
            bucket             = bucket,
            arn                = f'{bucket.arn!s}:{key!s}',
            last_modified_date = last_modified_date,
        )

    def __repr__(self):
        return super().__repr__ \
        ({
            'key': self.key,
            'bucket': self.bucket.name,
        })
