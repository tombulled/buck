from ..types import ObjectKey, DateTime
# from ..types import ObjectKey
# from .datetime import DateTime
from .bucket import Bucket
from . import base
# from . import validation

import datetime

class Object(base.BaseModel):
    bucket: Bucket
    key: str
    arn: str
    last_modified_date: DateTime

    # @validation.validate_arguments
    def __init__ \
            (
                self,
                key: str,
                bucket: Bucket,
                last_modified_date: datetime.datetime,
            ):
        super().__init__ \
        (
            key                = str(ObjectKey(key)),
            bucket             = bucket,
            arn                = f'{bucket.arn!s}:{key!s}',
            # last_modified_date = DateTime.fromdatetime(last_modified_date),
            # last_modified_date = DateTime(last_modified_date),
            last_modified_date = DateTime.fromdatetime(last_modified_date),
        )

    def __repr__(self):
        return super().__repr__ \
        (
            key    = self.key,
            bucket = self.bucket.name,
        )
