from .. import constants

from . import validation
from .types import BucketName, ObjectKey, RegionName, RegionCode

import datetime
import pydantic
import string
import re

from typing import Union

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

class Date(BaseModel):
    datetime: datetime.datetime

    def __init__(self, dt: Union[datetime.datetime, None] = None):
        if dt is None:
            dt = datetime.datetime.now()

        super().__init__ \
        (
            datetime = dt,
        )

    def __repr__(self):
        return super().__repr__ \
        ({
            'date': str(self),
        })

    def __str__(self):
        return f'{self.datetime.isoformat()}Z'

class Region(BaseModel):
    code: RegionCode
    name: RegionName

    def __init__ \
            (
                self,
                code: Union[RegionCode, str, None] = None,
                name: Union[RegionName, str, None] = None,
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
    creation_date: Date

    @validation.validate_arguments
    def __init__ \
            (
                self,
                name: Union[BucketName, str],
                region: Region,
                creation_date: Union[Date, datetime.datetime],
            ):
        if isinstance(creation_date, datetime.datetime):
            creation_date = Date(creation_date)

        name = BucketName(name)

        super().__init__ \
        (
            name          = name,
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
    last_modified_date: Date

    @validation.validate_arguments
    def __init__ \
            (
                self,
                key: Union[ObjectKey, str],
                bucket: Bucket,
                last_modified_date: Union[Date, datetime.datetime],
            ):
        if isinstance(last_modified_date, datetime.datetime):
            last_modified_date = Date(last_modified_date)

        key = ObjectKey(key)

        super().__init__ \
        (
            key                = key,
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
